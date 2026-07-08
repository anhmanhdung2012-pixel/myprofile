from http.server import BaseHTTPRequestHandler
import urllib.request
import json

ROBLOX_USER_ID = 4797411364

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = 'https://presence.roblox.com/v1/presence/users'
        body = json.dumps({'userIds': [ROBLOX_USER_ID]}).encode()
        try:
            req = urllib.request.Request(url, data=body, headers={'Content-Type': 'application/json'}, method='POST')
            with urllib.request.urlopen(req, timeout=5) as r:
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
