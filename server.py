import http.server
import urllib.request
import urllib.error
import json
import os

PORT = 5000

ROBLOX_USER_ID = 4797411364

class Handler(http.server.SimpleHTTPRequestHandler):

    def end_headers(self):
        # Không cache HTML để luôn nhận code mới nhất
        if hasattr(self, '_headers_buffer'):
            pass
        if self.path in ('/', '/index.html'):
            self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def do_GET(self):
        if self.path == '/api/roblox':
            self._proxy_roblox()
        elif self.path == '/api/roblox-avatar':
            self._proxy_roblox_avatar()
        elif self.path == '/api/roblox-presence':
            self._proxy_roblox_presence()
        elif self.path == '/api/discord':
            self._proxy_url('https://dragonbot-omgj.onrender.com/status')
        elif self.path == '/api/youtube':
            self._scrape_youtube()
        elif self.path.startswith('/api/img?url='):
            self._proxy_image(self.path[len('/api/img?url='):])
        elif self.path.startswith('/api/stream/video?url='):
            self._stream_yt('video', self.path[len('/api/stream/video?url='):])
        elif self.path.startswith('/api/stream/audio?url='):
            self._stream_yt('audio', self.path[len('/api/stream/audio?url='):])
        else:
            super().do_GET()

    def _stream_yt(self, mode, encoded_url):
        import urllib.parse, yt_dlp
        url = urllib.parse.unquote(encoded_url)
        # Local file — redirect thẳng
        if not url.startswith('http'):
            self.send_response(302)
            self.send_header('Location', '/' + url.lstrip('/'))
            self.end_headers()
            return
        # YouTube — dùng yt-dlp lấy direct stream URL rồi redirect
        try:
            fmt = 'bestaudio[ext=webm]/bestaudio/best' if mode == 'audio' else 'bestvideo[ext=mp4]+bestaudio/best[ext=mp4]/best'
            ydl_opts = {
                'format': fmt,
                'quiet': True,
                'no_warnings': True,
                'noplaylist': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                # audio mode → lấy url của audio stream
                if mode == 'audio':
                    stream_url = info.get('url') or info['requested_formats'][0]['url']
                else:
                    # video mode → ưu tiên format đã merge, fallback format đầu tiên
                    formats = info.get('requested_formats') or [info]
                    stream_url = formats[0].get('url', info.get('url'))
            self.send_response(302)
            self.send_header('Location', stream_url)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
        except Exception as e:
            self.send_response(502)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def _proxy_image(self, encoded_url):
        import urllib.parse
        url = urllib.parse.unquote(encoded_url)
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=8) as r:
                content_type = r.headers.get('Content-Type', 'image/png')
                data = r.read()
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'public, max-age=3600')
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            self.send_response(502)
            self.end_headers()

    def _proxy_url(self, url):
        try:
            with urllib.request.urlopen(url, timeout=8) as r:
                data = r.read()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(data)
        except urllib.error.URLError as e:
            self.send_response(502)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def _proxy_roblox_presence(self):
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

    def _proxy_roblox_avatar(self):
        url = f'https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={ROBLOX_USER_ID}&size=420x420&format=Png&isCircular=false'
        try:
            with urllib.request.urlopen(url, timeout=5) as r:
                data = r.read()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(data)
        except urllib.error.URLError as e:
            self.send_response(502)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def _scrape_youtube(self):
        import re
        url = 'https://www.youtube.com/channel/UCq_xLp1bKDhav_3EyLwLc3A/about'
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
            })
            with urllib.request.urlopen(req, timeout=10) as r:
                html = r.read().decode('utf-8', errors='ignore')

            m = re.search(r'var ytInitialData = ({.*?});</script>', html, re.DOTALL)
            if not m:
                raise ValueError('ytInitialData not found')
            data = json.loads(m.group(1))
            pm = data['header']['pageHeaderRenderer']['content']['pageHeaderViewModel']

            # Tên kênh
            author = pm.get('title', {}).get('dynamicTextViewModel', {}).get('text', {}).get('content', '')

            # Avatar thumbnails
            sources = (pm.get('image', {})
                         .get('decoratedAvatarViewModel', {})
                         .get('avatar', {})
                         .get('avatarViewModel', {})
                         .get('image', {})
                         .get('sources', []))
            author_thumbnails = [{'url': s['url'], 'width': s.get('width', 0)} for s in sources]

            # Subscriber count (lấy từ metadataRows)
            sub_count = 0
            rows = pm.get('metadata', {}).get('contentMetadataViewModel', {}).get('metadataRows', [])
            for row in rows:
                for part in row.get('metadataParts', []):
                    text = part.get('text', {}).get('content', '')
                    sub_m = re.match(r'^([\d,\.]+)\s+subscriber', text, re.IGNORECASE)
                    if sub_m:
                        sub_count = int(sub_m.group(1).replace(',', '').replace('.', ''))

            # Description
            description = (pm.get('description', {})
                             .get('descriptionPreviewViewModel', {})
                             .get('description', {})
                             .get('content', ''))

            # Video count + handle từ metadataRows
            video_count = 0
            handle = ''
            for row in rows:
                for part in row.get('metadataParts', []):
                    text = part.get('text', {}).get('content', '')
                    if text.startswith('@'):
                        handle = text
                    vid_m = re.match(r'^([\d,\.]+)\s+video', text, re.IGNORECASE)
                    if vid_m:
                        video_count = int(vid_m.group(1).replace(',', '').replace('.', ''))

            result = json.dumps({
                'author': author,
                'subCount': sub_count,
                'videoCount': video_count,
                'handle': handle,
                'description': description,
                'authorThumbnails': author_thumbnails,
            }).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(result)
        except Exception as e:
            self.send_response(502)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def _proxy_roblox(self):
        url = f'https://users.roblox.com/v1/users/{ROBLOX_USER_ID}'
        try:
            with urllib.request.urlopen(url, timeout=5) as r:
                data = r.read()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(data)
        except urllib.error.URLError as e:
            self.send_response(502)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def log_message(self, fmt, *args):
        print(fmt % args)

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with http.server.ThreadingHTTPServer(('', PORT), Handler) as httpd:
        print(f'Server chạy tại http://0.0.0.0:{PORT}')
        httpd.serve_forever()
