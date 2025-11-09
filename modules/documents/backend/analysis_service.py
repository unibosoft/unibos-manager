"""
OCR Analysis Service - Comprehensive Multi-Method Comparison
Compares multiple OCR approaches side-by-side:
1. Tesseract Pure OCR (baseline)
2. Llama 3.2-Vision (Meta's vision model - primary)
3. Moondream2 (lightweight vision model)
4. PaddleOCR (multilingual OCR)
5. Hybrid (Tesseract + Vision parsing)
6. Donut (OCR-free transformer)
7. LayoutLMv3 (layout-aware extraction)
"""

import time
import logging
import json
import base64
from typing import Dict, List, Optional
from PIL import Image
import io
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger('documents.analysis')


class OCRAnalysisService:
    """
    Comprehensive OCR analysis service that runs multiple OCR methods
    and provides detailed comparison metrics

    Results are stored in the database (Document.analysis_results) instead of cache
    """

    def __init__(self):
        # Removed: moondream (not suitable for OCR), minicpm-v (experimental)
        # Added: surya (all-in-one), doctr (modern DL), easyocr (fallback), ocrmypdf (PDF-optimized)
        self.methods = ['paddleocr', 'tesseract', 'llama_vision', 'trocr', 'donut', 'layoutlmv3', 'surya', 'doctr', 'easyocr', 'ocrmypdf', 'hybrid']

        # Initialize quality assessment service
        from .image_quality_service import ImageQualityService
        self.quality_service = ImageQualityService()

        # Initialize channel layer for WebSocket updates
        self.channel_layer = get_channel_layer()

    def _send_websocket_message(self, document_id, message_type: str, data: dict):
        """Send WebSocket message to frontend

        Args:
            document_id: Document ID (UUID or int) - will be converted to string
            message_type: Message type (log, status, result, complete)
            data: Message data dict
        """
        try:
            if self.channel_layer:
                # Convert UUID to string for group name
                room_group_name = f'ocr_analysis_{str(document_id)}'
                logger.info(f"📡 Sending WebSocket {message_type} to {room_group_name}")
                async_to_sync(self.channel_layer.group_send)(
                    room_group_name,
                    {
                        'type': f'analysis_{message_type}',
                        **data
                    }
                )
                logger.info(f"✅ WebSocket {message_type} sent successfully")
        except Exception as e:
            logger.error(f"Failed to send WebSocket message to {document_id}: {e}", exc_info=True)

    def _make_json_serializable(self, obj):
        """Convert numpy/pandas types to native Python types for JSON serialization"""
        import numpy as np

        if isinstance(obj, dict):
            return {key: self._make_json_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        elif isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        elif isinstance(obj, (np.bool_)):
            return bool(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return obj

    def analyze_document(self, document, force_refresh: bool = False, methods_to_run: list = None, max_workers: int = 2) -> Dict:
        """
        Run OCR methods on a document (fast methods by default, or specified methods)

        Includes comprehensive error handling and fallbacks for each method
        Results are stored in database (Document.analysis_results)

        Args:
            document: Document model instance
            force_refresh: If True, re-run analysis even if results exist in database
            methods_to_run: List of methods to run (default: ['paddleocr'] for fast initial load)
                          Available methods: 'paddleocr', 'tesseract', 'llama_vision', 'trocr', 'donut', 'layoutlmv3', 'surya', 'doctr', 'easyocr', 'ocrmypdf', 'hybrid'
            max_workers: Maximum number of concurrent workers (default: 2, max: 5)

        Returns:
            Dictionary with analysis results for requested methods
        """
        # Default to PaddleOCR only for initial page load (fast and accurate)
        if methods_to_run is None:
            methods_to_run = ['paddleocr']

        document_id = str(document.id)

        # Check database for existing results (unless force refresh)
        if not force_refresh and document.analysis_results:
            existing_results = document.analysis_results
            # Check if all requested methods have results
            all_methods_exist = all(method in existing_results for method in methods_to_run)

            if all_methods_exist:
                logger.info(f"Returning existing analysis from database for document {document_id}")
                existing_results['from_database'] = True
                existing_results['last_analysis_at'] = document.last_analysis_at.isoformat() if document.last_analysis_at else None
                return existing_results

        logger.info(f"Running fresh analysis for document {document_id}")
        analysis_start_time = time.time()  # Track total analysis time

        # Step 1: Assess image quality and get OCR recommendation
        image_path = document.file_path.path
        quality_assessment = self.quality_service.assess_quality(image_path)

        logger.info(f"Quality assessment for {document_id}:")
        logger.info(f"  - Quality level: {quality_assessment.get('quality_level', 'unknown')}")
        logger.info(f"  - Recommended OCR: {quality_assessment.get('recommended_ocr', 'unknown')}")
        logger.info(f"  - Blur score: {quality_assessment.get('blur_score', 0):.2f}")
        logger.info(f"  - Contrast: {quality_assessment.get('contrast_score', 0):.2f}")
        logger.info(f"  - DPI: {quality_assessment.get('dpi', 0)}")

        # Step 2: Apply preprocessing if needed
        preprocessed_path = None
        if quality_assessment.get('success') and any(quality_assessment.get('preprocessing_needed', {}).values()):
            logger.info("Applying preprocessing to improve OCR quality...")
            preprocessing_result = self.quality_service.preprocess_image(image_path)

            if preprocessing_result.get('success'):
                preprocessed_path = preprocessing_result['preprocessed_path']
                logger.info(f"Preprocessing applied: {preprocessing_result['preprocessing_applied']}")
                logger.info(f"Using preprocessed image: {preprocessed_path}")
            else:
                logger.warning(f"Preprocessing failed: {preprocessing_result.get('error')}")

        # Use preprocessed image if available, otherwise use original
        ocr_image_path = preprocessed_path if preprocessed_path else image_path

        results = {
            'document_id': document_id,
            'filename': document.original_filename,
            'quality_assessment': quality_assessment,  # Add quality info to results
            'preprocessed': preprocessed_path is not None,
            'paddleocr': {},
            'tesseract': {},
            'llama_vision': {},
            'trocr': {},
            'donut': {},
            'layoutlmv3': {},
            'surya': {},
            'doctr': {},
            'easyocr': {},
            'ocrmypdf': {},
            'hybrid': {},
            'has_processing': False,
            'analysis_errors': [],
            'from_cache': False,
            'methods_run': methods_to_run  # Track which methods were executed
        }

        # Map method names to their analysis functions
        method_map = {
            'paddleocr': self._analyze_paddleocr,
            'tesseract': self._analyze_tesseract,
            'llama_vision': self._analyze_llama_vision,
            'hybrid': self._analyze_hybrid,
            'trocr': self._analyze_trocr,
            'donut': self._analyze_donut,
            'layoutlmv3': self._analyze_layoutlmv3,
            'surya': self._analyze_surya,
            'doctr': self._analyze_doctr,
            'easyocr': self._analyze_easyocr,
            'ocrmypdf': self._analyze_ocrmypdf
        }

        # Execute selected methods in parallel using ThreadPoolExecutor
        logger.info(f"Running {len(methods_to_run)} methods in parallel: {', '.join(methods_to_run)} (max_workers={max_workers})")

        # Send WebSocket messages for queued methods
        for method_name in methods_to_run:
            self._send_websocket_message(document.id, 'log', {
                'message': f'{method_name} kuyruğa alındı',
                'level': 'info',
                'timestamp': timezone.now().isoformat()
            })
            self._send_websocket_message(document.id, 'status', {
                'method': method_name,
                'status': 'queued'
            })

        def run_method(method_name: str):
            """Execute a single OCR method and return results"""
            method_start = time.time()
            try:
                logger.info(f"[{method_name}] ⏱️  Started analysis for document {document.id}")

                # Send WebSocket update: method started
                self._send_websocket_message(document.id, 'status', {
                    'method': method_name,
                    'status': 'running'
                })
                self._send_websocket_message(document.id, 'log', {
                    'message': f'{method_name} işleniyor...',
                    'level': 'info',
                    'timestamp': timezone.now().isoformat()
                })

                analysis_func = method_map.get(method_name)
                if analysis_func:
                    result = method_name, analysis_func(document)
                    method_elapsed = time.time() - method_start
                    logger.info(f"[{method_name}] ✅ Completed in {method_elapsed:.2f}s (wall clock)")
                    return result
                else:
                    logger.warning(f"[{method_name}] ❌ Unknown method")
                    return method_name, self._get_error_result(f"Unknown method: {method_name}")
            except Exception as e:
                method_elapsed = time.time() - method_start
                logger.error(f"[{method_name}] ❌ Failed after {method_elapsed:.2f}s: {e}")
                return method_name, self._get_error_result(str(e))

        # Execute methods in parallel (max 2 concurrent workers to avoid memory issues)
        # Each deep learning model (TrOCR, LayoutLMv3, EasyOCR) can use 1-3GB RAM
        # Running too many in parallel causes OOM crashes (exit code 251)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all method tasks
            future_to_method = {
                executor.submit(run_method, method): method
                for method in methods_to_run
            }

            # Collect results as they complete and save to database incrementally
            for future in as_completed(future_to_method):
                method_name, result = future.result()
                # Add timestamp to each method result
                result['analyzed_at'] = timezone.now().isoformat()
                results[method_name] = result

                # Track errors
                if result.get('status') == 'error':
                    results['analysis_errors'].append(f"{method_name}: {result.get('error', 'Unknown error')}")
                    # Send WebSocket update: error
                    self._send_websocket_message(document.id, 'log', {
                        'message': f'{method_name} hatası: {result.get("error", "Bilinmeyen hata")}',
                        'level': 'error',
                        'timestamp': timezone.now().isoformat()
                    })
                else:
                    # Send WebSocket update: completed
                    self._send_websocket_message(document.id, 'log', {
                        'message': f'{method_name} tamamlandı ({result.get("processing_time", 0):.1f}s)',
                        'level': 'success',
                        'timestamp': timezone.now().isoformat()
                    })

                # Send result data via WebSocket
                self._send_websocket_message(document.id, 'result', {
                    'method': method_name,
                    'data': self._make_json_serializable(result)
                })

                # Save to database incrementally after each method completes
                # This allows polling endpoint to see real-time progress
                try:
                    # Refresh document from DB to avoid race conditions
                    document.refresh_from_db()

                    # Convert current results to JSON-serializable format
                    serializable_results = self._make_json_serializable(results)

                    # Merge with existing results if they exist
                    if document.analysis_results:
                        merged_results = document.analysis_results.copy()
                        merged_results[method_name] = serializable_results[method_name]
                        # Update meta fields
                        merged_results['document_id'] = serializable_results['document_id']
                        merged_results['filename'] = serializable_results['filename']
                        merged_results['quality_assessment'] = serializable_results['quality_assessment']
                        merged_results['preprocessed'] = serializable_results['preprocessed']
                        merged_results['analysis_errors'] = serializable_results['analysis_errors']
                        document.analysis_results = merged_results
                    else:
                        document.analysis_results = serializable_results

                    document.last_analysis_at = timezone.now()
                    document.save(update_fields=['analysis_results', 'last_analysis_at'])

                    logger.info(f"💾 Saved {method_name} results to database (incremental save)")
                except Exception as save_error:
                    logger.error(f"Failed to save {method_name} results incrementally: {save_error}")

        # Check if any method is still processing
        try:
            results['has_processing'] = any(
                results[method].get('status') == 'processing'
                for method in self.methods
            )
        except Exception as e:
            logger.error(f"Processing status check failed: {e}")
            results['has_processing'] = False

        # Save results to database
        # Convert to JSON-serializable format (handle numpy types)
        serializable_results = self._make_json_serializable(results)

        # Merge with existing results if they exist (to preserve previously run methods)
        if document.analysis_results:
            # Merge new results with existing ones
            merged_results = document.analysis_results.copy()
            for method in methods_to_run:
                if method in serializable_results:
                    merged_results[method] = serializable_results[method]
            # Update meta fields
            merged_results['document_id'] = serializable_results['document_id']
            merged_results['filename'] = serializable_results['filename']
            merged_results['quality_assessment'] = serializable_results['quality_assessment']
            merged_results['preprocessed'] = serializable_results['preprocessed']
            merged_results['has_processing'] = serializable_results['has_processing']
            merged_results['analysis_errors'] = serializable_results['analysis_errors']
            document.analysis_results = merged_results
        else:
            document.analysis_results = serializable_results

        document.last_analysis_at = timezone.now()
        document.save(update_fields=['analysis_results', 'last_analysis_at'])

        total_analysis_time = time.time() - analysis_start_time
        logger.info(f"✅ Analysis completed for document {document_id} in {total_analysis_time:.2f}s (wall clock time)")
        logger.info(f"   Saved analysis results to database for document {document_id}")

        # Send WebSocket completion message
        self._send_websocket_message(document.id, 'complete', {
            'message': f'Tüm işlemler tamamlandı ({total_analysis_time:.1f}s)'
        })

        # Add timestamp to returned results
        results['last_analysis_at'] = document.last_analysis_at.isoformat()
        results['from_database'] = False  # Freshly computed
        results['total_wall_time'] = total_analysis_time  # Add wall clock time to results

        return results

    def _get_error_result(self, error_msg: str) -> Dict:
        """Return standardized error result structure"""
        return {
            'status': 'error',
            'error': error_msg,
            'text': None,
            'confidence': 0,
            'char_count': 0,
            'word_count': 0,
            'processing_time': 0,
            'found_store': False,
            'store_name': None,
            'found_total': False,
            'total_amount': None,
            'found_date': False,
            'date_time': None,
            'found_bottom': False,
            'bottom_info': None
        }

    def _analyze_tesseract(self, document) -> Dict:
        """Analyze using pure Tesseract OCR"""
        try:
            if not document.tesseract_text:
                return {
                    'status': 'pending',
                    'text': None,
                    'confidence': 0,
                    'char_count': 0,
                    'word_count': 0,
                    'processing_time': 0,
                    'found_store': False,
                    'found_total': False,
                    'found_date': False,
                    'found_bottom': False
                }

            text = document.tesseract_text
            confidence = document.tesseract_confidence or 0

            # Analyze key findings
            findings = self._analyze_key_findings(text)

            return {
                'status': 'success',
                'text': text,
                'confidence': confidence,
                'char_count': len(text) if text else 0,
                'word_count': len(text.split()) if text else 0,
                'processing_time': 0,  # Already processed
                **findings
            }

        except Exception as e:
            logger.error(f"Tesseract analysis error: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'char_count': 0,
                'word_count': 0,
                'processing_time': 0
            }

    def _analyze_llama_vision(self, document) -> Dict:
        """Analyze using Llama 3.2-Vision (Meta's primary vision model)"""
        try:
            from .ollama_service import OllamaService

            # Check if Ollama result exists for llama3.2-vision
            if document.ollama_text and document.ollama_model == 'llama3.2-vision':
                text = document.ollama_text
                confidence = document.ollama_confidence or 0
                findings = self._analyze_key_findings(text)

                return {
                    'status': 'success',
                    'text': text,
                    'confidence': confidence,
                    'char_count': len(text) if text else 0,
                    'word_count': len(text.split()) if text else 0,
                    'processing_time': 0,  # Already processed
                    **findings
                }

            # Run fresh Llama 3.2-Vision analysis
            ollama = OllamaService()
            if not ollama.is_available():
                return {
                    'status': 'error',
                    'error': 'Ollama not available',
                    'char_count': 0,
                    'word_count': 0,
                'processing_time': 0
                }

            # Switch to Llama 3.2-Vision
            ollama.current_model = 'llama3.2-vision'

            # Load image as base64
            image_base64 = self._load_image_as_base64(document.file_path.path)
            if not image_base64:
                return {
                    'status': 'error',
                    'error': 'Failed to load image',
                    'char_count': 0,
                    'word_count': 0,
                'processing_time': 0
                }

            # Run pure vision OCR (no tesseract text)
            start_time = time.time()
            result = ollama.analyze_receipt(ocr_text='', image_base64=image_base64)
            processing_time = time.time() - start_time

            if result.get('success'):
                text = result.get('raw_response', '')
                findings = self._analyze_key_findings(text)

                return {
                    'status': 'success',
                    'text': text,
                    'confidence': result.get('confidence', 0),
                    'char_count': len(text),
                    'word_count': len(text.split()),
                    'processing_time': processing_time,
                    **findings
                }
            else:
                return {
                    'status': 'error',
                    'error': result.get('error', 'Unknown error'),
                    'char_count': 0,
                    'word_count': 0,
                'processing_time': 0
                }

        except Exception as e:
            logger.error(f"Llama 3.2-Vision analysis error: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'char_count': 0,
                'word_count': 0,
            'processing_time': 0
            }

    def _analyze_hybrid(self, document) -> Dict:
        """Analyze using Hybrid approach (PaddleOCR + Llama Vision parsing)"""
        try:
            from .ollama_service import OllamaService
            from .paddleocr_service import PaddleOCRService

            # Get PaddleOCR text (run it inline if needed)
            paddle_text = None

            # Try to get PaddleOCR text from document if it was stored
            if hasattr(document, 'paddle_text') and document.paddle_text:
                paddle_text = document.paddle_text
            else:
                # Run PaddleOCR inline to get the text
                try:
                    paddle = PaddleOCRService(lang='en', use_structure=False)
                    if paddle.is_available():
                        ocr_result = paddle.get_text_with_layout(document.file_path.path)
                        if ocr_result:
                            paddle_text = ocr_result if isinstance(ocr_result, str) else ocr_result.get('text', '')
                except Exception as paddle_error:
                    logger.warning(f"Failed to run PaddleOCR for hybrid: {paddle_error}")

            if not paddle_text:
                return {
                    'status': 'error',
                    'error': 'PaddleOCR text not available',
                    'char_count': 0,
                    'fields_extracted': 0
                }

            ollama = OllamaService()
            if not ollama.is_available():
                return {
                    'status': 'error',
                    'error': 'Ollama not available',
                    'char_count': 0,
                    'fields_extracted': 0
                }

            # Switch to Llama 3.2-Vision for parsing
            ollama.current_model = 'llama3.2-vision'

            # Load image as base64
            image_base64 = self._load_image_as_base64(document.file_path.path)

            # Run hybrid analysis (PaddleOCR text + image)
            start_time = time.time()
            result = ollama.analyze_receipt(
                ocr_text=paddle_text,
                image_base64=image_base64
            )
            processing_time = time.time() - start_time

            if result.get('success'):
                raw_text = result.get('raw_response', '')

                # Try to parse JSON from raw text
                parsed_data = {}
                try:
                    # First try: direct JSON parse
                    if raw_text.strip().startswith('{'):
                        parsed_data = json.loads(raw_text)
                    else:
                        # Second try: extract JSON from markdown code blocks
                        import re
                        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw_text, re.DOTALL)
                        if json_match:
                            parsed_data = json.loads(json_match.group(1))
                        else:
                            # Third try: find any JSON object in the text
                            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', raw_text, re.DOTALL)
                            if json_match:
                                parsed_data = json.loads(json_match.group(0))
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON decode error in hybrid result: {e}")
                    parsed_data = {}
                except Exception as e:
                    logger.warning(f"Failed to parse hybrid JSON: {e}")
                    parsed_data = {}

                # Pretty print JSON
                try:
                    json_str = json.dumps(parsed_data, indent=2, ensure_ascii=False) if parsed_data else '{}'
                except:
                    json_str = '{}'

                # Count extracted fields
                fields_count = self._count_extracted_fields(parsed_data)

                # Extract findings from both parsed data AND raw text
                findings_from_parsed = self._analyze_key_findings_from_parsed(parsed_data)
                findings_from_text = self._analyze_key_findings(raw_text)

                # Merge findings - prefer parsed data findings if available
                findings = {}
                for key in findings_from_text.keys():
                    if findings_from_parsed.get(key.replace('found_', '').replace('_', '')) or findings_from_parsed.get(key):
                        findings[key] = findings_from_parsed.get(key, findings_from_text[key])
                    else:
                        findings[key] = findings_from_text[key]

                return {
                    'status': 'success',
                    'parsed_json': json_str,
                    'text': raw_text,
                    'confidence': result.get('confidence', 0),
                    'char_count': len(raw_text),
                    'fields_extracted': fields_count,
                    'processing_time': processing_time,
                    'model_info': 'PaddleOCR + Llama 3.2-Vision',  # Model combination used
                    **findings
                }
            else:
                return {
                    'status': 'error',
                    'error': result.get('error', 'Unknown error'),
                    'char_count': 0,
                    'fields_extracted': 0
                }

        except Exception as e:
            logger.error(f"Hybrid analysis error: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'char_count': 0,
                'fields_extracted': 0
            }

    def _analyze_paddleocr(self, document) -> Dict:
        """Analyze using PaddleOCR (multilingual OCR with 80+ language support)"""
        try:
            from .paddleocr_service import PaddleOCRService

            # Check if already processed
            if hasattr(document, 'paddle_text') and document.paddle_text:
                text = document.paddle_text
                confidence = getattr(document, 'paddle_confidence', 0)
                findings = self._analyze_key_findings(text)

                return {
                    'status': 'success',
                    'text': text,
                    'confidence': confidence,
                    'char_count': len(text) if text else 0,
                    'word_count': len(text.split()) if text else 0,
                    'processing_time': 0,  # Already processed
                    **findings
                }

            # Initialize PaddleOCR service with PP-Structure support
            paddle = PaddleOCRService(lang='en', use_structure=True)

            if not paddle.is_available():
                return {
                    'status': 'not_available',
                    'text': '',
                    'confidence': 0,
                    'char_count': 0,
                    'word_count': 0,
                    'processing_time': 0,
                    'found_store': False,
                    'found_total': False,
                    'found_date': False,
                    'found_bottom': False,
                    'error': 'PaddleOCR library not installed',
                    'install_command': 'pip install paddleocr',
                    'install_with_structure': 'pip install "paddleocr[structure]"',
                    'note': 'Install PaddleOCR to enable this OCR method (80+ languages, layout analysis, table detection)'
                }

            # Try PP-Structure first if available
            start_time = time.time()
            text = None
            confidence = 0
            structure_result = None

            if paddle.is_structure_available():
                logger.info("Using PP-Structure for layout analysis")
                structure_result = paddle.analyze_structure(document.file_path.path)
                if structure_result.get('success'):
                    text = structure_result.get('text', '')
                    # Estimate confidence based on element detection
                    confidence = 85 if structure_result.get('element_count', 0) > 0 else 50
                    logger.info(f"PP-Structure found {structure_result.get('element_count', 0)} elements")
                else:
                    logger.warning(f"PP-Structure failed: {structure_result.get('error')}")

            # Fallback to basic OCR if structure analysis failed
            ocr_result = None
            if not text:
                logger.info("Using basic PaddleOCR (structure not available or failed)")
                ocr_result = paddle.get_text_with_layout(document.file_path.path)
                if ocr_result:
                    text = ocr_result if isinstance(ocr_result, str) else ocr_result.get('text', '')
                    confidence = ocr_result.get('confidence', 0) if isinstance(ocr_result, dict) else 0

            processing_time = time.time() - start_time

            if text:
                # Use PaddleOCR's built-in key findings if available
                # Otherwise fall back to generic text analysis
                if ocr_result and isinstance(ocr_result, dict):
                    # Check if PaddleOCR already extracted key findings
                    if ocr_result.get('found_store') or ocr_result.get('found_total'):
                        logger.info("Using PaddleOCR's intelligent key extraction")
                        findings = {
                            'found_store': ocr_result.get('found_store', False),
                            'store_name': ocr_result.get('store_name'),
                            'found_total': ocr_result.get('found_total', False),
                            'total_amount': ocr_result.get('total_amount'),
                            'found_date': ocr_result.get('found_date', False),
                            'date_time': ocr_result.get('date'),
                            'found_bottom': ocr_result.get('found_order', False),
                            'bottom_info': ocr_result.get('order_number') or ocr_result.get('tax_id')
                        }
                    else:
                        # Fallback to generic analysis
                        findings = self._analyze_key_findings(text)
                else:
                    # Generic text analysis
                    findings = self._analyze_key_findings(text)

                response = {
                    'status': 'success',
                    'text': text,
                    'confidence': confidence,
                    'char_count': len(text),
                    'word_count': len(text.split()),
                    'processing_time': processing_time,
                    **findings
                }

                # Add structure info if available
                if structure_result and structure_result.get('success'):
                    response['structure_info'] = {
                        'element_count': structure_result.get('element_count', 0),
                        'has_tables': structure_result.get('has_tables', False),
                        'has_figures': structure_result.get('has_figures', False)
                    }
                    response['note'] = f"PP-Structure: {structure_result.get('element_count', 0)} elements detected"

                return response
            else:
                return {
                    'status': 'error',
                    'error': 'PaddleOCR returned no text',
                    'char_count': 0,
                    'word_count': 0,
                'processing_time': 0
                }

        except ImportError as e:
            logger.warning(f"PaddleOCR import failed: {e}")
            return {
                'status': 'not_available',
                'text': '',
                'confidence': 0,
                'char_count': 0,
                'word_count': 0,
                'processing_time': 0,
                'found_store': False,
                'found_total': False,
                'found_date': False,
                'found_bottom': False,
                'error': 'PaddleOCR library not installed',
                'install_command': 'pip install paddleocr',
                'install_with_structure': 'pip install "paddleocr[structure]"',
                'note': 'Install PaddleOCR to enable this OCR method (80+ languages, layout analysis, table detection)'
            }
        except Exception as e:
            logger.error(f"PaddleOCR analysis error: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'char_count': 0,
                'word_count': 0,
            'processing_time': 0
            }

    def _analyze_key_findings(self, text: str) -> Dict:
        """Analyze text for key receipt elements and extract values"""
        import re

        if not text:
            return {
                'found_store': False,
                'store_name': None,
                'found_total': False,
                'total_amount': None,
                'found_date': False,
                'date_time': None,
                'found_bottom': False,
                'bottom_info': None
            }

        text_lower = text.lower()
        lines = text.split('\n')

        # Extract store name (usually in first few lines)
        # Enhanced to handle OCR errors and common Turkish brands
        store_name = None
        store_keywords = [
            'mcdonald', 'migros', 'a101', 'bim', 'carrefour', 'market', 'store',
            'yemek', 'sepet', 'getir', 'trendyol'  # Online food delivery brands
        ]
        for line in lines[:10]:  # Check first 10 lines (increased from 5)
            line_clean = line.strip()
            # More flexible matching - accept lines with 2+ chars that contain keywords
            if line_clean and len(line_clean) >= 2:
                if any(kw in line_clean.lower() for kw in store_keywords):
                    store_name = line_clean
                    break
                # Also check for consecutive capital letters (brand names)
                if len(line_clean) > 4 and sum(1 for c in line_clean if c.isupper()) > len(line_clean) * 0.5:
                    store_name = line_clean
                    break

        # Extract total amount - Enhanced patterns for Turkish format
        total_amount = None
        total_patterns = [
            r'toplam[:\s]*[₺®&]?\s*(\d+[.,]\d+)',  # "Toplam ₺ 240,00" or "Toplam 240,00"
            r'total[:\s]*[₺®&]?\s*(\d+[.,]\d+)',   # English variant
            r'ara\s*toplam[:\s]*[₺®&]?\s*(\d+[.,]\d+)',  # Ara toplam
            r'[₺®&]\s*(\d+[.,]\d+)',  # Just currency symbol + amount (® is OCR error for ₺)
            r'(\d+[.,]\d+)\s*[₺®&€¢]'  # Amount + currency (¢ and € are OCR errors)
        ]
        for pattern in total_patterns:
            match = re.search(pattern, text_lower)
            if match:
                # Get the captured amount, clean it up
                total_amount = match.group(1).replace(',', '.')
                break

        # Extract date/time - Enhanced for Turkish month names
        date_time = None
        date_patterns = [
            r'\d{1,2}\s+(?:ocak|şubat|mart|nisan|mayıs|haziran|temmuz|ağustos|eylül|ekim|kasım|aralık|ocak)\s+\d{4}',  # "14 Haziran 2024"
            r'\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}',  # DD/MM/YYYY HH:MM
            r'\d{2}-\d{2}-\d{4}\s+\d{2}:\d{2}',  # DD-MM-YYYY HH:MM
            r'\d{1,2}\s+[a-zğüşıöçA-ZĞÜŞİÖÇ]+\s+\d{4}',  # "14 Haziran 2024" (flexible)
            r'\d{2}/\d{2}/\d{4}',  # DD/MM/YYYY
            r'\d{2}-\d{2}-\d{4}',  # DD-MM-YYYY
            r'20\d{2}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}:\d{2}',  # Just time HH:MM
        ]
        for pattern in date_patterns:
            match = re.search(pattern, text_lower)
            if match:
                date_time = match.group(0)
                break

        # Extract bottom info (MERSIS, EKÜ, Sipariş No, etc.)
        bottom_info = []
        bottom_patterns = [
            (r'mersis\s*:?\s*(\d+[\d\s-]+)', 'MERSIS'),
            (r'ekü\s*:?\s*([\w\d]+)', 'EKÜ'),
            (r'ecu\s*:?\s*([\w\d]+)', 'ECU'),
            (r'mf\s*:?\s*([\w\d]+)', 'MF'),
            (r'vergi\s*(?:no|numarası)[:\s]*([\d\s-]+)', 'Tax No'),
            (r'sipari[şs]\s*no\.?\s*:?\s*([\w\d-]+)', 'Order No'),  # "Sipariş No."
            (r'#(\d+)', 'Order #'),  # Order number like "#1513"
        ]
        for pattern, label in bottom_patterns:
            match = re.search(pattern, text_lower)
            if match:
                value = match.group(1).strip()
                bottom_info.append(f"{label}: {value}")

        bottom_info_str = ' | '.join(bottom_info) if bottom_info else None

        return {
            'found_store': bool(store_name),
            'store_name': store_name,
            'found_total': bool(total_amount),
            'total_amount': total_amount,
            'found_date': bool(date_time),
            'date_time': date_time,
            'found_bottom': bool(bottom_info_str),
            'bottom_info': bottom_info_str
        }

    def _analyze_key_findings_from_parsed(self, parsed_data: Dict) -> Dict:
        """Analyze parsed JSON data for key findings and extract values"""
        if not parsed_data:
            return {
                'found_store': False,
                'store_name': None,
                'found_total': False,
                'total_amount': None,
                'found_date': False,
                'date_time': None,
                'found_bottom': False,
                'bottom_info': None
            }

        # Extract store name - check multiple possible keys
        store_name = None
        store_keys = ['store_name', 'merchant', 'vendor', 'business_name']
        for key in store_keys:
            if parsed_data.get(key):
                store_name = parsed_data[key]
                break

        # Also check nested store_info
        if not store_name and parsed_data.get('store_info'):
            store_info = parsed_data['store_info']
            if isinstance(store_info, dict):
                store_name = store_info.get('name')

        # Extract total amount - check multiple possible keys
        total_amount = None
        total_keys = ['total', 'amount', 'total_amount', 'grand_total']
        for key in total_keys:
            if parsed_data.get(key):
                total_amount = parsed_data[key]
                break

        # Also check nested financial data
        if not total_amount and parsed_data.get('financial'):
            financial = parsed_data['financial']
            if isinstance(financial, dict):
                total_amount = financial.get('total')

        # Convert to string if numeric
        if isinstance(total_amount, (int, float)):
            total_amount = str(total_amount)

        # Extract date/time - check multiple possible keys
        date_time = None
        date_keys = ['date', 'transaction_date', 'timestamp', 'datetime']
        for key in date_keys:
            if parsed_data.get(key):
                date_time = parsed_data[key]
                break

        # Also check nested transaction data
        if not date_time and parsed_data.get('transaction'):
            transaction = parsed_data['transaction']
            if isinstance(transaction, dict):
                date_val = transaction.get('date')
                time_val = transaction.get('time')
                if date_val and time_val:
                    date_time = f"{date_val} {time_val}"
                elif date_val:
                    date_time = date_val

        # Extract bottom info (receipt number, order number, etc.)
        bottom_parts = []

        # Check for receipt/order numbers
        receipt_no = None
        if parsed_data.get('transaction') and isinstance(parsed_data['transaction'], dict):
            receipt_no = parsed_data['transaction'].get('receipt_no')
        if not receipt_no:
            receipt_no = parsed_data.get('receipt_number') or parsed_data.get('order_number')

        if receipt_no:
            bottom_parts.append(f"Order No: {receipt_no}")

        # Check for tax/business identifiers
        if parsed_data.get('mersis'):
            bottom_parts.append(f"MERSIS: {parsed_data['mersis']}")

        if parsed_data.get('store_info') and isinstance(parsed_data['store_info'], dict):
            store_info = parsed_data['store_info']
            if store_info.get('tax_id'):
                bottom_parts.append(f"Tax: {store_info['tax_id']}")

        if parsed_data.get('tax_number'):
            bottom_parts.append(f"Tax: {parsed_data['tax_number']}")

        if parsed_data.get('fiscal_id'):
            bottom_parts.append(f"Fiscal ID: {parsed_data['fiscal_id']}")

        if parsed_data.get('ekü') or parsed_data.get('ecu'):
            ecu_val = parsed_data.get('ekü') or parsed_data.get('ecu')
            bottom_parts.append(f"EKÜ: {ecu_val}")

        bottom_info = ' | '.join(bottom_parts) if bottom_parts else None

        return {
            'found_store': bool(store_name),
            'store_name': store_name,
            'found_total': bool(total_amount),
            'total_amount': total_amount,
            'found_date': bool(date_time),
            'date_time': date_time,
            'found_bottom': bool(bottom_info),
            'bottom_info': bottom_info
        }

    def _count_extracted_fields(self, parsed_data: Dict) -> int:
        """Count non-empty fields in parsed data"""
        if not parsed_data:
            return 0

        count = 0
        for key, value in parsed_data.items():
            if value and value not in [None, '', [], {}]:
                count += 1

        return count

    def _load_image_as_base64(self, image_path: str, preprocess_for_vision: bool = True) -> Optional[str]:
        """
        Load image file and convert to base64

        Args:
            image_path: Path to image file
            preprocess_for_vision: If True, preprocess image for vision models (RGB, resize, padding)

        Includes comprehensive error handling for file access issues
        """
        try:
            import os
            from PIL import Image
            import io

            # Check if file exists
            if not os.path.exists(image_path):
                logger.error(f"Image file does not exist: {image_path}")
                return None

            # Check if file is readable
            if not os.access(image_path, os.R_OK):
                logger.error(f"Image file is not readable: {image_path}")
                return None

            # Check file size (warn if > 10MB)
            file_size = os.path.getsize(image_path)
            if file_size > 10 * 1024 * 1024:  # 10MB
                logger.warning(f"Large image file ({file_size / 1024 / 1024:.1f}MB): {image_path}")

            if preprocess_for_vision:
                # Preprocess image for vision models (GPT recommendations + pad-to-square)
                img = Image.open(image_path)
                logger.info(f"Original image: {img.size}, mode: {img.mode}")

                # Convert to RGB if needed
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                    logger.info("Converted image to RGB")

                # Step 1: Resize to optimal dimensions for vision models
                # Reduced size for faster processing: max 800px on longest side
                width, height = img.size
                long_side = max(width, height)

                # Scale down if too large
                if long_side > 800:
                    scale = 800 / long_side
                    new_width = int(width * scale)
                    new_height = int(height * scale)
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    logger.info(f"Resized image to {img.size}")
                    width, height = img.size

                # Step 2: Pad to square for better vision model performance
                # This prevents aspect ratio distortion and improves OCR accuracy
                target_size = max(width, height)

                # Create a white canvas
                padded_img = Image.new('RGB', (target_size, target_size), (255, 255, 255))

                # Calculate padding to center the image
                x_offset = (target_size - width) // 2
                y_offset = (target_size - height) // 2

                # Paste the original image onto the canvas
                padded_img.paste(img, (x_offset, y_offset))
                logger.info(f"Padded image to square: {padded_img.size}")

                # Save to bytes with optimized quality (faster processing)
                buffer = io.BytesIO()
                padded_img.save(buffer, format='JPEG', quality=85)
                image_data = buffer.getvalue()
                logger.info(f"Preprocessed image size: {len(image_data)} bytes")
            else:
                # Read raw image data
                with open(image_path, 'rb') as f:
                    image_data = f.read()

            if not image_data:
                logger.error(f"Image file is empty: {image_path}")
                return None

            return base64.b64encode(image_data).decode('utf-8')

        except PermissionError as e:
            logger.error(f"Permission denied reading image {image_path}: {e}")
            return None
        except IOError as e:
            logger.error(f"IO error reading image {image_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error loading image {image_path}: {e}")
            return None

    def _analyze_trocr(self, document) -> Dict:
        """
        Analyze using TrOCR (Transformer OCR for difficult fonts)
        Uses hybrid approach: PaddleOCR for line detection + TrOCR for text recognition
        This provides much better results than processing the entire image at once
        """
        try:
            from .trocr_service import TrOCRService
            from .paddleocr_service import PaddleOCRService
            from PIL import Image

            trocr = TrOCRService(language='tr')
            if not trocr.is_available():
                return {
                    'status': 'error',
                    'error': 'TrOCR not available (pip install transformers torch)',
                    'char_count': 0,
                    'word_count': 0,
                'processing_time': 0
                }

            start_time = time.time()

            # Use PaddleOCR to detect text regions (bounding boxes)
            logger.info("TrOCR: Using PaddleOCR for line detection")
            paddle = PaddleOCRService(lang='en')
            if paddle.is_available():
                paddle.initialize_ocr()
                paddle_result = paddle.process_image(document.file_path.path)

                if paddle_result.get('success') and paddle_result.get('lines'):
                    lines = paddle_result['lines']
                    logger.info(f"TrOCR: Detected {len(lines)} text regions")

                    # Extract bounding boxes for TrOCR
                    regions = []
                    for line in lines:
                        bbox = line.get('bbox', [])
                        if bbox and len(bbox) >= 4:
                            # Convert PaddleOCR bbox format to (x1, y1, x2, y2)
                            x_coords = [p[0] for p in bbox]
                            y_coords = [p[1] for p in bbox]
                            x1, x2 = min(x_coords), max(x_coords)
                            y1, y2 = min(y_coords), max(y_coords)
                            regions.append((int(x1), int(y1), int(x2), int(y2)))

                    # Process regions with TrOCR
                    result = trocr.process_image_regions(document.file_path.path, regions)
                else:
                    logger.warning("TrOCR: PaddleOCR detection failed, falling back to full image")
                    result = trocr.process_image(document.file_path.path)
            else:
                logger.warning("TrOCR: PaddleOCR not available, using full image processing")
                result = trocr.process_image(document.file_path.path)

            processing_time = time.time() - start_time

            if result.get('success'):
                text = result.get('text', '')
                # Use extracted fields from TrOCR service (already using universal extractor)
                data = result.get('data', {})

                return {
                    'status': 'success',
                    'text': text,
                    'confidence': result.get('confidence', 0),
                    'char_count': len(text),
                    'word_count': len(text.split()),
                    'processing_time': processing_time,
                    'model_info': 'Microsoft TrOCR + PaddleOCR (hybrid)',
                    'store_name': data.get('store_name'),
                    'total_amount': data.get('total_amount'),
                    'date_time': data.get('date'),
                    'bottom_info': data.get('address'),
                    'found_store': data.get('found_store', False),
                    'found_total': data.get('found_total', False),
                    'found_date': data.get('found_date', False),
                    'found_bottom': bool(data.get('address')),
                    'data': data  # Include full data for field extraction
                }
            else:
                return {
                    'status': 'error',
                    'error': result.get('error', 'Unknown error'),
                    'char_count': 0,
                    'word_count': 0,
                'processing_time': 0
                }

        except Exception as e:
            logger.error(f"TrOCR analysis error: {e}")
            import traceback
            logger.error(f"TrOCR traceback: {traceback.format_exc()}")
            return {
                'status': 'error',
                'error': str(e),
                'char_count': 0,
                'word_count': 0,
            'processing_time': 0
            }

    def _analyze_donut(self, document) -> Dict:
        """Analyze using Donut (OCR-free document understanding)"""
        try:
            from .donut_service import DonutService

            donut = DonutService(language='tr')
            if not donut.is_available():
                return {
                    'status': 'error',
                    'error': 'Donut not available (pip install transformers torch)',
                    'char_count': 0,
                    'word_count': 0,
                'processing_time': 0
                }

            start_time = time.time()
            result = donut.process_receipt(document.file_path.path)
            processing_time = time.time() - start_time

            if result.get('success'):
                text = result.get('text', '')
                data = result.get('data', {})

                # Safety check: ensure data is a dict (Donut sometimes returns list)
                if not isinstance(data, dict):
                    logger.warning(f"_analyze_donut received non-dict data from DonutService: {type(data)}")
                    data = {}

                # Count extracted fields
                fields_count = sum([
                    1 for key in ['store_name', 'total_amount', 'date', 'time', 'address', 'phone', 'tax_id']
                    if data.get(key)
                ])
                fields_count += len(data.get('items', []))

                return {
                    'status': 'success',
                    'text': text,
                    'confidence': result.get('confidence', 0),
                    'char_count': len(text),
                    'word_count': len(text.split()),
                    'processing_time': processing_time,
                    'model_info': 'Donut (OCR-free)',
                    'fields_extracted': fields_count,
                    'store_name': data.get('store_name'),
                    'total_amount': data.get('total_amount'),
                    'date_time': data.get('date') or data.get('time'),
                    'bottom_info': data.get('address') or data.get('phone'),
                    'found_store': data.get('found_store', False),
                    'found_total': data.get('found_total', False),
                    'found_date': data.get('found_date', False) or data.get('found_time', False),
                    'found_bottom': bool(data.get('address') or data.get('phone'))
                }
            else:
                return {
                    'status': 'error',
                    'error': result.get('error', 'Unknown error'),
                    'char_count': 0,
                    'word_count': 0,
                'processing_time': 0
                }

        except Exception as e:
            logger.error(f"Donut analysis error: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'char_count': 0,
                'word_count': 0,
            'processing_time': 0
            }

    def _analyze_layoutlmv3(self, document) -> Dict:
        """Analyze using LayoutLMv3 (layout-aware extraction)"""
        try:
            from .layoutlmv3_service import LayoutLMv3Service

            layoutlm = LayoutLMv3Service(language='tr')
            if not layoutlm.is_available():
                return {
                    'status': 'error',
                    'error': 'LayoutLMv3 not available (pip install transformers torch)',
                    'char_count': 0,
                    'word_count': 0,
                'processing_time': 0
                }

            start_time = time.time()
            result = layoutlm.process_with_paddleocr(document.file_path.path)
            processing_time = time.time() - start_time

            if result.get('success'):
                text = result.get('text', '')
                fields = result.get('fields', {})

                return {
                    'status': 'success',
                    'text': text,
                    'confidence': result.get('confidence', 0),
                    'char_count': len(text),
                    'word_count': len(text.split()),
                    'processing_time': processing_time,
                    'model_info': 'LayoutLMv3 + PaddleOCR',
                    'store_name': fields.get('store_name'),
                    'total_amount': fields.get('total_amount'),
                    'date_time': fields.get('date') or fields.get('time'),
                    'bottom_info': fields.get('address') or fields.get('phone'),
                    'found_store': fields.get('found_store', False),
                    'found_total': fields.get('found_total', False),
                    'found_date': fields.get('found_date', False) or fields.get('found_time', False),
                    'found_bottom': bool(fields.get('address') or fields.get('phone'))
                }
            else:
                return {
                    'status': 'error',
                    'error': result.get('error', 'Unknown error'),
                    'char_count': 0,
                    'word_count': 0,
                'processing_time': 0
                }

        except Exception as e:
            logger.error(f"LayoutLMv3 analysis error: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'char_count': 0,
                'word_count': 0,
            'processing_time': 0
            }

    def _analyze_surya(self, document) -> Dict:
        """Analyze using Surya OCR (all-in-one solution with 90+ language support)"""
        try:
            from .surya_service import SuryaOCRService

            surya = SuryaOCRService()

            # Check if Surya is available
            if not surya.is_available():
                return {
                    'status': 'error',
                    'error': 'Surya OCR not installed. Install with: pip install surya-ocr',
                    'char_count': 0,
                    'word_count': 0,
                    'processing_time': 0
                }

            start_time = time.time()
            result = surya.process_image(document.file_path.path)
            processing_time = time.time() - start_time

            if result.get('success'):
                text = result.get('text', '')
                key_findings = result.get('key_findings', {})
                metrics = result.get('metrics', {})

                return {
                    'status': 'success',
                    'text': text,
                    'confidence': result.get('confidence', 0),
                    'char_count': metrics.get('character_count', len(text)),
                    'word_count': metrics.get('word_count', len(text.split())),
                    'processing_time': processing_time,
                    'model_info': 'Surya OCR (90+ languages)',
                    'lines_detected': result.get('lines_detected', 0),
                    'store_name': key_findings.get('store_name'),
                    'total_amount': key_findings.get('total_amount'),
                    'date_time': key_findings.get('date'),
                    'bottom_info': key_findings.get('bottom_info'),
                    'found_store': bool(key_findings.get('store_name')),
                    'found_total': bool(key_findings.get('total_amount')),
                    'found_date': bool(key_findings.get('date')),
                    'found_bottom': bool(key_findings.get('bottom_info'))
                }
            else:
                return {
                    'status': 'error',
                    'error': result.get('error', 'Unknown error'),
                    'char_count': 0,
                    'word_count': 0,
                'processing_time': 0
                }

        except Exception as e:
            logger.error(f"Surya OCR analysis error: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'char_count': 0,
                'word_count': 0,
            'processing_time': 0
            }

    def _analyze_doctr(self, document) -> Dict:
        """Analyze using DocTR (modern PyTorch-based OCR)"""
        try:
            from .doctr_service import DocTROCRService

            doctr = DocTROCRService()
            start_time = time.time()
            result = doctr.process_image(document.file_path.path)
            processing_time = time.time() - start_time

            if result.get('success'):
                text = result.get('text', '')
                key_findings = result.get('key_findings', {})
                metrics = result.get('metrics', {})

                return {
                    'status': 'success',
                    'text': text,
                    'confidence': result.get('confidence', 0),
                    'char_count': metrics.get('character_count', len(text)),
                    'word_count': result.get('words_detected', len(text.split())),
                    'processing_time': processing_time,
                    'model_info': 'DocTR (DB-ResNet50 + CRNN-VGG16)',
                    'store_name': key_findings.get('store_name'),
                    'total_amount': key_findings.get('total_amount'),
                    'date_time': key_findings.get('date'),
                    'bottom_info': key_findings.get('bottom_info'),
                    'found_store': bool(key_findings.get('store_name')),
                    'found_total': bool(key_findings.get('total_amount')),
                    'found_date': bool(key_findings.get('date')),
                    'found_bottom': bool(key_findings.get('bottom_info'))
                }
            else:
                return {
                    'status': 'error',
                    'error': result.get('error', 'Unknown error'),
                    'char_count': 0,
                    'word_count': 0,
                'processing_time': 0
                }

        except Exception as e:
            logger.error(f"DocTR analysis error: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'char_count': 0,
                'word_count': 0,
            'processing_time': 0
            }

    def _analyze_easyocr(self, document) -> Dict:
        """Analyze using EasyOCR (multilingual fallback OCR)"""
        try:
            from .easyocr_service import EasyOCRService

            easyocr = EasyOCRService()
            start_time = time.time()
            result = easyocr.process_image(document.file_path.path)
            processing_time = time.time() - start_time

            if result.get('success'):
                text = result.get('text', '')
                key_findings = result.get('key_findings', {})
                metrics = result.get('metrics', {})

                return {
                    'status': 'success',
                    'text': text,
                    'confidence': result.get('confidence', 0),
                    'char_count': metrics.get('character_count', len(text)),
                    'word_count': metrics.get('word_count', len(text.split())),
                    'processing_time': processing_time,
                    'model_info': 'EasyOCR (EN/TR)',
                    'detections': result.get('detections', 0),
                    'store_name': key_findings.get('store_name'),
                    'total_amount': key_findings.get('total_amount'),
                    'date_time': key_findings.get('date'),
                    'bottom_info': key_findings.get('bottom_info'),
                    'found_store': bool(key_findings.get('store_name')),
                    'found_total': bool(key_findings.get('total_amount')),
                    'found_date': bool(key_findings.get('date')),
                    'found_bottom': bool(key_findings.get('bottom_info'))
                }
            else:
                return {
                    'status': 'error',
                    'error': result.get('error', 'Unknown error'),
                    'char_count': 0,
                    'word_count': 0,
                'processing_time': 0
                }

        except Exception as e:
            logger.error(f"EasyOCR analysis error: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'char_count': 0,
                'word_count': 0,
            'processing_time': 0
            }

    def _analyze_ocrmypdf(self, document) -> Dict:
        """Analyze using OCRMyPDF (PDF-optimized OCR with Tesseract backend)"""
        try:
            from .ocrmypdf_service import OCRMyPDFService

            ocrmypdf = OCRMyPDFService()
            start_time = time.time()
            result = ocrmypdf.process_image(document.file_path.path)
            processing_time = time.time() - start_time

            if result.get('success'):
                text = result.get('text', '')
                key_findings = result.get('key_findings', {})
                metrics = result.get('metrics', {})

                return {
                    'status': 'success',
                    'text': text,
                    'confidence': result.get('confidence', 0),
                    'char_count': metrics.get('character_count', len(text)),
                    'word_count': metrics.get('word_count', len(text.split())),
                    'processing_time': processing_time,
                    'model_info': result.get('backend', 'OCRMyPDF + Tesseract'),
                    'store_name': key_findings.get('store_name'),
                    'total_amount': key_findings.get('total_amount'),
                    'date_time': key_findings.get('date'),
                    'bottom_info': key_findings.get('bottom_info'),
                    'found_store': bool(key_findings.get('store_name')),
                    'found_total': bool(key_findings.get('total_amount')),
                    'found_date': bool(key_findings.get('date')),
                    'found_bottom': bool(key_findings.get('bottom_info'))
                }
            else:
                return {
                    'status': 'error',
                    'error': result.get('error', 'Unknown error'),
                    'char_count': 0,
                    'word_count': 0,
                'processing_time': 0
                }

        except Exception as e:
            logger.error(f"OCRMyPDF analysis error: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'char_count': 0,
                'word_count': 0,
            'processing_time': 0
            }
