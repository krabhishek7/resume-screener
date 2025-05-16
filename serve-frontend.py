#!/usr/bin/env python3
"""
Simple HTTP server for the ResuMatch frontend
"""

import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path

# Default port
PORT = 8080

def main():
    """Start the server and open browser"""
    # Get frontend directory
    frontend_dir = Path(__file__).parent / 'frontend'
    
    if not frontend_dir.exists():
        print(f"Error: Frontend directory not found at {frontend_dir}")
        sys.exit(1)
        
    # Change to frontend directory
    os.chdir(frontend_dir)
    
    handler = http.server.SimpleHTTPRequestHandler
    
    # Create the server
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"Serving ResuMatch frontend at http://localhost:{PORT}")
        print("Press Ctrl+C to stop the server")
        
        # Open browser
        webbrowser.open(f"http://localhost:{PORT}")
        
        # Serve until interrupted
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped")

if __name__ == "__main__":
    main() 