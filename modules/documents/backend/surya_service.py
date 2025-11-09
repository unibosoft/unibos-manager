"""
Surya OCR Service - All-in-one OCR solution
Surya is a comprehensive OCR toolkit that handles text detection, recognition, and layout analysis
Supports 90+ languages with high accuracy
"""

from PIL import Image
import logging
from typing import Dict, List, Optional, Tuple
import re

logger = logging.getLogger(__name__)


class SuryaOCRService:
    """Service for processing documents using Surya OCR"""

    def __init__(self):
        self.model = None
        self.detector = None
        self.recognizer = None
        self._initialize_model()

    def _initialize_model(self):
        """Initialize Surya OCR models (v0.17+ uses new predictor API with FoundationPredictor)"""
        self.is_available_flag = False
        try:
            from surya.foundation import FoundationPredictor
            from surya.recognition import RecognitionPredictor
            from surya.detection import DetectionPredictor

            # Initialize foundation predictor first (required for recognition and detection)
            self.foundation_predictor = FoundationPredictor()

            # Initialize detection and recognition predictors
            self.det_predictor = DetectionPredictor()
            self.rec_predictor = RecognitionPredictor(self.foundation_predictor)

            logger.info("Surya OCR models loaded successfully")
            self.is_available_flag = True
        except ImportError as e:
            logger.warning(f"Surya OCR not installed: {e}")
            self.is_available_flag = False
        except Exception as e:
            logger.error(f"Failed to load Surya models: {e}")
            self.is_available_flag = False

    def is_available(self) -> bool:
        """Check if Surya OCR is available"""
        return self.is_available_flag

    def process_image(self, image_path: str) -> Dict:
        """
        Process image with Surya OCR

        Args:
            image_path: Path to the image file

        Returns:
            Dictionary containing OCR results
        """
        # Check if Surya is available
        if not self.is_available():
            return {
                'success': False,
                'error': 'Surya OCR not installed. Install with: pip install surya-ocr',
                'text': '',
                'confidence': 0.0
            }

        try:
            # Load image
            image = Image.open(image_path)
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Use new predictor API (only API supported in surya-ocr 0.17+)
            # Recognition predictor handles both detection and recognition internally
            rec_result = self.rec_predictor(
                [image],
                det_predictor=self.det_predictor
            )

            if not rec_result or len(rec_result) == 0:
                return {
                    'success': False,
                    'error': 'No text detected',
                    'text': '',
                    'confidence': 0.0
                }

            # Extract text from results
            full_text = []
            total_confidence = 0
            text_count = 0

            for line in rec_result[0]:
                if hasattr(line, 'text'):
                    full_text.append(line.text)
                    if hasattr(line, 'confidence'):
                        total_confidence += line.confidence
                    text_count += 1

            combined_text = '\n'.join(full_text)
            avg_confidence = (total_confidence / text_count) if text_count > 0 else 0.5

            # Extract key information
            key_findings = self._extract_key_information(combined_text)

            # Calculate quality metrics
            metrics = self._calculate_metrics(combined_text, avg_confidence)

            return {
                'success': True,
                'text': combined_text,
                'confidence': avg_confidence * 100,  # Convert to percentage (0-100)
                'key_findings': key_findings,
                'metrics': metrics,
                'lines_detected': text_count,
                'languages': ['en', 'tr']
            }

        except Exception as e:
            logger.error(f"Surya OCR processing failed: {e}")
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

    def _calculate_metrics(self, text: str, confidence: float) -> Dict:
        """Calculate quality metrics for OCR output

        Args:
            text: OCR text output
            confidence: Confidence score in range 0-1
        """
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
            'confidence_score': round(confidence * 100, 2)  # confidence is 0-1, convert to percentage
        }
