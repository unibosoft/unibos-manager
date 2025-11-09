"""
Donut Integration Service for Document Understanding
OCR-free Document Understanding Transformer
Directly extracts structured data (JSON) from document images without OCR
"""

import logging
from typing import Dict, Optional
import os
import json
from PIL import Image
import re
from .receipt_field_extractor import ReceiptFieldExtractor

logger = logging.getLogger('documents.donut')


class DonutService:
    """
    Service for Donut integration (OCR-free Document Understanding)
    Uses Hugging Face Transformers library

    Models:
    - naver-clova-ix/donut-base-finetuned-cord-v2: Receipt understanding (recommended)
    - naver-clova-ix/donut-base-finetuned-docvqa: Document VQA
    - naver-clova-ix/donut-base: Base model (requires fine-tuning)
    """

    def __init__(self, model_name='naver-clova-ix/donut-base-finetuned-cord-v2', language='tr'):
        """
        Initialize Donut service

        Args:
            model_name: Hugging Face model name
                - 'naver-clova-ix/donut-base-finetuned-cord-v2' (receipt understanding, recommended)
                - 'naver-clova-ix/donut-base-finetuned-docvqa' (document QA)
            language: Primary language for field extraction ('tr', 'en')
        """
        self.model_name = model_name
        self.language = language
        self.available = False
        self.processor = None
        self.model = None

        # Initialize universal field extractor
        self.field_extractor = ReceiptFieldExtractor(language=language)

        # Try to import required libraries
        try:
            from transformers import AutoProcessor, VisionEncoderDecoderModel
            self.AutoProcessor = AutoProcessor
            self.VisionEncoderDecoderModel = VisionEncoderDecoderModel
            self.available = True
            logger.info(f"Donut libraries available")
        except ImportError as e:
            logger.warning(f"Donut not installed: {e}. Install with: pip install transformers torch pillow")
            self.available = False
        except Exception as e:
            logger.error(f"Donut initialization error: {type(e).__name__}: {e}")
            self.available = False

    def is_available(self) -> bool:
        """Check if Donut is available"""
        return self.available

    def initialize_model(self):
        """
        Initialize Donut model and processor
        Downloads model on first use (~500MB)
        """
        if not self.available:
            return False

        try:
            logger.info(f"Loading Donut model: {self.model_name}")

            # Load processor and model
            self.processor = self.AutoProcessor.from_pretrained(self.model_name)
            self.model = self.VisionEncoderDecoderModel.from_pretrained(self.model_name)

            # Move to GPU if available
            try:
                import torch
                if torch.cuda.is_available():
                    self.model = self.model.to('cuda')
                    logger.info("Donut using GPU acceleration")
                elif torch.backends.mps.is_available():
                    self.model = self.model.to('mps')
                    logger.info("Donut using Apple Silicon MPS acceleration")
                else:
                    logger.info("Donut using CPU")
            except Exception as e:
                logger.warning(f"Could not check GPU availability: {e}")

            logger.info(f"Donut model loaded successfully: {self.model_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize Donut: {e}")
            self.available = False
            return False

    def process_receipt(self, image_path: str) -> Dict:
        """
        Process receipt image with Donut (OCR-free)
        Extracts structured data directly as JSON

        Args:
            image_path: Path to receipt image

        Returns:
            Dictionary with structured receipt data
        """
        if not self.available:
            return {
                'success': False,
                'error': 'Donut not available',
                'data': {},
                'text': ''
            }

        # Initialize model if not done
        if self.model is None or self.processor is None:
            if not self.initialize_model():
                return {
                    'success': False,
                    'error': 'Failed to initialize Donut model',
                    'data': {},
                    'text': ''
                }

        try:
            # Check if file exists
            if not os.path.exists(image_path):
                return {
                    'success': False,
                    'error': f'Image file not found: {image_path}',
                    'data': {},
                    'text': ''
                }

            # Load image
            logger.info(f"Processing receipt with Donut: {image_path}")
            image = Image.open(image_path).convert('RGB')

            # Prepare image for model
            pixel_values = self.processor(image, return_tensors="pt").pixel_values

            # Move to same device as model
            try:
                import torch
                if torch.cuda.is_available():
                    pixel_values = pixel_values.to('cuda')
                elif torch.backends.mps.is_available():
                    pixel_values = pixel_values.to('mps')
            except Exception:
                pass  # Stay on CPU

            # Prepare decoder input for receipt parsing
            # Donut uses task prompts to guide generation
            task_prompt = "<s_cord-v2>"  # CORD v2 task prompt for receipt understanding
            decoder_input_ids = self.processor.tokenizer(
                task_prompt,
                add_special_tokens=False,
                return_tensors="pt"
            ).input_ids

            # Move to same device
            try:
                import torch
                if torch.cuda.is_available():
                    decoder_input_ids = decoder_input_ids.to('cuda')
                elif torch.backends.mps.is_available():
                    decoder_input_ids = decoder_input_ids.to('mps')
            except Exception:
                pass

            # Generate structured output
            outputs = self.model.generate(
                pixel_values,
                decoder_input_ids=decoder_input_ids,
                max_length=self.model.decoder.config.max_position_embeddings,
                pad_token_id=self.processor.tokenizer.pad_token_id,
                eos_token_id=self.processor.tokenizer.eos_token_id,
                use_cache=True,
                bad_words_ids=[[self.processor.tokenizer.unk_token_id]],
                return_dict_in_generate=True,
                output_scores=True
            )

            # Decode output
            sequence = self.processor.batch_decode(outputs.sequences)[0]
            sequence = sequence.replace(self.processor.tokenizer.eos_token, "").replace(self.processor.tokenizer.pad_token, "")
            sequence = re.sub(r"<.*?>", "", sequence, count=1).strip()  # Remove task start token

            # Parse JSON from output
            try:
                # Donut outputs JSON-like structure
                parsed_data = self.processor.token2json(sequence)
            except Exception as parse_error:
                logger.warning(f"Failed to parse Donut output as JSON: {parse_error}")
                # Try manual JSON parsing
                try:
                    parsed_data = json.loads(sequence)
                except:
                    parsed_data = {'raw_output': sequence}

            # Handle case where token2json returns a list instead of dict
            if isinstance(parsed_data, list):
                if len(parsed_data) > 0 and isinstance(parsed_data[0], dict):
                    # Use first dict in list
                    parsed_data = parsed_data[0]
                    logger.info("Donut returned list, using first element")
                else:
                    # Can't process this format
                    logger.warning(f"Donut returned unexpected list format: {type(parsed_data[0]) if parsed_data else 'empty'}")
                    parsed_data = {'raw_output': str(parsed_data)}

            # Extract key fields from parsed data
            extracted = self._extract_receipt_fields(parsed_data)

            # Generate readable text from structured data
            text = self._generate_text_from_data(extracted)

            logger.info(f"Donut extracted {len(extracted)} fields")

            return {
                'success': True,
                'data': extracted,
                'raw_data': parsed_data,
                'text': text,
                'confidence': 85.0,  # Donut is generally high confidence
                'char_count': len(text),
                'word_count': len(text.split()),
                'fields_extracted': len(extracted),
                'model_name': self.model_name
            }

        except Exception as e:
            import traceback
            error_traceback = traceback.format_exc()
            logger.error(f"Donut processing error: {e}")
            logger.error(f"Full traceback:\n{error_traceback}")
            return {
                'success': False,
                'error': str(e),
                'data': {},
                'text': ''
            }

    def _extract_receipt_fields(self, parsed_data: Dict) -> Dict:
        """
        Extract key receipt fields from Donut parsed data
        Uses universal ReceiptFieldExtractor for flexible, language-agnostic extraction

        Args:
            parsed_data: Parsed JSON data from Donut

        Returns:
            Dictionary with standardized receipt fields
        """
        # Safety check: ensure parsed_data is a dict
        if not isinstance(parsed_data, dict):
            logger.warning(f"_extract_receipt_fields received non-dict parsed_data: {type(parsed_data)}")
            parsed_data = {}

        # Use universal field extractor with structured data
        # Pass the parsed_data as structured_data for high-confidence extraction
        extracted = self.field_extractor.extract_all_fields(
            structured_data=parsed_data
        )

        # Safety check: ensure extracted is a dict
        if not isinstance(extracted, dict):
            logger.warning(f"extract_all_fields returned non-dict: {type(extracted)}")
            return {
                'store_name': None,
                'total_amount': None,
                'date': None,
                'time': None,
                'address': None,
                'phone': None,
                'items': [],
                'found_store': False,
                'found_total': False,
                'found_date': False,
                'found_time': False,
                'confidence_scores': {}
            }

        # Donut-specific enhancements
        # If we have menu items, also try to extract from them as plain text
        # This helps when Donut misstructures the data
        if 'menu' in parsed_data and parsed_data['menu']:
            # Build text representation of menu items for additional extraction
            menu_text_lines = []
            for item in parsed_data['menu']:
                if isinstance(item, dict):
                    # Combine all fields into a line of text
                    parts = []
                    for key in ['name', 'nm', 'quantity', 'cnt', 'price', 'unitprice']:
                        val = item.get(key, '')
                        if val:
                            parts.append(str(val))
                    if parts:
                        menu_text_lines.append(' '.join(parts))

            # If we still haven't found key fields, try extracting from menu text
            if menu_text_lines:
                menu_text = '\n'.join(menu_text_lines)

                # Create line-by-line data for the extractor
                lines_data = [{'text': line} for line in menu_text_lines]

                # Re-extract with line-by-line data if we're missing key fields
                if not extracted['found_store'] or not extracted['found_total'] or not extracted['found_date']:
                    additional = self.field_extractor.extract_all_fields(
                        text=menu_text,
                        lines=lines_data
                    )

                    # Merge results (prefer original structured extraction)
                    if not extracted['found_store'] and additional.get('found_store'):
                        extracted['store_name'] = additional.get('store_name')
                        extracted['found_store'] = True
                        if isinstance(extracted.get('confidence_scores'), dict) and isinstance(additional.get('confidence_scores'), dict):
                            extracted['confidence_scores']['store'] = additional['confidence_scores'].get('store', 80.0)

                    if not extracted['found_total'] and additional.get('found_total'):
                        extracted['total_amount'] = additional.get('total_amount')
                        extracted['found_total'] = True
                        if isinstance(extracted.get('confidence_scores'), dict) and isinstance(additional.get('confidence_scores'), dict):
                            extracted['confidence_scores']['total'] = additional['confidence_scores'].get('total', 80.0)

                    if not extracted['found_date'] and additional.get('found_date'):
                        extracted['date'] = additional.get('date')
                        extracted['found_date'] = True
                        if isinstance(extracted.get('confidence_scores'), dict) and isinstance(additional.get('confidence_scores'), dict):
                            extracted['confidence_scores']['date'] = additional['confidence_scores'].get('date', 80.0)

                    if not extracted['found_time'] and additional.get('found_time'):
                        extracted['time'] = additional.get('time')
                        extracted['found_time'] = True
                        if isinstance(extracted.get('confidence_scores'), dict) and isinstance(additional.get('confidence_scores'), dict):
                            extracted['confidence_scores']['time'] = additional['confidence_scores'].get('time', 80.0)

        return extracted

    def _generate_text_from_data(self, data: Dict) -> str:
        """
        Generate readable text from structured receipt data

        Args:
            data: Extracted receipt data

        Returns:
            Human-readable text representation
        """
        # Handle case where data is not a dict
        if not isinstance(data, dict):
            logger.warning(f"_generate_text_from_data received non-dict data: {type(data)}")
            return ""

        lines = []

        # Store name
        if data.get('store_name'):
            lines.append(f"STORE: {data['store_name']}")

        # Date/time
        if data.get('date'):
            date_str = f"DATE: {data['date']}"
            if data.get('time'):
                date_str += f" {data['time']}"
            lines.append(date_str)

        # Address
        if data.get('address'):
            lines.append(f"ADDRESS: {data['address']}")

        # Phone
        if data.get('phone'):
            lines.append(f"PHONE: {data['phone']}")

        # Items
        if data.get('items'):
            lines.append("\nITEMS:")
            for item in data['items']:
                item_line = f"  - {item.get('name', 'Unknown')}"
                if item.get('quantity'):
                    item_line += f" x{item['quantity']}"
                if item.get('price'):
                    item_line += f" = {item['price']}"
                lines.append(item_line)

        # Totals
        lines.append("")
        if data.get('subtotal'):
            lines.append(f"SUBTOTAL: {data['subtotal']}")
        if data.get('tax'):
            lines.append(f"TAX: {data['tax']}")
        if data.get('total_amount'):
            lines.append(f"TOTAL: {data['total_amount']}")

        return '\n'.join(lines)

    def process_document_qa(self, image_path: str, question: str) -> Dict:
        """
        Process document with question answering (if using DocVQA model)

        Args:
            image_path: Path to document image
            question: Question to ask about the document

        Returns:
            Dictionary with answer
        """
        # This requires the DocVQA fine-tuned model
        # Would need to switch model or have separate instance
        return {
            'success': False,
            'error': 'Document QA not implemented yet',
            'answer': ''
        }
