"""
Document Type Detection Service
"""

import re
import logging
from typing import Dict, Optional, List
from django.db.models import Q

logger = logging.getLogger(__name__)


class DocumentTypeDetector:
    """Detect document type from OCR text and metadata"""
    
    def __init__(self):
        from .document_models import DocumentType
        self.document_types = DocumentType.objects.filter(is_active=True)
    
    def detect_type(self, ocr_text: str, filename: str = '') -> Optional[Dict]:
        """
        Detect document type from OCR text and filename
        
        Returns:
            Dictionary with document type info and confidence score
        """
        if not ocr_text:
            return None
        
        ocr_lower = ocr_text.lower()
        scores = {}
        
        # Check each document type
        for doc_type in self.document_types:
            score = 0
            
            # Check keywords
            keywords = doc_type.keywords or []
            for keyword in keywords:
                if keyword.lower() in ocr_lower:
                    score += 10  # Each keyword match adds 10 points
            
            # Check regex patterns
            patterns = doc_type.regex_patterns or []
            for pattern in patterns:
                try:
                    if re.search(pattern, ocr_text, re.IGNORECASE):
                        score += 15  # Regex matches are more valuable
                except re.error:
                    logger.error(f"Invalid regex pattern: {pattern}")
            
            # Check filename hints
            if filename:
                name_lower = filename.lower()
                if doc_type.name.lower() in name_lower:
                    score += 20
            
            if score > 0:
                scores[doc_type] = score
        
        # Get the best match
        if scores:
            best_match = max(scores, key=scores.get)
            confidence = min(scores[best_match] / 100, 1.0)  # Normalize to 0-1
            
            return {
                'type': best_match,
                'type_name': best_match.name,
                'category': best_match.category,
                'confidence': confidence,
                'score': scores[best_match],
                'all_scores': {dt.name: s for dt, s in scores.items()}
            }
        
        return None
    
    def extract_fields_by_type(self, ocr_text: str, doc_type: str) -> Dict:
        """
        Extract specific fields based on document type
        """
        extractors = {
            'Receipt': self._extract_receipt_fields,
            'Invoice': self._extract_invoice_fields,
            'Parking Ticket': self._extract_parking_fields,
            'Gas Receipt': self._extract_gas_fields,
            'Prescription': self._extract_prescription_fields,
            'Lab Report': self._extract_lab_fields,
            'Bank Statement': self._extract_bank_fields,
        }
        
        extractor = extractors.get(doc_type, self._extract_generic_fields)
        return extractor(ocr_text)
    
    def _extract_receipt_fields(self, text: str) -> Dict:
        """Extract receipt-specific fields"""
        fields = {}
        
        # Store name (usually in first few lines)
        lines = text.split('\n')[:5]
        for line in lines:
            if len(line) > 3 and not any(kw in line.lower() for kw in ['fiş', 'fatura', 'tarih']):
                fields['store_name'] = line.strip()
                break
        
        # Total amount
        total_patterns = [
            r'TOPLAM[:\s]*([0-9]+[,.]?[0-9]*)',
            r'TOTAL[:\s]*([0-9]+[,.]?[0-9]*)',
            r'GENEL TOPLAM[:\s]*([0-9]+[,.]?[0-9]*)',
        ]
        
        for pattern in total_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                fields['total_amount'] = match.group(1).replace(',', '.')
                break
        
        # Date
        date_patterns = [
            r'(\d{2}[/-]\d{2}[/-]\d{4})',
            r'(\d{2}\.\d{2}\.\d{4})',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                fields['date'] = match.group(1)
                break
        
        # Tax number
        tax_patterns = [
            r'VER[Gİ]*\s*NO[:\s]*([0-9]+)',
            r'V\.?N[:\s]*([0-9]+)',
        ]
        
        for pattern in tax_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                fields['tax_number'] = match.group(1)
                break
        
        return fields
    
    def _extract_invoice_fields(self, text: str) -> Dict:
        """Extract invoice-specific fields"""
        fields = self._extract_receipt_fields(text)  # Similar base fields
        
        # Invoice number
        invoice_patterns = [
            r'FATURA NO[:\s]*([A-Z0-9]+)',
            r'SERİ[:\s]*([A-Z]+)\s*NO[:\s]*([0-9]+)',
        ]
        
        for pattern in invoice_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                fields['invoice_number'] = match.group(0)
                break
        
        return fields
    
    def _extract_parking_fields(self, text: str) -> Dict:
        """Extract parking ticket fields"""
        fields = {}
        
        # License plate
        plate_patterns = [
            r'([0-9]{2}\s*[A-Z]{1,3}\s*[0-9]{2,4})',
            r'PLAKA[:\s]*([0-9A-Z\s]+)',
        ]
        
        for pattern in plate_patterns:
            match = re.search(pattern, text)
            if match:
                fields['license_plate'] = match.group(1).strip()
                break
        
        # Entry/Exit times
        time_patterns = [
            r'GİRİŞ[:\s]*(\d{2}:\d{2})',
            r'ÇIKIŞ[:\s]*(\d{2}:\d{2})',
        ]
        
        for pattern in time_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                if 'giriş' in pattern.lower():
                    fields['entry_time'] = matches[0]
                else:
                    fields['exit_time'] = matches[0]
        
        # Fee
        fee_patterns = [
            r'ÜCRET[:\s]*([0-9]+[,.]?[0-9]*)',
            r'TUTAR[:\s]*([0-9]+[,.]?[0-9]*)',
        ]
        
        for pattern in fee_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                fields['fee'] = match.group(1).replace(',', '.')
                break
        
        return fields
    
    def _extract_gas_fields(self, text: str) -> Dict:
        """Extract gas/fuel receipt fields"""
        fields = self._extract_receipt_fields(text)
        
        # Liters
        liter_patterns = [
            r'([0-9]+[,.]?[0-9]*)\s*L[İI]TRE',
            r'LİTRE[:\s]*([0-9]+[,.]?[0-9]*)',
        ]
        
        for pattern in liter_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                fields['liters'] = match.group(1).replace(',', '.')
                break
        
        # Price per liter
        price_patterns = [
            r'BİRİM FİYAT[:\s]*([0-9]+[,.]?[0-9]*)',
            r'LİTRE FİYAT[:\s]*([0-9]+[,.]?[0-9]*)',
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                fields['price_per_liter'] = match.group(1).replace(',', '.')
                break
        
        # Pump number
        pump_patterns = [
            r'POMPA[:\s]*([0-9]+)',
            r'PUMP[:\s]*([0-9]+)',
        ]
        
        for pattern in pump_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                fields['pump_number'] = match.group(1)
                break
        
        return fields
    
    def _extract_prescription_fields(self, text: str) -> Dict:
        """Extract prescription fields"""
        fields = {}
        
        # Doctor name
        dr_patterns = [
            r'DR\.?\s*([A-ZÇĞİÖŞÜ\s]+)',
            r'DOKTOR[:\s]*([A-ZÇĞİÖŞÜ\s]+)',
        ]
        
        for pattern in dr_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                fields['doctor_name'] = match.group(1).strip()
                break
        
        # Medicine names (common patterns)
        med_patterns = [
            r'([A-Z][a-z]+\s+[0-9]+\s*mg)',
            r'([A-Z][a-z]+\s+tablet)',
        ]
        
        medicines = []
        for pattern in med_patterns:
            matches = re.findall(pattern, text)
            medicines.extend(matches)
        
        if medicines:
            fields['medicines'] = medicines
        
        return fields
    
    def _extract_lab_fields(self, text: str) -> Dict:
        """Extract lab report fields"""
        fields = {}
        
        # Patient name
        patient_patterns = [
            r'HASTA[:\s]*([A-ZÇĞİÖŞÜ\s]+)',
            r'ADI SOYADI[:\s]*([A-ZÇĞİÖŞÜ\s]+)',
        ]
        
        for pattern in patient_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                fields['patient_name'] = match.group(1).strip()
                break
        
        # Test results (numerical values)
        result_patterns = [
            r'([A-Za-z]+)[:\s]*([0-9]+[,.]?[0-9]*)\s*(mg/dl|g/dl|mmol/L|U/L)',
        ]
        
        results = {}
        matches = re.findall(result_patterns[0], text, re.IGNORECASE)
        for match in matches:
            test_name = match[0]
            value = match[1].replace(',', '.')
            unit = match[2]
            results[test_name] = f"{value} {unit}"
        
        if results:
            fields['test_results'] = results
        
        return fields
    
    def _extract_bank_fields(self, text: str) -> Dict:
        """Extract bank statement fields"""
        fields = {}
        
        # Account number
        account_patterns = [
            r'HESAP NO[:\s]*([0-9\-]+)',
            r'IBAN[:\s]*([A-Z]{2}[0-9]{2}[A-Z0-9]+)',
        ]
        
        for pattern in account_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                fields['account_number'] = match.group(1)
                break
        
        # Balance
        balance_patterns = [
            r'BAKİYE[:\s]*([0-9]+[,.]?[0-9]*)',
            r'BALANCE[:\s]*([0-9]+[,.]?[0-9]*)',
        ]
        
        for pattern in balance_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                fields['balance'] = match.group(1).replace(',', '.')
                break
        
        return fields
    
    def _extract_generic_fields(self, text: str) -> Dict:
        """Extract generic fields for unknown document types"""
        fields = {}
        
        # Try to extract any dates
        date_pattern = r'(\d{2}[/-]\d{2}[/-]\d{4})'
        dates = re.findall(date_pattern, text)
        if dates:
            fields['dates'] = dates
        
        # Try to extract amounts
        amount_pattern = r'([0-9]+[,.]?[0-9]*)\s*(TL|₺|USD|EUR|$|€)'
        amounts = re.findall(amount_pattern, text)
        if amounts:
            fields['amounts'] = [f"{amt[0]} {amt[1]}" for amt in amounts]
        
        # Try to extract names (capitalized words)
        name_pattern = r'([A-ZÇĞİÖŞÜ][a-zçğıöşü]+(?:\s+[A-ZÇĞİÖŞÜ][a-zçğıöşü]+)+)'
        names = re.findall(name_pattern, text)
        if names:
            fields['possible_names'] = names[:5]  # Limit to 5
        
        return fields