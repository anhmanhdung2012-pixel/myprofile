from http.server import BaseHTTPRequestHandler
import urllib.request
import json

ROBLOX_USER_ID = 4797411364

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = f'https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={ROBLOX_USER_ID}&size=420x420&format=Png&isCircular=false'
        try:
            with urllib.request.urlopen(url, timeout=5) as r:
                data = r.read()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            self.send_response(502)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def log_message(self, fmt, *args):
        pass
