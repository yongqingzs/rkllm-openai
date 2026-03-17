#!/usr/bin/env python3
"""
Frontend integration test script
Tests the RKLLM frontend and API endpoint functionality
"""
import requests
import json
import sys
import time
import base64
from pathlib import Path

# Configuration
FRONTEND_URL = "http://localhost:8000"
RKLLM_API_URL = "http://localhost:8080/v1"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def test_frontend_main_page():
    """Test 1: Frontend main page loads"""
    print(f"\n{Colors.BLUE}[Test 1]{Colors.RESET} Frontend main page...")
    try:
        response = requests.get(f"{FRONTEND_URL}/", timeout=5)
        if response.status_code == 200 and '<!DOCTYPE html>' in response.text:
            print(f"{Colors.GREEN}✓ PASS{Colors.RESET} - Frontend page loaded")
            return True
        else:
            print(f"{Colors.RED}✗ FAIL{Colors.RESET} - Unexpected response")
            return False
    except Exception as e:
        print(f"{Colors.RED}✗ FAIL{Colors.RESET} - {e}")
        return False

def test_frontend_config_api():
    """Test 2: Frontend config API"""
    print(f"\n{Colors.BLUE}[Test 2]{Colors.RESET} Frontend config API...")
    try:
        response = requests.get(f"{FRONTEND_URL}/api/config", timeout=5)
        if response.status_code == 200:
            config = response.json()
            required_keys = ['api_base_url', 'api_key', 'model', 'max_context_length']
            if all(key in config for key in required_keys):
                print(f"{Colors.GREEN}✓ PASS{Colors.RESET} - Config returned:")
                print(f"  - API Base: {config['api_base_url']}")
                print(f"  - Model: {config['model']}")
                print(f"  - Max Context: {config['max_context_length']}")
                return True
            else:
                print(f"{Colors.RED}✗ FAIL{Colors.RESET} - Missing keys in config")
                return False
        else:
            print(f"{Colors.RED}✗ FAIL{Colors.RESET} - Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"{Colors.RED}✗ FAIL{Colors.RESET} - {e}")
        return False

def test_text_only_query():
    """Test 3: Text-only query"""
    print(f"\n{Colors.BLUE}[Test 3]{Colors.RESET} Text-only query...")
    try:
        payload = {
            "model": "rkllm-model",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "你好，请用一句话介绍你自己。"}
                    ]
                }
            ],
            "stream": False
        }
        
        response = requests.post(
            f"{RKLLM_API_URL}/chat/completions",
            json=payload,
            timeout=120
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'choices' in data and len(data['choices']) > 0:
                content = data['choices'][0]['message']['content']
                print(f"{Colors.GREEN}✓ PASS{Colors.RESET} - Got response ({len(content)} chars)")
                print(f"  Response: {content[:100]}...")
                return True
            else:
                print(f"{Colors.RED}✗ FAIL{Colors.RESET} - No choices in response")
                return False
        else:
            print(f"{Colors.RED}✗ FAIL{Colors.RESET} - Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"{Colors.RED}✗ FAIL{Colors.RESET} - {e}")
        return False

def test_streaming_query():
    """Test 4: Streaming query"""
    print(f"\n{Colors.BLUE}[Test 4]{Colors.RESET} Streaming text query...")
    try:
        payload = {
            "model": "rkllm-model",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What is machine learning? (answer in English, briefly)"}
                    ]
                }
            ],
            "stream": True
        }
        
        response = requests.post(
            f"{RKLLM_API_URL}/chat/completions",
            json=payload,
            stream=True,
            timeout=120
        )
        
        if response.status_code == 200:
            chunk_count = 0
            full_text = ""
            
            for line in response.iter_lines():
                if line:
                    line_text = line.decode('utf-8') if isinstance(line, bytes) else line
                    if line_text.startswith('data: '):
                        data_text = line_text[6:]
                        if data_text != '[DONE]':
                            try:
                                data = json.loads(data_text)
                                chunk = data.get('choices', [{}])[0].get('delta', {}).get('content', '')
                                if chunk:
                                    full_text += chunk
                                    chunk_count += 1
                            except json.JSONDecodeError:
                                pass
            
            if chunk_count > 0:
                print(f"{Colors.GREEN}✓ PASS{Colors.RESET} - Streaming works ({chunk_count} chunks, {len(full_text)} chars)")
                return True
            else:
                print(f"{Colors.RED}✗ FAIL{Colors.RESET} - No chunks received")
                return False
        else:
            print(f"{Colors.RED}✗ FAIL{Colors.RESET} - Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"{Colors.RED}✗ FAIL{Colors.RESET} - {e}")
        return False

def test_image_query():
    """Test 5: Image query"""
    print(f"\n{Colors.BLUE}[Test 5]{Colors.RESET} Image + text query...")
    try:
        # Try to load the default test image
        image_path = Path("/home/cat/llm/rknn-llm/datasets/000000000025.jpg")
        if not image_path.exists():
            print(f"{Colors.YELLOW}⊘ SKIP{Colors.RESET} - Test image not found, skipping")
            return True  # Not a failure, just skip
        
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        payload = {
            "model": "rkllm-model",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "这张图片里有什么？"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        }
                    ]
                }
            ],
            "stream": False
        }
        
        response = requests.post(
            f"{RKLLM_API_URL}/chat/completions",
            json=payload,
            timeout=120
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'choices' in data and len(data['choices']) > 0:
                content = data['choices'][0]['message']['content']
                print(f"{Colors.GREEN}✓ PASS{Colors.RESET} - Image query works ({len(content)} chars)")
                print(f"  Response: {content[:100]}...")
                return True
            else:
                print(f"{Colors.RED}✗ FAIL{Colors.RESET} - No choices in response")
                return False
        else:
            print(f"{Colors.RED}✗ FAIL{Colors.RESET} - Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"{Colors.RED}✗ FAIL{Colors.RESET} - {e}")
        return False

def test_health_check():
    """Test 6: Health check"""
    print(f"\n{Colors.BLUE}[Test 6]{Colors.RESET} Frontend health check...")
    try:
        response = requests.get(f"{FRONTEND_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"{Colors.GREEN}✓ PASS{Colors.RESET} - Health check OK")
            return True
        else:
            print(f"{Colors.RED}✗ FAIL{Colors.RESET} - Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"{Colors.RED}✗ FAIL{Colors.RESET} - {e}")
        return False

def main():
    """Run all tests"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}RKLLM Frontend Integration Tests{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"\nFrontend: {FRONTEND_URL}")
    print(f"Backend:  {RKLLM_API_URL}")
    
    tests = [
        test_frontend_main_page,
        test_frontend_config_api,
        test_health_check,
        test_text_only_query,
        test_streaming_query,
        test_image_query,
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except KeyboardInterrupt:
            print(f"\n{Colors.RED}Test interrupted{Colors.RESET}")
            break
        except Exception as e:
            print(f"{Colors.RED}Unexpected error: {e}{Colors.RESET}")
            results.append(False)
    
    # Summary
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    passed = sum(results)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    if passed == total:
        color = Colors.GREEN
        status = "ALL TESTS PASSED"
    elif passed > total / 2:
        color = Colors.YELLOW
        status = "SOME TESTS FAILED"
    else:
        color = Colors.RED
        status = "MOST TESTS FAILED"
    
    print(f"{color}Result: {status} ({passed}/{total} - {percentage:.0f}%){Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}\n")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
