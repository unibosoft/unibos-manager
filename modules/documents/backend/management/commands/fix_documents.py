"""
Django management command to fix documents and regenerate thumbnails
Usage: python manage.py fix_documents [--regenerate-all] [--create-samples]
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()
from django.core.files.base import ContentFile
from modules.documents.backend.models import Document, ParsedReceipt
from modules.documents.backend.thumbnail_service import EnhancedThumbnailGenerator
from PIL import Image, ImageDraw, ImageFont
import random
import io
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Fix documents and regenerate thumbnails'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--regenerate-all',
            action='store_true',
            help='Regenerate all thumbnails'
        )
        parser.add_argument(
            '--create-samples',
            action='store_true',
            help='Create sample receipt documents'
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Username to use for operations'
        )
        parser.add_argument(
            '--count',
            type=int,
            default=5,
            help='Number of sample documents to create'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('DOCUMENT FIXER'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        # Get user
        username = options.get('user')
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'User {username} not found'))
                return
        else:
            user = User.objects.first()
            if not user:
                self.stdout.write(self.style.ERROR('No users found in database'))
                return
        
        self.stdout.write(f'Using user: {user.username}')
        
        # Create sample documents if requested
        if options['create_samples']:
            self.create_sample_documents(user, options['count'])
        
        # Regenerate thumbnails if requested
        if options['regenerate_all']:
            self.regenerate_all_thumbnails(user)
        
        # Show statistics
        self.show_statistics(user)
    
    def create_sample_documents(self, user, count):
        """Create sample receipt documents with images"""
        self.stdout.write(f'\nCreating {count} sample documents...')
        
        stores = [
            {"name": "MIGROS", "color": "#FF6B00"},
            {"name": "CARREFOURSA", "color": "#0055A4"},
            {"name": "A101", "color": "#FF0000"},
            {"name": "BIM", "color": "#FF0000"},
            {"name": "ŞOK", "color": "#FFA500"},
        ]
        
        created = 0
        for i in range(count):
            try:
                # Select random store
                store = random.choice(stores)
                
                # Create receipt image
                img = self.create_receipt_image(store)
                
                # Save image to buffer
                img_buffer = io.BytesIO()
                img.save(img_buffer, format='JPEG', quality=95)
                img_buffer.seek(0)
                
                # Create document
                document = Document.objects.create(
                    user=user,
                    document_type='receipt',
                    original_filename=f'{store["name"].lower()}_receipt_{i+1}.jpg',
                    processing_status='completed'
                )
                
                # Save file
                document.file_path.save(
                    f'receipt_{document.id}.jpg',
                    ContentFile(img_buffer.read()),
                    save=False
                )
                
                # Generate thumbnail
                generator = EnhancedThumbnailGenerator()
                thumb_file = generator.generate_from_django_file(
                    document.file_path,
                    f'thumb_{document.id}.jpg'
                )
                
                if thumb_file:
                    document.thumbnail_path.save(
                        f'thumb_{document.id}.jpg',
                        thumb_file,
                        save=False
                    )
                
                # Add sample OCR text
                document.ocr_text = f"""
                {store['name']} MARKET
                Merkez Şube
                Tel: 0212 444 1234
                
                TARİH: {datetime.now().strftime('%d/%m/%Y')}
                SAAT: {datetime.now().strftime('%H:%M')}
                
                EKMEK 2 x 7.50 = 15.00 TL
                SÜT 1L 1 x 35.90 = 35.90 TL
                YUMURTA 15'Lİ 1 x 89.90 = 89.90 TL
                
                ARA TOPLAM: 140.80 TL
                KDV %8: 11.26 TL
                TOPLAM: 152.06 TL
                
                ÖDEME: NAKİT
                FİŞ NO: {random.randint(100000, 999999)}
                
                TEŞEKKÜR EDERİZ
                """
                document.ocr_confidence = 95.0
                document.save()
                
                # Create parsed receipt
                ParsedReceipt.objects.create(
                    document=document,
                    store_name=store['name'],
                    transaction_date=timezone.now(),
                    total_amount=152.06,
                    payment_method='NAKİT',
                    currency='TRY'
                )
                
                created += 1
                self.stdout.write(f'  ✓ Created {store["name"]} receipt')
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ Error creating document: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Created {created} sample documents'))
    
    def create_receipt_image(self, store_config, width=400, height=600):
        """Create a simple receipt image"""
        # Create white background
        img = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(img)
        
        # Try to use a font
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
            small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
        except:
            font = ImageFont.load_default()
            small_font = font
        
        y = 20
        
        # Store name at top
        store_name = store_config['name']
        text_bbox = draw.textbbox((0, 0), store_name, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        x = (width - text_width) // 2
        draw.text((x, y), store_name, fill=store_config['color'], font=font)
        y += 40
        
        # Store details
        draw.text((20, y), "MERKEZ ŞUBE", fill='black', font=small_font)
        y += 25
        draw.text((20, y), "Tel: 0212 444 1234", fill='gray', font=small_font)
        y += 35
        
        # Date
        draw.text((20, y), f"TARİH: {datetime.now().strftime('%d/%m/%Y')}", fill='black', font=small_font)
        y += 20
        draw.text((20, y), f"SAAT: {datetime.now().strftime('%H:%M')}", fill='black', font=small_font)
        y += 30
        
        # Line
        draw.line([(20, y), (width-20, y)], fill='gray', width=1)
        y += 20
        
        # Items
        items = [
            ("EKMEK", "2 x 7.50", "15.00"),
            ("SÜT 1L", "1 x 35.90", "35.90"),
            ("YUMURTA", "1 x 89.90", "89.90"),
        ]
        
        for item_name, qty, price in items:
            draw.text((20, y), item_name, fill='black', font=small_font)
            draw.text((width-100, y), f"{price} TL", fill='black', font=small_font)
            y += 25
        
        # Total
        y += 10
        draw.line([(20, y), (width-20, y)], fill='black', width=2)
        y += 15
        draw.text((20, y), "TOPLAM:", fill='black', font=font)
        draw.text((width-120, y), "140.80 TL", fill='black', font=font)
        
        return img
    
    def regenerate_all_thumbnails(self, user):
        """Regenerate all thumbnails for user's documents"""
        self.stdout.write('\nRegenerating thumbnails...')
        
        documents = Document.objects.filter(user=user)
        generator = EnhancedThumbnailGenerator()
        
        results = generator.regenerate_all_thumbnails(documents, force=True)
        
        self.stdout.write(f'  ✓ Success: {results["success"]}')
        self.stdout.write(f'  ✗ Failed: {results["failed"]}')
        self.stdout.write(f'  - Skipped: {results["skipped"]}')
        
        if results['errors']:
            self.stdout.write(self.style.WARNING('\nErrors:'))
            for error in results['errors'][:5]:
                self.stdout.write(f'  - {error}')
    
    def show_statistics(self, user):
        """Show document statistics"""
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write('DOCUMENT STATISTICS')
        self.stdout.write('=' * 60)
        
        total = Document.objects.filter(user=user).count()
        with_thumbnails = Document.objects.filter(
            user=user,
            thumbnail_path__isnull=False
        ).exclude(thumbnail_path='').count()
        with_ocr = Document.objects.filter(
            user=user,
            ocr_text__isnull=False
        ).exclude(ocr_text='').count()
        
        self.stdout.write(f'Total documents: {total}')
        self.stdout.write(f'With thumbnails: {with_thumbnails}')
        self.stdout.write(f'With OCR text: {with_ocr}')
        
        # Status breakdown
        self.stdout.write('\nStatus breakdown:')
        for status, label in Document._meta.get_field('processing_status').choices:
            count = Document.objects.filter(user=user, processing_status=status).count()
            self.stdout.write(f'  {label}: {count}')
        
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('✓ COMPLETE'))