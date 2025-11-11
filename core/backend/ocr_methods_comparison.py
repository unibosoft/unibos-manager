#!/usr/bin/env python
"""
OCR Methods Comparison
Compares all implemented OCR methods on selected documents
"""

import os
import sys
import django
import json
from typing import Dict, List
from collections import Counter

# Setup Django
sys.path.insert(0, '/Users/berkhatirli/Desktop/unibos/apps/web/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unibos_backend.settings.development')
django.setup()

from modules.documents.backend.models import Document
from modules.documents.backend.analysis_service import OCRAnalysisService


def analyze_document_with_all_methods(document: Document, doc_info: Dict) -> Dict:
    """
    Analyze document with all OCR methods

    Args:
        document: Document model instance
        doc_info: Document information

    Returns:
        Dictionary with results from all OCR methods
    """
    print(f"  Analyzing document...")

    analysis_service = OCRAnalysisService(use_cache=False)

    try:
        results = analysis_service.analyze_document(document, force_refresh=True)

        comparison = {
            'document': doc_info,
            'quality_assessment': results.get('quality_assessment', {}),
            'methods': {},
            'consensus': {},
            'best_method': None
        }

        # Extract results for each method
        for method in ['tesseract', 'paddleocr', 'hybrid', 'minicpm']:
            method_result = results.get(method, {})

            if method_result.get('status') == 'success':
                comparison['methods'][method] = {
                    'status': 'success',
                    'confidence': method_result.get('confidence', 0),
                    'char_count': method_result.get('char_count', 0),
                    'store_name': method_result.get('store_name'),
                    'total_amount': method_result.get('total_amount'),
                    'date': method_result.get('date_time'),
                    'order_number': method_result.get('bottom_info'),
                    'found_store': method_result.get('found_store', False),
                    'found_total': method_result.get('found_total', False),
                    'found_date': method_result.get('found_date', False),
                    'text_preview': method_result.get('text', '')[:200] if method_result.get('text') else None
                }
            else:
                comparison['methods'][method] = {
                    'status': 'error',
                    'error': method_result.get('error', 'Unknown error')
                }

        # Calculate consensus (most common values)
        store_names = [m.get('store_name') for m in comparison['methods'].values()
                      if m.get('status') == 'success' and m.get('store_name')]
        total_amounts = [m.get('total_amount') for m in comparison['methods'].values()
                        if m.get('status') == 'success' and m.get('total_amount')]
        dates = [m.get('date') for m in comparison['methods'].values()
                if m.get('status') == 'success' and m.get('date')]

        comparison['consensus'] = {
            'store_name': Counter(store_names).most_common(1)[0][0] if store_names else None,
            'total_amount': Counter(total_amounts).most_common(1)[0][0] if total_amounts else None,
            'date': Counter(dates).most_common(1)[0][0] if dates else None,
            'agreement_count': {
                'store': len([s for s in store_names if s == Counter(store_names).most_common(1)[0][0]]) if store_names else 0,
                'total': len([t for t in total_amounts if t == Counter(total_amounts).most_common(1)[0][0]]) if total_amounts else 0,
                'date': len([d for d in dates if d == Counter(dates).most_common(1)[0][0]]) if dates else 0
            }
        }

        # Determine best method (highest confidence + most fields found)
        method_scores = {}
        for method, data in comparison['methods'].items():
            if data.get('status') == 'success':
                fields_found = sum([
                    1 if data.get('found_store') else 0,
                    1 if data.get('found_total') else 0,
                    1 if data.get('found_date') else 0
                ])
                confidence = data.get('confidence', 0)
                # Score = confidence * 0.7 + fields_found * 10 (max 30 from fields, max 70 from confidence)
                score = (confidence * 0.7) + (fields_found * 10)
                method_scores[method] = score

        if method_scores:
            best_method = max(method_scores.items(), key=lambda x: x[1])
            comparison['best_method'] = {
                'name': best_method[0],
                'score': best_method[1]
            }

        return comparison

    except Exception as e:
        return {
            'document': doc_info,
            'error': str(e),
            'methods': {}
        }


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
    report.append("OCR METHODS COMPREHENSIVE COMPARISON REPORT")
    report.append("=" * 100)
    report.append("")

    # Overall statistics
    report.append("## OVERALL STATISTICS")
    report.append("-" * 100)

    total_docs = len(all_comparisons)
    method_success_count = {'tesseract': 0, 'paddleocr': 0, 'hybrid': 0, 'minicpm': 0}
    method_avg_confidence = {'tesseract': [], 'paddleocr': [], 'hybrid': [], 'minicpm': []}
    method_fields_found = {'tesseract': [], 'paddleocr': [], 'hybrid': [], 'minicpm': []}
    best_method_counts = Counter()

    for comp in all_comparisons:
        methods = comp.get('methods', {})

        for method, data in methods.items():
            if data.get('status') == 'success':
                method_success_count[method] += 1
                method_avg_confidence[method].append(data.get('confidence', 0))

                fields_found = sum([
                    1 if data.get('found_store') else 0,
                    1 if data.get('found_total') else 0,
                    1 if data.get('found_date') else 0
                ])
                method_fields_found[method].append(fields_found)

        best = comp.get('best_method')
        if best:
            best_method_counts[best['name']] += 1

    report.append(f"Total documents analyzed: {total_docs}")
    report.append("")

    report.append("### SUCCESS RATES")
    for method in ['tesseract', 'paddleocr', 'hybrid', 'minicpm']:
        success_rate = (method_success_count[method] / total_docs * 100) if total_docs > 0 else 0
        report.append(f"{method.upper():12s}: {method_success_count[method]}/{total_docs} successful ({success_rate:5.1f}%)")

    report.append("")
    report.append("### AVERAGE CONFIDENCE")
    for method in ['tesseract', 'paddleocr', 'hybrid', 'minicpm']:
        if method_avg_confidence[method]:
            avg = sum(method_avg_confidence[method]) / len(method_avg_confidence[method])
            report.append(f"{method.upper():12s}: {avg:5.1f}%")
        else:
            report.append(f"{method.upper():12s}: N/A")

    report.append("")
    report.append("### AVERAGE FIELDS FOUND (out of 3: store, total, date)")
    for method in ['tesseract', 'paddleocr', 'hybrid', 'minicpm']:
        if method_fields_found[method]:
            avg = sum(method_fields_found[method]) / len(method_fields_found[method])
            report.append(f"{method.upper():12s}: {avg:.1f} fields")
        else:
            report.append(f"{method.upper():12s}: N/A")

    report.append("")
    report.append("### BEST METHOD FREQUENCY")
    for method, count in best_method_counts.most_common():
        percentage = (count / total_docs * 100) if total_docs > 0 else 0
        icon = '🏆' if percentage >= 50 else '✅' if percentage >= 30 else '⚠️'
        report.append(f"{icon} {method.upper():12s}: {count}/{total_docs} times ({percentage:5.1f}%)")

    report.append("")
    report.append("")

    # Document-by-document analysis
    for idx, comp in enumerate(all_comparisons, 1):
        doc_info = comp.get('document', {})

        report.append("=" * 100)
        report.append(f"DOCUMENT {idx}/{total_docs}: {doc_info.get('filename', 'Unknown')}")
        report.append("=" * 100)
        report.append(f"ID: {doc_info.get('id')}")
        report.append("")

        # Quality Assessment
        qa = comp.get('quality_assessment', {})
        if qa:
            report.append("### QUALITY ASSESSMENT")
            report.append("-" * 100)
            report.append(f"Quality Level     : {qa.get('quality_level', 'unknown')}")
            report.append(f"Recommended OCR   : {qa.get('recommended_ocr', 'unknown')}")
            report.append(f"Blur Score        : {qa.get('blur_score', 0):.2f}")
            report.append(f"Contrast Score    : {qa.get('contrast_score', 0):.2f}")
            report.append(f"DPI               : {qa.get('dpi', 0)}")
            report.append("")

        # Methods Results
        report.append("### OCR METHODS RESULTS")
        report.append("-" * 100)

        methods = comp.get('methods', {})

        for method in ['tesseract', 'paddleocr', 'hybrid', 'minicpm']:
            data = methods.get(method, {})

            if data.get('status') == 'success':
                fields_found = sum([
                    1 if data.get('found_store') else 0,
                    1 if data.get('found_total') else 0,
                    1 if data.get('found_date') else 0
                ])

                status_icon = '🏆' if fields_found == 3 else '✅' if fields_found >= 2 else '⚠️' if fields_found == 1 else '❌'

                report.append(f"{status_icon} {method.upper():12s} | Confidence: {data.get('confidence', 0):5.1f}% | Fields: {fields_found}/3 | Chars: {data.get('char_count', 0)}")
                report.append(f"   Store Name   : {data.get('store_name') or 'NOT FOUND'}")
                report.append(f"   Total Amount : {data.get('total_amount') or 'NOT FOUND'}")
                report.append(f"   Date         : {data.get('date') or 'NOT FOUND'}")
                report.append(f"   Order Number : {data.get('order_number') or 'NOT FOUND'}")

                if data.get('text_preview'):
                    preview = data['text_preview'].replace('\n', ' ')[:100]
                    report.append(f"   Text Preview : {preview}...")
            else:
                report.append(f"❌ {method.upper():12s} | ERROR: {data.get('error', 'Unknown error')}")

            report.append("")

        # Consensus
        consensus = comp.get('consensus', {})
        if consensus and any(consensus.values()):
            report.append("### CONSENSUS (Most Common Values)")
            report.append("-" * 100)

            if consensus.get('store_name'):
                agreement = consensus.get('agreement_count', {}).get('store', 0)
                report.append(f"Store Name   : {consensus['store_name']} ({agreement}/4 methods agree)")

            if consensus.get('total_amount'):
                agreement = consensus.get('agreement_count', {}).get('total', 0)
                report.append(f"Total Amount : {consensus['total_amount']} ({agreement}/4 methods agree)")

            if consensus.get('date'):
                agreement = consensus.get('agreement_count', {}).get('date', 0)
                report.append(f"Date         : {consensus['date']} ({agreement}/4 methods agree)")

            report.append("")

        # Best Method
        best = comp.get('best_method')
        if best:
            report.append("### BEST METHOD FOR THIS DOCUMENT")
            report.append("-" * 100)
            report.append(f"🏆 {best['name'].upper()} (score: {best['score']:.2f}/100)")
            report.append("")

        report.append("")

    # Summary and Recommendations
    report.append("=" * 100)
    report.append("SUMMARY & RECOMMENDATIONS")
    report.append("=" * 100)
    report.append("")

    # Method ranking
    method_overall_scores = {}
    for method in ['tesseract', 'paddleocr', 'hybrid', 'minicpm']:
        if method_avg_confidence[method] and method_fields_found[method]:
            avg_conf = sum(method_avg_confidence[method]) / len(method_avg_confidence[method])
            avg_fields = sum(method_fields_found[method]) / len(method_fields_found[method])
            # Overall score = confidence * 0.6 + fields * 13.33 (to normalize fields to 0-40 scale)
            overall = (avg_conf * 0.6) + (avg_fields * 13.33)
            method_overall_scores[method] = overall

    if method_overall_scores:
        sorted_methods = sorted(method_overall_scores.items(), key=lambda x: x[1], reverse=True)

        report.append("### METHOD RANKING (by overall performance)")
        report.append("-" * 100)
        for rank, (method, score) in enumerate(sorted_methods, 1):
            icon = '🥇' if rank == 1 else '🥈' if rank == 2 else '🥉' if rank == 3 else '  '
            report.append(f"{icon} #{rank}. {method.upper():12s} - Score: {score:5.1f}/100")

        report.append("")
        report.append("### RECOMMENDATIONS")
        report.append("-" * 100)

        best_method = sorted_methods[0][0]
        best_score = sorted_methods[0][1]

        if best_score >= 75:
            report.append(f"✅ {best_method.upper()} is performing excellently (score ≥75/100)")
            report.append(f"   → Recommended as primary OCR method")
        elif best_score >= 50:
            report.append(f"⚠️  {best_method.upper()} is performing adequately (score 50-75/100)")
            report.append(f"   → Consider using as primary method with quality checks")
        else:
            report.append(f"❌ All methods scoring below 50/100")
            report.append(f"   → Investigate document quality issues")
            report.append(f"   → Consider using multiple methods with consensus voting")

        report.append("")

        # Specific improvement suggestions
        report.append("### IMPROVEMENT SUGGESTIONS")
        report.append("-" * 100)

        for method, score in sorted_methods:
            if score < 75:
                report.append(f"{method.upper()}:")

                # Analyze failure patterns
                store_failures = 0
                total_failures = 0
                date_failures = 0

                for comp in all_comparisons:
                    method_data = comp.get('methods', {}).get(method, {})

                    if method_data.get('status') == 'success':
                        if not method_data.get('found_store'):
                            store_failures += 1
                        if not method_data.get('found_total'):
                            total_failures += 1
                        if not method_data.get('found_date'):
                            date_failures += 1

                failures = [
                    ('store_name extraction', store_failures),
                    ('total_amount extraction', total_failures),
                    ('date extraction', date_failures)
                ]

                failures.sort(key=lambda x: x[1], reverse=True)

                for field, count in failures[:2]:  # Show top 2 failures
                    if count > 0:
                        percentage = (count / total_docs) * 100
                        report.append(f"   - Improve {field} ({percentage:.0f}% failure rate)")

                report.append("")

    report.append("")
    report.append("=" * 100)
    report.append("END OF REPORT")
    report.append("=" * 100)

    return "\n".join(report)


def main():
    """Main execution function"""
    print("\n" + "=" * 100)
    print("OCR METHODS COMPARISON")
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

    print(f"Analyzing {len(selected_docs)} documents with all OCR methods...\n")

    all_comparisons = []

    for idx, doc_info in enumerate(selected_docs, 1):
        print(f"[{idx}/{len(selected_docs)}] Processing: {doc_info['filename']}")

        # Get Document instance
        try:
            document = Document.objects.get(id=doc_info['id'])
        except Document.DoesNotExist:
            print(f"  ERROR: Document not found in database")
            continue

        # Analyze with all OCR methods
        comparison = analyze_document_with_all_methods(document, doc_info)
        all_comparisons.append(comparison)

        print(f"  ✅ Analysis complete\n")

    # Generate report
    print("\nGenerating comparison report...")
    report = generate_report(all_comparisons)

    # Save report
    report_path = '/tmp/ocr_methods_comparison_report.txt'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    # Save detailed JSON results
    json_path = '/tmp/ocr_methods_comparison_data.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(all_comparisons, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n✅ Report saved to: {report_path}")
    print(f"✅ Detailed JSON saved to: {json_path}")
    print("\n" + "=" * 100)
    print("Displaying report:\n")
    print(report)


if __name__ == '__main__':
    main()
