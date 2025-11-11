#!/usr/bin/env python
"""
Claude Vision vs OCR Methods Comparison
Compares Claude's vision analysis with implemented OCR methods on selected documents
"""

import os
import sys
import django
import base64
import json
from typing import Dict, List
import anthropic

# Setup Django
sys.path.insert(0, '/Users/berkhatirli/Desktop/unibos/apps/web/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unibos_backend.settings.development')
django.setup()

from modules.documents.backend.models import Document
from modules.documents.backend.analysis_service import OCRAnalysisService

# Initialize Anthropic client
client = anthropic.Anthropic()


def analyze_with_claude_vision(image_path: str, filename: str) -> Dict:
    """
    Analyze document using Claude's vision API

    Args:
        image_path: Path to image file
        filename: Original filename for context

    Returns:
        Dictionary with Claude's analysis
    """
    print(f"  Analyzing with Claude Vision...")

    try:
        # Read and encode image
        with open(image_path, 'rb') as f:
            image_data = base64.standard_b64encode(f.read()).decode('utf-8')

        # Detect image type
        ext = os.path.splitext(image_path)[1].lower()
        media_type_map = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.webp': 'image/webp',
            '.gif': 'image/gif'
        }
        media_type = media_type_map.get(ext, 'image/jpeg')

        # Prompt for receipt analysis
        prompt = """Analyze this receipt/document image and extract the following information in JSON format:

{
    "store_name": "Name of store/merchant",
    "total_amount": "Total amount as number (e.g., 240.00)",
    "currency": "Currency symbol or code (e.g., TL, ₺, USD)",
    "date": "Date in any format found",
    "order_number": "Order/receipt number if present",
    "items": ["List of items purchased if visible"],
    "tax_id": "Tax ID or MERSIS number if present",
    "confidence": "Your confidence level (low/medium/high)",
    "notes": "Any important observations about document quality, language, or special features"
}

If you cannot find certain fields, use null for that field. Focus on Turkish receipts (common stores: Yemeksepeti, Migros, A101, BIM, Getir, etc.)."""

        # Call Claude API
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ],
                }
            ],
        )

        # Extract response text
        response_text = message.content[0].text

        # Try to parse JSON from response
        try:
            # Find JSON in response (might be wrapped in markdown code blocks)
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1

            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                parsed_data = json.loads(json_str)
            else:
                parsed_data = {"raw_response": response_text}
        except json.JSONDecodeError:
            parsed_data = {"raw_response": response_text}

        return {
            'success': True,
            'method': 'claude_vision',
            'data': parsed_data,
            'raw_response': response_text,
            'tokens_used': message.usage.input_tokens + message.usage.output_tokens
        }

    except Exception as e:
        return {
            'success': False,
            'method': 'claude_vision',
            'error': str(e)
        }


def analyze_with_ocr_methods(document: Document) -> Dict:
    """
    Analyze document with all OCR methods

    Args:
        document: Document model instance

    Returns:
        Dictionary with results from all OCR methods
    """
    print(f"  Analyzing with OCR methods...")

    analysis_service = OCRAnalysisService(use_cache=False)

    try:
        results = analysis_service.analyze_document(document, force_refresh=True)
        return {
            'success': True,
            'results': results
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def compare_results(claude_result: Dict, ocr_results: Dict, doc_info: Dict) -> Dict:
    """
    Compare Claude vision results with OCR methods

    Args:
        claude_result: Claude vision analysis result
        ocr_results: OCR methods analysis results
        doc_info: Document information

    Returns:
        Comparison dictionary
    """
    comparison = {
        'document': doc_info,
        'claude_vision': claude_result,
        'ocr_methods': {},
        'field_comparison': {},
        'accuracy_scores': {}
    }

    if not claude_result.get('success') or not ocr_results.get('success'):
        return comparison

    # Extract Claude's findings
    claude_data = claude_result.get('data', {})
    claude_store = claude_data.get('store_name')
    claude_total = claude_data.get('total_amount')
    claude_date = claude_data.get('date')
    claude_order = claude_data.get('order_number')

    # Compare with each OCR method
    ocr_data = ocr_results.get('results', {})

    for method in ['tesseract', 'paddleocr', 'hybrid', 'minicpm']:
        method_result = ocr_data.get(method, {})

        if method_result.get('status') != 'success':
            comparison['ocr_methods'][method] = {'status': 'error'}
            continue

        # Extract OCR findings
        ocr_store = method_result.get('store_name')
        ocr_total = method_result.get('total_amount')
        ocr_date = method_result.get('date_time')
        ocr_order = method_result.get('bottom_info')

        # Store OCR results
        comparison['ocr_methods'][method] = {
            'status': 'success',
            'confidence': method_result.get('confidence', 0),
            'store_name': ocr_store,
            'total_amount': ocr_total,
            'date': ocr_date,
            'order_number': ocr_order,
            'found_store': method_result.get('found_store', False),
            'found_total': method_result.get('found_total', False),
            'found_date': method_result.get('found_date', False)
        }

        # Calculate similarity scores
        scores = {
            'store_match': 0,
            'total_match': 0,
            'date_match': 0,
            'order_match': 0
        }

        # Store name comparison
        if claude_store and ocr_store:
            if claude_store.lower() in ocr_store.lower() or ocr_store.lower() in claude_store.lower():
                scores['store_match'] = 1
            elif any(word in ocr_store.lower() for word in claude_store.lower().split()):
                scores['store_match'] = 0.5

        # Total amount comparison
        if claude_total and ocr_total:
            try:
                claude_amount = float(str(claude_total).replace(',', '.'))
                ocr_amount = float(str(ocr_total).replace(',', '.'))
                if abs(claude_amount - ocr_amount) < 0.01:
                    scores['total_match'] = 1
                elif abs(claude_amount - ocr_amount) < 1.0:
                    scores['total_match'] = 0.5
            except (ValueError, TypeError):
                pass

        # Date comparison (simple substring check)
        if claude_date and ocr_date:
            if str(claude_date).lower() in str(ocr_date).lower() or str(ocr_date).lower() in str(claude_date).lower():
                scores['date_match'] = 1
            elif any(part in str(ocr_date).lower() for part in str(claude_date).lower().split()):
                scores['date_match'] = 0.5

        # Order number comparison
        if claude_order and ocr_order:
            if str(claude_order).lower() in str(ocr_order).lower() or str(ocr_order).lower() in str(claude_order).lower():
                scores['order_match'] = 1

        # Overall accuracy score
        total_score = sum(scores.values())
        max_score = 4  # 4 fields
        accuracy = (total_score / max_score) * 100

        comparison['accuracy_scores'][method] = {
            'overall': accuracy,
            'details': scores
        }

    # Field-by-field comparison
    comparison['field_comparison'] = {
        'store_name': {
            'claude': claude_store,
            'tesseract': comparison['ocr_methods'].get('tesseract', {}).get('store_name'),
            'paddleocr': comparison['ocr_methods'].get('paddleocr', {}).get('store_name'),
            'hybrid': comparison['ocr_methods'].get('hybrid', {}).get('store_name'),
            'minicpm': comparison['ocr_methods'].get('minicpm', {}).get('store_name')
        },
        'total_amount': {
            'claude': claude_total,
            'tesseract': comparison['ocr_methods'].get('tesseract', {}).get('total_amount'),
            'paddleocr': comparison['ocr_methods'].get('paddleocr', {}).get('total_amount'),
            'hybrid': comparison['ocr_methods'].get('hybrid', {}).get('total_amount'),
            'minicpm': comparison['ocr_methods'].get('minicpm', {}).get('total_amount')
        },
        'date': {
            'claude': claude_date,
            'tesseract': comparison['ocr_methods'].get('tesseract', {}).get('date'),
            'paddleocr': comparison['ocr_methods'].get('paddleocr', {}).get('date'),
            'hybrid': comparison['ocr_methods'].get('hybrid', {}).get('date'),
            'minicpm': comparison['ocr_methods'].get('minicpm', {}).get('date')
        },
        'order_number': {
            'claude': claude_order,
            'tesseract': comparison['ocr_methods'].get('tesseract', {}).get('order_number'),
            'paddleocr': comparison['ocr_methods'].get('paddleocr', {}).get('order_number'),
            'hybrid': comparison['ocr_methods'].get('hybrid', {}).get('order_number'),
            'minicpm': comparison['ocr_methods'].get('minicpm', {}).get('order_number')
        }
    }

    return comparison


def generate_report(all_comparisons: List[Dict]) -> str:
    """
    Generate comprehensive comparison report

    Args:
        all_comparisons: List of comparison dictionaries for all documents

    Returns:
        Formatted report string
    """
    report = []
    report.append("=" * 100)
    report.append("CLAUDE VISION vs OCR METHODS - COMPREHENSIVE COMPARISON REPORT")
    report.append("=" * 100)
    report.append("")

    # Overall statistics
    report.append("## OVERALL STATISTICS")
    report.append("-" * 100)

    total_docs = len(all_comparisons)
    method_scores = {'tesseract': [], 'paddleocr': [], 'hybrid': [], 'minicpm': []}

    for comp in all_comparisons:
        for method, score_data in comp.get('accuracy_scores', {}).items():
            if method in method_scores:
                method_scores[method].append(score_data.get('overall', 0))

    report.append(f"Total documents analyzed: {total_docs}")
    report.append("")

    for method, scores in method_scores.items():
        if scores:
            avg_score = sum(scores) / len(scores)
            max_score = max(scores)
            min_score = min(scores)
            report.append(f"{method.upper():12s}: Avg={avg_score:5.1f}% | Max={max_score:5.1f}% | Min={min_score:5.1f}%")

    report.append("")
    report.append("")

    # Document-by-document analysis
    for idx, comp in enumerate(all_comparisons, 1):
        doc_info = comp.get('document', {})

        report.append("=" * 100)
        report.append(f"DOCUMENT {idx}/{total_docs}: {doc_info.get('filename', 'Unknown')}")
        report.append("=" * 100)
        report.append(f"ID: {doc_info.get('id')}")
        report.append(f"Path: {doc_info.get('path')}")
        report.append("")

        # Claude Vision Results
        claude_result = comp.get('claude_vision', {})
        report.append("### CLAUDE VISION ANALYSIS")
        report.append("-" * 100)

        if claude_result.get('success'):
            claude_data = claude_result.get('data', {})
            report.append(f"Store Name    : {claude_data.get('store_name', 'N/A')}")
            report.append(f"Total Amount  : {claude_data.get('total_amount', 'N/A')} {claude_data.get('currency', '')}")
            report.append(f"Date          : {claude_data.get('date', 'N/A')}")
            report.append(f"Order Number  : {claude_data.get('order_number', 'N/A')}")
            report.append(f"Confidence    : {claude_data.get('confidence', 'N/A')}")
            report.append(f"Tokens Used   : {claude_result.get('tokens_used', 'N/A')}")
            if claude_data.get('notes'):
                report.append(f"Notes         : {claude_data.get('notes')}")
        else:
            report.append(f"ERROR: {claude_result.get('error', 'Unknown error')}")

        report.append("")

        # OCR Methods Results
        report.append("### OCR METHODS COMPARISON")
        report.append("-" * 100)

        accuracy_scores = comp.get('accuracy_scores', {})

        for method in ['tesseract', 'paddleocr', 'hybrid', 'minicpm']:
            method_data = comp.get('ocr_methods', {}).get(method, {})

            if method_data.get('status') == 'success':
                score = accuracy_scores.get(method, {})
                overall = score.get('overall', 0)
                details = score.get('details', {})

                status_icon = '🏆' if overall >= 75 else '✅' if overall >= 50 else '⚠️' if overall >= 25 else '❌'

                report.append(f"{status_icon} {method.upper():12s} | Accuracy: {overall:5.1f}% | OCR Conf: {method_data.get('confidence', 0):5.1f}%")
                report.append(f"   Store: {method_data.get('store_name', 'N/A'):30s} (match: {details.get('store_match', 0)*100:3.0f}%)")
                report.append(f"   Total: {str(method_data.get('total_amount', 'N/A')):30s} (match: {details.get('total_match', 0)*100:3.0f}%)")
                report.append(f"   Date:  {str(method_data.get('date', 'N/A')):30s} (match: {details.get('date_match', 0)*100:3.0f}%)")
                report.append(f"   Order: {str(method_data.get('order_number', 'N/A')):30s} (match: {details.get('order_match', 0)*100:3.0f}%)")
            else:
                report.append(f"❌ {method.upper():12s} | ERROR")

            report.append("")

        # Best & Worst performing methods for this document
        if accuracy_scores:
            sorted_methods = sorted(accuracy_scores.items(), key=lambda x: x[1].get('overall', 0), reverse=True)
            best_method = sorted_methods[0]
            worst_method = sorted_methods[-1]

            report.append("### PERFORMANCE SUMMARY")
            report.append("-" * 100)
            report.append(f"🏆 Best Method : {best_method[0].upper()} ({best_method[1].get('overall', 0):.1f}%)")
            report.append(f"⚠️  Worst Method: {worst_method[0].upper()} ({worst_method[1].get('overall', 0):.1f}%)")

        report.append("")
        report.append("")

    # Summary and Recommendations
    report.append("=" * 100)
    report.append("SUMMARY & RECOMMENDATIONS")
    report.append("=" * 100)
    report.append("")

    # Calculate average scores
    avg_scores = {}
    for method in ['tesseract', 'paddleocr', 'hybrid', 'minicpm']:
        scores = method_scores.get(method, [])
        if scores:
            avg_scores[method] = sum(scores) / len(scores)

    if avg_scores:
        sorted_avg = sorted(avg_scores.items(), key=lambda x: x[1], reverse=True)

        report.append("### METHOD RANKING (by average accuracy)")
        report.append("-" * 100)
        for rank, (method, score) in enumerate(sorted_avg, 1):
            icon = '🥇' if rank == 1 else '🥈' if rank == 2 else '🥉' if rank == 3 else '  '
            report.append(f"{icon} #{rank}. {method.upper():12s} - {score:5.1f}%")

        report.append("")
        report.append("### RECOMMENDATIONS")
        report.append("-" * 100)

        best_method = sorted_avg[0][0]
        best_score = sorted_avg[0][1]

        if best_score >= 75:
            report.append(f"✅ {best_method.upper()} is performing excellently (≥75% accuracy)")
            report.append(f"   → Recommended as primary OCR method")
        elif best_score >= 50:
            report.append(f"⚠️  {best_method.upper()} is performing adequately (50-75% accuracy)")
            report.append(f"   → Consider using Claude Vision as fallback for low-confidence results")
        else:
            report.append(f"❌ All methods scoring below 50% accuracy")
            report.append(f"   → Recommend using Claude Vision as primary method")
            report.append(f"   → Investigate OCR method improvements")

        report.append("")

        # Specific improvement suggestions
        report.append("### IMPROVEMENT SUGGESTIONS")
        report.append("-" * 100)

        for method, score in sorted_avg:
            if score < 75:
                report.append(f"{method.upper()}:")

                # Analyze common failure patterns
                method_failures = []
                for comp in all_comparisons:
                    method_data = comp.get('ocr_methods', {}).get(method, {})
                    scores = comp.get('accuracy_scores', {}).get(method, {}).get('details', {})

                    if scores.get('store_match', 0) < 1:
                        method_failures.append('store_name')
                    if scores.get('total_match', 0) < 1:
                        method_failures.append('total_amount')
                    if scores.get('date_match', 0) < 1:
                        method_failures.append('date')
                    if scores.get('order_match', 0) < 1:
                        method_failures.append('order_number')

                # Count failures
                from collections import Counter
                failure_counts = Counter(method_failures)

                if failure_counts:
                    most_common = failure_counts.most_common(2)
                    for field, count in most_common:
                        percentage = (count / total_docs) * 100
                        report.append(f"   - Improve {field} extraction ({percentage:.0f}% failure rate)")

                report.append("")

    report.append("")
    report.append("=" * 100)
    report.append("END OF REPORT")
    report.append("=" * 100)

    return "\n".join(report)


def main():
    """Main execution function"""
    print("\n" + "=" * 100)
    print("CLAUDE VISION vs OCR METHODS COMPARISON")
    print("=" * 100)
    print()

    # Load selected document IDs
    selected_docs = []
    with open('/tmp/selected_doc_ids.txt', 'r') as f:
        for line in f:
            doc_id, path, filename = line.strip().split(',')
            selected_docs.append({
                'id': doc_id,
                'path': path,
                'filename': filename
            })

    print(f"Analyzing {len(selected_docs)} documents...\n")

    all_comparisons = []

    for idx, doc_info in enumerate(selected_docs, 1):
        print(f"[{idx}/{len(selected_docs)}] Processing: {doc_info['filename']}")

        # Get Document instance
        try:
            document = Document.objects.get(id=doc_info['id'])
        except Document.DoesNotExist:
            print(f"  ERROR: Document not found in database")
            continue

        # Analyze with Claude Vision
        claude_result = analyze_with_claude_vision(doc_info['path'], doc_info['filename'])

        # Analyze with OCR methods
        ocr_results = analyze_with_ocr_methods(document)

        # Compare results
        comparison = compare_results(claude_result, ocr_results, doc_info)
        all_comparisons.append(comparison)

        print(f"  ✅ Analysis complete\n")

    # Generate report
    print("\nGenerating comparison report...")
    report = generate_report(all_comparisons)

    # Save report
    report_path = '/tmp/claude_vision_comparison_report.txt'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    # Save detailed JSON results
    json_path = '/tmp/claude_vision_comparison_data.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(all_comparisons, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n✅ Report saved to: {report_path}")
    print(f"✅ Detailed JSON saved to: {json_path}")
    print("\n" + "=" * 100)
    print("Displaying report:\n")
    print(report)


if __name__ == '__main__':
    main()
