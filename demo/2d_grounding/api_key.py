import requests
import os
import base64
import json

# RKLLM API Configuration
RKLLM_API_BASE_URL = os.environ.get('RKLLM_API_BASE_URL', 'http://localhost:8080/v1')
RKLLM_API_KEY = os.environ.get('RKLLM_API_KEY', 'sk-test-key')
RKLLM_MODEL = os.environ.get('RKLLM_MODEL', 'rkllm-model')

print(f"[DEBUG] RKLLM API Config: URL={RKLLM_API_BASE_URL}, Model={RKLLM_MODEL}")

def inference_with_openai_api(image_input, prompt):
    """
    Send inference request to RKLLM API server using requests.
    
    Args:
        image_input: Can be local file path or HTTP(S) URL
        prompt: Text prompt for the model
    
    Returns:
        str: Model response
    """
    try:
        # Build message content
        message_content = [{"type": "text", "text": prompt}]
        
        # Handle different image input types
        if image_input.startswith(('http://', 'https://')):
            # Remote URL - server will download it
            message_content.append({
                "type": "image_url",
                "image_url": {"url": image_input}
            })
            print(f"✓ Using remote image: {image_input}")
        elif os.path.isfile(image_input):
            # Local file - convert to base64
            with open(image_input, "rb") as image_file:
                image_data = image_file.read()
                b64_image = base64.b64encode(image_data).decode("utf-8")
                # Determine image type
                ext = os.path.splitext(image_input)[1].lower()
                mime_type = {'.jpg': 'jpeg', '.jpeg': 'jpeg', '.png': 'png', '.gif': 'gif', '.webp': 'webp'}.get(ext, 'jpeg')
                message_content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/{mime_type};base64,{b64_image}"}
                })
                print(f"✓ Using local image: {image_input} ({len(image_data)} bytes)")
        else:
            print(f"⚠ Warning: Image input '{image_input}' not found, sending text-only query")
        
        # Create chat completion request using requests library
        print(f"📝 Prompt: {prompt[:100]}...")
        print(f"🚀 Calling RKLLM API at {RKLLM_API_BASE_URL}/chat/completions...")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {RKLLM_API_KEY}"
        }
        
        payload = {
            "model": RKLLM_MODEL,
            "messages": [{
                "role": "user",
                "content": message_content
            }]
        }
        
        response = requests.post(
            f"{RKLLM_API_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=300
        )
        
        if response.status_code != 200:
            print(f"✗ API returned status {response.status_code}")
            print(f"  Response: {response.text[:500]}")
            response.raise_for_status()
        
        result = response.json()
        if "error" in result:
            raise Exception(f"API Error: {result['error']}")
        
        # Extract response content
        result_text = result['choices'][0]['message']['content']
        print(f"✓ Received response ({len(result_text)} chars)")
        return result_text
        
    except Exception as e:
        print(f"✗ API Error: {e}")
        import traceback
        traceback.print_exc()
        raise
