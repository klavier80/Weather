from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import ssl
import sys
import os
import re

API_KEY  = os.environ.get('KMA_API_KEY', 'JWmBKuA7QeepgSrgO2HnXw')
API_BASE = 'https://apihub.kma.go.kr/api/typ02/openApi/VilageFcstInfoService_2.0'

SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode    = ssl.CERT_NONE

ALLOWED_ENDPOINTS = {'getUltraSrtNcst', 'getVilageFcst'}

def _validate(qs: dict) -> str | None:
    """파라미터 유효성 검사. 오류 메시지 반환, 정상이면 None."""
    nx = qs.get('nx', '')
    ny = qs.get('ny', '')
    if not (nx.isdigit() and ny.isdigit()):
        return 'nx/ny must be integers'
    if not (1 <= int(nx) <= 149 and 1 <= int(ny) <= 253):
        return 'nx/ny out of Korea grid range'

    base_date = qs.get('base_date', '')
    if not re.fullmatch(r'\d{8}', base_date):
        return 'base_date must be YYYYMMDD'

    base_time = qs.get('base_time', '')
    if not re.fullmatch(r'\d{4}', base_time):
        return 'base_time must be HHMM'

    num = qs.get('numOfRows', '1000')
    if not (num.isdigit() and 1 <= int(num) <= 1000):
        return 'numOfRows must be 1–1000'

    if qs.get('dataType', 'JSON') != 'JSON':
        return 'dataType must be JSON'

    return None

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            qs       = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(self.path).query))
            endpoint = qs.pop('endpoint', '')
            if endpoint not in ALLOWED_ENDPOINTS:
                self._send(400, b'{"error":"invalid endpoint"}')
                return

            err = _validate(qs)
            if err:
                self._send(400, f'{{"error":"{err}"}}'.encode())
                return

            qs['authKey'] = API_KEY
            url = f"{API_BASE}/{endpoint}?{urllib.parse.urlencode(qs)}"
            print(f"[weather] {endpoint}", file=sys.stderr)

            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=SSL_CTX, timeout=15) as r:
                body = r.read()

            self._send(200, body)

        except Exception as e:
            print(f"[weather] error: {e}", file=sys.stderr)
            self._send(500, b'{"error":"upstream request failed"}')

    def _send(self, code, body):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass
