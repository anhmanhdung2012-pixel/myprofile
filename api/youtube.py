from http.server import BaseHTTPRequestHandler
import urllib.request
import json
import re

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            url = 'https://www.youtube.com/channel/UCq_xLp1bKDhav_3EyLwLc3A/about'
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

            author = pm.get('title', {}).get('dynamicTextViewModel', {}).get('text', {}).get('content', '')
            sources = (pm.get('image', {})
                         .get('decoratedAvatarViewModel', {})
                         .get('avatar', {})
                         .get('avatarViewModel', {})
                         .get('image', {})
                         .get('sources', []))
            author_thumbnails = [{'url': s['url'], 'width': s.get('width', 0)} for s in sources]

            sub_count = 0
            rows = pm.get('metadata', {}).get('contentMetadataViewModel', {}).get('metadataRows', [])
            for row in rows:
                for part in row.get('metadataParts', []):
                    text = part.get('text', {}).get('content', '')
                    sub_m = re.match(r'^([\d,\.]+)\s+subscriber', text, re.IGNORECASE)
                    if sub_m:
                        sub_count = int(sub_m.group(1).replace(',', '').replace('.', ''))

            description = (pm.get('description', {})
                             .get('descriptionPreviewViewModel', {})
                             .get('description', {})
                             .get('content', ''))
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

    def log_message(self, fmt, *args):
        pass
