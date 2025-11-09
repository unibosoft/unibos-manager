"""
Fetch earthquake data from multiple sources
Run every 5 minutes via cron job
"""

import requests
import re
import json
from datetime import datetime, timedelta
from decimal import Decimal
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from django.utils import timezone
from modules.birlikteyiz.backend.models import Earthquake, EarthquakeDataSource, CronJob


class Command(BaseCommand):
    help = 'Fetch earthquake data from all configured sources'

    def add_arguments(self, parser):
        parser.add_argument(
            '--source',
            type=str,
            help='Fetch from a specific source only (KANDILLI, AFAD, IRIS, USGS, GFZ)'
        )

    def __init__(self):
        super().__init__()
        self.sources = {
            'KANDILLI': {
                'url': 'http://www.koeri.boun.edu.tr/scripts/lst5.asp',
                'parser': self.parse_kandilli
            },
            'AFAD': {
                'url': 'https://servisnet.afad.gov.tr/apigateway/deprem/apiv2/event/filter',
                'parser': self.parse_afad
            },
            'IRIS': {  # Incorporated Research Institutions for Seismology - Global data
                'url': 'http://service.iris.edu/fdsnws/event/1/query',
                'parser': self.parse_iris
            },
            'USGS': {
                'url': 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson',
                'parser': self.parse_usgs
            },
            'GFZ': {  # German Research Centre for Geosciences - European data
                'url': 'http://geofon.gfz-potsdam.de/eqinfo/list.php',
                'parser': self.parse_gfz
            }
        }
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(f'Starting earthquake data fetch at {timezone.now()}'))

        # Update cron job status
        cron_job, _ = CronJob.objects.get_or_create(
            name='Fetch Earthquakes',
            defaults={
                'command': 'fetch_earthquakes',
                'schedule': '*/5 * * * *'  # Every 5 minutes
            }
        )
        cron_job.status = 'running'
        cron_job.last_run = timezone.now()
        cron_job.save()

        total_new = 0
        total_updated = 0
        errors = []

        # Filter sources if --source parameter is provided
        source_filter = options.get('source')
        sources_to_fetch = {}

        if source_filter:
            # Fetch only the specified source
            source_filter_upper = source_filter.upper()
            if source_filter_upper in self.sources:
                sources_to_fetch = {source_filter_upper: self.sources[source_filter_upper]}
                self.stdout.write(f'Fetching from single source: {source_filter_upper}')
            else:
                self.stdout.write(self.style.ERROR(f'Unknown source: {source_filter}. Available: {", ".join(self.sources.keys())}'))
                return
        else:
            # Fetch from all sources
            sources_to_fetch = self.sources

        for source_name, config in sources_to_fetch.items():
            data_source = None
            try:
                # Get or create data source with proper defaults
                data_source, created = EarthquakeDataSource.objects.get_or_create(
                    name=source_name,
                    defaults={
                        'url': config['url'],
                        'is_active': True,
                        'fetch_interval_minutes': 5,
                        'min_magnitude': Decimal('2.5'),
                        'max_results': 100,
                        'use_geographic_filter': source_name in ['KANDILLI', 'AFAD'],  # Turkey-only sources
                        'filter_min_lat': Decimal('35.0') if source_name in ['KANDILLI', 'AFAD'] else None,
                        'filter_max_lat': Decimal('43.0') if source_name in ['KANDILLI', 'AFAD'] else None,
                        'filter_min_lon': Decimal('25.0') if source_name in ['KANDILLI', 'AFAD'] else None,
                        'filter_max_lon': Decimal('45.0') if source_name in ['KANDILLI', 'AFAD'] else None,
                        'filter_region_name': 'Türkiye' if source_name in ['KANDILLI', 'AFAD'] else 'Küresel',
                        'description': self._get_source_description(source_name)
                    }
                )

                if created:
                    self.stdout.write(f'Created data source: {source_name}')

                if not data_source.is_active:
                    self.stdout.write(f'Skipping inactive source: {source_name}')
                    continue

                self.stdout.write(f'Fetching from {source_name}...')

                # Track response time
                start_time = timezone.now()

                # Fetch and parse data
                new_count, updated_count = config['parser'](config['url'], data_source)

                # Calculate response time
                response_time = (timezone.now() - start_time).total_seconds()

                # Update source stats
                data_source.last_fetch = timezone.now()
                data_source.last_success = timezone.now()
                data_source.fetch_count += 1
                data_source.success_count += 1
                data_source.total_earthquakes_fetched += new_count
                data_source.last_response_time = response_time

                # Update average response time
                if data_source.avg_response_time:
                    data_source.avg_response_time = (data_source.avg_response_time + response_time) / 2
                else:
                    data_source.avg_response_time = response_time

                data_source.last_error = None  # Clear error on success
                data_source.save()

                total_new += new_count
                total_updated += updated_count

                self.stdout.write(
                    self.style.SUCCESS(
                        f'{source_name}: {new_count} new, {updated_count} updated ({response_time:.2f}s)'
                    )
                )

            except Exception as e:
                error_msg = f'{source_name}: {str(e)}'
                errors.append(error_msg)
                self.stdout.write(self.style.ERROR(error_msg))

                # Update source error info
                if data_source:
                    data_source.last_error = str(e)
                    data_source.last_error_time = timezone.now()
                    data_source.error_count += 1
                    data_source.fetch_count += 1
                    data_source.save()
        
        # Update cron job result
        cron_job.status = 'failed' if errors else 'success'
        cron_job.run_count += 1
        if not errors:
            cron_job.success_count += 1
        else:
            cron_job.error_count += 1
        
        result_msg = f'Fetched {total_new} new, {total_updated} updated earthquakes'
        if errors:
            result_msg += f'\\nErrors: {"; ".join(errors)}'
        
        cron_job.last_result = result_msg
        cron_job.next_run = timezone.now() + timedelta(minutes=5)
        cron_job.save()
        
        self.stdout.write(
            self.style.SUCCESS(f'Completed: {result_msg}')
        )

    def _get_source_description(self, source_name):
        """Get description for data source"""
        descriptions = {
            'KANDILLI': 'Boğaziçi Üniversitesi Kandilli Rasathanesi ve Deprem Araştırma Enstitüsü - Türkiye deprem verileri',
            'AFAD': 'Afet ve Acil Durum Yönetimi Başkanlığı - Türkiye resmi deprem verileri',
            'IRIS': 'Incorporated Research Institutions for Seismology - Küresel deprem verileri',
            'USGS': 'United States Geological Survey - Küresel deprem verileri',
            'GFZ': 'German Research Centre for Geosciences - Avrupa deprem verileri',
            'EMSC': 'European-Mediterranean Seismological Centre - Gerçek zamanlı küresel deprem verileri (WebSocket)'
        }
        return descriptions.get(source_name, '')

    def parse_kandilli(self, url, data_source):
        """Parse Kandilli Rasathanesi data"""
        new_count = 0
        updated_count = 0
        
        try:
            response = requests.get(url, timeout=10)
            response.encoding = 'windows-1254'  # Turkish encoding
            
            # Parse HTML to find the pre-formatted text section
            soup = BeautifulSoup(response.text, 'html.parser')
            pre_element = soup.find('pre')
            
            if not pre_element:
                self.stdout.write('Kandilli: Could not find PRE element in HTML')
                return 0, 0
            
            lines = pre_element.text.split('\n')
        
            # Skip header lines and find data
            data_started = False
            for line in lines:
                # Look for the separator line to know when data starts
                if '------' in line and not data_started:
                    data_started = True
                    continue
                
                if not data_started or not line.strip():
                    continue
                
                try:
                    # Parse fixed-width format or space-separated
                    parts = line.split()
                    if len(parts) < 7:
                        continue
                    
                    # Expected format: Date Time Lat Lon Depth MD ML MW Location...
                    date_str = parts[0]
                    time_str = parts[1]
                    lat = parts[2]
                    lon = parts[3]
                    depth = parts[4]
                    
                    # Find magnitude columns (MD, ML, MW)
                    magnitude = None
                    location_start = 8  # Default position after MW column
                    
                    # Try to parse MD (position 5)
                    if len(parts) > 5 and parts[5] != '-.-':
                        try:
                            magnitude = float(parts[5])
                        except ValueError:
                            pass
                    
                    # Try ML if MD not found (position 6)
                    if not magnitude and len(parts) > 6 and parts[6] != '-.-':
                        try:
                            magnitude = float(parts[6])
                        except ValueError:
                            pass
                    
                    # Try MW if neither MD nor ML found (position 7)
                    if not magnitude and len(parts) > 7 and parts[7] != '-.-':
                        try:
                            magnitude = float(parts[7])
                        except ValueError:
                            pass
                    
                    if not magnitude:
                        continue
                    
                    # Rest is location
                    location = ' '.join(parts[location_start:]) if location_start < len(parts) else 'Unknown'
                
                    # Validate basic fields
                    if not all([date_str, time_str, lat, lon, depth]):
                        continue
                
                    # Parse datetime
                    dt_str = f"{date_str} {time_str}"
                    occurred_at = datetime.strptime(dt_str, "%Y.%m.%d %H:%M:%S")
                    # Kandilli uses Turkey time (UTC+3)
                    import pytz
                    turkey_tz = pytz.timezone('Europe/Istanbul')
                    occurred_at = turkey_tz.localize(occurred_at)
                
                    # Create unique ID
                    unique_id = f"KANDILLI_{date_str}_{time_str}_{lat}_{lon}"
                
                    # Save earthquake
                    earthquake, created = Earthquake.objects.update_or_create(
                        unique_id=unique_id,
                        defaults={
                            'source': 'KANDILLI',
                            'magnitude': Decimal(str(magnitude)),
                            'depth': Decimal(depth),
                            'latitude': Decimal(lat),
                            'longitude': Decimal(lon),
                            'location': location.replace('�lk sel', 'İlksel'),  # Fix encoding
                            'occurred_at': occurred_at,
                            'raw_data': {'original_line': line}
                        }
                    )
                
                    if created:
                        new_count += 1
                    else:
                        updated_count += 1
                        
                except Exception as e:
                    # Skip line if parsing fails
                    continue
                    
        except Exception as e:
            self.stdout.write(f'Error fetching Kandilli data: {e}')
        
        return new_count, updated_count
    
    def parse_afad(self, url, data_source):
        """Parse AFAD data"""
        new_count = 0
        updated_count = 0

        try:
            # Use the new AFAD API endpoint with proper headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
                'Connection': 'close'  # Prevent connection reset
            }

            params = {
                'start': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                'end': datetime.now().strftime('%Y-%m-%d'),
                'minmag': float(data_source.min_magnitude) if data_source.min_magnitude else 2.0,
                'limit': data_source.max_results if data_source.max_results else 100
            }

            response = requests.get(url, params=params, headers=headers, timeout=15)
            response.raise_for_status()

            data = response.json()

            # Handle both array and object responses
            events = data if isinstance(data, list) else data.get('data', [])

            for event in events:
                try:
                    # AFAD API field mapping
                    event_id = event.get('eventID') or event.get('id')
                    if not event_id:
                        continue

                    unique_id = f"AFAD_{event_id}"

                    # Parse datetime - AFAD uses ISO format
                    date_str = event.get('date') or event.get('eventDate') or event.get('time')
                    if date_str:
                        # Remove Z and parse
                        date_str = date_str.replace('Z', '').replace('+00:00', '')
                        try:
                            occurred_at = timezone.make_aware(datetime.fromisoformat(date_str))
                        except:
                            occurred_at = timezone.now()
                    else:
                        occurred_at = timezone.now()

                    earthquake, created = Earthquake.objects.update_or_create(
                        unique_id=unique_id,
                        defaults={
                            'source': 'AFAD',
                            'source_id': str(event_id),
                            'magnitude': Decimal(str(event.get('magnitude', event.get('mag', 0)))),
                            'depth': Decimal(str(event.get('depth', 0))),
                            'latitude': Decimal(str(event.get('latitude', event.get('lat', 0)))),
                            'longitude': Decimal(str(event.get('longitude', event.get('lon', 0)))),
                            'location': event.get('location', event.get('place', 'Unknown')),
                            'city': event.get('province', event.get('city')),
                            'district': event.get('district'),
                            'occurred_at': occurred_at,
                            'raw_data': event
                        }
                    )

                    if created:
                        new_count += 1
                    else:
                        updated_count += 1

                except Exception as e:
                    self.stdout.write(f'Error parsing AFAD event: {e}')
                    continue

        except requests.exceptions.RequestException as e:
            self.stdout.write(f'Error fetching AFAD data: {e}')
            raise

        return new_count, updated_count
    
    def parse_iris(self, url, data_source):
        """Parse IRIS (Incorporated Research Institutions for Seismology) data"""
        new_count = 0
        updated_count = 0

        try:
            # Build params from data source configuration
            params = {
                'format': 'text',
                'minmag': float(data_source.min_magnitude) if data_source.min_magnitude else 3.0,
                'starttime': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                'endtime': datetime.now().strftime('%Y-%m-%d'),
                'orderby': 'time-desc',
                'limit': data_source.max_results if data_source.max_results else 100
            }

            # Apply geographic filter if configured
            if data_source.use_geographic_filter:
                bounds = data_source.get_geographic_bounds()
                if bounds and all(bounds.values()):
                    params.update({
                        'minlat': bounds['min_lat'],
                        'maxlat': bounds['max_lat'],
                        'minlon': bounds['min_lon'],
                        'maxlon': bounds['max_lon']
                    })

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Connection': 'close'
            }

            response = requests.get(url, params=params, headers=headers, timeout=15)
            
            # Parse text format (pipe-separated values)
            lines = response.text.strip().split('\n')
            
            # Skip header line
            for line in lines[1:]:
                if not line.strip():
                    continue
                
                try:
                    # Parse pipe-separated values
                    parts = line.split('|')
                    if len(parts) < 13:
                        continue
                    
                    event_id = parts[0]
                    time_str = parts[1]
                    lat = parts[2]
                    lon = parts[3]
                    depth = parts[4]
                    magnitude = parts[10]
                    location = parts[12] if len(parts) > 12 else 'Unknown'
                    
                    # Parse datetime
                    occurred_at = datetime.fromisoformat(time_str.replace('T', ' ').replace('Z', '+00:00'))
                    
                    # Create unique ID
                    unique_id = f"IRIS_{event_id}"
                    
                    earthquake, created = Earthquake.objects.update_or_create(
                        unique_id=unique_id,
                        defaults={
                            'source': 'IRIS',
                            'source_id': event_id,
                            'magnitude': Decimal(magnitude),
                            'depth': Decimal(depth),
                            'latitude': Decimal(lat),
                            'longitude': Decimal(lon),
                            'location': location.strip(),
                            'occurred_at': timezone.make_aware(occurred_at.replace(tzinfo=None)),
                            'raw_data': {'original_line': line}
                        }
                    )
                    
                    if created:
                        new_count += 1
                    else:
                        updated_count += 1
                        
                except Exception as e:
                    continue
                    
        except Exception as e:
            self.stdout.write(f'Error fetching IRIS data: {e}')
        
        return new_count, updated_count
    
    def parse_usgs(self, url, data_source):
        """Parse USGS GeoJSON data"""
        new_count = 0
        updated_count = 0

        response = requests.get(url, timeout=10)
        data = response.json()

        # Get geographic filter bounds if configured
        bounds = None
        if data_source.use_geographic_filter:
            bounds = data_source.get_geographic_bounds()

        for feature in data['features']:
            props = feature['properties']
            coords = feature['geometry']['coordinates']

            lon, lat, depth = coords

            # Apply geographic filter if configured
            if bounds and all(bounds.values()):
                if not (bounds['min_lat'] <= lat <= bounds['max_lat'] and
                        bounds['min_lon'] <= lon <= bounds['max_lon']):
                    continue
            
            try:
                unique_id = f"USGS_{feature['id']}"
                import pytz
                occurred_at = datetime.fromtimestamp(props['time'] / 1000, tz=pytz.UTC)
                
                earthquake, created = Earthquake.objects.update_or_create(
                    unique_id=unique_id,
                    defaults={
                        'source': 'USGS',
                        'source_id': feature['id'],
                        'magnitude': Decimal(str(props['mag'])),
                        'depth': Decimal(str(depth)),
                        'latitude': Decimal(str(lat)),
                        'longitude': Decimal(str(lon)),
                        'location': props['place'],
                        'occurred_at': occurred_at,
                        'intensity': props.get('mmi'),
                        'felt_reports': props.get('felt') or 0,  # Handle None values
                        'raw_data': feature
                    }
                )
                
                if created:
                    new_count += 1
                else:
                    updated_count += 1
                    
            except Exception as e:
                self.stdout.write(f'Error parsing USGS event: {e}')
                continue
        
        return new_count, updated_count
    
    def parse_gfz(self, url, data_source):
        """Parse GFZ (German Research Centre for Geosciences) data"""
        new_count = 0
        updated_count = 0

        try:
            # GFZ provides data via their FDSNWS service
            api_url = 'https://geofon.gfz-potsdam.de/fdsnws/event/1/query'
            params = {
                'format': 'text',
                'minmag': float(data_source.min_magnitude) if data_source.min_magnitude else 3.0,
                'starttime': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                'endtime': datetime.now().strftime('%Y-%m-%d'),
                'orderby': 'time',
                'limit': data_source.max_results if data_source.max_results else 100
            }

            # Apply geographic filter if configured
            if data_source.use_geographic_filter:
                bounds = data_source.get_geographic_bounds()
                if bounds and all(bounds.values()):
                    params.update({
                        'minlat': bounds['min_lat'],
                        'maxlat': bounds['max_lat'],
                        'minlon': bounds['min_lon'],
                        'maxlon': bounds['max_lon']
                    })

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Connection': 'close'
            }

            response = requests.get(api_url, params=params, headers=headers, timeout=15)
            
            # Parse text format
            lines = response.text.strip().split('\n')
            
            # Skip header if present
            for line in lines:
                if not line.strip() or line.startswith('#'):
                    continue
                
                try:
                    # Parse pipe-separated values
                    parts = line.split('|')
                    if len(parts) < 13:
                        continue
                    
                    event_id = parts[0]
                    time_str = parts[1]
                    lat = parts[2]
                    lon = parts[3]
                    depth = parts[4]
                    magnitude = parts[10]
                    location = parts[12] if len(parts) > 12 else 'Unknown'
                    
                    # Parse datetime
                    occurred_at = datetime.fromisoformat(time_str.replace('T', ' ').replace('Z', ''))
                    
                    # Create unique ID
                    unique_id = f"GFZ_{event_id}"
                    
                    earthquake, created = Earthquake.objects.update_or_create(
                        unique_id=unique_id,
                        defaults={
                            'source': 'GFZ',
                            'source_id': event_id,
                            'magnitude': Decimal(magnitude),
                            'depth': Decimal(depth),
                            'latitude': Decimal(lat),
                            'longitude': Decimal(lon),
                            'location': location.strip(),
                            'occurred_at': timezone.make_aware(occurred_at),
                            'raw_data': {'original_line': line}
                        }
                    )
                    
                    if created:
                        new_count += 1
                    else:
                        updated_count += 1
                        
                except Exception as e:
                    continue
                    
        except Exception as e:
            self.stdout.write(f'Error fetching GFZ data: {e}')
        
        return new_count, updated_count