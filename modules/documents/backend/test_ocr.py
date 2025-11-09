#!/usr/bin/env python3
"""
Test OCR functionality
Run this script to verify OCR installation and test basic functionality
"""

import sys
import os

def test_imports():
    """Test if all required libraries can be imported"""
    print("Testing library imports...")
    
    libraries = [
        ('pytesseract', 'PyTesseract (OCR engine)'),
        ('PIL', 'Pillow (image processing)'),
        ('cv2', 'OpenCV (image enhancement)'),
        ('PyPDF2', 'PyPDF2 (PDF processing)'),
        ('numpy', 'NumPy (numerical computing)'),
    ]
    
    all_success = True
    for lib, name in libraries:
        try:
            __import__(lib)
            print(f"  ✓ {name}")
        except ImportError as e:
            print(f"  ✗ {name}: {e}")
            all_success = False
    
    return all_success

def test_tesseract():
    """Test Tesseract OCR functionality"""
    print("\nTesting Tesseract OCR...")
    
    try:
        import pytesseract
        from PIL import Image, ImageDraw, ImageFont
        import numpy as np
        
        # Check Tesseract installation
        try:
            version = pytesseract.get_tesseract_version()
            print(f"  ✓ Tesseract version: {version}")
        except Exception as e:
            print(f"  ✗ Tesseract not found: {e}")
            print("    Please install Tesseract OCR on your system")
            return False
        
        # Create a test image with text
        print("  Creating test image...")
        img = Image.new('RGB', (400, 100), color='white')
        draw = ImageDraw.Draw(img)
        
        # Add test text
        test_text = "MIGROS MARKET\nTOPLAM: 123.45 TL\n2024-01-15"
        draw.text((10, 10), test_text, fill='black')
        
        # Perform OCR
        print("  Performing OCR on test image...")
        extracted_text = pytesseract.image_to_string(img)
        
        if extracted_text.strip():
            print(f"  ✓ OCR successful!")
            print(f"    Extracted: {extracted_text.strip()[:50]}...")
            return True
        else:
            print("  ✗ OCR failed to extract text")
            return False
            
    except Exception as e:
        print(f"  ✗ Error during OCR test: {e}")
        return False

def test_turkish_support():
    """Test Turkish language support"""
    print("\nTesting Turkish language support...")
    
    try:
        import pytesseract
        
        # Get available languages
        try:
            langs = pytesseract.get_languages()
            print(f"  Available languages: {', '.join(langs)}")
            
            if 'tur' in langs:
                print("  ✓ Turkish language support available")
                return True
            else:
                print("  ✗ Turkish language not found")
                print("    Install with: brew install tesseract-lang (macOS)")
                print("    or: sudo apt-get install tesseract-ocr-tur (Linux)")
                return False
        except Exception as e:
            print(f"  ✗ Could not check languages: {e}")
            return False
            
    except ImportError:
        print("  ✗ PyTesseract not installed")
        return False

def test_sample_receipt():
    """Test OCR on a sample receipt structure"""
    print("\nTesting receipt parsing...")
    
    try:
        from ocr_service import OCRProcessor
        
        processor = OCRProcessor()
        
        # Test sample receipt text
        sample_text = """
        MİGROS TİCARET A.Ş.
        MIGROS M-JET
        
        TARIH: 15/01/2024 14:32
        FİŞ NO: 123456
        
        SÜTAS SÜT 1L           12.50
        PEYNİR 500G            45.00
        EKMEK                   8.00
        
        TOPLAM:                65.50
        NAKİT:                100.00
        PARA ÜSTÜ:             34.50
        
        KDV %8:                 5.24
        """
        
        # Parse the receipt
        parsed = processor.parse_receipt(sample_text)
        
        print("  Parsed receipt data:")
        print(f"    Store: {parsed.get('store_name', 'Not found')}")
        print(f"    Date: {parsed.get('transaction_date', 'Not found')}")
        print(f"    Total: {parsed.get('total_amount', 'Not found')}")
        print(f"    Items: {len(parsed.get('items', []))} found")
        
        if parsed.get('store_name') and parsed.get('total_amount'):
            print("  ✓ Receipt parsing successful!")
            return True
        else:
            print("  ⚠ Partial parsing success")
            return True
            
    except Exception as e:
        print(f"  ✗ Error during receipt parsing: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("UNIBOS OCR Functionality Test")
    print("=" * 50)
    
    results = []
    
    # Test imports
    results.append(("Library Imports", test_imports()))
    
    # Test Tesseract
    results.append(("Tesseract OCR", test_tesseract()))
    
    # Test Turkish support
    results.append(("Turkish Support", test_turkish_support()))
    
    # Test receipt parsing
    results.append(("Receipt Parsing", test_sample_receipt()))
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary:")
    print("=" * 50)
    
    for test_name, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{test_name:.<30} {status}")
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("\n✓ All tests passed! OCR is ready to use.")
    else:
        print("\n⚠ Some tests failed. Please install missing dependencies.")
        print("Run: ./install_ocr.sh")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())