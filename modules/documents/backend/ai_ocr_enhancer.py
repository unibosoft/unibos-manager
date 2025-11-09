"""
AI-Enhanced OCR Processing using Mistral AI and Hugging Face
Provides intelligent text extraction and understanding for receipts and documents
"""

import os
import re
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from decimal import Decimal
import requests
from time import sleep

logger = logging.getLogger('documents.ai_ocr')

class AIReceiptAnalyzer:
    """
    AI-powered receipt and document analyzer
    Supports multiple AI providers: Mistral, Hugging Face, and local models
    """
    
    def __init__(self, provider: str = "auto"):
        """
        Initialize AI analyzer
        Args:
            provider: "auto", "ollama", "mistral", "huggingface", or "local"
        """
        self.provider = provider
        self.api_key = None
        self.model_name = None
        self.base_url = None
        self.local_llm = None
        
        # Auto-detect best provider
        if provider == "auto":
            self.provider = self._auto_detect_provider()
            logger.info(f"Auto-detected provider: {self.provider}")
        
        # First try to load from saved keys file
        self._load_api_keys()
        
        # Initialize based on provider
        if self.provider == "ollama":
            self._init_ollama()
        elif self.provider == "mistral":
            self.api_key = os.getenv("MISTRAL_API_KEY")
            self.model_name = "mistral-small-latest"  # Cheapest model
            self.base_url = "https://api.mistral.ai/v1/chat/completions"
        elif self.provider == "huggingface":
            self.api_key = os.getenv("HUGGINGFACE_API_KEY")
            # Using free inference API with Mistral 7B
            self.model_name = "mistralai/Mistral-7B-Instruct-v0.2"
            self.base_url = "https://api-inference.huggingface.co/models/"
        else:  # local
            # Try to import local LLM processor
            try:
                from .local_llm_ocr import LocalLLMProcessor
                self.local_llm = LocalLLMProcessor(backend="auto")
                logger.info("Local LLM processor initialized")
            except Exception as e:
                logger.warning(f"Local LLM not available: {e}")
                self.model_name = "fallback"
    
    def _auto_detect_provider(self) -> str:
        """Auto-detect best available provider"""
        # 1. Check for Ollama (best for local)
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=1)
            if response.status_code == 200:
                return "ollama"
        except:
            pass
        
        # 2. Check for API keys
        if os.getenv("HUGGINGFACE_API_KEY"):
            return "huggingface"
        elif os.getenv("MISTRAL_API_KEY"):
            return "mistral"
        
        # 3. Fallback to local/pattern matching
        return "local"
    
    def _init_ollama(self):
        """Initialize Ollama connection"""
        self.base_url = "http://localhost:11434"
        self.model_name = "llama3.2:3b"  # Fast 3B model for OCR
        
        # Check if model exists
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=1)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m['name'] for m in models]
                if self.model_name not in model_names:
                    # Try alternative models
                    for alt_model in ['mistral:7b-instruct', 'llama2:7b', 'codellama:7b']:
                        if alt_model in model_names:
                            self.model_name = alt_model
                            logger.info(f"Using alternative Ollama model: {alt_model}")
                            break
        except Exception as e:
            logger.warning(f"Ollama check failed: {e}")
    
    def _load_api_keys(self):
        """Load API keys from saved file if exists"""
        try:
            from pathlib import Path
            import json
            from django.conf import settings
            
            keys_file = Path(settings.BASE_DIR) / '.api_keys.json'
            if keys_file.exists():
                with open(keys_file, 'r') as f:
                    keys = json.load(f)
                    # Set as environment variables
                    for key, value in keys.items():
                        if value:
                            os.environ[key] = value
                            logger.info(f"Loaded {key} from saved keys")
        except Exception as e:
            logger.debug(f"Could not load saved API keys: {e}")
            
    def analyze_receipt_with_ai(self, ocr_text: str, enhance_mode: str = "full") -> Dict:
        """
        Analyze receipt text using AI to extract structured data
        
        Args:
            ocr_text: Raw OCR text from receipt
            enhance_mode: "full", "quick", or "correction"
            
        Returns:
            Structured receipt data with AI enhancements
        """
        if not ocr_text:
            return {}
        
        # Use Ollama if available (best for local)
        if self.provider == "ollama":
            return self._analyze_with_ollama(ocr_text, enhance_mode)
        elif self.provider == "huggingface":
            return self._analyze_with_huggingface(ocr_text, enhance_mode)
        elif self.provider == "mistral":
            return self._analyze_with_mistral(ocr_text, enhance_mode)
        elif self.provider == "local" and self.local_llm:
            # Use local LLM processor
            result = self.local_llm.process_ocr_text(ocr_text, mode="enhance")
            return result
        else:
            return self._analyze_locally(ocr_text, enhance_mode)
    
    def _analyze_with_ollama(self, ocr_text: str, mode: str) -> Dict:
        """Use Ollama local LLM for analysis"""
        try:
            prompt = self._create_receipt_prompt(ocr_text, mode)
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "max_tokens": 500
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get('response', '')
                
                # Try to parse JSON from response
                json_match = re.search(r'\{.*\}', generated_text, re.DOTALL)
                if json_match:
                    try:
                        parsed_result = json.loads(json_match.group())
                        parsed_result['ai_enhanced'] = True
                        parsed_result['ai_provider'] = 'ollama'
                        parsed_result['model'] = self.model_name
                        return parsed_result
                    except json.JSONDecodeError:
                        logger.warning("Failed to parse Ollama response as JSON")
                
                # Return raw text for correction mode
                if mode == "correction":
                    return {"corrected_text": generated_text, "ai_provider": "ollama"}
            
        except Exception as e:
            logger.error(f"Ollama analysis failed: {str(e)}")
        
        # Fallback to pattern matching
        return self._fallback_analysis(ocr_text)
    
    def _create_receipt_prompt(self, ocr_text: str, mode: str) -> str:
        """Create appropriate prompt based on analysis mode"""
        
        if mode == "correction":
            prompt = f"""Fix OCR errors in this Turkish receipt text and return clean text:

{ocr_text}

Rules:
- Fix common OCR mistakes (0→O, 1→I, etc.)
- Fix Turkish character errors (i→ı, g→ğ, etc.)
- Keep original structure
- Return only corrected text"""

        elif mode == "quick":
            prompt = f"""Extract key information from this Turkish receipt:

{ocr_text}

Return JSON with:
- store_name: Store name
- date: Date (DD-MM-YYYY format)
- total: Total amount
- payment_method: Payment type"""

        else:  # full mode
            prompt = f"""Analyze this Turkish receipt and extract ALL information:

{ocr_text}

Return detailed JSON with:
{{
  "store_info": {{
    "name": "store name",
    "branch": "branch if exists",
    "tax_id": "tax number",
    "address": "address"
  }},
  "transaction": {{
    "date": "DD-MM-YYYY format",
    "time": "HH:MM format",
    "receipt_no": "receipt number",
    "cashier": "cashier name/id"
  }},
  "items": [
    {{
      "name": "product name",
      "quantity": numeric,
      "unit_price": numeric,
      "total_price": numeric,
      "category": "food/beverage/etc"
    }}
  ],
  "financial": {{
    "subtotal": numeric,
    "tax_amount": numeric,
    "tax_rate": numeric,
    "discount": numeric,
    "total": numeric
  }},
  "payment": {{
    "method": "cash/credit_card/debit_card",
    "card_last_digits": "if card payment",
    "amount_paid": numeric,
    "change": numeric
  }}
}}

Important:
- Extract Turkish text correctly
- Convert amounts to decimal numbers
- Identify product categories
- Fix obvious OCR errors"""

        return prompt
    
    def _analyze_with_huggingface(self, ocr_text: str, mode: str) -> Dict:
        """Use Hugging Face free inference API"""
        
        if not self.api_key:
            logger.warning("No Hugging Face API key found, using fallback analysis")
            return self._fallback_analysis(ocr_text)
        
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            prompt = self._create_receipt_prompt(ocr_text, mode)
            
            # Prepare request for Hugging Face
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 500,
                    "temperature": 0.3,
                    "return_full_text": False
                }
            }
            
            url = f"{self.base_url}{self.model_name}"
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 503:
                # Model is loading, wait and retry
                logger.info("Model is loading, waiting 20 seconds...")
                sleep(20)
                response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                # Parse the response
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get('generated_text', '')
                    
                    # Try to extract JSON from response
                    json_match = re.search(r'\{.*\}', generated_text, re.DOTALL)
                    if json_match:
                        try:
                            return json.loads(json_match.group())
                        except json.JSONDecodeError:
                            logger.warning("Failed to parse AI response as JSON")
                            
                    # If not JSON, use the text for correction mode
                    if mode == "correction":
                        return {"corrected_text": generated_text}
                        
            else:
                logger.error(f"Hugging Face API error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error in Hugging Face analysis: {str(e)}")
        
        return self._fallback_analysis(ocr_text)
    
    def _analyze_with_mistral(self, ocr_text: str, mode: str) -> Dict:
        """Use Mistral API (requires paid account)"""
        
        if not self.api_key:
            logger.warning("No Mistral API key found, using fallback analysis")
            return self._fallback_analysis(ocr_text)
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            prompt = self._create_receipt_prompt(ocr_text, mode)
            
            payload = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": "You are a receipt analysis expert. Extract information accurately."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 500
            }
            
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # Try to parse as JSON
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    try:
                        return json.loads(json_match.group())
                    except json.JSONDecodeError:
                        pass
                
                if mode == "correction":
                    return {"corrected_text": content}
                    
            else:
                logger.error(f"Mistral API error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error in Mistral analysis: {str(e)}")
        
        return self._fallback_analysis(ocr_text)
    
    def _analyze_locally(self, ocr_text: str, mode: str) -> Dict:
        """Placeholder for local model analysis"""
        # This could be implemented with llama.cpp, ONNX, or other local inference
        logger.info("Local model analysis not yet implemented, using fallback")
        return self._fallback_analysis(ocr_text)
    
    def _fallback_analysis(self, ocr_text: str) -> Dict:
        """Rule-based fallback when AI is not available"""
        
        result = {
            "store_info": {},
            "transaction": {},
            "items": [],
            "financial": {},
            "payment": {},
            "ai_enhanced": False
        }
        
        # Extract store name (first line usually)
        lines = ocr_text.strip().split('\n')
        if lines:
            result["store_info"]["name"] = lines[0].strip()
        
        # Extract date patterns
        date_patterns = [
            r'(\d{2}[-./]\d{2}[-./]\d{4})',
            r'TARİH\s*:?\s*(\d{2}[-./]\d{2}[-./]\d{4})',
            r'TARIH\s*:?\s*(\d{2}[-./]\d{2}[-./]\d{4})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, ocr_text, re.IGNORECASE)
            if match:
                result["transaction"]["date"] = match.group(1) if '(' in pattern else match.group()
                break
        
        # Extract total amount
        total_patterns = [
            r'TOPLAM\s*:?\s*([\d,\.]+)',
            r'TOTAL\s*:?\s*([\d,\.]+)',
            r'GENEL\s+TOPLAM\s*:?\s*([\d,\.]+)'
        ]
        
        for pattern in total_patterns:
            match = re.search(pattern, ocr_text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '.')
                try:
                    result["financial"]["total"] = float(amount_str)
                except ValueError:
                    pass
                break
        
        # Extract payment method
        if re.search(r'KREDİ KARTI|KREDI KARTI|K\.KARTI|\*{3,4}\d{4}', ocr_text, re.IGNORECASE):
            result["payment"]["method"] = "credit_card"
            
            # Try to find card last digits
            card_match = re.search(r'\*{3,4}(\d{4})', ocr_text)
            if card_match:
                result["payment"]["card_last_digits"] = card_match.group(1)
        elif re.search(r'NAKİT|NAKIT|PEŞİN|PESIN', ocr_text, re.IGNORECASE):
            result["payment"]["method"] = "cash"
        
        # Extract items (simple pattern matching)
        item_patterns = [
            r'([\w\s]+)\s+(\d+[,.]?\d*)\s*[xX*]\s*([\d,\.]+)\s*=?\s*([\d,\.]+)',  # name qty x price = total
            r'([\w\s]+)\s+([\d,\.]+)\s+TL',  # name price TL
        ]
        
        items = []
        for pattern in item_patterns:
            matches = re.finditer(pattern, ocr_text)
            for match in matches:
                try:
                    if len(match.groups()) == 4:
                        items.append({
                            "name": match.group(1).strip(),
                            "quantity": float(match.group(2).replace(',', '.')),
                            "unit_price": float(match.group(3).replace(',', '.')),
                            "total_price": float(match.group(4).replace(',', '.'))
                        })
                    elif len(match.groups()) == 2:
                        items.append({
                            "name": match.group(1).strip(),
                            "total_price": float(match.group(2).replace(',', '.'))
                        })
                except ValueError:
                    continue
        
        if items:
            result["items"] = items[:20]  # Limit to 20 items
        
        return result
    
    def batch_analyze_documents(self, documents: List[Dict], progress_callback=None) -> List[Dict]:
        """
        Batch process multiple documents with AI enhancement
        
        Args:
            documents: List of document dictionaries with 'id' and 'ocr_text'
            progress_callback: Optional callback function for progress updates
            
        Returns:
            List of enhanced document analyses
        """
        results = []
        total = len(documents)
        
        for idx, doc in enumerate(documents):
            if progress_callback:
                progress_callback(idx + 1, total)
            
            try:
                # Analyze with AI
                analysis = self.analyze_receipt_with_ai(
                    doc.get('ocr_text', ''),
                    enhance_mode='full'
                )
                
                analysis['document_id'] = doc.get('id')
                analysis['processing_time'] = datetime.now().isoformat()
                results.append(analysis)
                
                # Rate limiting for free APIs
                if self.provider == "huggingface":
                    sleep(0.5)  # Respect rate limits
                    
            except Exception as e:
                logger.error(f"Error processing document {doc.get('id')}: {str(e)}")
                results.append({
                    'document_id': doc.get('id'),
                    'error': str(e),
                    'ai_enhanced': False
                })
        
        return results