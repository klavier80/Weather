from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import ssl
import sys

API_KEY  = 'JWmBKuA7QeepgSrgO2HnXw'
API_BASE = 'https://apihub.kma.go.kr/api/typ02/openApi/VilageFcstInfoService_2.0'

SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode    = ssl.CERT_NONE

ALLOWED = {'getUltraSrtNcst', 'getVilageFcst'}

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            qs       = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(self.path).query))
            endpoint = qs.pop('endpoint', '')
            if endpoint not in ALLOWED:
                self._send(400, b'{"error":"invalid endpoint"}')
                return

            qs['authKey'] = API_KEY
            url = f"{API_BASE}/{endpoint}?{urllib.parse.urlencode(qs)}"
            print(f"[weather] {url}", file=sys.stderr)

            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=SSL_CTX, timeout=15) as r:
                body = r.read()

            self._send(200, body)

        except Exception as e:
            print(f"[weather] error: {e}", file=sys.stderr)
            self._send(500, f'{{"error":"{e}"}}'.encode())

    def _send(self, code, body):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass
