"""
Simple receipt processing view for testing
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json

@login_required
def simple_receipt_hub(request):
    """Simple receipt hub view with Ollama integration"""
    
    context = {
        'title': 'Receipt Processing Hub',
        'user': request.user,
        'ollama_status': check_ollama_status(),
    }
    
    return render(request, 'documents/simple_receipt_hub.html', context)


def check_ollama_status():
    """Check if Ollama is running"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=1)
        if response.status_code == 200:
            models = response.json().get('models', [])
            return {
                'running': True,
                'models': [m['name'] for m in models]
            }
    except:
        pass
    return {'running': False, 'models': []}


@login_required
@require_http_methods(["POST"])
def process_receipt_ollama(request):
    """Process receipt with Ollama"""
    try:
        import requests
        data = json.loads(request.body)
        ocr_text = data.get('text', '')
        
        # Create prompt for Ollama
        prompt = f"""Extract information from this Turkish receipt:
{ocr_text}

Return JSON with:
- store_name
- date
- total_amount
- items (list)

Only return valid JSON."""

        # Call Ollama
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "gemma3:latest",  # or llama2:latest
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "max_tokens": 500
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return JsonResponse({
                'success': True,
                'result': result.get('response', ''),
                'model': 'gemma3'
            })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
    
    return JsonResponse({'success': False, 'error': 'Processing failed'})