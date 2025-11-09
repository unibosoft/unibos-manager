"""
Receipt Field Extractor - Universal Field Extraction for Turkish and International Receipts
Provides flexible, pattern-based extraction that works with all OCR methods
"""

import logging
import re
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from decimal import Decimal, InvalidOperation

logger = logging.getLogger('documents.receipt_extractor')


class ReceiptFieldExtractor:
    """
    Universal receipt field extractor supporting multiple languages and formats

    Key Features:
    - Language-agnostic pattern matching
    - Flexible field detection (doesn't require exact keywords)
    - Works with any OCR method output
    - Supports Turkish, English, and other languages
    - Context-aware extraction (uses position, format, surrounding text)
    """

    def __init__(self, language='tr'):
        """
        Initialize field extractor

        Args:
            language: Primary language ('tr', 'en', 'multi')
        """
        self.language = language
        self._init_patterns()

    def _init_patterns(self):
        """Initialize extraction patterns for all field types"""

        # STORE NAME PATTERNS
        # Look for business entity indicators (not just "store" keyword)
        self.store_patterns = {
            'tr': {
                'keywords': [
                    'TİC', 'TIC', 'A.Ş', 'A.S', 'LTD', 'ŞTİ', 'STI',
                    'MARKET', 'SÜPERMARKET', 'SUPERMARKET', 'MAĞAZA',
                    'GIDA', 'PAZARLAMA', 'TICARET', 'SAN', 'HİZMET'
                ],
                'suffixes': ['A.Ş.', 'A.S.', 'LTD.', 'LTD.ŞTİ.', 'Ltd.Şti.'],
            },
            'en': {
                'keywords': ['INC', 'LLC', 'LTD', 'CORP', 'CO', 'COMPANY', 'STORE', 'MARKET'],
                'suffixes': ['INC.', 'LLC.', 'LTD.', 'CORP.', 'CO.'],
            }
        }

        # TOTAL AMOUNT PATTERNS
        # Look for total indicators and nearby numbers
        self.total_patterns = {
            'tr': {
                'keywords': [
                    'TOPLAM', 'GENEL TOPLAM', 'ÖDENECEK',
                    'TUTAR', 'ÖDENECEK TUTAR', 'NAKİT', 'NAKIT',
                    'TOPLAM TUTAR', 'ÖDENEN', 'ÖDEME'
                ],
                # Regex patterns for amount detection
                'amount_regex': [
                    r'(\d{1,3}(?:[.,]\d{3})*[.,]\d{2})\s*(?:TL|₺)',  # 138,00 TL or 1.234,56 TL
                    r'(\d{1,3}(?:[.,]\d{3})*[.,]\d{2})',  # 138,00 or 1.234,56
                    r'(\d+[.,]\d{2})',  # 138.00 or 138,00
                ],
            },
            'en': {
                'keywords': [
                    'TOTAL', 'GRAND TOTAL', 'AMOUNT DUE', 'BALANCE',
                    'PAYMENT', 'CASH', 'AMOUNT', 'SUM'
                ],
                'amount_regex': [
                    r'\$?\s*(\d{1,3}(?:,\d{3})*\.\d{2})',  # $1,234.56 or 1,234.56
                    r'(\d+\.\d{2})',  # 138.00
                ],
            }
        }

        # DATE PATTERNS
        # Flexible date detection without requiring "date" keyword
        self.date_patterns = {
            'formats': [
                # Turkish formats
                r'(\d{2})[./\-](\d{2})[./\-](\d{4})',  # 25.12.2023
                r'(\d{2})[./\-](\d{2})[./\-](\d{2})',  # 25.12.23
                r'(\d{4})[./\-](\d{2})[./\-](\d{2})',  # 2023.12.25
                # With month names
                r'(\d{1,2})\s+(Ocak|Şubat|Mart|Nisan|Mayıs|Haziran|Temmuz|Ağustos|Eylül|Ekim|Kasım|Aralık)\s+(\d{4})',
                r'(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})',
            ],
            'keywords': ['TARİH', 'TARIH', 'DATE', 'FECHA'],
        }

        # TIME PATTERNS
        # Flexible time detection
        self.time_patterns = {
            'formats': [
                r'(\d{2}):(\d{2}):(\d{2})',  # 14:30:45
                r'(\d{2}):(\d{2})',  # 14:30
                r'(\d{1,2}):(\d{2})\s*(AM|PM|am|pm)',  # 2:30 PM
            ],
            'keywords': ['SAAT', 'SAATİ', 'TIME', 'HORA'],
        }

        # TAX PATTERNS
        self.tax_patterns = {
            'tr': {
                'keywords': ['KDV', 'VERGİ', 'VERGI', 'KDV TUTARI', '%'],
            },
            'en': {
                'keywords': ['TAX', 'VAT', 'GST', 'SALES TAX'],
            }
        }

        # ADDRESS PATTERNS
        # Look for address indicators
        self.address_patterns = {
            'keywords': [
                'ADRES', 'SOKAK', 'SK', 'CAD', 'CADDE', 'MAHALLE', 'MAH',
                'NO', 'APT', 'DAIRE', 'İLÇE', 'İL',
                'ADDRESS', 'STREET', 'ST', 'AVE', 'AVENUE', 'CITY'
            ],
            # Postal code patterns
            'postal_codes': [
                r'\b\d{5}\b',  # Turkish/US 5-digit
                r'\b\d{5}-\d{4}\b',  # US ZIP+4
            ]
        }

        # PHONE PATTERNS
        self.phone_patterns = {
            'formats': [
                r'(\+90|0)?\s*\(?(\d{3})\)?\s*(\d{3})\s*(\d{2})\s*(\d{2})',  # Turkish: +90 (532) 123 45 67
                r'(\d{3})[-.\s]?(\d{3})[-.\s]?(\d{4})',  # 555-123-4567
                r'(\d{3})[-.\s]?(\d{4})',  # 555-1234
            ],
            'keywords': ['TEL', 'TELEFON', 'PHONE', 'TEL:', 'TEL.'],
        }

        # TAX ID / REGISTRATION PATTERNS (VKN, TC No, etc)
        self.tax_id_patterns = {
            'tr': {
                'keywords': ['VKN', 'V.K.N', 'VERGİ NO', 'VERGI NO', 'TC NO', 'TC'],
                'formats': [
                    r'VKN[:\s]*(\d{10})',  # VKN: 1234567890
                    r'V\.K\.N[:\s]*(\d{10})',
                    r'TC\s*NO[:\s]*(\d{11})',  # TC No: 12345678901
                ]
            }
        }

    def extract_all_fields(
        self,
        text: str = None,
        lines: List[Dict] = None,
        structured_data: Dict = None
    ) -> Dict:
        """
        Extract all fields from receipt using multiple sources

        Args:
            text: Plain text from OCR
            lines: Line-by-line OCR with positions (e.g., PaddleOCR output)
            structured_data: Pre-structured data (e.g., Donut output)

        Returns:
            Dictionary with all extracted fields
        """
        result = {
            'store_name': None,
            'total_amount': None,
            'date': None,
            'time': None,
            'address': None,
            'phone': None,
            'tax_id': None,
            'tax_amount': None,
            'items': [],
            'subtotal': None,
            'found_store': False,
            'found_total': False,
            'found_date': False,
            'found_time': False,
            'found_address': False,
            'found_phone': False,
            'confidence_scores': {}
        }

        # Extract from structured data first (highest confidence)
        if structured_data:
            result = self._extract_from_structured(structured_data, result)

        # Extract from line-by-line data (medium confidence)
        if lines:
            result = self._extract_from_lines(lines, result)

        # Extract from plain text (lowest confidence, fallback)
        if text:
            result = self._extract_from_text(text, result)

        return result

    def _extract_from_structured(self, data: Dict, result: Dict) -> Dict:
        """Extract from pre-structured data (e.g., Donut, LayoutLM)"""

        # Handle case where data is a list (some models return lists)
        if isinstance(data, list):
            # If it's a list, try to find the main object (usually first item)
            if len(data) > 0 and isinstance(data[0], dict):
                data = data[0]
            else:
                # Can't process list of non-dicts, return unchanged result
                return result

        # Ensure data is a dict
        if not isinstance(data, dict):
            return result

        # Store name
        if not result['found_store']:
            store = data.get('store_name') or data.get('store', {}).get('name')
            if store:
                result['store_name'] = str(store)
                result['found_store'] = True
                result['confidence_scores']['store'] = 95.0

        # Total amount
        if not result['found_total']:
            # Safely get nested total fields (data.get('total') might return list)
            total_field = data.get('total', {})
            if isinstance(total_field, dict):
                total_from_nested = total_field.get('total_price')
            else:
                total_from_nested = None

            total = (data.get('total_amount') or
                    total_from_nested or
                    data.get('total_price'))
            if total:
                result['total_amount'] = self._normalize_amount(str(total))
                result['found_total'] = True
                result['confidence_scores']['total'] = 95.0

        # Date
        if not result['found_date']:
            date = data.get('date')
            if date:
                result['date'] = str(date)
                result['found_date'] = True
                result['confidence_scores']['date'] = 95.0

        # Time
        if not result['found_time']:
            time = data.get('time')
            if time:
                result['time'] = str(time)
                result['found_time'] = True
                result['confidence_scores']['time'] = 95.0

        # Tax
        if not result.get('tax_amount'):
            # Safely get nested tax fields (data.get('total') might return list)
            total_field = data.get('total', {})
            if isinstance(total_field, dict):
                tax_from_nested = total_field.get('tax_price')
            else:
                tax_from_nested = None

            tax = (data.get('tax_amount') or
                  tax_from_nested or
                  data.get('tax'))
            if tax:
                result['tax_amount'] = self._normalize_amount(str(tax))

        # Items (from menu/items list)
        menu_items = data.get('menu', []) or data.get('items', [])
        if menu_items and not result['items']:
            for item in menu_items:
                if isinstance(item, dict):
                    item_name = item.get('name') or item.get('nm', '')
                    # Ensure item_name is a string
                    if isinstance(item_name, dict):
                        item_name = str(item_name)
                    elif not isinstance(item_name, str):
                        item_name = ''

                    # Skip if this looks like a total/header line
                    if item_name and not self._is_metadata_line(item_name):
                        result['items'].append({
                            'name': item_name,
                            'quantity': item.get('quantity') or item.get('cnt', ''),
                            'price': item.get('price') or item.get('unitprice', '')
                        })

        return result

    def _extract_from_lines(self, lines: List[Dict], result: Dict) -> Dict:
        """Extract from line-by-line OCR data with positions"""

        for i, line in enumerate(lines):
            text = line.get('text', '').strip()
            if not text:
                continue

            text_upper = text.upper()

            # Store name (usually at top, before first item)
            if not result['found_store'] and i < 5:  # Check first 5 lines
                if self._is_store_name(text):
                    result['store_name'] = text
                    result['found_store'] = True
                    result['confidence_scores']['store'] = 85.0

            # Total amount
            if not result['found_total']:
                if self._contains_total_keyword(text_upper):
                    amount = self._extract_amount_from_line(text)
                    if amount:
                        result['total_amount'] = amount
                        result['found_total'] = True
                        result['confidence_scores']['total'] = 90.0

            # Date
            if not result['found_date']:
                date = self._extract_date_from_line(text)
                if date:
                    result['date'] = date
                    result['found_date'] = True
                    result['confidence_scores']['date'] = 85.0

            # Time
            if not result['found_time']:
                time = self._extract_time_from_line(text)
                if time:
                    result['time'] = time
                    result['found_time'] = True
                    result['confidence_scores']['time'] = 85.0

            # Phone
            if not result['found_phone']:
                phone = self._extract_phone_from_line(text)
                if phone:
                    result['phone'] = phone
                    result['found_phone'] = True
                    result['confidence_scores']['phone'] = 80.0

        return result

    def _extract_from_text(self, text: str, result: Dict) -> Dict:
        """Extract from plain text (fallback method)"""

        lines = text.split('\n')

        # Store name (first few lines)
        if not result['found_store']:
            for line in lines[:5]:
                if self._is_store_name(line):
                    result['store_name'] = line.strip()
                    result['found_store'] = True
                    result['confidence_scores']['store'] = 70.0
                    break

        # Total amount
        if not result['found_total']:
            for line in lines:
                if self._contains_total_keyword(line.upper()):
                    amount = self._extract_amount_from_line(line)
                    if amount:
                        result['total_amount'] = amount
                        result['found_total'] = True
                        result['confidence_scores']['total'] = 75.0
                        break

        # Date (search entire text)
        if not result['found_date']:
            date = self._extract_date_from_text(text)
            if date:
                result['date'] = date
                result['found_date'] = True
                result['confidence_scores']['date'] = 70.0

        # Time
        if not result['found_time']:
            time = self._extract_time_from_text(text)
            if time:
                result['time'] = time
                result['found_time'] = True
                result['confidence_scores']['time'] = 70.0

        return result

    def _is_store_name(self, text: str) -> bool:
        """Check if line is likely a store name"""
        if not text or len(text) < 3:
            return False

        text_upper = text.upper()

        # Check for business entity keywords
        patterns = self.store_patterns.get(self.language, self.store_patterns['tr'])
        keywords = patterns['keywords']

        # Must contain at least one keyword
        if any(kw in text_upper for kw in keywords):
            # Additional checks
            # Must have some letters (not just numbers)
            if sum(c.isalpha() for c in text) >= 3:
                # Should not be too long (not a full paragraph)
                if len(text) < 100:
                    return True

        return False

    def _contains_total_keyword(self, text_upper: str) -> bool:
        """Check if line contains total amount keyword"""
        patterns = self.total_patterns.get(self.language, self.total_patterns['tr'])
        keywords = patterns['keywords']
        return any(kw in text_upper for kw in keywords)

    def _extract_amount_from_line(self, text: str) -> Optional[str]:
        """Extract amount from line using regex patterns"""
        patterns = self.total_patterns.get(self.language, self.total_patterns['tr'])

        for pattern in patterns['amount_regex']:
            match = re.search(pattern, text)
            if match:
                amount = match.group(1) if match.lastindex else match.group(0)
                return self._normalize_amount(amount)

        return None

    def _extract_date_from_line(self, text: str) -> Optional[str]:
        """Extract date from line"""
        for pattern in self.date_patterns['formats']:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return None

    def _extract_date_from_text(self, text: str) -> Optional[str]:
        """Extract date from entire text"""
        for pattern in self.date_patterns['formats']:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return None

    def _extract_time_from_line(self, text: str) -> Optional[str]:
        """Extract time from line"""
        for pattern in self.time_patterns['formats']:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return None

    def _extract_time_from_text(self, text: str) -> Optional[str]:
        """Extract time from entire text"""
        for pattern in self.time_patterns['formats']:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return None

    def _extract_phone_from_line(self, text: str) -> Optional[str]:
        """Extract phone number from line"""
        for pattern in self.phone_patterns['formats']:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return None

    def _normalize_amount(self, amount: str) -> str:
        """Normalize amount string (handle different decimal separators)"""
        if not amount:
            return None

        # Remove currency symbols
        amount = amount.replace('TL', '').replace('₺', '').replace('$', '').replace('€', '')
        amount = amount.replace('*', '').strip()

        # Remove spaces
        amount = amount.replace(' ', '')

        # Detect format: 1.234,56 (EU) vs 1,234.56 (US)
        if ',' in amount and '.' in amount:
            # Has both - determine which is decimal separator
            last_comma = amount.rfind(',')
            last_dot = amount.rfind('.')

            if last_comma > last_dot:
                # 1.234,56 format (comma is decimal)
                amount = amount.replace('.', '').replace(',', '.')
            else:
                # 1,234.56 format (dot is decimal)
                amount = amount.replace(',', '')
        elif ',' in amount:
            # Only comma - could be thousands or decimal
            parts = amount.split(',')
            if len(parts) == 2 and len(parts[1]) == 2:
                # Likely decimal: 138,00
                amount = amount.replace(',', '.')
            else:
                # Likely thousands: 1,234
                amount = amount.replace(',', '')

        # Validate it's a number
        try:
            float_val = float(amount)
            # Return with 2 decimal places
            return f"{float_val:.2f}"
        except:
            return None

    def _is_metadata_line(self, text: str) -> bool:
        """Check if line is metadata (not an item) - for filtering items"""
        if not text:
            return True

        text_upper = text.upper()

        # Check if it's a total line
        if self._contains_total_keyword(text_upper):
            return True

        # Check if it's a header/store line
        if self._is_store_name(text):
            return True

        # Check if it's date/time
        if any(kw in text_upper for kw in ['TARİH', 'TARIH', 'DATE', 'SAAT', 'TIME']):
            return True

        # Check if it's tax/payment info
        if any(kw in text_upper for kw in ['KDV', 'VERGİ', 'NAKİT', 'KART', 'TAX', 'PAYMENT']):
            return True

        return False
