#!/usr/bin/env python
"""
Test script for Quality-based OCR Router and JSON Guard
Tests the new GPT-recommended architecture improvements
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, '/Users/berkhatirli/Desktop/unibos/apps/web/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unibos_backend.settings.development')
django.setup()

from modules.documents.backend.models import Document
from modules.documents.backend.image_quality_service import ImageQualityService
from modules.documents.backend.analysis_service import OCRAnalysisService
import json


def test_quality_assessment():
    """Test image quality assessment"""
    print("=" * 80)
    print("TEST 1: Image Quality Assessment")
    print("=" * 80)

    # Get test document
    doc_id = '175a85f2-bdb9-4ad7-8b29-23b85a545364'
    document = Document.objects.get(id=doc_id)

    print(f"\nDocument: {document.original_filename}")
    print(f"File: {document.file_path.path}")

    # Assess quality
    quality_service = ImageQualityService()
    result = quality_service.assess_quality(document.file_path.path)

    if result.get('success'):
        print("\n✅ Quality Assessment Results:")
        print(f"  - Quality Level: {result['quality_level']}")
        print(f"  - Recommended OCR: {result['recommended_ocr']}")
        print(f"  - Blur Score: {result['blur_score']:.2f}")
        print(f"  - Contrast Score: {result['contrast_score']:.2f}")
        print(f"  - DPI: {result['dpi']}")
        print(f"  - Orientation: {result['orientation']}°")

        print("\n  Preprocessing Needed:")
        needs = result['preprocessing_needed']
        print(f"  - Deskew: {needs['deskew']}")
        print(f"  - Contrast Enhancement: {needs['contrast_enhancement']}")
        print(f"  - Denoising: {needs['denoising']}")
    else:
        print(f"\n❌ Quality assessment failed: {result.get('error')}")

    return result


def test_preprocessing():
    """Test image preprocessing"""
    print("\n" + "=" * 80)
    print("TEST 2: Image Preprocessing")
    print("=" * 80)

    doc_id = '175a85f2-bdb9-4ad7-8b29-23b85a545364'
    document = Document.objects.get(id=doc_id)

    quality_service = ImageQualityService()

    # Only preprocess if OpenCV is available
    if not quality_service.cv2_available:
        print("\n⚠️  OpenCV not available - skipping preprocessing test")
        return None

    result = quality_service.preprocess_image(document.file_path.path)

    if result.get('success'):
        print("\n✅ Preprocessing Results:")
        print(f"  - Original: {result['original_path']}")
        print(f"  - Preprocessed: {result['preprocessed_path']}")
        print(f"  - Applied: {', '.join(result['preprocessing_applied'])}")

        # Show quality improvements
        quality_before = result['quality_assessment']
        print(f"\n  Quality Before:")
        print(f"  - Blur: {quality_before['blur_score']:.2f}")
        print(f"  - Contrast: {quality_before['contrast_score']:.2f}")
    else:
        print(f"\n❌ Preprocessing failed: {result.get('error')}")

    return result


def test_json_guard():
    """Test JSON Guard with sample responses"""
    print("\n" + "=" * 80)
    print("TEST 3: JSON Guard Validation")
    print("=" * 80)

    from modules.documents.backend.ollama_service import OllamaService

    ollama = OllamaService()

    # Test cases for JSON Guard
    test_cases = [
        {
            'name': 'Valid JSON',
            'response': '{"store": "Yemeksepeti", "total": 240.00}',
            'expected': True
        },
        {
            'name': 'JSON with trailing comma',
            'response': '{"store": "Yemeksepeti", "total": 240.00,}',
            'expected': True
        },
        {
            'name': 'JSON with comments',
            'response': '{"store": "Yemeksepeti", // Brand name\n"total": 240.00}',
            'expected': True
        },
        {
            'name': 'JSON in text',
            'response': 'Here is the data: {"store": "Yemeksepeti", "total": 240.00} from the receipt.',
            'expected': True
        },
        {
            'name': 'Single quotes',
            'response': "{'store': 'Yemeksepeti', 'total': 240.00}",
            'expected': True
        },
        {
            'name': 'No JSON (plain text)',
            'response': 'The store is Yemeksepeti and the total is 240.00',
            'expected': False  # Will use structured text parser
        }
    ]

    for i, test in enumerate(test_cases, 1):
        print(f"\n  Test {i}: {test['name']}")
        print(f"  Input: {test['response'][:60]}...")

        try:
            result = ollama._parse_ollama_response(test['response'])

            if isinstance(result, dict) and result:
                print(f"  ✅ Parsed successfully")
                print(f"  Result: {json.dumps(result, indent=4)[:100]}...")
            else:
                print(f"  ⚠️  Parsed but empty/invalid")
        except Exception as e:
            print(f"  ❌ Failed: {e}")


def test_full_analysis():
    """Test complete OCR analysis with quality routing"""
    print("\n" + "=" * 80)
    print("TEST 4: Full OCR Analysis with Quality Routing")
    print("=" * 80)

    doc_id = '175a85f2-bdb9-4ad7-8b29-23b85a545364'
    document = Document.objects.get(id=doc_id)

    print(f"\nDocument: {document.original_filename}")

    # Run analysis with quality routing
    analysis_service = OCRAnalysisService(use_cache=False)  # Disable cache for testing
    results = analysis_service.analyze_document(document, force_refresh=True)

    print("\n✅ Analysis Complete!")

    # Show quality assessment
    if 'quality_assessment' in results:
        qa = results['quality_assessment']
        print(f"\n  Quality Assessment:")
        print(f"  - Level: {qa.get('quality_level', 'unknown')}")
        print(f"  - Recommended: {qa.get('recommended_ocr', 'unknown')}")
        print(f"  - Preprocessed: {results.get('preprocessed', False)}")

    # Show results for each method
    print(f"\n  OCR Results:")
    for method in ['tesseract', 'paddleocr', 'hybrid', 'minicpm']:
        method_result = results.get(method, {})
        status = method_result.get('status', 'unknown')
        confidence = method_result.get('confidence', 0)
        char_count = method_result.get('char_count', 0)

        status_icon = '✅' if status == 'success' else '❌' if status == 'error' else '⏳'
        print(f"  {status_icon} {method.upper():12s}: {status:10s} | Confidence: {confidence:5.1f}% | Chars: {char_count}")

        if status == 'success':
            # Show key findings
            if method_result.get('found_store'):
                print(f"      Store: {method_result.get('store_name', 'N/A')}")
            if method_result.get('found_total'):
                print(f"      Total: {method_result.get('total_amount', 'N/A')}")

    # Show best method
    best = results.get('best_method')
    if best:
        print(f"\n  🏆 Best Method: {best.upper()}")

    return results


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("QUALITY-BASED OCR ROUTER & JSON GUARD TEST SUITE")
    print("=" * 80)

    try:
        # Test 1: Quality Assessment
        quality_result = test_quality_assessment()

        # Test 2: Preprocessing (if OpenCV available)
        preprocessing_result = test_preprocessing()

        # Test 3: JSON Guard
        test_json_guard()

        # Test 4: Full Analysis
        analysis_result = test_full_analysis()

        print("\n" + "=" * 80)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
