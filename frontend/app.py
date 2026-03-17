"""
RKLLM Frontend Server
Simple Flask server to host the Web UI for RKLLM Vision-Language Model
"""
import os
import logging
import requests
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='templates', static_folder='static')

# Enable CORS with specific configuration
CORS(app, 
     origins=['*'],
     allow_headers=['*'],
     methods=['GET', 'POST', 'OPTIONS', 'PUT', 'DELETE'],
     max_age=3600)

# Backend API URL
BACKEND_API_URL = os.getenv('RKLLM_API_BASE_URL', 'http://localhost:8080/v1')

@app.route('/', methods=['GET'])
def index():
    """Serve the main page."""
    return render_template('index.html')

@app.route('/api/config', methods=['GET'])
def get_config():
    """Return frontend configuration."""
    return jsonify({
        'api_base_url': '/api/backend',  # Use frontend proxy instead of direct backend URL
        'api_key': os.getenv('RKLLM_API_KEY', 'none'),
        'model': os.getenv('RKLLM_MODEL_NAME', 'rkllm-model'),
        'max_context_length': int(os.getenv('RKLLM_MAX_CONTEXT', '4096'))
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok'})

@app.route('/api/backend/<path:endpoint>', methods=['GET', 'POST', 'OPTIONS'])
def proxy_backend(endpoint):
    """Proxy requests to RKLLM backend API."""
    try:
        # Build the target URL
        target_url = f"{BACKEND_API_URL}/{endpoint}"
        
        # Get request data
        request_data = request.get_json() if request.method in ['POST', 'PUT'] else None
        
        # Get request headers (exclude host-related headers)
        headers = {key: value for key, value in request.headers if key.lower() not in 
                  ['host', 'connection', 'content-length']}
        headers['Content-Type'] = 'application/json'
        
        logger.debug(f"Proxying {request.method} to {target_url}")
        
        # Forward request to backend
        if request.method == 'GET':
            response = requests.get(target_url, headers=headers, timeout=30)
        else:
            response = requests.post(target_url, json=request_data, headers=headers, 
                                   stream=True, timeout=120)
        
        # Handle streaming responses
        if request.method == 'POST' and response.headers.get('content-type', '').startswith('text/event-stream'):
            def generate():
                for line in response.iter_lines():
                    if line:
                        yield line + b'\n'
            
            return app.response_class(
                generate(),
                mimetype='text/event-stream',
                status=response.status_code
            )
        
        # Handle non-streaming responses
        return jsonify(response.json()) if response.headers.get('content-type', '').startswith('application/json') else response.text, response.status_code
        
    except requests.RequestException as e:
        logger.error(f"Backend proxy error: {e}")
        return jsonify({'error': f'Backend error: {str(e)}'}), 502
    except Exception as e:
        logger.error(f"Proxy error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Default to port 8000 to avoid conflict with RKLLM server (8080)
    port = int(os.getenv('FRONTEND_PORT', 8000))
    host = os.getenv('FRONTEND_HOST', '0.0.0.0')
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting RKLLM Frontend on {host}:{port}")
    app.run(host=host, port=port, debug=debug)
