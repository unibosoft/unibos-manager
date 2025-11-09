"""
TrOCR Integration Service for Document OCR
Microsoft's Transformer-based OCR for low-quality/difficult fonts
Especially good for handwritten text and poor quality scans
"""

import logging
from typing import Dict, Optional
import os
from PIL import Image
from .receipt_field_extractor import ReceiptFieldExtractor

logger = logging.getLogger('documents.trocr')


class TrOCRService:
    """
    Service for TrOCR integration (Microsoft's Transformer-based OCR)
    Uses Hugging Face Transformers library

    Models:
    - microsoft/trocr-base-printed: For printed text (faster)
    - microsoft/trocr-large-printed: For printed text (higher accuracy)
    - microsoft/trocr-base-handwritten: For handwritten text
    """

    def __init__(self, model_name='microsoft/trocr-base-printed', language='tr'):
        """
        Initialize TrOCR service

        Args:
            model_name: Hugging Face model name
                - 'microsoft/trocr-base-printed' (default, fast)
                - 'microsoft/trocr-large-printed' (slower, more accurate)
                - 'microsoft/trocr-base-handwritten' (for handwriting)
            language: Primary language for field extraction ('tr', 'en')
        """
        self.model_name = model_name
        self.language = language
        self.available = False
        self.processor = None
        self.model = None

        # Initialize universal field extractor
        self.field_extractor = ReceiptFieldExtractor(language=language)

        # Try to import required libraries
        try:
            from transformers import TrOCRProcessor, VisionEncoderDecoderModel
            self.TrOCRProcessor = TrOCRProcessor
            self.VisionEncoderDecoderModel = VisionEncoderDecoderModel
            self.available = True
            logger.info(f"TrOCR libraries available")
        except ImportError:
            logger.warning("TrOCR not installed. Install with: pip install transformers torch pillow")
            self.available = False

    def is_available(self) -> bool:
        """Check if TrOCR is available"""
        return self.available

    def initialize_model(self):
        """
        Initialize TrOCR model and processor
        Downloads model on first use (~1GB for base, ~3GB for large)
        """
        if not self.available:
            return False

        try:
            logger.info(f"Loading TrOCR model: {self.model_name}")

            # Load processor and model
            self.processor = self.TrOCRProcessor.from_pretrained(self.model_name)
            self.model = self.VisionEncoderDecoderModel.from_pretrained(self.model_name)

            # Move to GPU if available
            try:
                import torch
                if torch.cuda.is_available():
                    self.model = self.model.to('cuda')
                    logger.info("TrOCR using GPU acceleration")
                elif torch.backends.mps.is_available():
                    self.model = self.model.to('mps')
                    logger.info("TrOCR using Apple Silicon MPS acceleration")
                else:
                    logger.info("TrOCR using CPU")
            except Exception as e:
                logger.warning(f"Could not check GPU availability: {e}")

            logger.info(f"TrOCR model loaded successfully: {self.model_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize TrOCR: {e}")
            self.available = False
            return False

    def process_image(self, image_path: str, max_length: int = 512) -> Dict:
        """
        Process image with TrOCR

        Args:
            image_path: Path to image file
            max_length: Maximum number of tokens to generate (default: 512)

        Returns:
            Dictionary with OCR results
        """
        if not self.available:
            return {
                'success': False,
                'error': 'TrOCR not available',
                'text': '',
                'confidence': 0
            }

        # Initialize model if not done
        if self.model is None or self.processor is None:
            if not self.initialize_model():
                return {
                    'success': False,
                    'error': 'Failed to initialize TrOCR model',
                    'text': '',
                    'confidence': 0
                }

        try:
            # Check if file exists
            if not os.path.exists(image_path):
                return {
                    'success': False,
                    'error': f'Image file not found: {image_path}',
                    'text': '',
                    'confidence': 0
                }

            # Load image
            logger.info(f"Processing image with TrOCR: {image_path}")
            image = Image.open(image_path).convert('RGB')

            # Prepare image for model
            pixel_values = self.processor(image, return_tensors="pt").pixel_values

            # Move to same device as model
            try:
                import torch
                if torch.cuda.is_available():
                    pixel_values = pixel_values.to('cuda')
                elif torch.backends.mps.is_available():
                    pixel_values = pixel_values.to('mps')
            except Exception:
                pass  # Stay on CPU

            # Generate text
            generated_ids = self.model.generate(
                pixel_values,
                max_length=max_length,
                num_beams=5,  # Beam search for better quality
                early_stopping=True
            )

            # Decode generated text
            generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

            # TrOCR doesn't provide confidence scores directly
            # We'll estimate based on output length and quality
            confidence = self._estimate_confidence(generated_text)

            # Extract structured fields using universal extractor
            extracted_fields = self.field_extractor.extract_all_fields(text=generated_text)

            logger.info(f"TrOCR extracted {len(generated_text)} characters")

            return {
                'success': True,
                'text': generated_text,
                'confidence': confidence,
                'char_count': len(generated_text),
                'word_count': len(generated_text.split()),
                'model_name': self.model_name,
                # Add extracted fields
                'data': extracted_fields,
                'found_store': extracted_fields.get('found_store', False),
                'found_total': extracted_fields.get('found_total', False),
                'found_date': extracted_fields.get('found_date', False),
            }

        except Exception as e:
            logger.error(f"TrOCR processing error: {e}")
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'confidence': 0
            }

    def process_image_regions(self, image_path: str, regions: list) -> Dict:
        """
        Process multiple regions of an image separately
        Useful when combined with layout detection

        Args:
            image_path: Path to image file
            regions: List of bounding boxes [(x1, y1, x2, y2), ...]

        Returns:
            Dictionary with OCR results for each region
        """
        if not self.available:
            return {
                'success': False,
                'error': 'TrOCR not available',
                'regions': []
            }

        try:
            # Load full image
            image = Image.open(image_path).convert('RGB')

            results = []
            for i, (x1, y1, x2, y2) in enumerate(regions):
                # Crop region
                region_img = image.crop((x1, y1, x2, y2))

                # Save to temp file
                temp_path = f"/tmp/trocr_region_{i}.png"
                region_img.save(temp_path)

                # Process region
                result = self.process_image(temp_path)
                results.append({
                    'bbox': (x1, y1, x2, y2),
                    'text': result.get('text', ''),
                    'confidence': result.get('confidence', 0)
                })

                # Clean up temp file
                try:
                    os.remove(temp_path)
                except:
                    pass

            # Combine all region texts
            full_text = '\n'.join(r['text'] for r in results if r['text'])
            avg_confidence = sum(r['confidence'] for r in results) / len(results) if results else 0

            return {
                'success': True,
                'text': full_text,
                'confidence': avg_confidence,
                'regions': results,
                'region_count': len(results)
            }

        except Exception as e:
            logger.error(f"TrOCR region processing error: {e}")
            return {
                'success': False,
                'error': str(e),
                'regions': []
            }

    def _estimate_confidence(self, text: str) -> float:
        """
        Estimate confidence based on text quality
        TrOCR doesn't provide confidence scores, so we estimate

        Args:
            text: Generated text

        Returns:
            Estimated confidence (0-100)
        """
        if not text:
            return 0.0

        # Base confidence
        confidence = 70.0

        # Boost if text has reasonable length
        if len(text) >= 10:
            confidence += 10.0

        # Boost if text has multiple words
        words = text.split()
        if len(words) >= 5:
            confidence += 10.0

        # Penalize if text is very short
        if len(text) < 5:
            confidence -= 20.0

        # Penalize if text has too many special characters
        special_char_ratio = sum(1 for c in text if not c.isalnum() and not c.isspace()) / len(text)
        if special_char_ratio > 0.3:
            confidence -= 15.0

        # Clamp to 0-100 range
        return max(0.0, min(100.0, confidence))
