"""
PaddleOCR Integration Service for Document OCR
Alternative OCR engine with 80+ language support and high accuracy
Includes PP-Structure for layout analysis and table recognition
"""

import logging
from typing import Dict, Optional, List
import os

logger = logging.getLogger('documents.paddleocr')


class PaddleOCRService:
    """
    Service for PaddleOCR integration
    Provides fast, multilingual OCR with 80+ language support
    Supports both basic OCR and PP-Structure layout analysis
    """

    def __init__(self, lang='en', use_structure=False):
        """
        Initialize PaddleOCR service

        Args:
            lang: Language code (en, tr, ch, etc.)
            use_structure: Enable PP-Structure for layout analysis
        """
        self.lang = lang
        self.use_structure = use_structure
        self.available = False
        self.structure_available = False
        self.ocr = None
        self.structure_engine = None

        # Try to import PaddleOCR
        try:
            from paddleocr import PaddleOCR
            self.PaddleOCR = PaddleOCR
            self.available = True
            logger.info("PaddleOCR library available")
        except ImportError:
            logger.warning("PaddleOCR not installed. Install with: pip install paddleocr")
            self.available = False

        # Try to import PP-Structure (v3.3+ uses PPStructureV3)
        if use_structure:
            try:
                from paddleocr import PPStructureV3
                self.PPStructure = PPStructureV3
                self.structure_available = True
                logger.info("PP-Structure V3 available")
            except ImportError:
                logger.warning("PP-Structure not available. Install with: pip install 'paddleocr[structure]'")
                self.structure_available = False

    def is_available(self) -> bool:
        """Check if PaddleOCR is available"""
        return self.available

    def is_structure_available(self) -> bool:
        """Check if PP-Structure is available"""
        return self.structure_available

    def initialize_ocr(self, use_angle_cls=True, use_gpu=False):
        """
        Initialize PaddleOCR instance

        Args:
            use_angle_cls: Enable angle classification for rotated text (legacy param, ignored in v3.3+)
            use_gpu: Use GPU acceleration if available (legacy param, ignored in v3.3+)
        """
        if not self.available:
            return False

        try:
            # PaddleOCR v3.3+ has simplified API - only accepts lang and ocr_version
            self.ocr = self.PaddleOCR(lang=self.lang)
            logger.info(f"PaddleOCR initialized (lang={self.lang})")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize PaddleOCR: {e}")
            self.available = False
            return False

    def initialize_structure(self, use_gpu=False):
        """
        Initialize PP-Structure engine for layout analysis

        Args:
            use_gpu: Use GPU acceleration if available (legacy param, ignored in v3.3+)
        """
        if not self.structure_available:
            return False

        try:
            # PPStructureV3 API - accepts lang and various use_* flags
            self.structure_engine = self.PPStructure(
                lang=self.lang,
                use_table_recognition=True,  # Enable table detection
                use_chart_recognition=True,  # Enable chart detection
                use_formula_recognition=False  # Skip formula recognition for speed
            )
            logger.info(f"PP-Structure V3 initialized (lang={self.lang})")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize PP-Structure: {e}")
            self.structure_available = False
            return False

    def process_image(self, image_path: str) -> Dict:
        """
        Process image with PaddleOCR

        Args:
            image_path: Path to image file

        Returns:
            Dictionary with OCR results
        """
        if not self.available:
            return {
                'success': False,
                'error': 'PaddleOCR not available',
                'text': '',
                'confidence': 0,
                'lines': []
            }

        # Initialize OCR if not already done
        if self.ocr is None:
            if not self.initialize_ocr():
                return {
                    'success': False,
                    'error': 'Failed to initialize PaddleOCR',
                    'text': '',
                    'confidence': 0,
                    'lines': []
                }

        try:
            # Check if file exists
            if not os.path.exists(image_path):
                return {
                    'success': False,
                    'error': f'Image file not found: {image_path}',
                    'text': '',
                    'confidence': 0,
                    'lines': []
                }

            # Run OCR (v3.3+ uses predict() and returns OCRResult object)
            logger.info(f"Running PaddleOCR on {image_path}")
            result = self.ocr.predict(image_path, use_textline_orientation=True)

            # Process results (v3.3+ returns list with OCRResult dict-like object)
            if not result or len(result) == 0:
                return {
                    'success': True,
                    'text': '',
                    'confidence': 0,
                    'lines': [],
                    'warning': 'No text detected'
                }

            ocr_result = result[0]

            # Check if we got any text
            if 'rec_texts' not in ocr_result or not ocr_result['rec_texts']:
                return {
                    'success': True,
                    'text': '',
                    'confidence': 0,
                    'lines': [],
                    'warning': 'No text detected'
                }

            # Extract text and confidence scores from v3.3+ format
            rec_texts = ocr_result['rec_texts']
            rec_scores = ocr_result.get('rec_scores', [])
            dt_polys = ocr_result.get('dt_polys', [])

            lines = []
            for i, text in enumerate(rec_texts):
                conf = rec_scores[i] if i < len(rec_scores) else 0.0
                bbox = dt_polys[i] if i < len(dt_polys) else []
                lines.append({
                    'text': text,
                    'confidence': float(conf),
                    'bbox': bbox.tolist() if hasattr(bbox, 'tolist') else bbox
                })

            # Combine all text
            full_text = '\n'.join(rec_texts)

            # Calculate average confidence
            avg_confidence = sum(rec_scores) / len(rec_scores) if rec_scores else 0

            # Extract key information from detected text using spatial analysis
            key_findings = self._extract_key_information(lines, rec_texts)

            result = {
                'success': True,
                'text': full_text,
                'confidence': avg_confidence * 100,  # Convert to percentage
                'lines': lines,
                'line_count': len(lines)
            }

            # Add key findings if any were extracted
            if key_findings:
                result.update(key_findings)

            return result

        except Exception as e:
            logger.error(f"PaddleOCR processing error: {e}")
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'confidence': 0,
                'lines': []
            }

    def process_image_base64(self, image_base64: str) -> Dict:
        """
        Process base64 encoded image

        Args:
            image_base64: Base64 encoded image data

        Returns:
            Dictionary with OCR results
        """
        import tempfile
        import base64

        try:
            # Decode base64
            image_data = base64.b64decode(image_base64)

            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                tmp_file.write(image_data)
                tmp_path = tmp_file.name

            # Process image
            result = self.process_image(tmp_path)

            # Clean up temp file
            try:
                os.unlink(tmp_path)
            except:
                pass

            return result

        except Exception as e:
            logger.error(f"Base64 image processing error: {e}")
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'confidence': 0,
                'lines': []
            }

    def get_text_with_layout(self, image_path: str) -> Dict:
        """
        Get OCR text preserving spatial layout

        Args:
            image_path: Path to image file

        Returns:
            Dictionary with text (preserving layout) and confidence
        """
        result = self.process_image(image_path)

        if not result.get('success') or not result.get('lines'):
            return result

        # Sort lines by vertical position (top to bottom)
        lines = result['lines']
        lines_sorted = sorted(lines, key=lambda x: x['bbox'][0][1])  # Sort by top-left y coordinate

        # Group lines by approximate Y position (horizontal lines)
        line_groups = []
        current_group = []
        last_y = None
        y_threshold = 20  # pixels threshold for same line

        for line in lines_sorted:
            y_pos = line['bbox'][0][1]

            if last_y is None or abs(y_pos - last_y) < y_threshold:
                current_group.append(line)
            else:
                if current_group:
                    line_groups.append(current_group)
                current_group = [line]

            last_y = y_pos

        if current_group:
            line_groups.append(current_group)

        # Build text with layout
        output_lines = []
        for group in line_groups:
            # Sort group by x position (left to right)
            group_sorted = sorted(group, key=lambda x: x['bbox'][0][0])
            text_parts = [item['text'] for item in group_sorted]
            output_lines.append(' '.join(text_parts))

        # Return full result with layout-formatted text
        layout_result = {
            'success': True,
            'text': '\n'.join(output_lines),
            'confidence': result.get('confidence', 0),
            'lines': result.get('lines', []),
            'line_count': result.get('line_count', 0)
        }

        # Include key findings from original result if available
        key_fields = ['store_name', 'total_amount', 'date', 'order_number', 'tax_id',
                      'found_store', 'found_total', 'found_date', 'found_order']
        for field in key_fields:
            if field in result:
                layout_result[field] = result[field]

        return layout_result

    def analyze_structure(self, image_path: str) -> Dict:
        """
        Analyze document structure using PP-Structure
        Detects layout elements (text, tables, figures, etc.)

        Args:
            image_path: Path to image file

        Returns:
            Dictionary with structure analysis results
        """
        if not self.structure_available:
            return {
                'success': False,
                'error': 'PP-Structure not available',
                'text': '',
                'elements': []
            }

        # Initialize structure engine if not done
        if self.structure_engine is None:
            if not self.initialize_structure():
                return {
                    'success': False,
                    'error': 'Failed to initialize PP-Structure',
                    'text': '',
                    'elements': []
                }

        try:
            # Check if file exists
            if not os.path.exists(image_path):
                return {
                    'success': False,
                    'error': f'Image file not found: {image_path}',
                    'text': '',
                    'elements': []
                }

            # Run structure analysis
            logger.info(f"Running PP-Structure analysis on {image_path}")
            result = self.structure_engine(image_path)

            # Process results
            if not result:
                return {
                    'success': True,
                    'text': '',
                    'elements': [],
                    'warning': 'No structure detected'
                }

            # Extract structured elements
            elements = []
            all_text = []

            for item in result:
                element_type = item.get('type', 'unknown')

                if element_type == 'text':
                    # Text region
                    text_content = item.get('res', '')
                    if isinstance(text_content, list):
                        # Extract text from OCR results
                        text_parts = [line.get('text', '') for line in text_content if isinstance(line, dict)]
                        text_content = '\n'.join(text_parts)

                    elements.append({
                        'type': 'text',
                        'content': text_content,
                        'bbox': item.get('bbox', [])
                    })
                    all_text.append(text_content)

                elif element_type == 'table':
                    # Table region
                    table_html = item.get('res', {}).get('html', '')
                    elements.append({
                        'type': 'table',
                        'html': table_html,
                        'bbox': item.get('bbox', [])
                    })
                    # Extract text from table for full text output
                    table_text = self._extract_text_from_table_html(table_html)
                    if table_text:
                        all_text.append(f"[TABLE]\n{table_text}\n[/TABLE]")

                elif element_type == 'figure':
                    # Figure/image region
                    elements.append({
                        'type': 'figure',
                        'bbox': item.get('bbox', [])
                    })
                    all_text.append('[FIGURE]')

            # Combine all text
            full_text = '\n\n'.join(all_text)

            return {
                'success': True,
                'text': full_text,
                'elements': elements,
                'element_count': len(elements),
                'has_tables': any(e['type'] == 'table' for e in elements),
                'has_figures': any(e['type'] == 'figure' for e in elements)
            }

        except Exception as e:
            logger.error(f"PP-Structure analysis error: {e}")
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'elements': []
            }

    def _extract_key_information(self, lines: List[Dict], texts: List[str]) -> Dict:
        """
        Extract key receipt information from PaddleOCR results
        Uses spatial positioning (bbox) and text patterns for intelligent extraction

        Args:
            lines: List of detected text lines with bbox and confidence
            texts: List of recognized texts

        Returns:
            Dictionary with extracted key findings (store, total, date, etc.)
        """
        import re

        findings = {
            'store_name': None,
            'total_amount': None,
            'date': None,
            'order_number': None,
            'tax_id': None,
            'found_store': False,
            'found_total': False,
            'found_date': False,
            'found_order': False
        }

        if not lines or not texts:
            return findings

        # Strategy 1: Extract store name from top area (first 20% of image)
        # Store names are typically at the top in large font
        if lines:
            # Sort lines by vertical position (top to bottom)
            sorted_lines = sorted(lines, key=lambda x: x['bbox'][0][1] if x['bbox'] else 999999)

            # Check first 5 lines for store name
            store_keywords = [
                'yemeksepeti', 'yemekse', 'migros', 'a101', 'bim', 'şok', 'carrefour',
                'market', 'store', 'restaurant', 'cafe', 'mcdonald', 'burger',
                'getir', 'trendyol', 'hepsiburada'
            ]

            for i, line in enumerate(sorted_lines[:5]):
                text = line['text'].strip()
                text_lower = text.lower()

                # Check if line contains store keywords
                if any(kw in text_lower for kw in store_keywords):
                    findings['store_name'] = text
                    findings['found_store'] = True
                    logger.info(f"PaddleOCR: Found store name '{text}' (keyword match)")
                    break

                # Check if line is mostly uppercase and long enough (likely a brand)
                if len(text) >= 4 and sum(1 for c in text if c.isupper()) > len(text) * 0.6:
                    if not findings['store_name']:  # Only use if we haven't found one yet
                        findings['store_name'] = text
                        findings['found_store'] = True
                        logger.info(f"PaddleOCR: Found store name '{text}' (uppercase pattern)")
                        break

        # Strategy 2: Extract total amount
        # Look for currency symbols and "toplam" keyword with spatial awareness
        total_patterns = [
            # Turkish patterns with "toplam" keyword (highest priority)
            (r'toplam[:\s]*[₺®&b★☆*]?\s*(\d+[.,]\d+)', 'toplam keyword'),
            (r'genel\s*toplam[:\s]*[₺®&b★☆*]?\s*(\d+[.,]\d+)', 'genel toplam'),
            (r'ara\s*toplam[:\s]*[₺®&b★☆*]?\s*(\d+[.,]\d+)', 'ara toplam'),
            (r"kdv['\s]*li\s*toplam[:\s]*[₺®&b★☆*]?\s*(\d+[.,]\d+)", 'kdvli toplam'),
            # English patterns
            (r'total[:\s]*[₺®&b$€★☆*]?\s*(\d+[.,]\d+)', 'total keyword'),
            (r'grand\s*total[:\s]*[₺®&b$€★☆*]?\s*(\d+[.,]\d+)', 'grand total'),
            (r'amount[:\s]*[₺®&b$€★☆*]?\s*(\d+[.,]\d+)', 'amount'),
            # Currency/Star symbol patterns (®, &, B/b, ★, ☆, * are common OCR variations for ₺ or decorative stars)
            (r'[₺®&b★☆*]\s*(\d+[.,]\d+)', 'currency/star prefix'),
            (r'(\d+[.,]\d+)\s*[₺®&b€$¢★☆*]', 'currency/star suffix'),
        ]

        # Try to find total with highest confidence
        best_total = None
        best_total_confidence = 0

        for line in lines:
            text = line['text']
            text_lower = text.lower()
            confidence = line.get('confidence', 0)

            for pattern, pattern_name in total_patterns:
                match = re.search(pattern, text_lower)
                if match:
                    amount = match.group(1).replace(',', '.')

                    # Clean OCR errors: "0C" at end → "00" (case-insensitive)
                    amount = re.sub(r'0[Cc]$', '00', amount)
                    amount = re.sub(r'[Cc]$', '0', amount)
                    # Also fix "0C" or "0c" in middle
                    amount = re.sub(r'0[Cc]', '00', amount)

                    # Validate amount is reasonable (between 0.01 and 999999)
                    try:
                        amount_float = float(amount)
                        if 0.01 <= amount_float <= 999999:
                            # Prefer matches with "toplam" keyword (higher confidence)
                            pattern_confidence = confidence
                            if 'toplam' in pattern_name or 'total' in pattern_name:
                                pattern_confidence *= 1.5  # Boost confidence for keyword matches

                            if pattern_confidence > best_total_confidence:
                                best_total = amount
                                best_total_confidence = pattern_confidence
                                logger.info(f"PaddleOCR: Found total candidate '{amount}' via {pattern_name} (conf: {pattern_confidence:.2f})")
                    except ValueError:
                        continue

        if best_total:
            findings['total_amount'] = best_total
            findings['found_total'] = True

        # Strategy 3: Extract date/time
        # Turkish month names and common date formats
        date_patterns = [
            # Turkish month names
            (r'\d{1,2}\s+(ocak|şubat|mart|nisan|mayıs|haziran|temmuz|ağustos|eylül|ekim|kasım|aralık)\s+\d{4}', 'Turkish month'),
            # Date with time
            (r'\d{2}[/-]\d{2}[/-]\d{4}\s+\d{2}:\d{2}', 'datetime DD/MM/YYYY HH:MM'),
            (r'\d{4}[/-]\d{2}[/-]\d{2}\s+\d{2}:\d{2}', 'datetime YYYY-MM-DD HH:MM'),
            # Date only
            (r'\d{2}[/-]\d{2}[/-]\d{4}', 'date DD/MM/YYYY'),
            (r'\d{4}[/-]\d{2}[/-]\d{2}', 'date YYYY-MM-DD'),
            # Flexible Turkish date
            (r'\d{1,2}\s+[a-zğüşıöçA-ZĞÜŞİÖÇ]{4,}\s+\d{4}', 'flexible Turkish'),
        ]

        for line in lines:
            text = line['text']
            text_lower = text.lower()

            for pattern, pattern_name in date_patterns:
                match = re.search(pattern, text_lower)
                if match:
                    findings['date'] = match.group(0)
                    findings['found_date'] = True
                    logger.info(f"PaddleOCR: Found date '{findings['date']}' via {pattern_name}")
                    break

            if findings['found_date']:
                break

        # Strategy 4: Extract order number / sipariş no
        order_patterns = [
            (r'sipari[şs]\s*no\.?\s*:?\s*([\w\d-]+)', 'Sipariş No'),
            (r'order\s*no\.?\s*:?\s*([\w\d-]+)', 'Order No'),
            (r'fiş\s*no\.?\s*:?\s*([\w\d-]+)', 'Fiş No'),
            (r'#(\d+)', 'Order #'),
            (r'no\.?\s*:?\s*(\d+)', 'No:'),
        ]

        for line in lines:
            text = line['text']
            text_lower = text.lower()

            for pattern, pattern_name in order_patterns:
                match = re.search(pattern, text_lower)
                if match:
                    findings['order_number'] = match.group(1).strip()
                    findings['found_order'] = True
                    logger.info(f"PaddleOCR: Found order number '{findings['order_number']}' via {pattern_name}")
                    break

            if findings['found_order']:
                break

        # Strategy 5: Extract tax ID / MERSIS / VKN
        tax_patterns = [
            (r'vergi\s*(?:no|numarası)[:\s]*([\d\s-]+)', 'Vergi No'),
            (r'v\.?k\.?n\.?\s*:?\s*([\d\s-]+)', 'VKN'),
            (r'tax\s*id[:\s]*([\d\s-]+)', 'Tax ID'),
            (r'mersis[:\s]*([\d\s-]+)', 'MERSIS'),
        ]

        for line in lines:
            text = line['text']
            text_lower = text.lower()

            for pattern, pattern_name in tax_patterns:
                match = re.search(pattern, text_lower)
                if match:
                    tax_value = match.group(1).strip()
                    # Clean up spacing
                    tax_value = re.sub(r'\s+', '', tax_value)

                    # Validate length (Turkish VKN is 10 digits, MERSIS is 16)
                    if len(tax_value) >= 10:
                        findings['tax_id'] = tax_value
                        logger.info(f"PaddleOCR: Found tax ID '{tax_value}' via {pattern_name}")
                        break

        # Log summary of findings
        found_count = sum([
            findings['found_store'],
            findings['found_total'],
            findings['found_date'],
            findings['found_order']
        ])
        logger.info(f"PaddleOCR: Extracted {found_count}/4 key fields")

        return findings

    def _extract_text_from_table_html(self, html: str) -> str:
        """
        Extract plain text from HTML table

        Args:
            html: HTML table string

        Returns:
            Plain text representation
        """
        if not html:
            return ''

        try:
            # Simple HTML tag removal (could be enhanced with BeautifulSoup)
            import re
            # Remove HTML tags
            text = re.sub(r'<[^>]+>', ' ', html)
            # Clean up whitespace
            text = re.sub(r'\s+', ' ', text)
            return text.strip()
        except Exception as e:
            logger.error(f"Failed to extract text from table HTML: {e}")
            return ''
