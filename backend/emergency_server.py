"""
EMERGENCY MINIMAL SERVER - Absolutely no dependencies except standard library
Use this if all other solutions fail
"""
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class MinimalHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        # Health check
        if path in ['/api/health', '/health']:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                "status": "healthy",
                "version": "1.0.0",
                "server": "emergency_minimal",
                "message": "Emergency server running - no dependencies"
            }
            self.wfile.write(json.dumps(response).encode())
            return
        
        # Status check
        if path in ['/api/status', '/status', '/api/', '/']:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                "status": "ok",
                "environment": os.getenv("ENVIRONMENT", "production"),
                "server": "emergency_minimal",
                "message": "Flow Invest API - Emergency Mode"
            }
            self.wfile.write(json.dumps(response).encode())
            return
        
        # Supported exchanges
        if path == '/api/exchange-keys/supported-exchanges':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                "success": True,
                "exchanges": [
                    {
                        "id": "bybit",
                        "name": "Bybit",
                        "supports_testnet": True,
                        "message": "Emergency mode - limited functionality"
                    }
                ]
            }
            self.wfile.write(json.dumps(response).encode())
            return
        
        # Default 404
        self.send_response(404)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        response = {"error": "Not found", "path": path}
        self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        # Handle CORS preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        
        response = {
            "success": False,
            "message": "Emergency server mode - POST endpoints not available",
            "instructions": "Please deploy full server for complete functionality"
        }
        self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        # Handle CORS preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress default logging
        print(f"[{self.address_string()}] {format % args}")

def run_emergency_server():
    port = int(os.getenv('PORT', 8001))
    server = HTTPServer(('0.0.0.0', port), MinimalHandler)
    
    print(f"🚨 EMERGENCY MINIMAL SERVER STARTED")
    print(f"Port: {port}")
    print(f"Environment: {os.getenv('ENVIRONMENT', 'production')}")
    print(f"Mode: EMERGENCY - No external dependencies")
    print(f"Health check: http://localhost:{port}/api/health")
    print("This server uses ONLY Python standard library!")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down emergency server...")
        server.shutdown()

if __name__ == '__main__':
    run_emergency_server()