#!/usr/bin/env python3
"""Debug proxy to log requests between frontend and RAG server"""

from flask import Flask, request, Response
import requests
import json

app = Flask(__name__)

RAG_SERVER_URL = "http://localhost:8081"

@app.route('/v1/generate', methods=['POST', 'OPTIONS'])
def proxy_generate():
    if request.method == 'OPTIONS':
        # Handle CORS preflight
        response = Response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    # Log the incoming request
    data = request.get_json()
    print(f"\n=== FRONTEND REQUEST ===")
    print(f"Headers: {dict(request.headers)}")
    print(f"Body: {json.dumps(data, indent=2)}")
    print(f"========================\n")
    
    # Forward to RAG server
    try:
        resp = requests.post(
            f"{RAG_SERVER_URL}/v1/generate",
            json=data,
            headers={'Content-Type': 'application/json'},
            stream=True,
            timeout=60
        )
        
        print(f"\n=== RAG SERVER RESPONSE ===")
        print(f"Status: {resp.status_code}")
        print(f"Headers: {dict(resp.headers)}")
        print(f"===========================\n")
        
        # Forward response back to frontend
        def generate():
            for chunk in resp.iter_content(chunk_size=1024):
                if chunk:
                    yield chunk
        
        response = Response(generate(), status=resp.status_code)
        response.headers['Content-Type'] = resp.headers.get('Content-Type', 'text/event-stream')
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return {'error': str(e)}, 500

if __name__ == '__main__':
    print("Starting debug proxy on http://localhost:8888")
    print(f"Proxying to: {RAG_SERVER_URL}")
    app.run(host='0.0.0.0', port=8888, debug=True)

