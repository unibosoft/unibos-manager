#!/usr/bin/env python
"""Generate thumbnails for all documents"""

import os
import sys
import django
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unibos_backend.settings.emergency')
sys.path.insert(0, '/Users/berkhatirli/Desktop/unibos/apps/web/backend')
django.setup()

from modules.documents.backend.models import Document

def generate_thumbnail(image_path, size=(150, 150)):
    """Generate thumbnail from image file"""
    try:
        img = Image.open(image_path)
        
        # Convert to RGB if necessary
        if img.mode not in ('RGB', 'L'):
            img = img.convert('RGB')
        
        # Create thumbnail
        img.thumbnail(size, Image.Resampling.LANCZOS)
        
        # Save to BytesIO
        thumb_io = BytesIO()
        img.save(thumb_io, format='JPEG', quality=85)
        thumb_io.seek(0)
        
        return ContentFile(thumb_io.read())
    except Exception as e:
        print(f"Error generating thumbnail: {e}")
        return None

def generate_all_thumbnails():
    """Generate thumbnails for all documents"""
    
    documents = Document.objects.all()
    total = documents.count()
    success = 0
    failed = 0
    
    print(f"Generating thumbnails for {total} documents...")
    
    for i, doc in enumerate(documents):
        try:
            if doc.file_path:
                # Generate thumbnail
                thumb = generate_thumbnail(doc.file_path.path)
                
                if thumb:
                    # Save thumbnail
                    thumb_name = f"thumb_{doc.id}.jpg"
                    doc.thumbnail_path.save(thumb_name, thumb, save=True)
                    success += 1
                    
                    if (i + 1) % 10 == 0:
                        print(f"  Generated {i + 1}/{total} thumbnails...")
                else:
                    failed += 1
            else:
                failed += 1
                
        except Exception as e:
            print(f"  Error for document {doc.id}: {e}")
            failed += 1
    
    print(f"\n✅ Thumbnail generation complete!")
    print(f"  Success: {success}")
    print(f"  Failed: {failed}")
    print(f"  Total: {total}")

if __name__ == "__main__":
    generate_all_thumbnails()