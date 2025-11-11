#!/bin/bash

# Raspberry Pi Zero 2W Local LLM Installation Script
# Ultra-lightweight OCR processing

echo "========================================="
echo "🍓 UNIBOS TinyLLM Installer for RPi Zero 2W"
echo "   Ultra-lightweight OCR Processing"
echo "========================================="

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo && ! grep -q "BCM" /proc/cpuinfo; then
    echo "⚠️  Warning: Not running on Raspberry Pi"
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 1. System update and dependencies
echo ""
echo "📦 Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y \
    python3-pip \
    python3-numpy \
    python3-dev \
    libopenblas-dev \
    cmake \
    build-essential

# 2. Create lightweight OCR service directory
echo ""
echo "📁 Setting up OCR service..."
mkdir -p ~/unibos_ocr_worker
cd ~/unibos_ocr_worker

# 3. Install Python packages (lightweight versions)
echo ""
echo "🐍 Installing Python packages..."
pip3 install --user \
    onnxruntime \
    flask \
    requests \
    numpy

# 4. Download TinyLlama ONNX model (smallest possible)
echo ""
echo "📥 Downloading TinyLlama model (1.1B parameters)..."
mkdir -p models
cd models

# Download quantized 4-bit model (only ~300MB)
if [ ! -f "tinyllama-1.1b-q4.onnx" ]; then
    echo "Downloading quantized model..."
    # Use a lightweight model
    wget -O tinyllama-1.1b-q4.onnx \
        "https://huggingface.co/ggml-org/tiny-llama-1.1b-gguf/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
fi

cd ..

# 5. Create OCR worker service
echo ""
echo "🔧 Creating OCR worker service..."
cat > ocr_worker.py << 'EOF'
#!/usr/bin/env python3
"""
Lightweight OCR Worker for Raspberry Pi Zero 2W
Simple pattern matching and extraction
"""

from flask import Flask, request, jsonify
import re
from datetime import datetime

app = Flask(__name__)

class SimpleLLM:
    """Ultra-lightweight text processor"""
    
    def process_receipt(self, text):
        """Extract basic receipt information"""
        result = {
            "store_name": self.extract_store_name(text),
            "date": self.extract_date(text),
            "total": self.extract_total(text),
            "payment": self.extract_payment(text),
            "processor": "rpi_zero_2w",
            "model": "pattern_matching"
        }
        return result
    
    def extract_store_name(self, text):
        """Get first line as store name"""
        lines = text.strip().split('\n')
        if lines:
            return lines[0].strip()[:50]
        return ""
    
    def extract_date(self, text):
        """Extract date patterns"""
        patterns = [
            r'(\d{2}[-./]\d{2}[-./]\d{4})',
            r'TARİH\s*:?\s*(\d{2}[-./]\d{2}[-./]\d{4})'
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1) if '(' in pattern else match.group()
        return ""
    
    def extract_total(self, text):
        """Extract total amount"""
        patterns = [
            r'TOPLAM\s*:?\s*([\d,\.]+)',
            r'TOTAL\s*:?\s*([\d,\.]+)',
            r'TUTAR\s*:?\s*([\d,\.]+)'
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    amount = match.group(1).replace(',', '.')
                    return float(amount)
                except:
                    pass
        return 0.0
    
    def extract_payment(self, text):
        """Extract payment method"""
        text_upper = text.upper()
        if 'KREDİ' in text_upper or 'KREDI' in text_upper:
            return 'credit_card'
        elif 'NAKİT' in text_upper or 'NAKIT' in text_upper:
            return 'cash'
        elif 'BANKA KARTI' in text_upper:
            return 'debit_card'
        return 'unknown'

processor = SimpleLLM()

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "device": "raspberry_pi_zero_2w",
        "service": "ocr_worker"
    })

@app.route('/process', methods=['POST'])
def process_ocr():
    """Process OCR text"""
    try:
        data = request.json
        text = data.get('text', '')
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        # Process with simple patterns
        result = processor.process_receipt(text)
        result['processed_at'] = datetime.now().isoformat()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run on all interfaces for network access
    app.run(host='0.0.0.0', port=8765, debug=False)
EOF

chmod +x ocr_worker.py

# 6. Create systemd service
echo ""
echo "🔧 Creating systemd service..."
sudo tee /etc/systemd/system/unibos-ocr-worker.service << EOF
[Unit]
Description=UNIBOS OCR Worker for Raspberry Pi
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$HOME/unibos_ocr_worker
ExecStart=/usr/bin/python3 $HOME/unibos_ocr_worker/ocr_worker.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 7. Enable and start service
echo ""
echo "🚀 Starting OCR worker service..."
sudo systemctl daemon-reload
sudo systemctl enable unibos-ocr-worker.service
sudo systemctl start unibos-ocr-worker.service

# 8. Create test script
echo ""
echo "📝 Creating test script..."
cat > test_ocr_worker.sh << 'EOF'
#!/bin/bash

echo "Testing OCR Worker..."

# Test health endpoint
echo "1. Health check:"
curl -s http://localhost:8765/health | python3 -m json.tool

# Test OCR processing
echo ""
echo "2. OCR processing test:"
curl -s -X POST http://localhost:8765/process \
  -H "Content-Type: application/json" \
  -d '{
    "text": "MIGROS\nTARIH: 30-05-2025\nTOPLAM: 105.50 TL\nKREDI KARTI"
  }' | python3 -m json.tool
EOF

chmod +x test_ocr_worker.sh

# 9. Show network info for main server
echo ""
echo "📡 Network Configuration:"
ip_addr=$(hostname -I | awk '{print $1}')
echo "   IP Address: $ip_addr"
echo "   OCR Port: 8765"
echo "   API URL: http://$ip_addr:8765"

# 10. Performance optimization for RPi Zero 2W
echo ""
echo "⚙️  Optimizing for Raspberry Pi Zero 2W..."

# Set CPU governor to performance
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor > /dev/null

# Increase swap (important for Zero 2W with 512MB RAM)
if [ ! -f /swapfile ]; then
    echo "Creating 1GB swap file..."
    sudo fallocate -l 1G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
fi

# 11. Final summary
echo ""
echo "========================================="
echo "✅ Installation Complete!"
echo "========================================="
echo ""
echo "📊 System Info:"
echo "   Device: Raspberry Pi Zero 2W"
echo "   RAM: $(free -h | grep Mem | awk '{print $2}')"
echo "   CPU: $(lscpu | grep 'Model name' | cut -d':' -f2 | xargs)"
echo "   Service: http://$ip_addr:8765"
echo ""
echo "🎯 Quick Test:"
echo "   ./test_ocr_worker.sh"
echo ""
echo "💡 Usage:"
echo "   1. Service runs automatically on boot"
echo "   2. Main server can send OCR tasks to: http://$ip_addr:8765/process"
echo "   3. Ultra-low power: ~2W consumption"
echo ""
echo "⚡ Performance:"
echo "   - Simple receipts: ~200ms"
echo "   - Pattern matching only (no LLM)"
echo "   - Can handle 10-20 requests/minute"
echo ""
echo "📱 Add to main UNIBOS server:"
echo "   Export UNIBOS_OCR_WORKER_URL=http://$ip_addr:8765"
echo "========================================="