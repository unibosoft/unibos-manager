"""
DocTR OCR Service - Modern Deep Learning OCR
DocTR (Document Text Recognition) is a modern PyTorch/TensorFlow-based OCR library
Provides state-of-the-art text detection and recognition with layout analysis
"""

from PIL import Image
import logging
from typing import Dict, List, Optional
import re

logger = logging.getLogger(__name__)


class DocTROCRService:
    """Service for processing documents using DocTR"""

    def __init__(self):
        self.model = None
        self._initialize_model()

    def _initialize_model(self):
        """Initialize DocTR model lazily"""
        try:
            from doctr.models import ocr_predictor

            # Use pretrained model with best accuracy
            self.model = ocr_predictor(
                det_arch='db_resnet50',  # Detection architecture
                reco_arch='crnn_vgg16_bn',  # Recognition architecture
                pretrained=True
            )

            logger.info("DocTR OCR model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load DocTR model: {e}")
            raise

    def process_image(self, image_path: str) -> Dict:
        """
        Process image with DocTR OCR

        Args:
            image_path: Path to the image file

        Returns:
            Dictionary containing OCR results
        """
        try:
            from doctr.io import DocumentFile

            # Load image using DocTR's document loader
            doc = DocumentFile.from_images(image_path)

            # Run OCR
            result = self.model(doc)

            # Extract text and confidence
            full_text = []
            confidences = []

            # Iterate through pages, blocks, lines, and words
            for page in result.pages:
                for block in page.blocks:
                    block_text = []
                    for line in block.lines:
                        line_text = []
                        for word in line.words:
                            line_text.append(word.value)
                            confidences.append(word.confidence)
                        if line_text:
                            block_text.append(' '.join(line_text))
                    if block_text:
                        full_text.append('\n'.join(block_text))

            combined_text = '\n\n'.join(full_text)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

            # Extract key information
            key_findings = self._extract_key_information(combined_text)

            # Calculate quality metrics
            metrics = self._calculate_metrics(combined_text, avg_confidence, len(confidences))

            return {
                'success': True,
                'text': combined_text,
                'confidence': avg_confidence,
                'key_findings': key_findings,
                'metrics': metrics,
                'words_detected': len(confidences)
            }

        except Exception as e:
            logger.error(f"DocTR OCR processing failed: {e}")
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

    def _calculate_metrics(self, text: str, confidence: float, word_count: int) -> Dict:
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
            'word_count': word_count,
            'line_count': len(lines),
            'avg_word_length': round(avg_word_length, 2),
            'confidence_score': round(confidence * 100, 2)
        }
