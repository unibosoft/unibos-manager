"""
EasyOCR Service - Easy-to-use multilingual OCR
EasyOCR supports 80+ languages and is designed to be simple and effective
Great as a fallback OCR method when other methods fail
"""

from PIL import Image
import logging
from typing import Dict, List, Optional
import re

logger = logging.getLogger(__name__)


class EasyOCRService:
    """Service for processing documents using EasyOCR"""

    def __init__(self):
        self.reader = None
        self._initialize_model()

    def _initialize_model(self):
        """Initialize EasyOCR reader lazily"""
        try:
            import easyocr

            # Initialize reader with English and Turkish support
            # gpu=False for CPU mode (set to True if CUDA is available)
            self.reader = easyocr.Reader(['en', 'tr'], gpu=False)

            logger.info("EasyOCR reader initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize EasyOCR: {e}")
            raise

    def process_image(self, image_path: str) -> Dict:
        """
        Process image with EasyOCR

        Args:
            image_path: Path to the image file

        Returns:
            Dictionary containing OCR results
        """
        try:
            # Read text from image
            # Returns list of (bbox, text, confidence)
            results = self.reader.readtext(image_path)

            if not results:
                return {
                    'success': False,
                    'error': 'No text detected',
                    'text': '',
                    'confidence': 0.0
                }

            # Extract text and calculate average confidence
            full_text = []
            confidences = []

            for (bbox, text, conf) in results:
                full_text.append(text)
                confidences.append(conf)

            combined_text = '\n'.join(full_text)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

            # Extract key information
            key_findings = self._extract_key_information(combined_text)

            # Calculate quality metrics
            metrics = self._calculate_metrics(combined_text, avg_confidence, len(results))

            return {
                'success': True,
                'text': combined_text,
                'confidence': avg_confidence,
                'key_findings': key_findings,
                'metrics': metrics,
                'detections': len(results),
                'languages': ['en', 'tr']
            }

        except Exception as e:
            logger.error(f"EasyOCR processing failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'confidence': 0.0
            }

    def _extract_key_information(self, text: str) -> Dict:
        """Extract key receipt information from text"""
        key_findings = {
            'store_name': '',
            'total_amount': '',
            'date': '',
            'bottom_info': ''
        }

        if not text:
            return key_findings

        lines = text.split('\n')

        # Store name - usually in first few lines
        for line in lines[:5]:
            line = line.strip()
            if len(line) > 3 and not any(char.isdigit() for char in line):
                key_findings['store_name'] = line
                break

        # Total amount - look for keywords
        total_patterns = [
            r'(?:TOPLAM|TOTAL|T\.TUTAR|GENEL\s*TOPLAM)[:\s]*([0-9,.]+)',
            r'(?:TOPLAM|TOTAL)[:\s]*TL[:\s]*([0-9,.]+)',
            r'([0-9]+[.,][0-9]{2})\s*(?:TL|₺)',
        ]

        for line in lines:
            line_upper = line.upper()
            for pattern in total_patterns:
                match = re.search(pattern, line_upper)
                if match:
                    key_findings['total_amount'] = match.group(1).replace(',', '.')
                    break
            if key_findings['total_amount']:
                break

        # Date - look for date patterns
        date_patterns = [
            r'(\d{2}[/.-]\d{2}[/.-]\d{4})',
            r'(\d{2}[/.-]\d{2}[/.-]\d{2})',
            r'(\d{4}[/.-]\d{2}[/.-]\d{2})',
        ]

        for line in lines:
            for pattern in date_patterns:
                match = re.search(pattern, line)
                if match:
                    key_findings['date'] = match.group(1)
                    break
            if key_findings['date']:
                break

        # Bottom info - last few lines
        bottom_lines = [line.strip() for line in lines[-3:] if line.strip()]
        key_findings['bottom_info'] = ' | '.join(bottom_lines)

        return key_findings

    def _calculate_metrics(self, text: str, confidence: float, detection_count: int) -> Dict:
        """Calculate quality metrics for OCR output"""
        if not text:
            return {
                'character_count': 0,
                'word_count': 0,
                'line_count': 0,
                'avg_word_length': 0.0,
                'confidence_score': 0.0
            }

        lines = [l for l in text.split('\n') if l.strip()]
        words = text.split()

        avg_word_length = sum(len(w) for w in words) / len(words) if words else 0

        return {
            'character_count': len(text),
            'word_count': len(words),
            'line_count': len(lines),
            'avg_word_length': round(avg_word_length, 2),
            'confidence_score': round(confidence * 100, 2),
            'detections': detection_count
        }
