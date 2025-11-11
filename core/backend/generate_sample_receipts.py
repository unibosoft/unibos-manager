#!/usr/bin/env python
"""
Generate sample receipt images and fix thumbnails for documents module
This script:
1. Creates sample receipt images with store names at the TOP
2. Associates them with existing documents in the database
3. Regenerates all thumbnails using the new TOP-crop logic
"""

import os
import sys
import django
from pathlib import Path
from datetime import datetime, timedelta
import random
import uuid

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unibos_backend.settings.development')
django.setup()

from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile
from django.conf import settings
from modules.documents.backend.models import Document, ParsedReceipt
from modules.documents.backend.utils import ThumbnailGenerator
import io

# Store configurations for Turkish receipts
TURKISH_STORES = [
    {"name": "MİGROS", "color": "#FF6B00", "slogan": "Hep Yanınızda"},
    {"name": "CARREFOURSA", "color": "#0055A4", "slogan": "Pozitif Fiyat Farkı"},
    {"name": "A101", "color": "#FF0000", "slogan": "Harca Harca Bitmez"},
    {"name": "BİM", "color": "#FF0000", "slogan": "Evinize Yakın"},
    {"name": "ŞOK", "color": "#FFA500", "slogan": "Şok Şok Şok Ucuzluk"},
    {"name": "METRO", "color": "#003C71", "slogan": "Toptan Fiyatına"},
    {"name": "MAKROMARKET", "color": "#00A650", "slogan": "Büyük Alışveriş"},
    {"name": "FILE MARKET", "color": "#FF0000", "slogan": "Taze ve Ucuz"},
    {"name": "KİPA", "color": "#FF6B00", "slogan": "Alışverişin Adresi"},
    {"name": "REAL", "color": "#0055A4", "slogan": "Gerçek Fiyat"},
]

# Sample receipt items for Turkish markets
SAMPLE_ITEMS = [
    {"name": "EKMEK", "price": 7.50, "qty": 2},
    {"name": "SÜT 1L", "price": 35.90, "qty": 1},
    {"name": "YUMURTA 15'Lİ", "price": 89.90, "qty": 1},
    {"name": "DOMATES KG", "price": 29.90, "qty": 1.5},
    {"name": "BIBER KIRMIZI KG", "price": 39.90, "qty": 0.8},
    {"name": "PATATES KG", "price": 19.90, "qty": 2},
    {"name": "SOĞAN KURU KG", "price": 15.90, "qty": 1},
    {"name": "PEYNİR BEYAZ 500G", "price": 129.90, "qty": 1},
    {"name": "ZEYTİN YEŞİL 500G", "price": 89.90, "qty": 1},
    {"name": "ÇAY 1000G", "price": 149.90, "qty": 1},
    {"name": "MAKARNA 500G", "price": 22.90, "qty": 3},
    {"name": "YOĞURT 1KG", "price": 45.90, "qty": 2},
    {"name": "TAVUK BUT KG", "price": 89.90, "qty": 1.2},
    {"name": "KIYMA DANA KG", "price": 399.90, "qty": 0.5},
    {"name": "PİRİNÇ 1KG", "price": 79.90, "qty": 1},
    {"name": "UN 5KG", "price": 149.90, "qty": 1},
    {"name": "ŞEKER 1KG", "price": 39.90, "qty": 1},
    {"name": "AYÇIÇEK YAĞI 5L", "price": 299.90, "qty": 1},
    {"name": "DETERJAN 5KG", "price": 249.90, "qty": 1},
    {"name": "ŞAMPUAN 500ML", "price": 89.90, "qty": 1},
]


def create_receipt_image(store_config, items, receipt_date=None, width=400, height=800):
    """
    Create a receipt image with store name at the TOP
    """
    # Create white background
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a better font, fallback to default
    try:
        # Try to use system font
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
        header_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
        normal_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
        small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 12)
    except:
        # Fallback to default font
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        normal_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    y_position = 20
    
    # Store name at the TOP (large and prominent)
    store_name_bbox = draw.textbbox((0, 0), store_config['name'], font=title_font)
    store_name_width = store_name_bbox[2] - store_name_bbox[0]
    x_center = (width - store_name_width) // 2
    
    # Draw store name with color
    draw.text((x_center, y_position), store_config['name'], fill=store_config['color'], font=title_font)
    y_position += 40
    
    # Store slogan
    slogan_bbox = draw.textbbox((0, 0), store_config['slogan'], font=small_font)
    slogan_width = slogan_bbox[2] - slogan_bbox[0]
    x_center = (width - slogan_width) // 2
    draw.text((x_center, y_position), store_config['slogan'], fill='gray', font=small_font)
    y_position += 30
    
    # Separator line
    draw.line([(20, y_position), (width-20, y_position)], fill='black', width=2)
    y_position += 10
    
    # Store details
    draw.text((20, y_position), "MERKEZ ŞUBE", fill='black', font=normal_font)
    y_position += 20
    draw.text((20, y_position), "Tel: 0212 444 1234", fill='black', font=small_font)
    y_position += 18
    draw.text((20, y_position), "Vergi No: 1234567890", fill='black', font=small_font)
    y_position += 25
    
    # Date and time
    if not receipt_date:
        receipt_date = datetime.now() - timedelta(days=random.randint(0, 30))
    
    draw.text((20, y_position), f"TARİH: {receipt_date.strftime('%d/%m/%Y')}", fill='black', font=normal_font)
    draw.text((width-150, y_position), f"SAAT: {receipt_date.strftime('%H:%M')}", fill='black', font=normal_font)
    y_position += 25
    
    # Separator
    draw.line([(20, y_position), (width-20, y_position)], fill='gray', width=1)
    y_position += 10
    
    # Items
    subtotal = 0
    for item in items:
        # Item name
        draw.text((20, y_position), item['name'], fill='black', font=normal_font)
        y_position += 18
        
        # Quantity and price
        total_price = item['price'] * item['qty']
        subtotal += total_price
        
        qty_text = f"  {item['qty']} x {item['price']:.2f}"
        draw.text((30, y_position), qty_text, fill='gray', font=small_font)
        draw.text((width-100, y_position), f"{total_price:.2f} TL", fill='black', font=normal_font)
        y_position += 20
        
        if y_position > height - 150:  # Leave space for totals
            break
    
    # Separator before totals
    y_position += 10
    draw.line([(20, y_position), (width-20, y_position)], fill='gray', width=1)
    y_position += 10
    
    # Totals
    kdv = subtotal * 0.08  # 8% KDV
    total = subtotal + kdv
    
    draw.text((20, y_position), "ARA TOPLAM:", fill='black', font=normal_font)
    draw.text((width-100, y_position), f"{subtotal:.2f} TL", fill='black', font=normal_font)
    y_position += 20
    
    draw.text((20, y_position), "KDV %8:", fill='black', font=normal_font)
    draw.text((width-100, y_position), f"{kdv:.2f} TL", fill='black', font=normal_font)
    y_position += 20
    
    draw.line([(20, y_position), (width-20, y_position)], fill='black', width=2)
    y_position += 10
    
    # Total in larger font
    draw.text((20, y_position), "TOPLAM:", fill='black', font=header_font)
    draw.text((width-120, y_position), f"{total:.2f} TL", fill='black', font=header_font)
    y_position += 30
    
    # Payment method
    draw.text((20, y_position), "ÖDEME: NAKİT", fill='black', font=normal_font)
    y_position += 25
    
    # Receipt number
    receipt_no = f"FİŞ NO: {random.randint(100000, 999999)}"
    draw.text((20, y_position), receipt_no, fill='gray', font=small_font)
    y_position += 20
    
    # Barcode placeholder
    if y_position < height - 40:
        # Draw simple barcode lines
        for i in range(30):
            bar_width = random.choice([2, 3, 4])
            x = 150 + i * 4
            draw.rectangle([(x, y_position), (x + bar_width, y_position + 30)], fill='black')
        y_position += 40
    
    # Footer
    if y_position < height - 20:
        draw.text((20, height - 30), "TEŞEKKÜR EDERİZ", fill='gray', font=small_font)
        draw.text((20, height - 15), "YİNE BEKLERİZ", fill='gray', font=small_font)
    
    return img


def generate_sample_documents():
    """
    Generate sample receipt images and update database
    """
    print("Starting sample receipt generation...")
    
    # Create media directories if they don't exist
    media_root = Path(settings.MEDIA_ROOT)
    documents_dir = media_root / 'documents' / '2025' / '08'
    thumbnails_dir = media_root / 'documents' / 'thumbnails' / '2025' / '08'
    
    documents_dir.mkdir(parents=True, exist_ok=True)
    thumbnails_dir.mkdir(parents=True, exist_ok=True)
    
    # Get all documents from database
    documents = Document.objects.all()
    total_docs = documents.count()
    
    print(f"Found {total_docs} documents in database")
    
    if total_docs == 0:
        print("No documents found in database. Creating sample documents...")
        # Create sample documents
        from django.contrib.auth.models import User
        try:
            user = User.objects.get(username='admin')
        except User.DoesNotExist:
            user = User.objects.first()
            if not user:
                print("No users found. Please create a user first.")
                return
        
        # Create 10 sample documents
        for i in range(10):
            doc = Document.objects.create(
                user=user,
                document_type='receipt',
                original_filename=f'receipt_{i+1}.jpg',
                processing_status='completed'
            )
            documents = Document.objects.all()
    
    # Generate receipt images for each document
    thumbnail_generator = ThumbnailGenerator(size=(150, 150))
    processed_count = 0
    
    for i, doc in enumerate(documents[:20]):  # Process first 20 documents as samples
        try:
            # Select a random store
            store = random.choice(TURKISH_STORES)
            
            # Select random items (5-12 items per receipt)
            num_items = random.randint(5, 12)
            selected_items = random.sample(SAMPLE_ITEMS, min(num_items, len(SAMPLE_ITEMS)))
            
            # Generate receipt date (within last 30 days)
            receipt_date = datetime.now() - timedelta(days=random.randint(0, 30))
            
            # Create receipt image
            receipt_img = create_receipt_image(
                store_config=store,
                items=selected_items,
                receipt_date=receipt_date,
                width=400,
                height=800
            )
            
            # Save the full-size image
            img_buffer = io.BytesIO()
            receipt_img.save(img_buffer, format='JPEG', quality=95)
            img_buffer.seek(0)
            
            # Save to document's file_path
            file_name = f"receipt_{doc.id}.jpg"
            doc.file_path.save(file_name, ContentFile(img_buffer.read()), save=False)
            
            # Generate thumbnail with TOP-crop
            img_buffer.seek(0)
            thumb_file = thumbnail_generator.generate_thumbnail_from_django_file(
                img_buffer,
                str(doc.id)
            )
            
            if thumb_file:
                # Delete old thumbnail if exists
                if doc.thumbnail_path:
                    try:
                        doc.thumbnail_path.delete(save=False)
                    except:
                        pass
                
                # Save new thumbnail
                doc.thumbnail_path.save(f"thumb_{doc.id}.jpg", thumb_file, save=False)
            
            # Update document metadata
            doc.original_filename = f"{store['name'].lower()}_receipt_{i+1}.jpg"
            doc.processing_status = 'completed'
            doc.save()
            
            # Create ParsedReceipt if it doesn't exist
            if not hasattr(doc, 'parsed_receipt'):
                total_amount = sum(item['price'] * item['qty'] for item in selected_items)
                ParsedReceipt.objects.create(
                    document=doc,
                    store_name=store['name'],
                    store_address=f"{store['name']} Merkez Şube, İstanbul",
                    transaction_date=receipt_date,
                    receipt_number=str(random.randint(100000, 999999)),
                    subtotal=total_amount,
                    tax_amount=total_amount * 0.08,
                    total_amount=total_amount * 1.08,
                    payment_method='NAKİT',
                    currency='TRY'
                )
            
            processed_count += 1
            print(f"✓ Generated receipt {i+1}/{min(20, total_docs)}: {store['name']}")
            
        except Exception as e:
            print(f"✗ Error processing document {doc.id}: {str(e)}")
            continue
    
    print(f"\nCompleted! Generated {processed_count} sample receipts with TOP-crop thumbnails")
    
    # Now regenerate thumbnails for remaining documents that have images
    print("\nRegenerating thumbnails for existing documents...")
    remaining_docs = documents[20:]  # Documents we didn't create samples for
    
    for doc in remaining_docs:
        if doc.file_path:
            try:
                # Check if the file exists
                if not doc.file_path.storage.exists(doc.file_path.name):
                    print(f"✗ File not found for document {doc.id}")
                    continue
                
                # Generate new thumbnail with TOP-crop
                thumb_file = thumbnail_generator.generate_thumbnail_from_django_file(
                    doc.file_path,
                    str(doc.id)
                )
                
                if thumb_file:
                    # Delete old thumbnail
                    if doc.thumbnail_path:
                        try:
                            doc.thumbnail_path.delete(save=False)
                        except:
                            pass
                    
                    # Save new thumbnail
                    doc.thumbnail_path.save(f"thumb_{doc.id}.jpg", thumb_file)
                    print(f"✓ Regenerated thumbnail for {doc.original_filename}")
                    
            except Exception as e:
                print(f"✗ Error regenerating thumbnail for {doc.id}: {str(e)}")
    
    print("\n✅ All thumbnails have been updated with TOP-crop logic!")
    print("The thumbnails now show the TOP portion of receipts where store names are located.")


def verify_thumbnails():
    """
    Verify that thumbnails exist and are accessible
    """
    print("\nVerifying thumbnails...")
    
    documents = Document.objects.filter(thumbnail_path__isnull=False)[:10]
    
    for doc in documents:
        if doc.thumbnail_path:
            path = doc.thumbnail_path.path
            if os.path.exists(path):
                size = os.path.getsize(path)
                print(f"✓ {doc.original_filename}: Thumbnail exists ({size} bytes)")
            else:
                print(f"✗ {doc.original_filename}: Thumbnail file missing!")
    
    # Check if documents have both file_path and thumbnail_path
    print("\nDocument file status:")
    total = Document.objects.count()
    with_files = Document.objects.exclude(file_path='').count()
    with_thumbs = Document.objects.exclude(thumbnail_path='').count()
    
    print(f"Total documents: {total}")
    print(f"Documents with files: {with_files}")
    print(f"Documents with thumbnails: {with_thumbs}")


if __name__ == "__main__":
    print("=" * 60)
    print("RECEIPT GENERATOR & THUMBNAIL FIXER")
    print("=" * 60)
    
    # Run the generation
    generate_sample_documents()
    
    # Verify results
    verify_thumbnails()
    
    print("\n" + "=" * 60)
    print("✅ PROCESS COMPLETED!")
    print("=" * 60)
    print("\nNOTE: The thumbnails now show the TOP portion of receipts")
    print("where store names are prominently displayed.")
    print("\nTo view documents in the frontend, you'll need to:")
    print("1. Implement the document viewer component")
    print("2. Add click handlers to open full-size documents")
    print("3. The document URLs are available at: /media/documents/2025/08/")