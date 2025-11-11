#!/usr/bin/env python
"""
Create sample receipt images for Documents module testing
These will be simple placeholder images with store names at the top
"""

import os
import sys
import django
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import random

# Django setup
sys.path.append(str(Path(__file__).parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unibos_backend.settings.emergency')
django.setup()

from modules.documents.backend.models import Document
from modules.documents.backend.utils import ThumbnailGenerator
from django.contrib.auth import get_user_model

User = get_user_model()

def create_receipt_image(store_name, receipt_number, width=400, height=600):
    """Create a simple receipt image with store name at top"""
    # Create white background
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a font, fallback to default if not available
    try:
        # Try different font sizes
        font_large = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
        font_medium = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
        font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
    except:
        # Use default font if system font not found
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Draw store name at TOP (this is what we want to see in thumbnails)
    draw.text((width//2, 30), store_name, fill='black', font=font_large, anchor='mt')
    draw.text((width//2, 70), "FİŞ NO: " + receipt_number, fill='black', font=font_medium, anchor='mt')
    
    # Draw some line items
    y_pos = 120
    items = [
        ("EKMEK", "8.50"),
        ("SÜT 1L", "24.90"),
        ("YUMURTA 15'Lİ", "45.00"),
        ("DOMATES KG", "18.90"),
        ("PEYNİR 500G", "89.90"),
    ]
    
    for item, price in items:
        draw.text((20, y_pos), item, fill='black', font=font_small)
        draw.text((width-80, y_pos), price + " TL", fill='black', font=font_small)
        y_pos += 30
    
    # Draw total at bottom
    draw.line([(20, y_pos), (width-20, y_pos)], fill='black', width=2)
    y_pos += 20
    draw.text((20, y_pos), "TOPLAM:", fill='black', font=font_medium)
    total = sum(float(p) for _, p in items)
    draw.text((width-80, y_pos), f"{total:.2f} TL", fill='black', font=font_medium)
    
    # Add date at bottom
    y_pos += 40
    draw.text((width//2, y_pos), "07/08/2025 14:23", fill='gray', font=font_small, anchor='mt')
    
    return img

def main():
    print("Creating sample receipt images...")
    
    # Create media directories
    media_dir = Path(__file__).parent / 'media' / 'documents' / '2025' / '08'
    media_dir.mkdir(parents=True, exist_ok=True)
    
    thumb_dir = Path(__file__).parent / 'media' / 'documents' / 'thumbnails' / '2025' / '08'
    thumb_dir.mkdir(parents=True, exist_ok=True)
    
    # Get first user
    user = User.objects.first()
    if not user:
        print("No user found! Please run import_unicorn_users first.")
        return
    
    # Store names to use
    stores = [
        "MIGROS", "CARREFOUR", "A101", "BİM", "ŞOK",
        "METRO", "MAKRO", "TESCO", "REAL", "ALDI"
    ]
    
    # Initialize thumbnail generator
    thumb_gen = ThumbnailGenerator()
    
    # Update existing documents with new images
    documents = Document.objects.filter(document_type='receipt').order_by('created_at')[:10]
    
    for idx, doc in enumerate(documents):
        store = stores[idx % len(stores)]
        receipt_num = f"2025{random.randint(100000, 999999)}"
        
        # Create receipt image
        img = create_receipt_image(store, receipt_num)
        
        # Save full image
        img_path = media_dir / f"receipt_{idx+1:03d}.jpg"
        img.save(img_path, 'JPEG', quality=85)
        
        # Update document path
        doc.file_path = f"documents/2025/08/receipt_{idx+1:03d}.jpg"
        
        # Generate thumbnail using our new TOP-cropping logic
        thumb_path = thumb_gen.generate_thumbnail(str(img_path))
        if thumb_path:
            # Move thumbnail to correct location
            final_thumb_path = thumb_dir / f"thumb_{doc.id}.jpg"
            if Path(thumb_path).exists():
                Path(thumb_path).rename(final_thumb_path)
                doc.thumbnail_path = f"documents/thumbnails/2025/08/thumb_{doc.id}.jpg"
        
        doc.save()
        print(f"✓ Created receipt {idx+1}: {store} - {receipt_num}")
    
    print(f"\n✅ Created {len(documents)} sample receipts with store names at TOP")
    print("Thumbnails will now show store names!")

if __name__ == "__main__":
    main()