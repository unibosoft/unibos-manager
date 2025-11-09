"""
OCRMyPDF Service - PDF OCR Orchestration
OCRMyPDF adds OCR text layers to PDF files and can extract text from scanned documents
Works as a wrapper around Tesseract with PDF-specific optimizations
"""

from PIL import Image
import logging
from typing import Dict, List, Optional
import tempfile
import os
import re
import subprocess

logger = logging.getLogger(__name__)


class OCRMyPDFService:
    """Service for processing documents using OCRMyPDF"""

    def __init__(self):
        """Initialize OCRMyPDF service"""
        self.available = self._verify_installation()

    def _verify_installation(self) -> bool:
        """Verify OCRMyPDF is installed and accessible

        Returns:
            bool: True if OCRMyPDF is available, False otherwise
        """
        try:
            result = subprocess.run(
                ['ocrmypdf', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info(f"OCRMyPDF version: {result.stdout.strip()}")
                return True
            else:
                logger.warning("OCRMyPDF may not be properly installed")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.error(f"OCRMyPDF verification failed: {e}")
            return False

    def is_available(self) -> bool:
        """Check if OCRMyPDF is available

        Returns:
            bool: True if OCRMyPDF is installed and working
        """
        return self.available

    def process_image(self, image_path: str) -> Dict:
        """
        Process image with OCRMyPDF

        Note: OCRMyPDF works best with PDFs, but we can convert images to PDF first

        Args:
            image_path: Path to the image file

        Returns:
            Dictionary containing OCR results
        """
        try:
            # Check if it's already a PDF
            is_pdf = image_path.lower().endswith('.pdf')

            if is_pdf:
                return self._process_pdf(image_path)
            else:
                return self._process_image_as_pdf(image_path)

        except Exception as e:
            logger.error(f"OCRMyPDF processing failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'confidence': 0.0
            }

    def _process_image_as_pdf(self, image_path: str) -> Dict:
        """Convert image to PDF and process with OCRMyPDF"""
        temp_pdf_path = None
        try:
            from PIL import Image

            # Create temporary PDF from image - get path only, close file handle
            temp_pdf_fd = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
            temp_pdf_path = temp_pdf_fd.name
            temp_pdf_fd.close()  # Close file handle before writing

            # Convert image to PDF
            image = Image.open(image_path)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            image.save(temp_pdf_path, 'PDF', resolution=300.0)

            # Process the PDF
            result = self._process_pdf(temp_pdf_path)

            # Cleanup
            try:
                os.unlink(temp_pdf_path)
            except:
                pass

            return result

        except Exception as e:
            logger.error(f"Image to PDF conversion failed: {e}")
            # Cleanup on error
            if temp_pdf_path:
                try:
                    os.unlink(temp_pdf_path)
                except:
                    pass
            return {
                'success': False,
                'error': f'Image conversion failed: {str(e)}',
                'text': '',
                'confidence': 0.0
            }

    def _process_pdf(self, pdf_path: str) -> Dict:
        """Process PDF with OCRMyPDF"""
        temp_output_path = None
        temp_text_path = None
        try:
            # Create temporary output PDF - get path only, close file handle
            temp_output_fd = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
            temp_output_path = temp_output_fd.name
            temp_output_fd.close()  # Close file handle before OCRMyPDF writes to it

            # Create temporary text output - get path only, close file handle
            temp_text_fd = tempfile.NamedTemporaryFile(suffix='.txt', delete=False, mode='w')
            temp_text_path = temp_text_fd.name
            temp_text_fd.close()  # Close file handle before OCRMyPDF writes to it

            # Run OCRMyPDF with sidecar text output
            cmd = [
                'ocrmypdf',
                '--force-ocr',  # Always OCR, even if PDF already has text
                '--sidecar', temp_text_path,  # Output text to separate file
                '--output-type', 'pdf',
                '--optimize', '0',  # No optimization for speed
                '--language', 'eng+tur',  # English and Turkish
                '--deskew',  # Correct skew
                '--rotate-pages',  # Auto-rotate pages
                '--clean',  # Clean up artifacts
                pdf_path,
                temp_output_path
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                error_msg = result.stderr if result.stderr else 'Unknown error'
                logger.error(f"OCRMyPDF failed: {error_msg}")
                # Cleanup
                try:
                    os.unlink(temp_output_path)
                    os.unlink(temp_text_path)
                except:
                    pass
                return {
                    'success': False,
                    'error': f'OCRMyPDF error: {error_msg}',
                    'text': '',
                    'confidence': 0.0
                }

            # Read extracted text
            with open(temp_text_path, 'r', encoding='utf-8') as f:
                extracted_text = f.read()

            # Cleanup
            try:
                os.unlink(temp_output_path)
                os.unlink(temp_text_path)
            except:
                pass

            if not extracted_text or not extracted_text.strip():
                return {
                    'success': False,
                    'error': 'No text extracted',
                    'text': '',
                    'confidence': 0.0
                }

            # Extract key information
            key_findings = self._extract_key_information(extracted_text)

            # Calculate quality metrics
            # OCRMyPDF doesn't provide confidence scores, so we estimate based on text quality
            confidence = self._estimate_confidence(extracted_text)
            metrics = self._calculate_metrics(extracted_text, confidence)

            return {
                'success': True,
                'text': extracted_text,
                'confidence': confidence * 100,  # Convert to percentage (0-100)
                'key_findings': key_findings,
                'metrics': metrics,
                'backend': 'Tesseract (via OCRMyPDF)'
            }

        except subprocess.TimeoutExpired:
            logger.error("OCRMyPDF processing timed out")
            # Cleanup on timeout
            try:
                if temp_output_path:
                    os.unlink(temp_output_path)
                if temp_text_path:
                    os.unlink(temp_text_path)
            except:
                pass
            return {
                'success': False,
                'error': 'Processing timed out after 30 seconds',
                'text': '',
                'confidence': 0.0
            }
        except Exception as e:
            logger.error(f"OCRMyPDF PDF processing failed: {e}")
            # Cleanup on error
            try:
                if temp_output_path:
                    os.unlink(temp_output_path)
                if temp_text_path:
                    os.unlink(temp_text_path)
            except:
                pass
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'confidence': 0.0
            }

    def _estimate_confidence(self, text: str) -> float:
        """
        Estimate confidence based on text quality
        OCRMyPDF doesn't provide confidence scores, so we estimate
        """
        if not text or not text.strip():
            return 0.0

        # Simple heuristic based on text characteristics
        score = 0.5  # Base score

        # Check for reasonable word length
        words = text.split()
        if words:
            avg_word_len = sum(len(w) for w in words) / len(words)
            if 3 <= avg_word_len <= 8:  # Reasonable average word length
                score += 0.2

        # Check for reasonable character distribution
        alpha_count = sum(1 for c in text if c.isalpha())
        if alpha_count > len(text) * 0.5:  # At least 50% letters
            score += 0.2

        # Check for structure (newlines indicate proper text structure)
        lines = [l for l in text.split('\n') if l.strip()]
        if len(lines) > 3:
            score += 0.1

        return min(score, 1.0)

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
