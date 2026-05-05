"""로컬 개발 서버 — 정적 파일 서빙 + /api/weather 프록시"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.request
import urllib.parse
import ssl
import os
import re

API_KEY  = os.environ.get('KMA_API_KEY', 'JWmBKuA7QeepgSrgO2HnXw')
API_BASE = 'https://apihub.kma.go.kr/api/typ02/openApi/VilageFcstInfoService_2.0'

SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode    = ssl.CERT_NONE

ALLOWED = {'getUltraSrtNcst', 'getVilageFcst'}

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory='public', **kwargs)

    def do_GET(self):
        if self.path.startswith('/api/weather'):
            self._weather()
        else:
            super().do_GET()

    def _weather(self):
        try:
            qs       = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(self.path).query))
            endpoint = qs.pop('endpoint', '')
            if endpoint not in ALLOWED:
                self._send(400, b'{"error":"invalid endpoint"}')
                return

            qs['authKey'] = API_KEY
            url = f"{API_BASE}/{endpoint}?{urllib.parse.urlencode(qs)}"

            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=SSL_CTX, timeout=15) as r:
                body = r.read()
            self._send(200, body)

        except urllib.error.HTTPError as e:
            self._send(e.code, e.fp.read() if hasattr(e, 'fp') else b'{}')
        except Exception as e:
            self._send(500, f'{{"error":"{e}"}}'.encode())

    def _send(self, code, body):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass

if __name__ == '__main__':
    print('서버 시작: http://localhost:5500')
    HTTPServer(('', 5500), Handler).serve_forever()
