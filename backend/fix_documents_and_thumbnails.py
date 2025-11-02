#!/usr/bin/env python
"""
Fix documents and thumbnails without full Django setup
Creates sample receipt images and regenerates thumbnails with TOP-crop

NOTE: This is a legacy utility script that uses SQLite for direct database access
without Django ORM. The main application uses PostgreSQL exclusively.
This script should be updated to use Django ORM or deprecated.
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import random
import io
import sqlite3  # Legacy - TODO: migrate to Django ORM with PostgreSQL
import json

# Add PIL import
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("ERROR: PIL/Pillow not installed. Installing...")
    os.system("pip install Pillow")
    from PIL import Image, ImageDraw, ImageFont

# Configuration
BASE_DIR = Path(__file__).resolve().parent
MEDIA_ROOT = BASE_DIR / 'media'
DB_PATH = BASE_DIR / 'db.sqlite3'

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
]

# Sample receipt items
SAMPLE_ITEMS = [
    {"name": "EKMEK", "price": 7.50, "qty": 2},
    {"name": "SÜT 1L", "price": 35.90, "qty": 1},
    {"name": "YUMURTA 15'Lİ", "price": 89.90, "qty": 1},
    {"name": "DOMATES KG", "price": 29.90, "qty": 1.5},
    {"name": "PEYNİR BEYAZ 500G", "price": 129.90, "qty": 1},
    {"name": "ÇAY 1000G", "price": 149.90, "qty": 1},
    {"name": "MAKARNA 500G", "price": 22.90, "qty": 3},
    {"name": "TAVUK BUT KG", "price": 89.90, "qty": 1.2},
    {"name": "PİRİNÇ 1KG", "price": 79.90, "qty": 1},
    {"name": "DETERJAN 5KG", "price": 249.90, "qty": 1},
]


def create_receipt_image(store_config, items, width=400, height=800):
    """Create a receipt image with store name at the TOP"""
    # Create white background
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a better font, fallback to default
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
        header_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
        normal_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
        small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 12)
    except:
        from PIL import ImageFont
        title_font = ImageFont.load_default()
        header_font = title_font
        normal_font = title_font
        small_font = title_font
    
    y_position = 20
    
    # Store name at the TOP (large and prominent)
    store_name = store_config['name']
    # Estimate text width (approximate)
    text_width = len(store_name) * 20
    x_center = (width - text_width) // 2
    
    # Draw store name with color
    draw.text((x_center, y_position), store_name, fill=store_config['color'], font=title_font)
    y_position += 45
    
    # Store slogan
    slogan = store_config['slogan']
    slogan_width = len(slogan) * 8
    x_center = (width - slogan_width) // 2
    draw.text((x_center, y_position), slogan, fill='gray', font=small_font)
    y_position += 30
    
    # Separator line
    draw.line([(20, y_position), (width-20, y_position)], fill='black', width=2)
    y_position += 15
    
    # Store details
    draw.text((20, y_position), "MERKEZ ŞUBE", fill='black', font=normal_font)
    y_position += 20
    draw.text((20, y_position), "Tel: 0212 444 1234", fill='black', font=small_font)
    y_position += 20
    draw.text((20, y_position), "Vergi No: 1234567890", fill='black', font=small_font)
    y_position += 30
    
    # Date and time
    receipt_date = datetime.now() - timedelta(days=random.randint(0, 30))
    draw.text((20, y_position), f"TARİH: {receipt_date.strftime('%d/%m/%Y')}", fill='black', font=normal_font)
    draw.text((width-150, y_position), f"SAAT: {receipt_date.strftime('%H:%M')}", fill='black', font=normal_font)
    y_position += 30
    
    # Separator
    draw.line([(20, y_position), (width-20, y_position)], fill='gray', width=1)
    y_position += 15
    
    # Items
    subtotal = 0
    for item in items[:8]:  # Limit items to fit
        # Item name
        draw.text((20, y_position), item['name'], fill='black', font=normal_font)
        y_position += 20
        
        # Quantity and price
        total_price = item['price'] * item['qty']
        subtotal += total_price
        
        qty_text = f"  {item['qty']} x {item['price']:.2f}"
        draw.text((30, y_position), qty_text, fill='gray', font=small_font)
        draw.text((width-100, y_position), f"{total_price:.2f} TL", fill='black', font=normal_font)
        y_position += 25
    
    # Separator before totals
    y_position += 10
    draw.line([(20, y_position), (width-20, y_position)], fill='gray', width=1)
    y_position += 15
    
    # Totals
    kdv = subtotal * 0.08
    total = subtotal + kdv
    
    draw.text((20, y_position), "ARA TOPLAM:", fill='black', font=normal_font)
    draw.text((width-100, y_position), f"{subtotal:.2f} TL", fill='black', font=normal_font)
    y_position += 25
    
    draw.text((20, y_position), "KDV %8:", fill='black', font=normal_font)
    draw.text((width-100, y_position), f"{kdv:.2f} TL", fill='black', font=normal_font)
    y_position += 25
    
    draw.line([(20, y_position), (width-20, y_position)], fill='black', width=2)
    y_position += 15
    
    # Total in larger font
    draw.text((20, y_position), "TOPLAM:", fill='black', font=header_font)
    draw.text((width-120, y_position), f"{total:.2f} TL", fill='black', font=header_font)
    y_position += 35
    
    # Payment method
    draw.text((20, y_position), "ÖDEME: NAKİT", fill='black', font=normal_font)
    y_position += 30
    
    # Receipt number
    receipt_no = f"FİŞ NO: {random.randint(100000, 999999)}"
    draw.text((20, y_position), receipt_no, fill='gray', font=small_font)
    
    # Footer
    draw.text((20, height - 40), "TEŞEKKÜR EDERİZ", fill='gray', font=small_font)
    draw.text((20, height - 20), "YİNE BEKLERİZ", fill='gray', font=small_font)
    
    return img, receipt_date, total


def generate_thumbnail(image, size=(150, 150)):
    """Generate thumbnail with TOP-crop for receipts"""
    # Create a copy to work with
    img = image.copy()
    
    # Calculate dimensions
    width, height = img.size
    target_width, target_height = size
    
    # Calculate aspect ratios
    img_ratio = width / height
    target_ratio = target_width / target_height
    
    if img_ratio > target_ratio:
        # Image is wider - scale by height and crop width
        new_height = target_height
        new_width = int(target_height * img_ratio)
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        # Crop from center horizontally
        left = (new_width - target_width) // 2
        img = img.crop((left, 0, left + target_width, target_height))
    else:
        # Image is taller - scale by width and crop height from TOP
        new_width = target_width
        new_height = int(target_width / img_ratio)
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        # Crop from TOP (0, 0) to show store names on receipts
        img = img.crop((0, 0, target_width, min(target_height, new_height)))
    
    # If the cropped image is smaller than target, resize to fit
    if img.size != size:
        # Create a new image with target size and paste the cropped image
        final_img = Image.new('RGB', size, (255, 255, 255))
        # Center the image if it's smaller
        x = (size[0] - img.width) // 2
        y = (size[1] - img.height) // 2
        final_img.paste(img, (x, y))
        img = final_img
    
    return img


def main():
    """Main function to generate receipts and thumbnails"""
    print("=" * 60)
    print("RECEIPT GENERATOR & THUMBNAIL FIXER")
    print("=" * 60)
    
    # Create media directories
    documents_dir = MEDIA_ROOT / 'documents' / '2025' / '08'
    thumbnails_dir = MEDIA_ROOT / 'documents' / 'thumbnails' / '2025' / '08'
    
    documents_dir.mkdir(parents=True, exist_ok=True)
    thumbnails_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📁 Media directories created/verified:")
    print(f"   Documents: {documents_dir}")
    print(f"   Thumbnails: {thumbnails_dir}")
    
    # Connect to database
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get document records
        cursor.execute("""
            SELECT id, original_filename, file_path, thumbnail_path 
            FROM documents_document 
            ORDER BY uploaded_at DESC
            LIMIT 20
        """)
        documents = cursor.fetchall()
        
        if not documents:
            print("\n⚠️ No documents found in database")
            print("Creating sample documents...")
            
            # Get first user
            cursor.execute("SELECT id, username FROM auth_user LIMIT 1")
            user = cursor.fetchone()
            if not user:
                print("❌ No users found. Please create a user first.")
                return
            
            user_id = user[0]
            print(f"Using user: {user[1]}")
            
            # Create 10 sample documents
            for i in range(10):
                doc_id = f"{random.randint(1000, 9999)}{random.randint(1000, 9999)}{random.randint(10, 99)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(100000000000, 999999999999)}"
                cursor.execute("""
                    INSERT INTO documents_document 
                    (id, user_id, document_type, original_filename, processing_status, uploaded_at, updated_at, tags, custom_metadata)
                    VALUES (?, ?, 'receipt', ?, 'completed', datetime('now'), datetime('now'), '[]', '{}')
                """, (doc_id, user_id, f'receipt_{i+1}.jpg'))
            
            conn.commit()
            
            # Re-fetch documents
            cursor.execute("""
                SELECT id, original_filename, file_path, thumbnail_path 
                FROM documents_document 
                ORDER BY uploaded_at DESC
                LIMIT 20
            """)
            documents = cursor.fetchall()
        
        print(f"\n📋 Found {len(documents)} documents to process")
        
        # Process each document
        processed = 0
        for doc_id, orig_filename, file_path, thumb_path in documents:
            try:
                # Select random store and items
                store = random.choice(TURKISH_STORES)
                items = random.sample(SAMPLE_ITEMS, random.randint(5, 8))
                
                # Create receipt image
                receipt_img, receipt_date, total = create_receipt_image(store, items)
                
                # Save full-size image
                doc_filename = f"receipt_{doc_id}.jpg"
                doc_path = documents_dir / doc_filename
                receipt_img.save(doc_path, 'JPEG', quality=95)
                
                # Generate thumbnail with TOP-crop
                thumbnail_img = generate_thumbnail(receipt_img)
                thumb_filename = f"thumb_{doc_id}.jpg"
                thumb_path = thumbnails_dir / thumb_filename
                thumbnail_img.save(thumb_path, 'JPEG', quality=85)
                
                # Update database
                new_filename = f"{store['name'].lower()}_receipt_{processed+1}.jpg"
                cursor.execute("""
                    UPDATE documents_document 
                    SET original_filename = ?,
                        file_path = ?,
                        thumbnail_path = ?,
                        processing_status = 'completed'
                    WHERE id = ?
                """, (
                    new_filename,
                    f"documents/2025/08/{doc_filename}",
                    f"documents/thumbnails/2025/08/{thumb_filename}",
                    doc_id
                ))
                
                # Check if ParsedReceipt exists
                cursor.execute("SELECT id FROM documents_parsedreceipt WHERE document_id = ?", (doc_id,))
                if not cursor.fetchone():
                    # Create ParsedReceipt record
                    cursor.execute("""
                        INSERT INTO documents_parsedreceipt 
                        (document_id, store_name, store_address, transaction_date, 
                         receipt_number, subtotal, tax_amount, total_amount, 
                         payment_method, currency, raw_ocr_data, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
                    """, (
                        doc_id,
                        store['name'],
                        f"{store['name']} Merkez Şube, İstanbul",
                        receipt_date.isoformat(),
                        str(random.randint(100000, 999999)),
                        float(total / 1.08),
                        float(total * 0.08 / 1.08),
                        float(total),
                        'NAKİT',
                        'TRY',
                        '{}'
                    ))
                
                processed += 1
                print(f"✓ Generated receipt {processed}: {store['name']}")
                
            except Exception as e:
                print(f"✗ Error processing document {doc_id}: {str(e)}")
                continue
        
        # Commit all changes
        conn.commit()
        conn.close()
        
        print(f"\n✅ Successfully generated {processed} receipts with TOP-crop thumbnails!")
        
        # Verify files
        print("\n📸 Verifying generated files:")
        doc_files = list(documents_dir.glob("*.jpg"))
        thumb_files = list(thumbnails_dir.glob("*.jpg"))
        
        print(f"   Document images: {len(doc_files)}")
        print(f"   Thumbnail images: {len(thumb_files)}")
        
        if doc_files:
            print("\n   Sample files created:")
            for f in doc_files[:3]:
                size = f.stat().st_size
                print(f"   - {f.name} ({size:,} bytes)")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
    print("\n" + "=" * 60)
    print("✅ PROCESS COMPLETED!")
    print("=" * 60)
    print("\nThe thumbnails now show the TOP portion of receipts")
    print("where store names are prominently displayed.")
    print("\nDocument URLs: /media/documents/2025/08/")
    print("Thumbnail URLs: /media/documents/thumbnails/2025/08/")