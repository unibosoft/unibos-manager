"""
Local LLM OCR Enhancement System
Supports Ollama, llama.cpp, MLX for Apple Silicon
"""

import os
import json
import logging
import subprocess
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import platform

logger = logging.getLogger('documents.local_llm')

class LocalLLMProcessor:
    """
    Local LLM processor for OCR enhancement
    Optimized for Apple Silicon (M4 Max) and Raspberry Pi
    """
    
    def __init__(self, backend: str = "auto"):
        """
        Initialize local LLM processor
        
        Args:
            backend: "ollama", "llamacpp", "mlx", "tinyllama", or "auto"
        """
        self.backend = backend
        self.model_name = None
        self.is_apple_silicon = self._detect_apple_silicon()
        self.is_raspberry_pi = self._detect_raspberry_pi()
        
        if backend == "auto":
            self.backend = self._auto_select_backend()
        
        self._initialize_backend()
    
    def _detect_apple_silicon(self) -> bool:
        """Detect if running on Apple Silicon"""
        try:
            if platform.system() == "Darwin":
                result = subprocess.run(
                    ["sysctl", "-n", "machdep.cpu.brand_string"],
                    capture_output=True,
                    text=True
                )
                return "Apple" in result.stdout
        except:
            pass
        return False
    
    def _detect_raspberry_pi(self) -> bool:
        """Detect if running on Raspberry Pi"""
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
                return 'Raspberry Pi' in cpuinfo or 'BCM' in cpuinfo
        except:
            return False
    
    def _auto_select_backend(self) -> str:
        """Auto-select best backend for current hardware"""
        if self.is_apple_silicon:
            # M4 Max - use MLX for best performance
            if self._check_mlx_available():
                logger.info("Auto-selected MLX for Apple Silicon")
                return "mlx"
            elif self._check_ollama_available():
                logger.info("Auto-selected Ollama for Apple Silicon")
                return "ollama"
        elif self.is_raspberry_pi:
            # Raspberry Pi - use TinyLlama
            logger.info("Auto-selected TinyLlama for Raspberry Pi")
            return "tinyllama"
        
        # Default to Ollama if available
        if self._check_ollama_available():
            return "ollama"
        
        # Fallback to llama.cpp
        return "llamacpp"
    
    def _check_ollama_available(self) -> bool:
        """Check if Ollama is installed and running"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=1)
            return response.status_code == 200
        except:
            return False
    
    def _check_mlx_available(self) -> bool:
        """Check if MLX is available (Apple Silicon only)"""
        try:
            import mlx
            return True
        except ImportError:
            return False
    
    def _initialize_backend(self):
        """Initialize the selected backend"""
        if self.backend == "ollama":
            self._init_ollama()
        elif self.backend == "mlx":
            self._init_mlx()
        elif self.backend == "llamacpp":
            self._init_llamacpp()
        elif self.backend == "tinyllama":
            self._init_tinyllama()
    
    def _init_ollama(self):
        """Initialize Ollama backend"""
        self.base_url = "http://localhost:11434"
        # Use Mistral or Llama 3.2 for OCR
        self.model_name = "llama3.2:3b"  # 3B model, perfect for OCR
        
        # Check if model is available, if not, pull it
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m['name'] for m in models]
                
                if self.model_name not in model_names:
                    logger.info(f"Pulling {self.model_name} model...")
                    self._pull_ollama_model(self.model_name)
        except Exception as e:
            logger.error(f"Ollama initialization failed: {e}")
    
    def _pull_ollama_model(self, model_name: str):
        """Pull Ollama model"""
        try:
            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name},
                stream=True
            )
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if 'status' in data:
                        logger.info(f"Ollama: {data['status']}")
        except Exception as e:
            logger.error(f"Failed to pull model: {e}")
    
    def _init_mlx(self):
        """Initialize MLX backend for Apple Silicon"""
        try:
            import mlx_lm
            from huggingface_hub import snapshot_download
            
            # Use quantized model for speed
            self.model_name = "mlx-community/Llama-3.2-3B-Instruct-4bit"
            
            # Download model if not exists
            model_path = Path.home() / ".cache" / "mlx_models" / self.model_name
            if not model_path.exists():
                logger.info(f"Downloading {self.model_name}...")
                snapshot_download(
                    repo_id=self.model_name,
                    local_dir=model_path
                )
            
            # Load model
            self.model, self.tokenizer = mlx_lm.load(str(model_path))
            logger.info("MLX model loaded successfully")
            
        except Exception as e:
            logger.error(f"MLX initialization failed: {e}")
            # Fallback to Ollama
            self.backend = "ollama"
            self._init_ollama()
    
    def _init_llamacpp(self):
        """Initialize llama.cpp backend"""
        try:
            from llama_cpp import Llama
            
            # Use quantized GGUF model
            model_path = Path.home() / ".cache" / "llama_models" / "llama-3.2-3b-instruct.Q4_K_M.gguf"
            
            if not model_path.exists():
                logger.info("Downloading llama.cpp model...")
                self._download_gguf_model(model_path)
            
            # Initialize with optimal settings for M4 Max
            self.llm = Llama(
                model_path=str(model_path),
                n_ctx=2048,  # Context window for OCR
                n_threads=8,  # Use 8 threads
                n_gpu_layers=-1,  # Use all GPU layers on M4 Max
                verbose=False
            )
            logger.info("Llama.cpp initialized successfully")
            
        except ImportError:
            logger.error("llama-cpp-python not installed")
        except Exception as e:
            logger.error(f"Llama.cpp initialization failed: {e}")
    
    def _init_tinyllama(self):
        """Initialize TinyLlama for Raspberry Pi"""
        try:
            # Use ONNX runtime for ARM processors
            import onnxruntime as ort
            
            model_path = Path.home() / ".cache" / "tiny_models" / "tinyllama-1.1b.onnx"
            
            if not model_path.exists():
                logger.info("Downloading TinyLlama for Raspberry Pi...")
                self._download_tiny_model(model_path)
            
            # Create ONNX session optimized for ARM
            self.session = ort.InferenceSession(
                str(model_path),
                providers=['CPUExecutionProvider']
            )
            logger.info("TinyLlama initialized for Raspberry Pi")
            
        except Exception as e:
            logger.error(f"TinyLlama initialization failed: {e}")
    
    def process_ocr_text(self, ocr_text: str, mode: str = "enhance") -> Dict:
        """
        Process OCR text with local LLM
        
        Args:
            ocr_text: Raw OCR text
            mode: "enhance", "correct", or "extract"
        """
        if self.backend == "ollama":
            return self._process_with_ollama(ocr_text, mode)
        elif self.backend == "mlx":
            return self._process_with_mlx(ocr_text, mode)
        elif self.backend == "llamacpp":
            return self._process_with_llamacpp(ocr_text, mode)
        elif self.backend == "tinyllama":
            return self._process_with_tinyllama(ocr_text, mode)
        else:
            return {"error": "No backend available"}
    
    def _process_with_ollama(self, text: str, mode: str) -> Dict:
        """Process with Ollama API"""
        try:
            prompt = self._create_prompt(text, mode)
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "max_tokens": 500,
                        "top_p": 0.9
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return self._parse_llm_response(result.get('response', ''))
            
        except Exception as e:
            logger.error(f"Ollama processing failed: {e}")
        
        return {}
    
    def _process_with_mlx(self, text: str, mode: str) -> Dict:
        """Process with MLX (Apple Silicon optimized)"""
        try:
            import mlx_lm
            
            prompt = self._create_prompt(text, mode)
            
            # Generate with MLX
            response = mlx_lm.generate(
                self.model,
                self.tokenizer,
                prompt=prompt,
                max_tokens=500,
                temp=0.3
            )
            
            return self._parse_llm_response(response)
            
        except Exception as e:
            logger.error(f"MLX processing failed: {e}")
            return {}
    
    def _process_with_llamacpp(self, text: str, mode: str) -> Dict:
        """Process with llama.cpp"""
        try:
            prompt = self._create_prompt(text, mode)
            
            # Generate with llama.cpp
            response = self.llm(
                prompt,
                max_tokens=500,
                temperature=0.3,
                top_p=0.9,
                echo=False
            )
            
            generated_text = response['choices'][0]['text']
            return self._parse_llm_response(generated_text)
            
        except Exception as e:
            logger.error(f"Llama.cpp processing failed: {e}")
            return {}
    
    def _process_with_tinyllama(self, text: str, mode: str) -> Dict:
        """Process with TinyLlama (Raspberry Pi)"""
        # Simplified processing for low-power devices
        try:
            # Basic extraction only due to limited resources
            result = {
                "store_name": self._extract_store_name(text),
                "date": self._extract_date(text),
                "total": self._extract_total(text),
                "method": "tinyllama",
                "device": "raspberry_pi"
            }
            return result
            
        except Exception as e:
            logger.error(f"TinyLlama processing failed: {e}")
            return {}
    
    def _create_prompt(self, text: str, mode: str) -> str:
        """Create prompt for LLM"""
        if mode == "enhance":
            return f"""Analyze this Turkish receipt and extract information in JSON format:

Receipt text:
{text}

Extract:
- store_name: Store name
- date: Date in DD-MM-YYYY
- total_amount: Total amount (number only)
- items: List of items with name and price
- payment_method: cash/credit_card

Return only valid JSON."""

        elif mode == "correct":
            return f"""Fix OCR errors in this Turkish text:
{text}

Fix character errors (0→O, 1→I, etc.) and return corrected text only."""

        else:  # extract mode
            return f"""Extract the total amount from this receipt:
{text}

Return only the number."""
    
    def _parse_llm_response(self, response: str) -> Dict:
        """Parse LLM response to structured data"""
        try:
            # Try to extract JSON
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        # Fallback to text response
        return {"raw_response": response}
    
    def _extract_store_name(self, text: str) -> str:
        """Simple store name extraction"""
        lines = text.strip().split('\n')
        if lines:
            return lines[0].strip()
        return ""
    
    def _extract_date(self, text: str) -> str:
        """Simple date extraction"""
        import re
        date_pattern = r'(\d{2}[-./]\d{2}[-./]\d{4})'
        match = re.search(date_pattern, text)
        if match:
            return match.group(1)
        return ""
    
    def _extract_total(self, text: str) -> float:
        """Simple total extraction"""
        import re
        patterns = [
            r'TOPLAM\s*:?\s*([\d,\.]+)',
            r'TOTAL\s*:?\s*([\d,\.]+)'
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1).replace(',', '.'))
                except:
                    pass
        return 0.0


class DistributedOCRProcessor:
    """
    Distributed OCR processing across multiple devices
    Coordinates between M4 Max (main) and Raspberry Pi (workers)
    """
    
    def __init__(self):
        self.main_processor = None
        self.worker_nodes = []
        self.setup_network()
    
    def setup_network(self):
        """Setup distributed processing network"""
        # Main node (M4 Max)
        if platform.system() == "Darwin":
            self.main_processor = LocalLLMProcessor(backend="auto")
            logger.info("Main processor initialized on M4 Max")
        
        # Discover Raspberry Pi workers
        self.discover_workers()
    
    def discover_workers(self):
        """Discover Raspberry Pi workers on network"""
        # Simple mDNS discovery
        import socket
        
        # Scan for Raspberry Pi devices
        # Port 8765 for OCR worker service
        worker_port = 8765
        
        # Add discovered workers
        # This would scan local network for RPi devices
        pass
    
    def distribute_batch(self, documents: List[Dict]) -> List[Dict]:
        """
        Distribute OCR processing across available nodes
        
        M4 Max handles complex documents
        Raspberry Pi handles simple receipts
        """
        results = []
        
        # Sort documents by complexity
        simple_docs = []
        complex_docs = []
        
        for doc in documents:
            text_length = len(doc.get('ocr_text', ''))
            if text_length < 500:
                simple_docs.append(doc)
            else:
                complex_docs.append(doc)
        
        # Process complex on M4 Max
        if self.main_processor and complex_docs:
            logger.info(f"Processing {len(complex_docs)} complex documents on M4 Max")
            for doc in complex_docs:
                result = self.main_processor.process_ocr_text(
                    doc['ocr_text'],
                    mode='enhance'
                )
                result['document_id'] = doc['id']
                results.append(result)
        
        # Distribute simple to Raspberry Pi workers
        if self.worker_nodes and simple_docs:
            logger.info(f"Distributing {len(simple_docs)} simple documents to workers")
            # Round-robin distribution
            for i, doc in enumerate(simple_docs):
                worker = self.worker_nodes[i % len(self.worker_nodes)]
                # Send to worker via HTTP
                # result = self.send_to_worker(worker, doc)
                # results.append(result)
        
        return results


# Installation helper script
def generate_install_script():
    """Generate installation script for different platforms"""
    
    macos_script = """#!/bin/bash
# macOS (M4 Max) Installation Script

echo "🍎 Installing Local LLM for macOS (Apple Silicon)..."

# Install Ollama
if ! command -v ollama &> /dev/null; then
    echo "Installing Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
fi

# Start Ollama service
ollama serve &

# Pull recommended model
ollama pull llama3.2:3b

# Install Python packages
pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir
pip install mlx mlx-lm  # For Apple Silicon optimization

echo "✅ Installation complete!"
echo "Recommended models:"
echo "  - Ollama: llama3.2:3b (3B parameters, fast)"
echo "  - MLX: Llama-3.2-3B-Instruct-4bit (optimized for M4)"
"""

    rpi_script = """#!/bin/bash
# Raspberry Pi Zero 2W Installation Script

echo "🍓 Installing TinyLLM for Raspberry Pi..."

# Install dependencies
sudo apt-get update
sudo apt-get install -y python3-pip python3-numpy

# Install ONNX Runtime for ARM
pip3 install onnxruntime

# Download TinyLlama model
mkdir -p ~/.cache/tiny_models
cd ~/.cache/tiny_models

# Download quantized model (smaller for RPi)
wget https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0/resolve/main/onnx/model_quantized.onnx

echo "✅ Installation complete!"
echo "TinyLlama 1.1B ready for OCR processing"
"""

    return {
        'macos': macos_script,
        'raspberry_pi': rpi_script
    }