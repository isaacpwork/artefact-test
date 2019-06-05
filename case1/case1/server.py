from http.server import BaseHTTPRequestHandler, HTTPServer
from db import CommentsDb
from urllib.parse import parse_qs
import json

# Handler for displaying results
class Handler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()

    def do_GET(self):
        self._set_headers()

        params = parse_qs(self.path.split('?')[-1])

        if 'keyword' in params:
            comments_db = CommentsDb()
            comments_db.connect()

            # Search in comment content for keyword
            results = comments_db.select(params['keyword'][0])
            self.wfile.write(str(results).encode('utf-8'))

PORT = 8000

httpd = HTTPServer(('', PORT), Handler)

print("serving at port", PORT)
httpd.serve_forever()