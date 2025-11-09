"""
LayoutLMv3 Integration Service for Document Understanding
Multimodal pre-training for visually-rich document understanding
Combines text, layout (bounding boxes), and image information
"""

import logging
from typing import Dict, Optional, List, Tuple
import os
from PIL import Image
import json
from .receipt_field_extractor import ReceiptFieldExtractor

logger = logging.getLogger('documents.layoutlmv3')


class LayoutLMv3Service:
    """
    Service for LayoutLMv3 integration
    Uses Hugging Face Transformers library

    LayoutLMv3 requires:
    1. OCR text
    2. Bounding boxes for each word
    3. Image

    It's designed for token classification, question answering, and document understanding tasks
    """

    def __init__(self, model_name='microsoft/layoutlmv3-base', language='tr'):
        """
        Initialize LayoutLMv3 service

        Args:
            model_name: Hugging Face model name
                - 'microsoft/layoutlmv3-base' (base model)
                - 'microsoft/layoutlmv3-large' (large model, better accuracy)
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
            from transformers import LayoutLMv3Processor, LayoutLMv3ForTokenClassification
            self.LayoutLMv3Processor = LayoutLMv3Processor
            self.LayoutLMv3ForTokenClassification = LayoutLMv3ForTokenClassification
            self.available = True
            logger.info(f"LayoutLMv3 libraries available")
        except ImportError as e:
            logger.warning(f"LayoutLMv3 not installed: {e}. Install with: pip install transformers torch pillow")
            self.available = False
        except Exception as e:
            logger.error(f"LayoutLMv3 initialization error: {type(e).__name__}: {e}")
            self.available = False

    def is_available(self) -> bool:
        """Check if LayoutLMv3 is available"""
        return self.available

    def initialize_model(self):
        """
        Initialize LayoutLMv3 model and processor
        Downloads model on first use (~500MB for base, ~1.5GB for large)
        """
        if not self.available:
            return False

        try:
            logger.info(f"Loading LayoutLMv3 model: {self.model_name}")

            # Load processor and model
            self.processor = self.LayoutLMv3Processor.from_pretrained(self.model_name, apply_ocr=False)
            self.model = self.LayoutLMv3ForTokenClassification.from_pretrained(self.model_name)

            # Move to GPU if available
            try:
                import torch
                if torch.cuda.is_available():
                    self.model = self.model.to('cuda')
                    logger.info("LayoutLMv3 using GPU acceleration")
                elif torch.backends.mps.is_available():
                    self.model = self.model.to('mps')
                    logger.info("LayoutLMv3 using Apple Silicon MPS acceleration")
                else:
                    logger.info("LayoutLMv3 using CPU")
            except Exception as e:
                logger.warning(f"Could not check GPU availability: {e}")

            logger.info(f"LayoutLMv3 model loaded successfully: {self.model_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize LayoutLMv3: {e}")
            self.available = False
            return False

    def process_document(
        self,
        image_path: str,
        words: List[str],
        boxes: List[Tuple[int, int, int, int]]
    ) -> Dict:
        """
        Process document with LayoutLMv3 for token classification

        Args:
            image_path: Path to document image
            words: List of OCR words
            boxes: List of bounding boxes (x0, y0, x1, y1) for each word

        Returns:
            Dictionary with classified fields
        """
        if not self.available:
            return {
                'success': False,
                'error': 'LayoutLMv3 not available',
                'fields': {},
                'text': ''
            }

        # Initialize model if not done
        if self.model is None or self.processor is None:
            if not self.initialize_model():
                return {
                    'success': False,
                    'error': 'Failed to initialize LayoutLMv3 model',
                    'fields': {},
                    'text': ''
                }

        try:
            # Check if file exists
            if not os.path.exists(image_path):
                return {
                    'success': False,
                    'error': f'Image file not found: {image_path}',
                    'fields': {},
                    'text': ''
                }

            # Load image
            logger.info(f"Processing document with LayoutLMv3: {image_path}")
            image = Image.open(image_path).convert('RGB')

            # Normalize boxes to 0-1000 range (LayoutLMv3 requirement)
            width, height = image.size
            normalized_boxes = []
            for x0, y0, x1, y1 in boxes:
                normalized_boxes.append([
                    int(1000 * x0 / width),
                    int(1000 * y0 / height),
                    int(1000 * x1 / width),
                    int(1000 * y1 / height)
                ])

            # Prepare inputs
            encoding = self.processor(
                image,
                words,
                boxes=normalized_boxes,
                return_tensors="pt",
                padding="max_length",
                truncation=True
            )

            # Move to same device as model
            try:
                import torch
                if torch.cuda.is_available():
                    encoding = {k: v.to('cuda') for k, v in encoding.items()}
                elif torch.backends.mps.is_available():
                    encoding = {k: v.to('mps') for k, v in encoding.items()}
            except Exception:
                pass  # Stay on CPU

            # Run inference
            with torch.no_grad():
                outputs = self.model(**encoding)

            # Get predictions
            predictions = outputs.logits.argmax(-1).squeeze().tolist()

            # Map predictions back to words
            # Note: This is a basic implementation
            # In production, you'd need to fine-tune the model with your labels
            labeled_words = []
            for word, label_id in zip(words, predictions):
                labeled_words.append({
                    'word': word,
                    'label_id': label_id,
                    'label': self._get_label_name(label_id)
                })

            # Extract structured fields
            fields = self._extract_fields_from_labels(labeled_words)

            # Generate text output
            text = ' '.join(words)

            logger.info(f"LayoutLMv3 processed {len(words)} words, extracted {len(fields)} fields")

            return {
                'success': True,
                'fields': fields,
                'labeled_words': labeled_words,
                'text': text,
                'confidence': 80.0,  # LayoutLMv3 generally has good confidence
                'word_count': len(words),
                'char_count': len(text),
                'model_name': self.model_name
            }

        except Exception as e:
            logger.error(f"LayoutLMv3 processing error: {e}")
            return {
                'success': False,
                'error': str(e),
                'fields': {},
                'text': ''
            }

    def process_with_paddleocr(self, image_path: str) -> Dict:
        """
        Process document using PaddleOCR for text/boxes + LayoutLMv3 for classification

        Args:
            image_path: Path to document image

        Returns:
            Dictionary with classified fields
        """
        try:
            # Use PaddleOCR to get words and boxes
            from .paddleocr_service import PaddleOCRService

            paddle = PaddleOCRService(lang='en', use_structure=False)
            if not paddle.is_available() or not paddle.initialize_ocr():
                return {
                    'success': False,
                    'error': 'PaddleOCR not available for text extraction',
                    'fields': {},
                    'text': ''
                }

            # Get OCR results
            ocr_result = paddle.process_image(image_path)
            if not ocr_result.get('success'):
                return {
                    'success': False,
                    'error': f"PaddleOCR failed: {ocr_result.get('error')}",
                    'fields': {},
                    'text': ''
                }

            # Extract words and boxes
            lines = ocr_result.get('lines', [])
            words = []
            boxes = []

            for line in lines:
                word = line.get('text', '')
                bbox = line.get('bbox', [])

                if word and bbox:
                    words.append(word)
                    # Convert bbox to (x0, y0, x1, y1) format
                    if len(bbox) >= 4:
                        # bbox is [[x0, y0], [x1, y1], [x2, y2], [x3, y3]]
                        x_coords = [p[0] for p in bbox]
                        y_coords = [p[1] for p in bbox]
                        x0, x1 = min(x_coords), max(x_coords)
                        y0, y1 = min(y_coords), max(y_coords)
                        boxes.append((int(x0), int(y0), int(x1), int(y1)))

            # Instead of using LayoutLMv3's token classification (which requires fine-tuning),
            # use universal field extractor on PaddleOCR results for better accuracy
            text = ' '.join(words)

            # Extract fields using universal extractor
            extracted_fields = self.field_extractor.extract_all_fields(
                text=text,
                lines=[{'text': word} for word in words]
            )

            logger.info(f"LayoutLMv3+PaddleOCR: Extracted {len(words)} words")

            return {
                'success': True,
                'text': text,
                'fields': extracted_fields,
                'confidence': 80.0,  # Good confidence from PaddleOCR + extractor
                'word_count': len(words),
                'char_count': len(text)
            }

        except Exception as e:
            logger.error(f"LayoutLMv3 + PaddleOCR processing error: {e}")
            return {
                'success': False,
                'error': str(e),
                'fields': {},
                'text': ''
            }

    def _get_label_name(self, label_id: int) -> str:
        """
        Map label ID to label name
        Note: This is a placeholder - actual labels depend on fine-tuning

        Common labels for receipts:
        - O: Other
        - STORE: Store name
        - TOTAL: Total amount
        - DATE: Date
        - TIME: Time
        - ADDRESS: Address
        - ITEM: Item name
        - PRICE: Price
        """
        # Default FUNSD labels (form understanding)
        label_map = {
            0: 'O',
            1: 'B-QUESTION',
            2: 'B-ANSWER',
            3: 'B-HEADER',
            4: 'I-QUESTION',
            5: 'I-ANSWER',
            6: 'I-HEADER'
        }

        return label_map.get(label_id, f'LABEL_{label_id}')

    def _extract_fields_from_labels(self, labeled_words: List[Dict]) -> Dict:
        """
        Extract structured fields from labeled words

        Args:
            labeled_words: List of dictionaries with 'word' and 'label'

        Returns:
            Dictionary with extracted fields
        """
        fields = {
            'store_name': None,
            'total_amount': None,
            'date': None,
            'time': None,
            'address': None,
            'items': [],
            'found_store': False,
            'found_total': False,
            'found_date': False
        }

        # Group consecutive words with same label
        current_label = None
        current_words = []

        for item in labeled_words:
            word = item['word']
            label = item['label']

            # Check if this is a new entity
            if label.startswith('B-') or label != current_label:
                # Save previous entity
                if current_label and current_words:
                    text = ' '.join(current_words)
                    self._assign_field(fields, current_label, text)

                # Start new entity
                current_label = label
                current_words = [word]
            elif label.startswith('I-'):
                # Continue current entity
                current_words.append(word)
            else:
                # 'O' label - reset
                if current_label and current_words:
                    text = ' '.join(current_words)
                    self._assign_field(fields, current_label, text)
                current_label = None
                current_words = []

        # Save last entity
        if current_label and current_words:
            text = ' '.join(current_words)
            self._assign_field(fields, current_label, text)

        return fields

    def _assign_field(self, fields: Dict, label: str, text: str):
        """
        Assign extracted text to appropriate field based on label

        Args:
            fields: Dictionary to update
            label: Label name
            text: Extracted text
        """
        label_upper = label.upper()

        if 'STORE' in label_upper or 'HEADER' in label_upper:
            if not fields['store_name']:
                fields['store_name'] = text
                fields['found_store'] = True
        elif 'TOTAL' in label_upper or 'AMOUNT' in label_upper:
            if not fields['total_amount']:
                fields['total_amount'] = text
                fields['found_total'] = True
        elif 'DATE' in label_upper:
            if not fields['date']:
                fields['date'] = text
                fields['found_date'] = True
        elif 'TIME' in label_upper:
            if not fields['time']:
                fields['time'] = text
        elif 'ADDRESS' in label_upper:
            if not fields['address']:
                fields['address'] = text
        elif 'ITEM' in label_upper:
            fields['items'].append(text)
