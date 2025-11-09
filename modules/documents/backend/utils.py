"""
Document utilities - Thumbnail generation and helper functions
"""

import os
import logging
from pathlib import Path
from typing import Optional, Tuple
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import io

# Try to import image processing libraries
try:
    from PIL import Image, ImageOps
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: PIL not installed. Thumbnail generation will be disabled.")

logger = logging.getLogger('documents.utils')


class ThumbnailGenerator:
    """Generate thumbnails for document images"""
    
    THUMBNAIL_SIZE = (150, 150)  # Default thumbnail size
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    
    def __init__(self, size: Tuple[int, int] = None):
        self.size = size or self.THUMBNAIL_SIZE
        self.pil_available = PIL_AVAILABLE
    
    def generate_thumbnail(self, file_path: str, output_path: str = None) -> Optional[str]:
        """
        Generate thumbnail for an image file
        
        Args:
            file_path: Path to the original image
            output_path: Optional path for the thumbnail. If not provided, will auto-generate
            
        Returns:
            Path to the generated thumbnail or None if failed
        """
        if not self.pil_available:
            logger.warning("PIL not available, cannot generate thumbnail")
            return None
        
        try:
            # Check if file exists and is supported
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return None
            
            file_ext = Path(file_path).suffix.lower()
            if file_ext not in self.SUPPORTED_FORMATS:
                logger.warning(f"Unsupported format for thumbnail: {file_ext}")
                return None
            
            # Open and process image
            with Image.open(file_path) as img:
                # Convert to RGB if necessary (for PNG with transparency)
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Create a white background
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Apply auto-orientation based on EXIF data first
                img = ImageOps.exif_transpose(img)
                
                # For receipts, we need to crop from the top to show store names
                # Calculate the crop area to get top portion
                width, height = img.size
                target_width, target_height = self.size
                
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
                if img.size != self.size:
                    # Create a new image with target size and paste the cropped image
                    final_img = Image.new('RGB', self.size, (255, 255, 255))
                    # Center the image if it's smaller
                    x = (self.size[0] - img.width) // 2
                    y = (self.size[1] - img.height) // 2
                    final_img.paste(img, (x, y))
                    img = final_img
                
                # Generate output path if not provided
                if not output_path:
                    base_dir = os.path.dirname(file_path)
                    base_name = Path(file_path).stem
                    output_path = os.path.join(base_dir, f"{base_name}_thumb.jpg")
                
                # Save thumbnail
                img.save(output_path, 'JPEG', quality=85, optimize=True)
                
                logger.info(f"Thumbnail generated: {output_path}")
                return output_path
                
        except Exception as e:
            logger.error(f"Failed to generate thumbnail for {file_path}: {str(e)}")
            return None
    
    def generate_thumbnail_from_django_file(self, django_file, document_id: str) -> Optional[ContentFile]:
        """
        Generate thumbnail from a Django file field
        
        Args:
            django_file: Django FileField or UploadedFile
            document_id: Document ID for naming
            
        Returns:
            ContentFile with thumbnail data or None if failed
        """
        if not self.pil_available:
            return None
        
        try:
            # Open image from Django file
            img = Image.open(django_file)
            
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Apply auto-orientation first
            img = ImageOps.exif_transpose(img)
            
            # For receipts, crop from top to show store names
            width, height = img.size
            target_width, target_height = self.size
            
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
            if img.size != self.size:
                # Create a new image with target size and paste the cropped image
                final_img = Image.new('RGB', self.size, (255, 255, 255))
                # Center the image if it's smaller
                x = (self.size[0] - img.width) // 2
                y = (self.size[1] - img.height) // 2
                final_img.paste(img, (x, y))
                img = final_img
            
            # Save to bytes buffer
            thumb_io = io.BytesIO()
            img.save(thumb_io, 'JPEG', quality=85, optimize=True)
            thumb_io.seek(0)
            
            # Create ContentFile
            thumb_file = ContentFile(thumb_io.read())
            thumb_file.name = f"thumb_{document_id}.jpg"
            
            return thumb_file
            
        except Exception as e:
            logger.error(f"Failed to generate thumbnail from Django file: {str(e)}")
            return None
    
    def batch_generate_thumbnails(self, file_paths: list) -> dict:
        """
        Generate thumbnails for multiple files
        
        Args:
            file_paths: List of file paths
            
        Returns:
            Dictionary with original paths as keys and thumbnail paths as values
        """
        results = {}
        
        for file_path in file_paths:
            thumb_path = self.generate_thumbnail(file_path)
            results[file_path] = thumb_path
        
        return results


class DocumentHelper:
    """Helper functions for document processing"""
    
    @staticmethod
    def get_file_type(filename: str) -> str:
        """
        Determine file type from filename
        """
        ext = Path(filename).suffix.lower()
        
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
        pdf_extensions = {'.pdf'}
        
        if ext in image_extensions:
            return 'image'
        elif ext in pdf_extensions:
            return 'pdf'
        else:
            return 'unknown'
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """
        Format file size in human-readable format
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename for safe storage
        """
        import re
        # Remove or replace unsafe characters
        filename = re.sub(r'[^\w\s\-\.]', '_', filename)
        # Remove multiple underscores
        filename = re.sub(r'_+', '_', filename)
        # Remove leading/trailing underscores
        filename = filename.strip('_')
        
        return filename
    
    @staticmethod
    def get_unique_filename(user, original_filename: str) -> str:
        """
        Generate unique filename if file already exists
        Adds incrementing number or timestamp to avoid overwriting
        """
        from modules.documents.backend.models import Document
        from datetime import datetime
        
        sanitized = DocumentHelper.sanitize_filename(original_filename)
        name, ext = os.path.splitext(sanitized)
        
        # Check if file with same name exists for this user
        existing = Document.objects.filter(
            user=user,
            original_filename=sanitized,
            is_deleted=False
        ).exists()
        
        if not existing:
            return sanitized
        
        # Try numbered versions first (up to 99)
        for i in range(2, 100):
            new_filename = f"{name}_{i}{ext}"
            if not Document.objects.filter(
                user=user,
                original_filename=new_filename,
                is_deleted=False
            ).exists():
                return new_filename
        
        # If still not unique, add timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{name}_{timestamp}{ext}"
    
    @staticmethod
    def extract_metadata(file_path: str) -> dict:
        """
        Extract metadata from an image file
        """
        metadata = {
            'size': 0,
            'dimensions': None,
            'format': None,
            'mode': None
        }
        
        try:
            if os.path.exists(file_path):
                metadata['size'] = os.path.getsize(file_path)
                
                if PIL_AVAILABLE:
                    with Image.open(file_path) as img:
                        metadata['dimensions'] = img.size
                        metadata['format'] = img.format
                        metadata['mode'] = img.mode
                        
                        # Try to get EXIF data
                        if hasattr(img, '_getexif') and img._getexif():
                            from PIL.ExifTags import TAGS
                            exif_data = {}
                            for tag, value in img._getexif().items():
                                decoded = TAGS.get(tag, tag)
                                exif_data[decoded] = value
                            metadata['exif'] = exif_data
        except Exception as e:
            logger.error(f"Failed to extract metadata from {file_path}: {str(e)}")
        
        return metadata


class PaginationHelper:
    """Helper for dynamic pagination"""

    ALLOWED_PAGE_SIZES = [10, 20, 50, 100, 250]
    DEFAULT_PAGE_SIZE = 20

    @staticmethod
    def get_page_size(request, default: int = None) -> int:
        """
        Get page size from request
        Accepts both 'page_size' and 'per_page' parameters
        """
        default = default or PaginationHelper.DEFAULT_PAGE_SIZE

        try:
            # Check both 'per_page' and 'page_size' parameters
            page_size = request.GET.get('per_page') or request.GET.get('page_size')
            if page_size:
                page_size = int(page_size)
                # Validate against allowed sizes
                if page_size in PaginationHelper.ALLOWED_PAGE_SIZES:
                    return page_size
                # Find closest allowed size
                return min(PaginationHelper.ALLOWED_PAGE_SIZES,
                          key=lambda x: abs(x - page_size))
            return default
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def get_pagination_context(page_obj, request) -> dict:
        """
        Get pagination context for templates
        """
        # Calculate page range for display
        paginator = page_obj.paginator
        current_page = page_obj.number
        total_pages = paginator.num_pages
        
        # Create a range of pages to display
        if total_pages <= 7:
            page_range = range(1, total_pages + 1)
        else:
            if current_page <= 4:
                page_range = list(range(1, 6)) + ['...', total_pages]
            elif current_page >= total_pages - 3:
                page_range = [1, '...'] + list(range(total_pages - 4, total_pages + 1))
            else:
                page_range = [1, '...'] + list(range(current_page - 1, current_page + 2)) + ['...', total_pages]
        
        # Get current query parameters
        query_params = request.GET.copy()
        if 'page' in query_params:
            query_params.pop('page')
        
        # Get current page size (check both per_page and page_size)
        current_page_size = request.GET.get('per_page') or request.GET.get('page_size')
        if current_page_size:
            try:
                current_page_size = int(current_page_size)
            except (ValueError, TypeError):
                current_page_size = PaginationHelper.DEFAULT_PAGE_SIZE
        else:
            current_page_size = PaginationHelper.DEFAULT_PAGE_SIZE

        return {
            'page_range': page_range,
            'current_page': current_page,
            'total_pages': total_pages,
            'has_previous': page_obj.has_previous(),
            'has_next': page_obj.has_next(),
            'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
            'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
            'total_items': paginator.count,
            'page_size': current_page_size,
            'per_page': current_page_size,  # Add this for template compatibility
            'allowed_page_sizes': PaginationHelper.ALLOWED_PAGE_SIZES,
            'query_params': query_params.urlencode() if query_params else '',
            'start_index': page_obj.start_index(),
            'end_index': page_obj.end_index(),
        }