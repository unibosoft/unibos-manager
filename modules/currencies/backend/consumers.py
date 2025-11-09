"""
WebSocket consumers for Currencies module
Provides real-time currency rates and portfolio updates
"""

import json
import asyncio
from decimal import Decimal
from datetime import datetime
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.cache import cache
from django.utils import timezone
from .models import Currency, ExchangeRate, Portfolio, CurrencyAlert
from .serializers import ExchangeRateSerializer, PortfolioSerializer


class CurrencyRatesConsumer(AsyncJsonWebsocketConsumer):
    """Real-time currency exchange rates"""
    
    async def connect(self):
        """Accept WebSocket connection"""
        self.user = self.scope["user"]
        self.room_group_name = "currency_rates"
        
        # Join currency rates group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial rates on connection
        await self.send_initial_rates()
        
        # Start periodic rate updates
        self.update_task = asyncio.create_task(self.periodic_rate_update())
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnect"""
        # Cancel periodic updates
        if hasattr(self, 'update_task'):
            self.update_task.cancel()
        
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive_json(self, content):
        """Handle incoming WebSocket messages"""
        message_type = content.get('type')
        
        if message_type == 'subscribe_pair':
            await self.subscribe_to_currency_pair(content.get('data'))
        elif message_type == 'unsubscribe_pair':
            await self.unsubscribe_from_currency_pair(content.get('data'))
        elif message_type == 'get_historical':
            await self.send_historical_data(content.get('data'))
    
    async def subscribe_to_currency_pair(self, data):
        """Subscribe to specific currency pair updates"""
        base_currency = data.get('base_currency')
        target_currency = data.get('target_currency')
        
        if base_currency and target_currency:
            # Store subscription in user's session
            subscriptions = self.scope.get('subscriptions', set())
            subscriptions.add(f"{base_currency}/{target_currency}")
            self.scope['subscriptions'] = subscriptions
            
            # Send current rate
            await self.send_currency_pair_rate(base_currency, target_currency)
    
    async def unsubscribe_from_currency_pair(self, data):
        """Unsubscribe from currency pair updates"""
        base_currency = data.get('base_currency')
        target_currency = data.get('target_currency')
        
        if base_currency and target_currency:
            subscriptions = self.scope.get('subscriptions', set())
            subscriptions.discard(f"{base_currency}/{target_currency}")
            self.scope['subscriptions'] = subscriptions
    
    async def send_initial_rates(self):
        """Send initial currency rates on connection"""
        rates = await self.get_latest_rates()
        await self.send_json({
            'type': 'initial_rates',
            'data': rates,
            'timestamp': timezone.now().isoformat()
        })
    
    async def send_currency_pair_rate(self, base_currency, target_currency):
        """Send specific currency pair rate"""
        rate = await self.get_currency_pair_rate(base_currency, target_currency)
        if rate:
            await self.send_json({
                'type': 'rate_update',
                'data': {
                    'pair': f"{base_currency}/{target_currency}",
                    'rate': rate
                },
                'timestamp': timezone.now().isoformat()
            })
    
    async def send_historical_data(self, data):
        """Send historical rate data"""
        base_currency = data.get('base_currency')
        target_currency = data.get('target_currency')
        period = data.get('period', '24h')
        
        historical_data = await self.get_historical_rates(
            base_currency, target_currency, period
        )
        
        await self.send_json({
            'type': 'historical_data',
            'data': {
                'pair': f"{base_currency}/{target_currency}",
                'period': period,
                'rates': historical_data
            },
            'timestamp': timezone.now().isoformat()
        })
    
    async def periodic_rate_update(self):
        """Send periodic rate updates"""
        while True:
            try:
                await asyncio.sleep(10)  # Update every 10 seconds
                
                # Get subscribed pairs
                subscriptions = self.scope.get('subscriptions', set())
                
                if subscriptions:
                    updates = {}
                    for pair in subscriptions:
                        base, target = pair.split('/')
                        rate = await self.get_currency_pair_rate(base, target)
                        if rate:
                            updates[pair] = rate
                    
                    if updates:
                        await self.send_json({
                            'type': 'rate_updates',
                            'data': updates,
                            'timestamp': timezone.now().isoformat()
                        })
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in periodic update: {e}")
                await asyncio.sleep(30)  # Wait longer on error
    
    # Group message handlers
    async def rate_update(self, event):
        """Handle rate update from group"""
        await self.send_json({
            'type': 'rate_update',
            'data': event['data'],
            'timestamp': event['timestamp']
        })
    
    @database_sync_to_async
    def get_latest_rates(self):
        """Get latest currency rates from database"""
        # Try cache first
        cached_rates = cache.get('latest_currency_rates')
        if cached_rates:
            return cached_rates
        
        # Get from database
        rates = {}
        latest_rates = ExchangeRate.objects.select_related(
            'base_currency', 'target_currency'
        ).filter(
            timestamp__gte=timezone.now() - timezone.timedelta(hours=1)
        ).order_by('base_currency', 'target_currency', '-timestamp').distinct(
            'base_currency', 'target_currency'
        )
        
        for rate in latest_rates:
            pair = f"{rate.base_currency.code}/{rate.target_currency.code}"
            rates[pair] = {
                'rate': float(rate.rate),
                'change_24h': float(rate.change_percentage_24h) if rate.change_percentage_24h else 0,
                'timestamp': rate.timestamp.isoformat()
            }
        
        # Cache for 1 minute
        cache.set('latest_currency_rates', rates, 60)
        return rates
    
    @database_sync_to_async
    def get_currency_pair_rate(self, base_currency, target_currency):
        """Get rate for specific currency pair"""
        cache_key = f'rate_{base_currency}_{target_currency}'
        cached_rate = cache.get(cache_key)
        
        if cached_rate:
            return cached_rate
        
        try:
            rate = ExchangeRate.objects.select_related(
                'base_currency', 'target_currency'
            ).filter(
                base_currency__code=base_currency,
                target_currency__code=target_currency
            ).latest('timestamp')
            
            rate_data = {
                'rate': float(rate.rate),
                'bid': float(rate.bid) if rate.bid else None,
                'ask': float(rate.ask) if rate.ask else None,
                'change_24h': float(rate.change_percentage_24h) if rate.change_percentage_24h else 0,
                'volume_24h': float(rate.volume_24h) if rate.volume_24h else 0,
                'timestamp': rate.timestamp.isoformat()
            }
            
            cache.set(cache_key, rate_data, 30)
            return rate_data
        except ExchangeRate.DoesNotExist:
            return None
    
    @database_sync_to_async
    def get_historical_rates(self, base_currency, target_currency, period):
        """Get historical rates for a currency pair"""
        # Determine time range
        end_time = timezone.now()
        if period == '24h':
            start_time = end_time - timezone.timedelta(days=1)
        elif period == '7d':
            start_time = end_time - timezone.timedelta(days=7)
        elif period == '1m':
            start_time = end_time - timezone.timedelta(days=30)
        else:
            start_time = end_time - timezone.timedelta(days=1)
        
        rates = ExchangeRate.objects.filter(
            base_currency__code=base_currency,
            target_currency__code=target_currency,
            timestamp__range=(start_time, end_time)
        ).order_by('timestamp').values('timestamp', 'rate')
        
        return [
            {
                'timestamp': rate['timestamp'].isoformat(),
                'rate': float(rate['rate'])
            }
            for rate in rates
        ]


class PortfolioConsumer(AsyncJsonWebsocketConsumer):
    """Real-time portfolio value updates"""
    
    async def connect(self):
        """Accept WebSocket connection"""
        self.user = self.scope["user"]
        self.portfolio_id = self.scope['url_route']['kwargs']['portfolio_id']
        self.room_group_name = f"portfolio_{self.portfolio_id}"
        
        # Verify portfolio ownership
        if not await self.verify_portfolio_access():
            await self.close()
            return
        
        # Join portfolio group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial portfolio state
        await self.send_portfolio_state()
        
        # Start periodic portfolio update
        self.update_task = asyncio.create_task(self.periodic_portfolio_update())
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnect"""
        if hasattr(self, 'update_task'):
            self.update_task.cancel()
        
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive_json(self, content):
        """Handle incoming WebSocket messages"""
        message_type = content.get('type')
        
        if message_type == 'refresh_portfolio':
            await self.send_portfolio_state()
        elif message_type == 'add_transaction':
            await self.handle_add_transaction(content.get('data'))
    
    async def send_portfolio_state(self):
        """Send current portfolio state"""
        portfolio_data = await self.get_portfolio_data()
        if portfolio_data:
            await self.send_json({
                'type': 'portfolio_update',
                'data': portfolio_data,
                'timestamp': timezone.now().isoformat()
            })
    
    async def periodic_portfolio_update(self):
        """Periodically update portfolio value"""
        while True:
            try:
                await asyncio.sleep(30)  # Update every 30 seconds
                await self.send_portfolio_state()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in portfolio update: {e}")
                await asyncio.sleep(60)
    
    async def handle_add_transaction(self, data):
        """Handle new transaction addition"""
        # This would typically validate and add the transaction
        # Then broadcast the update to all connected clients
        success = await self.add_transaction(data)
        
        if success:
            # Notify all group members
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'transaction_added',
                    'data': data,
                    'user': self.user.username,
                    'timestamp': timezone.now().isoformat()
                }
            )
    
    # Group message handlers
    async def portfolio_update(self, event):
        """Handle portfolio update from group"""
        await self.send_json({
            'type': 'portfolio_update',
            'data': event['data'],
            'timestamp': event['timestamp']
        })
    
    async def transaction_added(self, event):
        """Handle new transaction notification"""
        await self.send_json({
            'type': 'transaction_added',
            'data': event['data'],
            'user': event['user'],
            'timestamp': event['timestamp']
        })
        # Refresh portfolio state
        await self.send_portfolio_state()
    
    @database_sync_to_async
    def verify_portfolio_access(self):
        """Verify user has access to the portfolio"""
        try:
            portfolio = Portfolio.objects.get(
                id=self.portfolio_id,
                user=self.user
            )
            return True
        except Portfolio.DoesNotExist:
            return False
    
    @database_sync_to_async
    def get_portfolio_data(self):
        """Get portfolio data with current values"""
        try:
            portfolio = Portfolio.objects.prefetch_related(
                'holdings__currency',
                'transactions'
            ).get(id=self.portfolio_id)
            
            # Calculate current values
            total_value = portfolio.calculate_total_value()
            holdings_data = []
            
            for holding in portfolio.holdings.all():
                current_value = holding.get_current_value()
                holdings_data.append({
                    'currency': holding.currency.code,
                    'amount': float(holding.amount),
                    'average_buy_price': float(holding.average_buy_price),
                    'current_value': float(current_value) if current_value else 0,
                    'profit_loss': float(
                        (current_value - (holding.amount * holding.average_buy_price))
                    ) if current_value else 0
                })
            
            return {
                'id': str(portfolio.id),
                'name': portfolio.name,
                'total_value': float(total_value),
                'holdings': holdings_data,
                'last_updated': timezone.now().isoformat()
            }
        except Portfolio.DoesNotExist:
            return None
    
    @database_sync_to_async
    def add_transaction(self, data):
        """Add new transaction to portfolio"""
        # This is a simplified version - add proper validation
        try:
            portfolio = Portfolio.objects.get(id=self.portfolio_id)
            # Transaction creation logic here
            return True
        except Exception as e:
            print(f"Error adding transaction: {e}")
            return False


class CurrencyAlertsConsumer(AsyncJsonWebsocketConsumer):
    """Real-time currency alerts"""
    
    async def connect(self):
        """Accept WebSocket connection"""
        self.user = self.scope["user"]
        self.room_group_name = f"alerts_{self.user.id}"
        
        # Join user's alerts group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send active alerts
        await self.send_active_alerts()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnect"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive_json(self, content):
        """Handle incoming WebSocket messages"""
        message_type = content.get('type')
        
        if message_type == 'create_alert':
            await self.create_alert(content.get('data'))
        elif message_type == 'delete_alert':
            await self.delete_alert(content.get('alert_id'))
        elif message_type == 'toggle_alert':
            await self.toggle_alert(content.get('alert_id'))
    
    async def send_active_alerts(self):
        """Send user's active alerts"""
        alerts = await self.get_user_alerts()
        await self.send_json({
            'type': 'alerts_list',
            'data': alerts,
            'timestamp': timezone.now().isoformat()
        })
    
    async def create_alert(self, data):
        """Create new price alert"""
        alert = await self.create_currency_alert(data)
        if alert:
            await self.send_json({
                'type': 'alert_created',
                'data': alert,
                'timestamp': timezone.now().isoformat()
            })
    
    async def delete_alert(self, alert_id):
        """Delete price alert"""
        success = await self.delete_currency_alert(alert_id)
        if success:
            await self.send_json({
                'type': 'alert_deleted',
                'alert_id': alert_id,
                'timestamp': timezone.now().isoformat()
            })
    
    async def toggle_alert(self, alert_id):
        """Toggle alert active status"""
        alert = await self.toggle_currency_alert(alert_id)
        if alert:
            await self.send_json({
                'type': 'alert_updated',
                'data': alert,
                'timestamp': timezone.now().isoformat()
            })
    
    # Group message handlers
    async def alert_triggered(self, event):
        """Handle alert trigger notification"""
        await self.send_json({
            'type': 'alert_triggered',
            'data': event['data'],
            'timestamp': event['timestamp']
        })
    
    @database_sync_to_async
    def get_user_alerts(self):
        """Get user's currency alerts"""
        alerts = CurrencyAlert.objects.filter(
            user=self.user
        ).select_related('base_currency', 'target_currency')
        
        return [
            {
                'id': str(alert.id),
                'base_currency': alert.base_currency.code,
                'target_currency': alert.target_currency.code,
                'alert_type': alert.alert_type,
                'threshold_value': float(alert.threshold_value),
                'is_active': alert.is_active,
                'last_triggered': alert.last_triggered.isoformat() if alert.last_triggered else None
            }
            for alert in alerts
        ]
    
    @database_sync_to_async
    def create_currency_alert(self, data):
        """Create new currency alert"""
        try:
            alert = CurrencyAlert.objects.create(
                user=self.user,
                base_currency_id=data['base_currency'],
                target_currency_id=data['target_currency'],
                alert_type=data['alert_type'],
                threshold_value=data['threshold_value']
            )
            return {
                'id': str(alert.id),
                'base_currency': alert.base_currency.code,
                'target_currency': alert.target_currency.code,
                'alert_type': alert.alert_type,
                'threshold_value': float(alert.threshold_value),
                'is_active': alert.is_active
            }
        except Exception as e:
            print(f"Error creating alert: {e}")
            return None
    
    @database_sync_to_async
    def delete_currency_alert(self, alert_id):
        """Delete currency alert"""
        try:
            CurrencyAlert.objects.filter(
                id=alert_id,
                user=self.user
            ).delete()
            return True
        except Exception:
            return False
    
    @database_sync_to_async
    def toggle_currency_alert(self, alert_id):
        """Toggle alert active status"""
        try:
            alert = CurrencyAlert.objects.get(
                id=alert_id,
                user=self.user
            )
            alert.is_active = not alert.is_active
            alert.save()
            return {
                'id': str(alert.id),
                'is_active': alert.is_active
            }
        except CurrencyAlert.DoesNotExist:
            return None