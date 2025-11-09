"""
OCR Service for Document Processing
Handles OCR operations using Tesseract and fallback methods
"""

import re
import json
import os
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
import logging
from pathlib import Path

# Import advanced parser
try:
    from .advanced_ocr_parser import TurkishReceiptParser
    ADVANCED_PARSER_AVAILABLE = True
except ImportError:
    ADVANCED_PARSER_AVAILABLE = False
    print("Warning: Advanced parser not available.")

# Import AI enhancer
try:
    from .ai_ocr_enhancer import AIReceiptAnalyzer
    AI_ENHANCER_AVAILABLE = True
except ImportError:
    AI_ENHANCER_AVAILABLE = False
    print("Warning: AI enhancer not available.")

# OCR libraries - graceful degradation if not available
try:
    import pytesseract
    from PIL import Image, ImageEnhance, ImageFilter
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    print("Warning: pytesseract not installed. OCR features will be limited.")

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("Warning: OpenCV not installed. Image preprocessing will be limited.")

logger = logging.getLogger('documents.ocr')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class OCRProcessor:
    """Main OCR processing class"""
    
    # Common Turkish store names and patterns
    STORE_PATTERNS = {
        'migros': ['MİGROS', 'MIGROS', 'M-JET'],
        'a101': ['A101', 'A 101'],
        'bim': ['BİM', 'BIM', 'BİM BİRLEŞİK'],
        'şok': ['ŞOK', 'SOK', 'ŞOK MARKET'],
        'carrefour': ['CARREFOUR', 'CARREFOURSA'],
        'metro': ['METRO', 'METRO GROSS'],
    }
    
    # Payment method patterns
    PAYMENT_PATTERNS = {
        'credit_card': [r'KREDI KARTI', r'KREDİ KARTI', r'K\.KARTI', r'\*{3,4}\d{4}'],
        'debit_card': [r'BANKA KARTI', r'DEBIT', r'DEBİT'],
        'cash': [r'NAKİT', r'NAKIT', r'PEŞİN', r'PESIN'],
    }
    
    # Date patterns - Updated to support Turkish receipt formats
    DATE_PATTERNS = [
        r'(\d{2})-(\d{2})-(\d{4})',           # DD-MM-YYYY (tire ile)
        r'(\d{2})\.(\d{2})\.(\d{4})',         # DD.MM.YYYY (nokta ile)
        r'(\d{2})/(\d{2})/(\d{4})',           # DD/MM/YYYY (slash ile)
        r'(\d{2})-(\d{2})-(\d{2})',           # DD-MM-YY (tire ile kısa)
        r'(\d{2})\.(\d{2})\.(\d{2})',         # DD.MM.YY (nokta ile kısa)
        r'(\d{2})/(\d{2})/(\d{2})',           # DD/MM/YY (slash ile kısa)
        r'(\d{4})-(\d{2})-(\d{2})',           # YYYY-MM-DD (ISO format)
        r'(\d{4})\.(\d{2})\.(\d{2})',         # YYYY.MM.DD
        r'(\d{4})/(\d{2})/(\d{2})',           # YYYY/MM/DD
    ]
    
    # Amount patterns
    AMOUNT_PATTERNS = [
        r'TOPLAM\s*:?\s*([\d,\.]+)',
        r'TOTAL\s*:?\s*([\d,\.]+)',
        r'GENEL TOPLAM\s*:?\s*([\d,\.]+)',
        r'ÖDENECEK\s*:?\s*([\d,\.]+)',
    ]
    
    def __init__(self):
        self.tesseract_available = TESSERACT_AVAILABLE
        self.cv2_available = CV2_AVAILABLE
        self.ai_enhancer = None
        self.ollama_service = None

        # Initialize AI enhancer if available
        if AI_ENHANCER_AVAILABLE:
            try:
                # Default to Hugging Face for free usage
                self.ai_enhancer = AIReceiptAnalyzer(provider="huggingface")
                logger.info("AI enhancer initialized with Hugging Face")
            except Exception as e:
                logger.warning(f"Failed to initialize AI enhancer: {e}")
                self.ai_enhancer = None

        # Initialize Ollama service for direct LLM OCR
        try:
            from .ollama_service import OllamaService
            self.ollama_service = OllamaService()
            if self.ollama_service.is_available():
                logger.info(f"Ollama service initialized with models: {self.ollama_service.models}")
            else:
                logger.info("Ollama service not available")
                self.ollama_service = None
        except Exception as e:
            logger.warning(f"Failed to initialize Ollama service: {e}")
            self.ollama_service = None
    
    def process_document(self, image_path: str, document_type: str = 'receipt', force_ocr: bool = False, force_enhance: bool = False, document_instance=None) -> Dict:
        """
        Main entry point for OCR processing - processes ALL document types
        Now runs BOTH Tesseract and Ollama in parallel for comparison
        """
        logger.info(f"Starting DUAL OCR processing for: {image_path}, type: {document_type}")

        try:
            # Check if processing is paused (early abort)
            from django.core.cache import cache
            if cache.get('ocr_processing_paused', False):
                logger.info("OCR processing paused - aborting document processing")
                return {
                    'success': False,
                    'error': 'Processing paused by user',
                    'ocr_text': '',
                    'parsed_data': {},
                    'confidence': 0
                }

            # Ensure file exists
            if not os.path.exists(image_path):
                logger.error(f"File not found: {image_path}")
                return {
                    'success': False,
                    'error': f'File not found: {image_path}',
                    'ocr_text': '',
                    'parsed_data': {},
                    'confidence': 0
                }

            # Preprocess image if OpenCV available
            if self.cv2_available:
                # Use forced enhancement if this is a rescan
                processed_image = self.preprocess_image(image_path, force_enhance=force_ocr or force_enhance)
            else:
                processed_image = image_path

            # === PARALLEL PROCESSING: Run both Tesseract and Ollama independently ===
            tesseract_result = self._process_with_tesseract(processed_image, image_path, document_type)

            # Check pause again before Ollama (in case user paused during Tesseract)
            if cache.get('ocr_processing_paused', False):
                logger.info("OCR processing paused - aborting before Ollama processing")
                return {
                    'success': False,
                    'error': 'Processing paused by user',
                    'ocr_text': '',
                    'parsed_data': {},
                    'confidence': 0
                }

            ollama_result = self._process_with_ollama(image_path, document_type)

            # Store both results in document instance if provided
            if document_instance:
                # Save Tesseract results
                document_instance.tesseract_text = tesseract_result.get('text', '')
                document_instance.tesseract_confidence = tesseract_result.get('confidence', 0)
                document_instance.tesseract_parsed_data = tesseract_result.get('parsed_data', {})

                # Save Ollama results
                document_instance.ollama_text = ollama_result.get('text', '')
                document_instance.ollama_confidence = ollama_result.get('confidence', 0)
                document_instance.ollama_parsed_data = ollama_result.get('parsed_data', {})
                document_instance.ollama_model = ollama_result.get('model', '')

                # Set default OCR text based on preferred method or best confidence
                if document_instance.preferred_ocr_method == 'tesseract':
                    document_instance.ocr_text = tesseract_result.get('text', '')
                    document_instance.ocr_confidence = tesseract_result.get('confidence', 0)
                    ocr_method = 'tesseract (preferred)'
                elif document_instance.preferred_ocr_method == 'ollama':
                    document_instance.ocr_text = ollama_result.get('text', '')
                    document_instance.ocr_confidence = ollama_result.get('confidence', 0)
                    ocr_method = 'ollama (preferred)'
                else:
                    # Auto-select best result
                    if ollama_result.get('confidence', 0) > tesseract_result.get('confidence', 0):
                        document_instance.ocr_text = ollama_result.get('text', '')
                        document_instance.ocr_confidence = ollama_result.get('confidence', 0)
                        ocr_method = 'ollama (auto-selected)'
                    else:
                        document_instance.ocr_text = tesseract_result.get('text', '')
                        document_instance.ocr_confidence = tesseract_result.get('confidence', 0)
                        ocr_method = 'tesseract (auto-selected)'

                # Mark as completed
                from django.utils import timezone
                document_instance.processing_status = 'completed'
                document_instance.ocr_processed_at = timezone.now()

                # Save the document
                document_instance.save()

                logger.info(f"Dual OCR complete - Tesseract: {len(tesseract_result.get('text', ''))} chars, "
                           f"Ollama: {len(ollama_result.get('text', ''))} chars - Using: {ocr_method}")

            # Use preferred or best result for parsed_data
            if ollama_result.get('success') and ollama_result.get('confidence', 0) > tesseract_result.get('confidence', 0):
                parsed_data = ollama_result.get('parsed_data', {})
                confidence = ollama_result.get('confidence', 0)
                ocr_text = ollama_result.get('text', '')
            else:
                parsed_data = tesseract_result.get('parsed_data', {})
                confidence = tesseract_result.get('confidence', 0)
                ocr_text = tesseract_result.get('text', '')

            # Create ParsedReceipt if document instance is provided and type is receipt
            if document_instance and document_type == 'receipt' and parsed_data and ocr_text:
                self.create_parsed_receipt(document_instance, parsed_data)

            return {
                'success': True,
                'ocr_text': ocr_text,
                'parsed_data': parsed_data,
                'confidence': confidence,
                'ocr_method': ocr_method if document_instance else 'dual',
                'text_length': len(ocr_text),
                'tesseract_result': tesseract_result,
                'ollama_result': ollama_result
            }

        except Exception as e:
            logger.error(f"OCR processing failed with exception: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'ocr_text': '',
                'parsed_data': {},
                'confidence': 0
            }

    def _process_with_tesseract(self, processed_image: str, original_image: str, document_type: str) -> Dict:
        """Process document using Tesseract OCR"""
        try:
            ocr_text = ""
            ocr_method = "none"

            if self.tesseract_available:
                try:
                    ocr_text = self.extract_text_tesseract(processed_image)
                    ocr_method = "tesseract"
                    logger.info(f"Tesseract extracted {len(ocr_text)} characters")
                except Exception as e:
                    logger.error(f"Tesseract failed: {e}, trying enhanced method")
                    ocr_text = self.extract_text_enhanced(original_image)
                    ocr_method = "enhanced"
            else:
                logger.warning("Tesseract not available, using fallback OCR")
                ocr_text = self.fallback_ocr(original_image)
                ocr_method = "fallback"

            # Parse the extracted text
            parsed_data = {}
            ai_enhanced_data = {}

            # Try AI enhancement if available
            if self.ai_enhancer and ocr_text and len(ocr_text) > 50:
                try:
                    logger.info("Attempting AI enhancement of Tesseract OCR text...")
                    ai_enhanced_data = self.ai_enhancer.analyze_receipt_with_ai(
                        ocr_text,
                        enhance_mode='full' if document_type == 'receipt' else 'quick'
                    )

                    if ai_enhanced_data and ai_enhanced_data.get('store_info'):
                        logger.info("AI enhancement successful")
                        parsed_data['ai_enhanced'] = True
                        parsed_data['ai_confidence'] = 0.85
                except Exception as e:
                    logger.warning(f"AI enhancement failed: {e}")
                    ai_enhanced_data = {}

            if document_type == 'receipt':
                if ADVANCED_PARSER_AVAILABLE:
                    try:
                        advanced_parser = TurkishReceiptParser()
                        advanced_result = advanced_parser.parse(ocr_text)
                        if advanced_result.get('success'):
                            parsed_data = OCRProcessorHelper._convert_advanced_result(advanced_result)
                            parsed_data['needs_review'] = True
                            parsed_data['confidence_score'] = OCRProcessorHelper._calculate_confidence(advanced_result)
                            parsed_data['validation'] = advanced_result.get('validation', {})
                        else:
                            parsed_data = self.parse_receipt(ocr_text)
                            parsed_data['needs_review'] = True
                    except Exception as e:
                        logger.error(f"Advanced parser failed: {e}")
                        parsed_data = self.parse_receipt(ocr_text)
                        parsed_data['needs_review'] = True
                else:
                    parsed_data = self.parse_receipt(ocr_text)
                    parsed_data['needs_review'] = True

                if ai_enhanced_data:
                    parsed_data = self._merge_ai_data(parsed_data, ai_enhanced_data)
            elif document_type == 'invoice':
                parsed_data = self.parse_invoice(ocr_text)
            elif document_type in ['bank_statement', 'cc_statement']:
                parsed_data = self.parse_statement(ocr_text)
            else:
                parsed_data = {
                    'raw_text': ocr_text,
                    'document_type': document_type,
                    'lines': ocr_text.split('\n') if ocr_text else [],
                    'word_count': len(ocr_text.split()) if ocr_text else 0
                }

            confidence = self.calculate_confidence(parsed_data) if ocr_text else 0

            return {
                'success': bool(ocr_text),
                'text': ocr_text,
                'parsed_data': parsed_data,
                'confidence': confidence,
                'method': ocr_method
            }
        except Exception as e:
            logger.error(f"Tesseract processing failed: {e}")
            return {
                'success': False,
                'text': '',
                'parsed_data': {},
                'confidence': 0,
                'error': str(e)
            }

    def _process_with_ollama(self, image_path: str, document_type: str) -> Dict:
        """Process document using Ollama LLM - completely independent vision-based OCR"""
        try:
            if not self.ollama_service or not self.ollama_service.is_available():
                logger.info("Ollama service not available, skipping")
                return {
                    'success': False,
                    'text': '',
                    'parsed_data': {},
                    'confidence': 0,
                    'model': ''
                }

            # Use Ollama to read the image directly with vision model
            logger.info("Processing with Ollama vision model (independent from Tesseract)...")

            # Read image and convert to base64
            import base64
            with open(image_path, 'rb') as f:
                image_data = f.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')

            # Analyze with Ollama - NO OCR text, let it read the image itself
            ollama_result = self.ollama_service.analyze_receipt(
                ocr_text='',  # Empty - Ollama will read image directly
                image_base64=image_base64
            )

            if ollama_result and ollama_result.get('success'):
                logger.info(f"Ollama processing successful with model {self.ollama_service.current_model}")

                # Get the raw OCR text from Ollama's vision output
                raw_text = ollama_result.get('raw_response', '').strip()

                # Extract structured data (if available from parsing)
                parsed_data = {
                    'store_name': ollama_result.get('store_info', {}).get('name', ''),
                    'store_address': ollama_result.get('store_info', {}).get('address', ''),
                    'transaction_date': ollama_result.get('transaction_info', {}).get('date', ''),
                    'total_amount': ollama_result.get('transaction_info', {}).get('total', 0),
                    'items': ollama_result.get('items', []),
                    'payment_method': ollama_result.get('transaction_info', {}).get('payment_method', ''),
                    'raw_ollama_data': ollama_result,
                    'needs_review': False
                }

                # Get confidence from Ollama (default to 85% for vision OCR)
                confidence = ollama_result.get('confidence', 85.0)
                # If confidence is between 0-1, convert to percentage
                if confidence <= 1.0:
                    confidence = confidence * 100

                return {
                    'success': True,
                    'text': raw_text,  # Direct OCR text from vision model
                    'parsed_data': parsed_data,
                    'confidence': confidence,
                    'model': self.ollama_service.current_model
                }
            else:
                logger.warning("Ollama processing returned no results")
                return {
                    'success': False,
                    'text': '',
                    'parsed_data': {},
                    'confidence': 0,
                    'model': self.ollama_service.current_model
                }
        except Exception as e:
            logger.error(f"Ollama processing failed: {e}")
            return {
                'success': False,
                'text': '',
                'parsed_data': {},
                'confidence': 0,
                'error': str(e)
            }
    
    def preprocess_image(self, image_path: str, force_enhance: bool = False) -> str:
        """
        Preprocess image for better OCR results with optional forced enhancement
        """
        if not self.cv2_available:
            return image_path
        
        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                logger.error(f"Failed to read image: {image_path}")
                return image_path
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            if force_enhance:
                logger.info("Applying gentle enhancement preprocessing...")
                
                # 1. Resize for better OCR (if too small)
                height, width = gray.shape
                if width < 800:  # Only resize if really small
                    scale = 1200 / width
                    new_width = int(width * scale)
                    new_height = int(height * scale)
                    gray = cv2.resize(gray, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
                    logger.info(f"Resized image from {width}x{height} to {new_width}x{new_height}")
                
                # 2. Gentle contrast enhancement
                # Simple brightness/contrast adjustment
                alpha = 1.2  # Contrast control (1.0-3.0)
                beta = 10    # Brightness control (0-100)
                gray = cv2.convertScaleAbs(gray, alpha=alpha, beta=beta)
                
                # 3. Light denoising (less aggressive)
                gray = cv2.medianBlur(gray, 3)
                
                # 4. Binary threshold with OTSU (more reliable than adaptive)
                _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                
                # 5. Small morphological cleanup
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
                thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
                
                # Skip deskew and shadow removal - they can distort text
                
            else:
                # Standard preprocessing
                # Apply thresholding
                _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                
                # Denoise
                thresh = cv2.medianBlur(thresh, 1)
            
            # Save processed image
            processed_path = image_path.replace('.', '_processed.')
            cv2.imwrite(processed_path, thresh)
            logger.info(f"Saved preprocessed image to: {processed_path}")
            
            return processed_path
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {str(e)}")
            return image_path
    
    def deskew_image(self, image):
        """Deskew image to correct rotation"""
        try:
            coords = np.column_stack(np.where(image > 0))
            angle = cv2.minAreaRect(coords)[-1]
            
            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle
            
            if abs(angle) > 0.5:  # Only deskew if angle is significant
                (h, w) = image.shape[:2]
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                rotated = cv2.warpAffine(image, M, (w, h),
                                        flags=cv2.INTER_CUBIC,
                                        borderMode=cv2.BORDER_REPLICATE)
                logger.info(f"Deskewed image by {angle:.2f} degrees")
                return rotated
        except:
            pass
        return image
    
    def remove_shadows(self, image):
        """Remove shadows from image for better OCR"""
        try:
            dilated = cv2.dilate(image, np.ones((7,7), np.uint8))
            bg = cv2.medianBlur(dilated, 21)
            diff = 255 - cv2.absdiff(image, bg)
            norm = cv2.normalize(diff, None, alpha=0, beta=255,
                               norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
            return norm
        except:
            return image
    
    def extract_text_tesseract(self, image_path: str) -> str:
        """
        Extract text using Tesseract OCR with multiple attempts
        """
        if not self.tesseract_available:
            return ""
        
        try:
            # Open image
            image = Image.open(image_path)
            
            # Try multiple OCR configurations for better results
            # Optimized configs: PSM 6 (uniform block) works best for receipts
            # OEM 1 (LSTM) is more accurate than OEM 3 (legacy+LSTM hybrid)
            configs = [
                r'--oem 1 --psm 6 -l eng',      # English with LSTM (PRIMARY - best for receipts)
                r'--oem 1 --psm 6 -l tur+eng',  # Turkish+English with LSTM
                r'--oem 1 --psm 4 -l eng',      # Single column English
                r'--oem 1 --psm 3 -l eng',      # Fully automatic (fallback)
            ]
            
            best_text = ""
            best_length = 0
            
            for config in configs:
                try:
                    text = pytesseract.image_to_string(image, config=config)
                    if len(text) > best_length:
                        best_text = text
                        best_length = len(text)
                        logger.debug(f"Config {config} extracted {len(text)} chars")
                except Exception as e:
                    logger.debug(f"Config {config} failed: {e}")
                    continue
            
            return best_text
            
        except Exception as e:
            logger.error(f"Tesseract OCR failed: {str(e)}")
            return ""
    
    def extract_text_enhanced(self, image_path: str) -> str:
        """
        Enhanced text extraction with image preprocessing
        """
        if not self.tesseract_available:
            return ""
        
        try:
            # Open and enhance image
            image = Image.open(image_path)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Gentle enhancement (aggressive enhancement causes artifacts)
            # For receipts, subtle improvements work better
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.2)  # Reduced from 2.0 to 1.2

            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.3)  # Reduced from 2.0 to 1.3

            # Skip median filter (can blur small text)
            # image = image.filter(ImageFilter.MedianFilter(size=3))

            # Try OCR on enhanced image with optimized config
            text = pytesseract.image_to_string(image, config=r'--oem 1 --psm 6 -l eng')
            
            return text
            
        except Exception as e:
            logger.error(f"Enhanced OCR failed: {str(e)}")
            return ""
    
    def fallback_ocr(self, image_path: str) -> str:
        """
        Fallback OCR method when Tesseract is not available
        Returns empty string or error message instead of random text
        """
        logger.warning("Using fallback OCR - Tesseract not available")
        
        try:
            # Try to use PIL to at least verify the image is readable
            from PIL import Image
            
            # Open the image to verify it's valid
            img = Image.open(image_path)
            width, height = img.size
            
            logger.warning(f"Fallback OCR: Image loaded ({width}x{height}), but cannot extract text without Tesseract")
            
            # Return empty string to indicate OCR couldn't be performed
            # This will trigger manual review status
            return ""
            
        except Exception as e:
            logger.error(f"Fallback OCR failed to open image: {e}")
            # Return empty string to indicate OCR failed
            return ""
    
    def parse_receipt(self, ocr_text: str) -> Dict:
        """
        Parse receipt text to extract structured data
        """
        lines = ocr_text.split('\n')
        parsed = {
            'store_name': '',
            'transaction_date': None,
            'total_amount': None,
            'items': [],
            'payment_method': '',
            'card_last_digits': '',
            'receipt_number': '',
            'raw_lines': lines
        }
        
        # Extract store name
        parsed['store_name'] = self.extract_store_name(lines)
        
        # Extract date
        parsed['transaction_date'] = self.extract_date(ocr_text)
        
        # Extract total amount
        parsed['total_amount'] = self.extract_total_amount(ocr_text)
        
        # Extract items
        parsed['items'] = self.extract_items(lines)
        
        # Extract payment method
        parsed['payment_method'], parsed['card_last_digits'] = self.extract_payment_info(ocr_text)
        
        # Extract receipt number
        parsed['receipt_number'] = self.extract_receipt_number(ocr_text)
        
        return parsed
    
    def extract_store_name(self, lines: List[str]) -> str:
        """
        Extract store name from receipt lines
        """
        # Check first 5 lines for store patterns
        for line in lines[:5]:
            line_upper = line.upper()
            for store, patterns in self.STORE_PATTERNS.items():
                for pattern in patterns:
                    if pattern in line_upper:
                        return store.upper()
        
        # If no known store found, return first non-empty line
        for line in lines[:3]:
            if line.strip():
                return line.strip()
        
        return "Unknown Store"
    
    def extract_date(self, text: str) -> Optional[datetime]:
        """
        Extract date from OCR text - Improved for Turkish receipts
        """
        # First, try to find date with "TARİH" keyword
        tarih_patterns = [
            r'TAR[İI]H\s*:?\s*(\d{2}[-./]\d{2}[-./]\d{2,4})',
            r'DATE\s*:?\s*(\d{2}[-./]\d{2}[-./]\d{2,4})',
            r'(\d{2}[-./]\d{2}[-./]\d{2,4})\s+(?:SAAT|TIME)',
        ]
        
        for pattern in tarih_patterns:
            match = re.search(pattern, text.upper())
            if match:
                date_str = match.group(1)
                parsed_date = self._parse_date_string(date_str)
                if parsed_date:
                    return parsed_date
        
        # If no keyword found, try general date patterns
        for pattern in self.DATE_PATTERNS:
            matches = re.finditer(pattern, text)
            for match in matches:
                try:
                    groups = match.groups()
                    if len(groups) == 3:
                        # Determine date format based on values
                        first, second, third = map(int, groups)
                        
                        # Check if it's YYYY-MM-DD format
                        if first > 1900 and first < 2100:
                            # YYYY-MM-DD or YYYY/MM/DD or YYYY.MM.DD
                            return datetime(first, second, third)
                        
                        # Otherwise assume DD-MM-YYYY format (Turkish standard)
                        if third > 1900 and third < 2100:
                            # Full year: DD-MM-YYYY
                            return datetime(third, second, first)
                        elif third < 100:
                            # Two digit year: DD-MM-YY
                            year = 2000 + third if third < 50 else 1900 + third
                            return datetime(year, second, first)
                except (ValueError, TypeError):
                    continue
        
        # Try Turkish month names as fallback
        turkish_months = {
            'OCAK': 1, 'ŞUBAT': 2, 'MART': 3, 'NİSAN': 4,
            'MAYIS': 5, 'HAZİRAN': 6, 'TEMMUZ': 7, 'AĞUSTOS': 8,
            'EYLÜL': 9, 'EKİM': 10, 'KASIM': 11, 'ARALIK': 12
        }
        
        pattern = r'(\d{1,2})\s+(OCAK|ŞUBAT|MART|NİSAN|MAYIS|HAZİRAN|TEMMUZ|AĞUSTOS|EYLÜL|EKİM|KASIM|ARALIK)\s+(\d{4})'
        match = re.search(pattern, text.upper())
        if match:
            try:
                day = int(match.group(1))
                month = turkish_months[match.group(2)]
                year = int(match.group(3))
                return datetime(year, month, day)
            except (ValueError, KeyError):
                pass
        
        return None
    
    def _parse_date_string(self, date_str: str) -> Optional[datetime]:
        """
        Helper method to parse various date string formats
        """
        # Clean the date string
        date_str = date_str.strip()
        
        # Try different separators and formats
        for separator in ['-', '.', '/']:
            if separator in date_str:
                parts = date_str.split(separator)
                if len(parts) == 3:
                    try:
                        day, month, year = map(int, parts)
                        
                        # Handle 2-digit years
                        if year < 100:
                            year = 2000 + year if year < 50 else 1900 + year
                        
                        # Validate and create date
                        if 1 <= day <= 31 and 1 <= month <= 12 and 1900 <= year <= 2100:
                            return datetime(year, month, day)
                    except (ValueError, TypeError):
                        continue
        
        return None
    
    def extract_total_amount(self, text: str) -> Optional[Decimal]:
        """
        Extract total amount from OCR text
        """
        for pattern in self.AMOUNT_PATTERNS:
            match = re.search(pattern, text.upper())
            if match:
                try:
                    # Clean amount string
                    amount_str = match.group(1)
                    amount_str = amount_str.replace(',', '.')
                    amount_str = re.sub(r'[^\d\.]', '', amount_str)
                    
                    return Decimal(amount_str)
                except:
                    continue
        
        return None
    
    def extract_items(self, lines: List[str]) -> List[Dict]:
        """
        Extract individual items from receipt
        """
        items = []
        item_pattern = r'(.+?)\s+([\d,\.]+)\s*[xX*]\s*([\d,\.]+)\s*=?\s*([\d,\.]+)'
        
        for line in lines:
            # Try to match item pattern
            match = re.search(item_pattern, line)
            if match:
                try:
                    items.append({
                        'name': match.group(1).strip(),
                        'quantity': float(match.group(2).replace(',', '.')),
                        'unit_price': float(match.group(3).replace(',', '.')),
                        'total_price': float(match.group(4).replace(',', '.'))
                    })
                except:
                    # Try simpler pattern
                    simple_pattern = r'(.+?)\s+([\d,\.]+)$'
                    simple_match = re.search(simple_pattern, line)
                    if simple_match:
                        try:
                            items.append({
                                'name': simple_match.group(1).strip(),
                                'quantity': 1,
                                'unit_price': float(simple_match.group(2).replace(',', '.')),
                                'total_price': float(simple_match.group(2).replace(',', '.'))
                            })
                        except:
                            pass
        
        return items
    
    def extract_payment_info(self, text: str) -> Tuple[str, str]:
        """
        Extract payment method and card digits
        """
        payment_method = 'unknown'
        card_digits = ''
        
        # Check for payment patterns
        for method, patterns in self.PAYMENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text.upper()):
                    payment_method = method
                    break
        
        # Extract card last 4 digits
        card_pattern = r'\*{3,4}(\d{4})'
        match = re.search(card_pattern, text)
        if match:
            card_digits = match.group(1)
        
        return payment_method, card_digits
    
    def extract_receipt_number(self, text: str) -> str:
        """
        Extract receipt/fiscal number
        """
        patterns = [
            r'FİŞ NO\s*:?\s*(\S+)',
            r'FIS NO\s*:?\s*(\S+)',
            r'BELGE NO\s*:?\s*(\S+)',
            r'NO\s*:?\s*(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.upper())
            if match:
                return match.group(1)
        
        return ''
    
    def create_parsed_receipt(self, document_instance, parsed_data: Dict):
        """
        Create or update ParsedReceipt from parsed data
        """
        from .models import ParsedReceipt, ReceiptItem
        from decimal import Decimal
        
        try:
            # Delete existing parsed receipt if exists
            if hasattr(document_instance, 'parsed_receipt'):
                document_instance.parsed_receipt.delete()
            
            # Create new ParsedReceipt
            receipt = ParsedReceipt.objects.create(
                document=document_instance,
                store_name=parsed_data.get('store_name', ''),
                store_address=parsed_data.get('store_address', ''),
                store_phone=parsed_data.get('store_phone', ''),
                store_tax_id=parsed_data.get('store_tax_id', ''),
                transaction_date=parsed_data.get('transaction_date'),
                receipt_number=parsed_data.get('receipt_number', ''),
                cashier_id=parsed_data.get('cashier_id', ''),
                subtotal=Decimal(str(parsed_data['total_amount'])) if parsed_data.get('total_amount') else None,
                tax_amount=parsed_data.get('tax_amount'),
                discount_amount=parsed_data.get('discount_amount'),
                total_amount=Decimal(str(parsed_data['total_amount'])) if parsed_data.get('total_amount') else None,
                payment_method=parsed_data.get('payment_method', ''),
                card_last_digits=parsed_data.get('card_last_digits', ''),
                currency=parsed_data.get('currency', 'TRY'),
                raw_ocr_data=parsed_data
            )
            
            # Create ReceiptItems
            for item_data in parsed_data.get('items', []):
                ReceiptItem.objects.create(
                    receipt=receipt,
                    name=item_data.get('name', ''),
                    quantity=Decimal(str(item_data.get('quantity', 1))),
                    unit_price=Decimal(str(item_data.get('unit_price', 0))),
                    total_price=Decimal(str(item_data.get('total_price', 0))),
                    category=item_data.get('category', ''),
                    barcode=item_data.get('barcode', ''),
                    discount_amount=Decimal(str(item_data.get('discount', 0))) if item_data.get('discount') else None
                )
            
            logger.info(f"Created ParsedReceipt for document {document_instance.id} with {len(parsed_data.get('items', []))} items")
            return receipt
            
        except Exception as e:
            logger.error(f"Failed to create ParsedReceipt: {str(e)}", exc_info=True)
            return None
    
    def calculate_confidence(self, parsed_data: Dict) -> float:
        """
        Calculate confidence score for parsed data
        """
        score = 0.0
        max_score = 100.0
        
        # For receipts
        if 'store_name' in parsed_data:
            if parsed_data.get('store_name') and parsed_data['store_name'] != 'Unknown Store':
                score += 20
            
            if parsed_data.get('transaction_date'):
                score += 20
            
            if parsed_data.get('total_amount'):
                score += 25
            
            if parsed_data.get('items'):
                score += 20
            
            if parsed_data.get('payment_method') != 'unknown':
                score += 10
            
            if parsed_data.get('receipt_number'):
                score += 5
        # For other document types
        elif 'raw_text' in parsed_data:
            text = parsed_data.get('raw_text', '')
            if len(text) > 100:
                score += 40
            elif len(text) > 50:
                score += 20
            elif len(text) > 0:
                score += 10
            
            if parsed_data.get('lines', []):
                score += min(30, len(parsed_data['lines']) * 2)
            
            if parsed_data.get('word_count', 0) > 10:
                score += 30
        
        return min(score, 100.0)
    
    def _merge_ai_data(self, parsed_data: Dict, ai_data: Dict) -> Dict:
        """
        Merge AI-enhanced data with existing parsed data
        Prioritize AI data when confidence is high
        """
        if not ai_data:
            return parsed_data
        
        # Merge store info
        if ai_data.get('store_info'):
            if not parsed_data.get('store_name') or len(ai_data['store_info'].get('name', '')) > len(parsed_data.get('store_name', '')):
                parsed_data['store_name'] = ai_data['store_info'].get('name')
            if ai_data['store_info'].get('tax_id'):
                parsed_data['tax_id'] = ai_data['store_info'].get('tax_id')
            if ai_data['store_info'].get('address'):
                parsed_data['store_address'] = ai_data['store_info'].get('address')
        
        # Merge transaction data
        if ai_data.get('transaction'):
            if ai_data['transaction'].get('date'):
                parsed_data['transaction_date'] = ai_data['transaction'].get('date')
            if ai_data['transaction'].get('time'):
                parsed_data['transaction_time'] = ai_data['transaction'].get('time')
            if ai_data['transaction'].get('receipt_no'):
                parsed_data['receipt_number'] = ai_data['transaction'].get('receipt_no')
        
        # Merge financial data
        if ai_data.get('financial'):
            if ai_data['financial'].get('total'):
                parsed_data['total_amount'] = ai_data['financial'].get('total')
            if ai_data['financial'].get('tax_amount'):
                parsed_data['tax_amount'] = ai_data['financial'].get('tax_amount')
            if ai_data['financial'].get('discount'):
                parsed_data['discount_amount'] = ai_data['financial'].get('discount')
        
        # Merge payment data
        if ai_data.get('payment'):
            parsed_data['payment_method'] = ai_data['payment'].get('method')
            if ai_data['payment'].get('card_last_digits'):
                parsed_data['card_last_digits'] = ai_data['payment'].get('card_last_digits')
        
        # Merge items
        if ai_data.get('items') and len(ai_data['items']) > 0:
            parsed_data['items'] = ai_data['items']
            parsed_data['item_count'] = len(ai_data['items'])
        
        # Mark as AI enhanced
        parsed_data['ai_enhanced'] = True
        parsed_data['ai_provider'] = 'huggingface'  # or mistral/local
        
        return parsed_data
    
    def batch_ai_process(self, document_ids: List[int], progress_callback=None) -> Dict:
        """
        Batch process documents with AI enhancement
        
        Args:
            document_ids: List of document IDs to process
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dictionary with processing results
        """
        if not self.ai_enhancer:
            return {
                'success': False,
                'error': 'AI enhancer not available',
                'processed': 0
            }
        
        results = {
            'success': True,
            'processed': 0,
            'enhanced': 0,
            'failed': 0,
            'documents': []
        }
        
        # Import Document model here to avoid circular import
        from .models import Document
        
        documents = Document.objects.filter(id__in=document_ids)
        total = documents.count()
        
        for idx, doc in enumerate(documents):
            if progress_callback:
                progress_callback(idx + 1, total, f"Processing {doc.original_filename}")
            
            try:
                # Get OCR text
                ocr_text = doc.ocr_text or ""
                
                if not ocr_text:
                    # Try to extract OCR first
                    ocr_result = self.process_document(
                        doc.file_path.path,
                        document_type=doc.document_type
                    )
                    ocr_text = ocr_result.get('ocr_text', '')
                    
                    if ocr_text:
                        doc.ocr_text = ocr_text
                        doc.save()
                
                if ocr_text:
                    # Enhance with AI
                    ai_result = self.ai_enhancer.analyze_receipt_with_ai(
                        ocr_text,
                        enhance_mode='full'
                    )
                    
                    if ai_result:
                        # Update document with AI data
                        doc.ai_parsed_data = ai_result
                        doc.ai_processed = True
                        doc.save()
                        
                        results['enhanced'] += 1
                        results['documents'].append({
                            'id': doc.id,
                            'filename': doc.original_filename,
                            'ai_enhanced': True,
                            'data': ai_result
                        })
                
                results['processed'] += 1
                
            except Exception as e:
                logger.error(f"Error processing document {doc.id}: {str(e)}")
                results['failed'] += 1
                results['documents'].append({
                    'id': doc.id,
                    'filename': doc.original_filename,
                    'error': str(e)
                })
        
        return results
    
    def parse_invoice(self, ocr_text: str) -> Dict:
        """
        Parse invoice text to extract structured data
        """
        lines = ocr_text.split('\n') if ocr_text else []
        return {
            'document_type': 'invoice',
            'raw_text': ocr_text,
            'lines': lines,
            'company_name': self.extract_company_name(lines),
            'invoice_number': self.extract_invoice_number(ocr_text),
            'invoice_date': self.extract_date(ocr_text),
            'total_amount': self.extract_total_amount(ocr_text),
            'tax_amount': self.extract_tax_amount(ocr_text)
        }
    
    def parse_statement(self, ocr_text: str) -> Dict:
        """
        Parse bank/credit card statement
        """
        lines = ocr_text.split('\n') if ocr_text else []
        return {
            'document_type': 'statement',
            'raw_text': ocr_text,
            'lines': lines,
            'statement_date': self.extract_date(ocr_text),
            'transactions': self.extract_transactions(lines),
            'total_amount': self.extract_total_amount(ocr_text)
        }
    
    def extract_company_name(self, lines: List[str]) -> str:
        """
        Extract company name from invoice
        """
        for line in lines[:10]:
            if line.strip() and len(line.strip()) > 5:
                return line.strip()
        return "Unknown Company"
    
    def extract_invoice_number(self, text: str) -> str:
        """
        Extract invoice number
        """
        patterns = [
            r'FATURA NO\s*:?\s*(\S+)',
            r'INVOICE NO\s*:?\s*(\S+)',
            r'FATURA\s*#\s*(\S+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.upper())
            if match:
                return match.group(1)
        return ''
    
    def extract_tax_amount(self, text: str) -> Optional[Decimal]:
        """
        Extract tax amount from text
        """
        patterns = [
            r'KDV\s*:?\s*([\d,\.]+)',
            r'VAT\s*:?\s*([\d,\.]+)',
            r'TAX\s*:?\s*([\d,\.]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.upper())
            if match:
                try:
                    amount_str = match.group(1).replace(',', '.')
                    return Decimal(amount_str)
                except:
                    continue
        return None
    
    def extract_transactions(self, lines: List[str]) -> List[Dict]:
        """
        Extract transactions from statement
        """
        transactions = []
        # Simple transaction pattern
        pattern = r'(\d{2}[\./]\d{2}[\./]\d{2,4})\s+(.+?)\s+([\d,\.]+)'
        
        for line in lines:
            match = re.search(pattern, line)
            if match:
                transactions.append({
                    'date': match.group(1),
                    'description': match.group(2).strip(),
                    'amount': match.group(3)
                })
        
        return transactions


class BatchProcessor:
    """Process multiple documents in batch"""
    
    def __init__(self):
        self.ocr_processor = OCRProcessor()
    
    def process_batch(self, file_paths: List[str], user_id: int) -> Dict:
        """
        Process multiple documents
        """
        results = {
            'total': len(file_paths),
            'processed': 0,
            'failed': 0,
            'documents': []
        }
        
        for file_path in file_paths:
            try:
                # Process each document
                result = self.ocr_processor.process_document(file_path)
                
                if result['success']:
                    results['processed'] += 1
                else:
                    results['failed'] += 1
                
                results['documents'].append({
                    'file': file_path,
                    'result': result
                })
                
            except Exception as e:
                results['failed'] += 1
                results['documents'].append({
                    'file': file_path,
                    'error': str(e)
                })
        
        return results


class CrossModuleIntegrator:
    """
    Integrate parsed document data with other modules
    """
    
    @staticmethod
    def distribute_receipt_data(parsed_receipt: Dict, user_id: int):
        """
        Distribute receipt data to relevant modules
        """
        distributions = {
            'wimm': [],  # Financial transactions
            'kisisel_enflasyon': [],  # Price tracking
            'wims': []  # Inventory updates
        }
        
        # WIMM - Create transaction record
        if parsed_receipt.get('total_amount'):
            distributions['wimm'].append({
                'type': 'expense',
                'amount': parsed_receipt['total_amount'],
                'date': parsed_receipt.get('transaction_date'),
                'vendor': parsed_receipt.get('store_name'),
                'payment_method': parsed_receipt.get('payment_method'),
                'card_digits': parsed_receipt.get('card_last_digits')
            })
        
        # Kişisel Enflasyon - Track item prices
        for item in parsed_receipt.get('items', []):
            distributions['kisisel_enflasyon'].append({
                'product_name': item['name'],
                'price': item['unit_price'],
                'quantity': item['quantity'],
                'store': parsed_receipt.get('store_name'),
                'date': parsed_receipt.get('transaction_date')
            })
        
        # WIMS - Update inventory if applicable
        # (Check if items match user's tracked inventory)
        for item in parsed_receipt.get('items', []):
            # This would check against user's inventory items
            distributions['wims'].append({
                'item_name': item['name'],
                'quantity_added': item['quantity'],
                'purchase_price': item['unit_price'],
                'purchase_date': parsed_receipt.get('transaction_date')
            })
        
        return distributions


class OCRProcessorHelper:
    """Helper methods for OCRProcessor"""
    
    @staticmethod
    def _convert_advanced_result(advanced_result: Dict) -> Dict:
        """Convert advanced parser result to our format"""
        parsed_data = {
            'store_name': None,
            'store_address': None,
            'store_phone': None,
            'store_tax_id': None,
            'transaction_date': None,
            'transaction_time': None,
            'receipt_number': None,
            'cashier': None,
            'subtotal': None,
            'tax_amount': None,
            'total_amount': None,
            'payment_method': None,
            'card_last_digits': None,
            'items': [],
            'kdv_details': [],
            'validation_errors': [],
            'validation_warnings': []
        }
        
        # Store info
        if advanced_result.get('store_info'):
            store = advanced_result['store_info']
            parsed_data['store_name'] = store.get('name') or store.get('detected_chain')
            parsed_data['store_address'] = store.get('address')
            parsed_data['store_phone'] = store.get('phone')
            parsed_data['store_tax_id'] = store.get('tax_id')
        
        # Transaction info
        if advanced_result.get('transaction'):
            trans = advanced_result['transaction']
            parsed_data['transaction_date'] = trans.get('date')
            parsed_data['transaction_time'] = trans.get('time')
            parsed_data['receipt_number'] = trans.get('receipt_no')
            parsed_data['cashier'] = trans.get('cashier')
        
        # Financial info
        if advanced_result.get('financial'):
            fin = advanced_result['financial']
            parsed_data['subtotal'] = fin.get('subtotal')
            parsed_data['tax_amount'] = fin.get('total_kdv')
            parsed_data['total_amount'] = fin.get('total')
            parsed_data['payment_method'] = fin.get('payment_method')
            parsed_data['card_last_digits'] = fin.get('card_info')
            parsed_data['kdv_details'] = fin.get('kdv_details', [])
        
        # Items
        if advanced_result.get('items'):
            parsed_data['items'] = advanced_result['items']
        
        # Validation
        if advanced_result.get('validation'):
            parsed_data['validation_errors'] = advanced_result['validation'].get('errors', [])
            parsed_data['validation_warnings'] = advanced_result['validation'].get('warnings', [])
            parsed_data['kdv_valid'] = advanced_result['validation'].get('kdv_valid', False)
            parsed_data['total_valid'] = advanced_result['validation'].get('total_valid', False)
        
        return parsed_data
    
    @staticmethod
    def _calculate_confidence(advanced_result: Dict) -> float:
        """Calculate confidence score for parsed data"""
        score = 0.0
        total_checks = 0
        
        # Check store detection
        if advanced_result.get('store_info', {}).get('detected_chain'):
            score += 20
        total_checks += 20
        
        # Check financial validation
        if advanced_result.get('validation', {}).get('kdv_valid'):
            score += 30
        total_checks += 30
        
        if advanced_result.get('validation', {}).get('total_valid'):
            score += 30
        total_checks += 30
        
        # Check items
        if advanced_result.get('items'):
            score += 20
        total_checks += 20
        
        return (score / total_checks) * 100 if total_checks > 0 else 0