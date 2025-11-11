#!/bin/bash

# OCR Installation Script for macOS/Linux
# This script installs open-source OCR dependencies

echo "====================================="
echo "UNIBOS OCR Dependencies Installation"
echo "====================================="

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "macOS detected. Installing with Homebrew..."
    
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        echo "Homebrew not found. Please install Homebrew first:"
        echo "/bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi
    
    # Install Tesseract OCR
    echo "Installing Tesseract OCR..."
    brew install tesseract
    
    # Install language packs
    echo "Installing Turkish language pack..."
    brew install tesseract-lang
    
    # Install Poppler for PDF support
    echo "Installing Poppler for PDF support..."
    brew install poppler
    
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Linux detected. Installing with apt-get..."
    
    # Update package list
    sudo apt-get update
    
    # Install Tesseract OCR
    echo "Installing Tesseract OCR..."
    sudo apt-get install -y tesseract-ocr
    
    # Install Turkish language pack
    echo "Installing Turkish language pack..."
    sudo apt-get install -y tesseract-ocr-tur
    
    # Install Poppler for PDF support
    echo "Installing Poppler for PDF support..."
    sudo apt-get install -y poppler-utils
    
    # Install additional dependencies
    sudo apt-get install -y libgl1-mesa-glx
else
    echo "Unsupported OS: $OSTYPE"
    exit 1
fi

# Install Python dependencies
echo ""
echo "Installing Python OCR libraries..."
pip install -r requirements_ocr.txt

# Verify installation
echo ""
echo "Verifying installation..."
echo "========================"

# Check Tesseract
if command -v tesseract &> /dev/null; then
    echo "✓ Tesseract installed: $(tesseract --version | head -n 1)"
    echo "  Available languages: $(tesseract --list-langs 2>&1 | grep -E 'tur|eng' | tr '\n' ' ')"
else
    echo "✗ Tesseract not found"
fi

# Check Python libraries
python3 << EOF
import sys
libraries = {
    'pytesseract': 'PyTesseract',
    'PIL': 'Pillow',
    'cv2': 'OpenCV',
    'PyPDF2': 'PyPDF2'
}

for lib, name in libraries.items():
    try:
        __import__(lib)
        print(f"✓ {name} installed")
    except ImportError:
        print(f"✗ {name} not found")
EOF

echo ""
echo "====================================="
echo "Installation complete!"
echo "====================================="
echo ""
echo "To test OCR functionality, run:"
echo "python3 -m apps.documents.test_ocr"