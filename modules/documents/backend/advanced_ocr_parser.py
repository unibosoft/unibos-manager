"""
Advanced OCR Parser for Turkish Receipts
Handles store info, items, barcodes, KDV calculations
"""

import re
import json
from decimal import Decimal
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger('documents.ocr_parser')


class TurkishReceiptParser:
    """Advanced parser for Turkish receipts with item extraction and KDV validation"""
    
    # Common Turkish store chains and their patterns
    STORE_PATTERNS = {
        'Migros': {
            'name_patterns': [r'M\s*İ\s*G\s*R\s*O\s*S', r'MIGROS\s+TİCARET'],
            'tax_id_prefix': 'VKN:',
            'item_pattern': r'^(.+?)\s+(\d+[,.]?\d*)\s*[xX*]\s*(\d+[,.]?\d+)\s+(%?\d+)\s+(\d+[,.]?\d+)$'
        },
        'CarrefourSA': {
            'name_patterns': [r'CarrefourSA', r'CARREFOUR\s*SA'],
            'tax_id_prefix': 'V.D:',
            'item_pattern': r'^(.+?)\s+(\d+[,.]?\d*)\s*ADT?\s+(\d+[,.]?\d+)\s+(\d+[,.]?\d+)$'
        },
        'BİM': {
            'name_patterns': [r'BİM\s+BİRLEŞİK', r'B\s*İ\s*M'],
            'tax_id_prefix': 'VN:',
            'item_pattern': r'^(.+?)\s+(\d+[,.]?\d*)\s+(\d+[,.]?\d+)\s+([*%]\d+)$'
        },
        'A101': {
            'name_patterns': [r'A\s*101', r'A101\s+YENI\s+MAGAZACILIK'],
            'tax_id_prefix': 'VKN:',
            'item_pattern': r'^(.+?)\s+(\d+[,.]?\d*)\s*[xX]\s*(\d+[,.]?\d+)\s+(\d+[,.]?\d+)$'
        },
        'ŞOK': {
            'name_patterns': [r'ŞOK\s+MARKETLER', r'Ş\s*O\s*K'],
            'tax_id_prefix': 'VKN:',
            'item_pattern': r'^(.+?)\s+(\d+)\s+(\d+[,.]?\d+)\s+(\d+[,.]?\d+)$'
        }
    }
    
    # Turkish KDV rates
    KDV_RATES = {
        'GIDA': 8,      # Food
        'TEMEL': 1,     # Basic necessities
        'GENEL': 18,    # General
        'LÜKS': 20,     # Luxury
        'İLAÇ': 8,      # Medicine
        'KİTAP': 8      # Books
    }
    
    # Product category patterns
    CATEGORY_PATTERNS = {
        'GIDA': [
            r'EKMEK', r'SÜT', r'YOĞURT', r'PEYNIR', r'ET', r'TAVUK', 
            r'MEYVE', r'SEBZE', r'UN', r'MAKARNA', r'PİRİNÇ'
        ],
        'TEMİZLİK': [
            r'DETERJAN', r'SABUN', r'ŞAMPUAN', r'DİŞ\s*MACUNU', r'TUVALET\s*KAĞIDI'
        ],
        'İÇECEK': [
            r'SU', r'KOLA', r'COLA', r'FANTA', r'AYRAN', r'MEYVE\s*SUYU', r'ÇAY', r'KAHVE'
        ],
        'ATIŞTIIRMALIK': [
            r'CİPS', r'KRAKER', r'BİSKÜVİ', r'ÇİKOLATA', r'ŞEKER', r'GÖFRETw'
        ]
    }
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        
    def parse(self, ocr_text: str) -> Dict:
        """Main parsing method"""
        if not ocr_text:
            return {'success': False, 'error': 'No OCR text provided'}
        
        lines = ocr_text.strip().split('\n')
        result = {
            'success': True,
            'store_info': self._extract_store_info(lines),
            'items': self._extract_items(lines),
            'financial': self._extract_financial_info(lines),
            'transaction': self._extract_transaction_info(lines),
            'validation': {
                'kdv_valid': False,
                'total_valid': False,
                'errors': [],
                'warnings': []
            }
        }
        
        # Validate KDV and totals
        self._validate_financial(result)
        
        # Add any parsing errors/warnings
        result['validation']['errors'].extend(self.errors)
        result['validation']['warnings'].extend(self.warnings)
        
        return result
    
    def _extract_store_info(self, lines: List[str]) -> Dict:
        """Extract store information from receipt"""
        store_info = {
            'name': None,
            'branch': None,
            'address': None,
            'phone': None,
            'tax_id': None,
            'tax_office': None,
            'detected_chain': None
        }
        
        # Try to detect known store chains
        for store_name, patterns in self.STORE_PATTERNS.items():
            for pattern in patterns['name_patterns']:
                for line in lines[:10]:  # Check first 10 lines
                    if re.search(pattern, line, re.IGNORECASE):
                        store_info['detected_chain'] = store_name
                        store_info['name'] = store_name
                        break
                if store_info['detected_chain']:
                    break
            if store_info['detected_chain']:
                break
        
        # Extract tax ID (Vergi Kimlik No)
        tax_patterns = [
            r'V\.?K\.?N\.?\s*[:=]\s*(\d{10,11})',
            r'VERGİ\s+NO\s*[:=]\s*(\d{10,11})',
            r'V\.?D\.?\s*[:=]\s*(.+?)\s+(\d{10,11})'
        ]
        
        for pattern in tax_patterns:
            for line in lines:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    if match.lastindex == 2:
                        store_info['tax_office'] = match.group(1).strip()
                        store_info['tax_id'] = match.group(2).strip()
                    else:
                        store_info['tax_id'] = match.group(1).strip()
                    break
            if store_info['tax_id']:
                break
        
        # Extract phone number
        phone_patterns = [
            r'TEL\s*[:=]\s*([\d\s\-\(\)]+)',
            r'TELEFON\s*[:=]\s*([\d\s\-\(\)]+)',
            r'(\d{3,4}[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2})'
        ]
        
        for pattern in phone_patterns:
            for line in lines:
                match = re.search(pattern, line)
                if match:
                    phone = re.sub(r'[^\d]', '', match.group(1))
                    if len(phone) >= 10:
                        store_info['phone'] = phone
                        break
            if store_info['phone']:
                break
        
        # Extract address (usually multi-line)
        address_start_patterns = [
            r'ADRES\s*[:=]',
            r'ADR\s*[:=]',
            r'^.+?(MAH\.|MAHALLE|CAD\.|CADDE|SOK\.|SOKAK)'
        ]
        
        for i, line in enumerate(lines):
            for pattern in address_start_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # Collect address lines
                    address_lines = []
                    for j in range(i, min(i+3, len(lines))):
                        if not re.search(r'(TEL|VKN|TARIH|SAAT|FİŞ)', lines[j], re.IGNORECASE):
                            address_lines.append(lines[j].strip())
                    if address_lines:
                        store_info['address'] = ' '.join(address_lines)
                    break
            if store_info['address']:
                break
        
        return store_info
    
    def _extract_items(self, lines: List[str]) -> List[Dict]:
        """Extract individual items from receipt"""
        items = []
        
        # Find items section
        items_start = None
        items_end = None
        
        for i, line in enumerate(lines):
            # Start markers
            if not items_start and re.search(r'(ÜRÜN|MALZEME|AÇIKLAMA)', line, re.IGNORECASE):
                items_start = i + 1
            # End markers
            if items_start and re.search(r'(TOPLAM|ARA\s*TOPLAM|SUBTOTAL|KDV)', line, re.IGNORECASE):
                items_end = i
                break
        
        if not items_start:
            items_start = 10  # Skip header lines
            items_end = len(lines) - 10  # Skip footer lines
        
        # Parse items
        for i in range(items_start, items_end or len(lines)):
            line = lines[i].strip()
            if not line:
                continue
            
            item = self._parse_item_line(line, lines, i)
            if item:
                # Try to detect category
                item['category'] = self._detect_category(item['name'])
                # Try to extract barcode from next line
                if i + 1 < len(lines):
                    barcode = self._extract_barcode(lines[i + 1])
                    if barcode:
                        item['barcode'] = barcode
                items.append(item)
        
        return items
    
    def _parse_item_line(self, line: str, lines: List[str], line_index: int) -> Optional[Dict]:
        """Parse a single item line"""
        
        # Clean the line
        line = re.sub(r'\s+', ' ', line.strip())
        
        # Common patterns for Turkish receipts
        patterns = [
            # Pattern: NAME QUANTITY x PRICE TOTAL
            r'^(.+?)\s+(\d+[,.]?\d*)\s*[xX*]\s*(\d+[,.]?\d+)\s+(\d+[,.]?\d+)$',
            # Pattern: NAME QUANTITY PRICE TOTAL
            r'^(.+?)\s+(\d+[,.]?\d*)\s+(\d+[,.]?\d+)\s+(\d+[,.]?\d+)$',
            # Pattern: NAME PRICE (single item)
            r'^(.+?)\s+(\d+[,.]?\d+)$',
            # Pattern with KDV indicator: NAME QTY x PRICE %KDV TOTAL
            r'^(.+?)\s+(\d+[,.]?\d*)\s*[xX*]\s*(\d+[,.]?\d+)\s+%(\d+)\s+(\d+[,.]?\d+)$'
        ]
        
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                groups = match.groups()
                
                if len(groups) == 5:  # With KDV
                    return {
                        'name': groups[0].strip(),
                        'quantity': self._parse_decimal(groups[1]),
                        'unit_price': self._parse_decimal(groups[2]),
                        'kdv_rate': int(groups[3]),
                        'total': self._parse_decimal(groups[4]),
                        'barcode': None,
                        'category': None
                    }
                elif len(groups) == 4:  # Standard format
                    return {
                        'name': groups[0].strip(),
                        'quantity': self._parse_decimal(groups[1]),
                        'unit_price': self._parse_decimal(groups[2]),
                        'total': self._parse_decimal(groups[3]),
                        'kdv_rate': 18,  # Default KDV
                        'barcode': None,
                        'category': None
                    }
                elif len(groups) == 2:  # Single item
                    return {
                        'name': groups[0].strip(),
                        'quantity': 1,
                        'unit_price': self._parse_decimal(groups[1]),
                        'total': self._parse_decimal(groups[1]),
                        'kdv_rate': 18,
                        'barcode': None,
                        'category': None
                    }
        
        return None
    
    def _extract_barcode(self, line: str) -> Optional[str]:
        """Extract barcode from line"""
        # Common barcode patterns
        barcode_patterns = [
            r'(\d{13})',  # EAN-13
            r'(\d{12})',  # UPC-A
            r'(\d{8})',   # EAN-8
            r'BARKOD\s*[:=]\s*(\d+)',
            r'BRK\s*[:=]\s*(\d+)',
            r'^\s*(\d{8,13})\s*$'  # Just numbers on a line
        ]
        
        for pattern in barcode_patterns:
            match = re.search(pattern, line)
            if match:
                barcode = match.group(1)
                # Validate barcode length
                if len(barcode) in [8, 12, 13]:
                    return barcode
        
        return None
    
    def _detect_category(self, product_name: str) -> str:
        """Detect product category from name"""
        product_upper = product_name.upper()
        
        for category, patterns in self.CATEGORY_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, product_upper):
                    return category
        
        return 'DİĞER'
    
    def _extract_financial_info(self, lines: List[str]) -> Dict:
        """Extract financial information"""
        financial = {
            'subtotal': None,
            'kdv_details': [],
            'total_kdv': None,
            'total': None,
            'paid': None,
            'change': None,
            'payment_method': None,
            'card_info': None
        }
        
        # Extract amounts
        for line in lines:
            # Subtotal
            if re.search(r'(ARA\s*TOPLAM|SUBTOTAL)', line, re.IGNORECASE):
                match = re.search(r'(\d+[,.]?\d+)', line)
                if match:
                    financial['subtotal'] = self._parse_decimal(match.group(1))
            
            # KDV details
            kdv_match = re.search(r'KDV\s*%(\d+)\s*[:=]?\s*(\d+[,.]?\d+)', line, re.IGNORECASE)
            if kdv_match:
                financial['kdv_details'].append({
                    'rate': int(kdv_match.group(1)),
                    'amount': self._parse_decimal(kdv_match.group(2))
                })
            
            # Total KDV
            if re.search(r'(TOPLAM\s*KDV|KDV\s*TOPLAMI)', line, re.IGNORECASE):
                match = re.search(r'(\d+[,.]?\d+)', line)
                if match:
                    financial['total_kdv'] = self._parse_decimal(match.group(1))
            
            # Total
            if re.search(r'(GENEL\s*TOPLAM|TOPLAM|TOTAL)', line, re.IGNORECASE):
                match = re.search(r'(\d+[,.]?\d+)', line)
                if match and not financial['total']:
                    financial['total'] = self._parse_decimal(match.group(1))
            
            # Payment info
            if re.search(r'(NAKİT|NAKIT)', line, re.IGNORECASE):
                financial['payment_method'] = 'NAKİT'
                match = re.search(r'(\d+[,.]?\d+)', line)
                if match:
                    financial['paid'] = self._parse_decimal(match.group(1))
            
            if re.search(r'(KART|KREDI\s*KARTI|BANKA\s*KARTI)', line, re.IGNORECASE):
                financial['payment_method'] = 'KART'
                # Try to extract card last 4 digits
                card_match = re.search(r'\*+(\d{4})', line)
                if card_match:
                    financial['card_info'] = card_match.group(1)
            
            # Change
            if re.search(r'(PARA\s*ÜSTÜ|DEĞİŞİM)', line, re.IGNORECASE):
                match = re.search(r'(\d+[,.]?\d+)', line)
                if match:
                    financial['change'] = self._parse_decimal(match.group(1))
        
        # Calculate total KDV if not found but have details
        if not financial['total_kdv'] and financial['kdv_details']:
            financial['total_kdv'] = sum(d['amount'] for d in financial['kdv_details'])
        
        return financial
    
    def _extract_transaction_info(self, lines: List[str]) -> Dict:
        """Extract transaction information"""
        transaction = {
            'date': None,
            'time': None,
            'receipt_no': None,
            'cashier': None,
            'pos_no': None,
            'store_no': None
        }
        
        for line in lines:
            # Date patterns - Enhanced for Turkish receipts
            # First try with TARİH keyword
            date_patterns = [
                r'TAR[İI]H\s*:?\s*(\d{1,2}[-./]\d{1,2}[-./]\d{2,4})',
                r'DATE\s*:?\s*(\d{1,2}[-./]\d{1,2}[-./]\d{2,4})',
                r'(\d{1,2}[-./]\d{1,2}[-./]\d{2,4})'  # General pattern
            ]
            
            for pattern in date_patterns:
                date_match = re.search(pattern, line.upper())
                if date_match:
                    transaction['date'] = date_match.group(1)
                    break
            
            # Time patterns
            time_match = re.search(r'(\d{1,2}:\d{2}(?::\d{2})?)', line)
            if time_match:
                transaction['time'] = time_match.group(1)
            
            # Receipt number
            receipt_patterns = [
                r'FİŞ\s*NO\s*[:=]\s*(\d+)',
                r'FİŞ\s*[:=]\s*(\d+)',
                r'BELGE\s*NO\s*[:=]\s*(\d+)',
                r'NO\s*[:=]\s*(\d+)'
            ]
            for pattern in receipt_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    transaction['receipt_no'] = match.group(1)
                    break
            
            # Cashier
            cashier_match = re.search(r'(KASİYER|KASIYER|KASA)\s*[:=]\s*(.+?)(?:\s|$)', line, re.IGNORECASE)
            if cashier_match:
                transaction['cashier'] = cashier_match.group(2).strip()
            
            # POS number
            pos_match = re.search(r'(POS|KASA)\s*NO\s*[:=]\s*(\d+)', line, re.IGNORECASE)
            if pos_match:
                transaction['pos_no'] = pos_match.group(2)
        
        return transaction
    
    def _validate_financial(self, result: Dict) -> None:
        """Validate KDV calculations and totals"""
        financial = result['financial']
        items = result['items']
        
        if not items or not financial['total']:
            result['validation']['warnings'].append('Cannot validate: missing items or total')
            return
        
        # Calculate expected totals
        calculated_subtotal = sum(Decimal(str(item['total'])) for item in items)
        
        # Check subtotal
        if financial['subtotal']:
            diff = abs(calculated_subtotal - Decimal(str(financial['subtotal'])))
            if diff > Decimal('0.10'):  # Allow 10 kuruş difference
                result['validation']['errors'].append(
                    f'Subtotal mismatch: calculated={calculated_subtotal}, receipt={financial["subtotal"]}'
                )
            else:
                result['validation']['total_valid'] = True
        
        # Validate KDV
        if financial['kdv_details']:
            for kdv in financial['kdv_details']:
                rate = kdv['rate']
                if rate not in [0, 1, 8, 10, 18, 20]:
                    result['validation']['warnings'].append(f'Unusual KDV rate: {rate}%')
            
            # Check KDV calculation
            if financial['subtotal'] and financial['total_kdv']:
                calculated_total = Decimal(str(financial['subtotal'])) + Decimal(str(financial['total_kdv']))
                if financial['total']:
                    diff = abs(calculated_total - Decimal(str(financial['total'])))
                    if diff > Decimal('0.10'):
                        result['validation']['errors'].append(
                            f'Total mismatch: subtotal+kdv={calculated_total}, receipt={financial["total"]}'
                        )
                    else:
                        result['validation']['kdv_valid'] = True
    
    def _parse_decimal(self, value: str) -> float:
        """Parse decimal number from Turkish format"""
        if not value:
            return 0.0
        # Replace Turkish decimal separator
        value = value.replace(',', '.')
        # Remove any spaces
        value = value.replace(' ', '')
        try:
            return float(value)
        except ValueError:
            self.warnings.append(f'Could not parse number: {value}')
            return 0.0


class StoreTemplateManager:
    """Manage store-specific OCR templates"""
    
    def __init__(self):
        self.templates = {}
        self._load_default_templates()
    
    def _load_default_templates(self):
        """Load default store templates"""
        self.templates['Migros'] = {
            'item_section_start': r'ÜRÜN\s+ADI',
            'item_section_end': r'ARA\s*TOPLAM',
            'item_pattern': r'^(.+?)\s+(\d+)\s*[xX]\s*(\d+[,.]?\d+)\s+%(\d+)\s+(\d+[,.]?\d+)$',
            'barcode_next_line': True,
            'kdv_in_item': True
        }
        
        self.templates['CarrefourSA'] = {
            'item_section_start': r'AÇIKLAMA',
            'item_section_end': r'TOPLAM',
            'item_pattern': r'^(.+?)\s+(\d+)\s+ADT\s+(\d+[,.]?\d+)\s+(\d+[,.]?\d+)$',
            'barcode_next_line': False,
            'kdv_separate': True
        }
    
    def get_template(self, store_name: str) -> Optional[Dict]:
        """Get template for specific store"""
        return self.templates.get(store_name)
    
    def add_template(self, store_name: str, template: Dict):
        """Add or update store template"""
        self.templates[store_name] = template