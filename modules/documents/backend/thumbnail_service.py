"""
Enhanced Thumbnail Generation Service for Documents
Provides comprehensive thumbnail generation with multiple strategies
"""

import os
import io
import logging
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

logger = logging.getLogger('documents.thumbnail')


class EnhancedThumbnailGenerator:
    """Enhanced thumbnail generator with multiple crop strategies"""
    
    DEFAULT_SIZE = (150, 150)
    QUALITY = 85
    
    def __init__(self, size: Tuple[int, int] = None):
        self.size = size or self.DEFAULT_SIZE
        
    def generate_from_file(self, file_path: str, output_name: str = None) -> Optional[ContentFile]:
        """Generate thumbnail from file path"""
        try:
            with Image.open(file_path) as img:
                return self._create_thumbnail(img, output_name)
        except Exception as e:
            logger.error(f"Error generating thumbnail from file {file_path}: {e}")
            return self._create_error_thumbnail(output_name)
    
    def generate_from_django_file(self, django_file, output_name: str = None) -> Optional[ContentFile]:
        """Generate thumbnail from Django FileField"""
        try:
            with Image.open(django_file) as img:
                return self._create_thumbnail(img, output_name)
        except Exception as e:
            logger.error(f"Error generating thumbnail from Django file: {e}")
            return self._create_error_thumbnail(output_name)
    
    def _create_thumbnail(self, img: Image.Image, output_name: str = None) -> ContentFile:
        """Create thumbnail with smart cropping based on document type"""
        # Convert to RGB if necessary
        if img.mode not in ('RGB', 'RGBA'):
            img = img.convert('RGB')
        
        # Determine crop strategy based on aspect ratio
        if self._is_receipt_like(img):
            thumbnail = self._crop_top(img)
        else:
            thumbnail = self._crop_center(img)
        
        # Save to buffer
        buffer = io.BytesIO()
        thumbnail.save(buffer, format='JPEG', quality=self.QUALITY, optimize=True)
        buffer.seek(0)
        
        return ContentFile(buffer.read(), name=output_name or 'thumbnail.jpg')
    
    def _is_receipt_like(self, img: Image.Image) -> bool:
        """Check if image appears to be a receipt (tall and narrow)"""
        width, height = img.size
        aspect_ratio = height / width
        return aspect_ratio > 1.5  # Receipt-like if height is 1.5x+ the width
    
    def _crop_top(self, img: Image.Image) -> Image.Image:
        """Crop from top - ideal for receipts showing store name"""
        width, height = img.size
        target_width, target_height = self.size
        
        # Calculate scaling
        scale = max(target_width / width, target_height / height)
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        # Resize
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Crop from top-center
        left = (new_width - target_width) // 2
        top = 0  # Start from top
        right = left + target_width
        bottom = min(top + target_height, new_height)
        
        cropped = img.crop((left, top, right, bottom))
        
        # If cropped is smaller than target, pad with white
        if cropped.size != self.size:
            final = Image.new('RGB', self.size, (255, 255, 255))
            paste_x = (self.size[0] - cropped.width) // 2
            paste_y = 0
            final.paste(cropped, (paste_x, paste_y))
            return final
        
        return cropped
    
    def _crop_center(self, img: Image.Image) -> Image.Image:
        """Center crop - ideal for documents and general images"""
        width, height = img.size
        target_width, target_height = self.size
        
        # Calculate scaling
        scale = max(target_width / width, target_height / height)
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        # Resize
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Center crop
        left = (new_width - target_width) // 2
        top = (new_height - target_height) // 2
        right = left + target_width
        bottom = top + target_height
        
        return img.crop((left, top, right, bottom))
    
    def _create_error_thumbnail(self, output_name: str = None) -> ContentFile:
        """Create a placeholder thumbnail for errors"""
        # Create a gray image with error icon
        img = Image.new('RGB', self.size, (200, 200, 200))
        draw = ImageDraw.Draw(img)
        
        # Draw an X
        margin = 20
        draw.line(
            [(margin, margin), (self.size[0] - margin, self.size[1] - margin)],
            fill=(150, 150, 150), width=3
        )
        draw.line(
            [(self.size[0] - margin, margin), (margin, self.size[1] - margin)],
            fill=(150, 150, 150), width=3
        )
        
        # Add text
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 12)
        except:
            font = ImageFont.load_default()
        
        text = "Error"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = (self.size[0] - text_width) // 2
        text_y = (self.size[1] - text_height) // 2
        draw.text((text_x, text_y), text, fill=(100, 100, 100), font=font)
        
        # Save to buffer
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=70)
        buffer.seek(0)
        
        return ContentFile(buffer.read(), name=output_name or 'error_thumbnail.jpg')
    
    def regenerate_all_thumbnails(self, documents_queryset, force: bool = False):
        """Regenerate thumbnails for multiple documents"""
        results = {
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'errors': []
        }
        
        for document in documents_queryset:
            try:
                # Skip if thumbnail exists and not forcing
                if document.thumbnail_path and not force:
                    results['skipped'] += 1
                    continue
                
                # Check if source file exists
                if not document.file_path:
                    results['failed'] += 1
                    results['errors'].append(f"{document.id}: No source file")
                    continue
                
                # Generate thumbnail
                thumb_file = self.generate_from_django_file(
                    document.file_path,
                    f"thumb_{document.id}.jpg"
                )
                
                if thumb_file:
                    # Delete old thumbnail if exists
                    if document.thumbnail_path:
                        try:
                            document.thumbnail_path.delete(save=False)
                        except:
                            pass
                    
                    # Save new thumbnail
                    document.thumbnail_path.save(
                        f"thumb_{document.id}.jpg",
                        thumb_file,
                        save=True
                    )
                    results['success'] += 1
                    logger.info(f"Thumbnail regenerated for document {document.id}")
                else:
                    results['failed'] += 1
                    results['errors'].append(f"{document.id}: Generation failed")
                    
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"{document.id}: {str(e)}")
                logger.error(f"Error regenerating thumbnail for {document.id}: {e}")
        
        return results


class DocumentPreviewGenerator:
    """Generate document previews for non-image formats"""
    
    @staticmethod
    def generate_pdf_preview(pdf_path: str, output_size: Tuple[int, int] = (150, 150)) -> Optional[ContentFile]:
        """Generate preview thumbnail for PDF files"""
        try:
            import fitz  # PyMuPDF
            
            # Open PDF
            pdf_document = fitz.open(pdf_path)
            
            # Get first page
            page = pdf_document[0]
            
            # Render page to image
            mat = fitz.Matrix(2, 2)  # 2x zoom for better quality
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to PIL Image
            img_data = pix.tobytes("ppm")
            img = Image.open(io.BytesIO(img_data))
            
            # Create thumbnail
            generator = EnhancedThumbnailGenerator(size=output_size)
            return generator._create_thumbnail(img, "pdf_preview.jpg")
            
        except ImportError:
            logger.warning("PyMuPDF not installed, cannot generate PDF previews")
            return None
        except Exception as e:
            logger.error(f"Error generating PDF preview: {e}")
            return None
    
    @staticmethod
    def generate_text_preview(text_content: str, output_size: Tuple[int, int] = (150, 150)) -> ContentFile:
        """Generate preview thumbnail for text content"""
        # Create white background
        img = Image.new('RGB', output_size, 'white')
        draw = ImageDraw.Draw(img)
        
        # Try to use a monospace font
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Courier.ttc", 10)
        except:
            font = ImageFont.load_default()
        
        # Draw text lines
        lines = text_content.split('\n')[:10]  # First 10 lines
        y = 5
        for line in lines:
            if y > output_size[1] - 15:
                break
            draw.text((5, y), line[:20], fill='black', font=font)
            y += 12
        
        # Save to buffer
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=80)
        buffer.seek(0)
        
        return ContentFile(buffer.read(), name='text_preview.jpg')