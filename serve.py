"""
Simple HTTP Server for QIE Nexus Frontend
Serves the frontend on http://localhost:8080
This allows MetaMask extension to work properly
"""

import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

# Configuration
PORT = 8080
DIRECTORY = Path(__file__).parent / "frontend"

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)
    
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def main():
    print("=" * 60)
    print("QIE Nexus - Frontend Server")
    print("=" * 60)
    print()
    print(f"Serving directory: {DIRECTORY}")
    print(f"Server URL: http://localhost:{PORT}")
    print()
    print("Available Pages:")
    print(f"   - Home:       http://localhost:{PORT}/index.html")
    print(f"   - Dashboard:  http://localhost:{PORT}/dashboard.html")
    print(f"   - Portfolio:  http://localhost:{PORT}/portfolio.html")
    print(f"   - Governance: http://localhost:{PORT}/governance.html")
    print()
    print("MetaMask extension will work properly on http://")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    print()
    
    # Start server
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        # Open browser
        webbrowser.open(f"http://localhost:{PORT}/index.html")
        
        print(f"Server started successfully!")
        print(f"Opening http://localhost:{PORT}/index.html in your browser...")
        print()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\nServer stopped by user")
            print("=" * 60)

if __name__ == "__main__":
    main()
