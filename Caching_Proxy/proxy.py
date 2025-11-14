import argparse
import sys
import http.server
import requests
import json
import os
import base64
from socketserver import ThreadingTCPServer
# --- Cache Configuration ---
CACHE_FILE = 'proxy_cache.json'

def load_cache():
    """Loads the cache from a JSON file."""
    if not os.path.exists(CACHE_FILE):
        return {}
    try:
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_cache(cache_data):
    """Saves the cache dictionary to a JSON file."""
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache_data, f, indent=4)

def clear_cache():
    """Deletes the cache file."""
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)
        print("Cache cleared successfully.")
    else:
        print("No cache file to clear.")

# --- Proxy Server Logic ---

def make_handler(origin_url):
    """
    Factory function to create a handler class that knows about the origin_url.
    """
    
    class CachingProxyHandler(http.server.BaseHTTPRequestHandler):
        
        def __init__(self, *args, **kwargs):
            self.origin_url = origin_url
            super().__init__(*args, **kwargs)

        def _handle_request(self):
            """Handles all HTTP methods (GET, POST, etc.)."""
            cache = load_cache()
            
            # Create a unique key for the request (method + path)
            cache_key = f"{self.command}:{self.path}"

            # --- 1. Check if the request is in the cache ---
            if cache_key in cache:
                print(f"CACHE HIT: {self.command} {self.path}")
                cached_data = cache[cache_key]
                
                # Send cached response
                self.send_response(cached_data['status_code'])
                self.send_header('X-Cache', 'HIT')
                
                # Send cached headers
                for key, value in cached_data['headers'].items():
                    self.send_header(key, value)
                self.end_headers()
                
                # Send cached content (decode from base64)
                content_bytes = base64.b64decode(cached_data['content_b64'])
                self.wfile.write(content_bytes)
                return

            # --- 2. If not in cache, forward the request ---
            print(f"CACHE MISS: {self.command} {self.path}")
            
            # Read request body if it exists (for POST, PUT)
            content_length = int(self.headers.get('Content-Length', 0))
            request_body = self.rfile.read(content_length)
            
            try:
                # Forward the request to the origin server
                response = requests.request(
                    method=self.command,
                    url=f"{self.origin_url}{self.path}",
                    headers=self.headers,
                    data=request_body,
                    allow_redirects=False # Important for proxying
                )

                # --- 3. Save the response to the cache ---
                
                # We can't cache all headers, e.g., 'Content-Encoding'
                # as 'requests' handles decompression for us.
                headers_to_cache = {
                    k: v for k, v in response.headers.items() 
                    if k.lower() not in ['content-encoding', 'transfer-encoding', 'connection']
                }

                cache_data = {
                    'status_code': response.status_code,
                    'headers': headers_to_cache,
                    # Store content as base64 to handle binary files (images, etc.)
                    'content_b64': base64.b64encode(response.content).decode('utf-8')
                }
                cache[cache_key] = cache_data
                save_cache(cache)

                # --- 4. Send the origin response back to the client ---
                self.send_response(response.status_code)
                self.send_header('X-Cache', 'MISS')
                
                # Send filtered headers
                for key, value in headers_to_cache.items():
                    self.send_header(key, value)
                self.end_headers()
                
                self.wfile.write(response.content)

            except requests.exceptions.RequestException as e:
                self.send_error(502, f"Proxy error: {e}")

        # Map all common HTTP methods to our handler
        do_GET = _handle_request
        do_POST = _handle_request
        do_PUT = _handle_request
        do_DELETE = _handle_request
        do_HEAD = _handle_request
        do_OPTIONS = _handle_request

    return CachingProxyHandler


# --- Main execution to handle CLI commands ---

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A simple caching proxy server.")
    
    # Add arguments
    parser.add_argument('--port', type=int, help="Port to run the proxy server on.")
    parser.add_argument('--origin', type=str, help="Origin server URL to forward requests to.")
    parser.add_argument('--clear-cache', action='store_true', help="Clear the cache file.")
    
    args = parser.parse_args()

    # --- Handle --clear-cache command ---
    if args.clear_cache:
        clear_cache()
        sys.exit()

    # --- Handle server start command ---
    if not args.port or not args.origin:
        print("Error: Both --port and --origin are required to start the server.")
        parser.print_help()
        sys.exit(1)

    # Start the server
    port = args.port
    origin = args.origin
    
    HandlerClass = make_handler(origin)
    httpd = ThreadingTCPServer(("", port), HandlerClass)
    
    print(f"Starting caching proxy for {origin} on http://localhost:{port} ...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()