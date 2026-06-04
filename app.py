from http.server import HTTPServer, BaseHTTPRequestHandler
import os

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(f"Hello from {os.environ.get('APP_ENV', 'development')} - port {os.environ.get('APP_PORT', '8000')}".encode())

    def log_message(self, format, *args):
        pass

httpd = HTTPServer(('0.0.0.0', int(os.environ.get('APP_PORT', '8000'))), Handler)
httpd.serve_forever()
