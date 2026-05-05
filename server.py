"""
날씨 웹사이트 서버
- 정적 파일 서빙 (weather.html 등)
- /proxy/ → 기상청 API Hub 프록시 (CORS 우회)
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.request
import urllib.error
import ssl

API_HUB = 'https://apihub.kma.go.kr'
# 기상청 API Hub 자체서명 인증서 허용
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/proxy/'):
            self._proxy(API_HUB + self.path[6:])  # /proxy → '' 제거 후 /api/... 유지
        else:
            super().do_GET()

    def _proxy(self, url):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=SSL_CTX, timeout=10) as r:
                body = r.read()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(body)
        except urllib.error.HTTPError as e:
            body = e.fp.read() if hasattr(e, 'fp') else b'{}'
            self.send_response(e.code)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(body)
        except Exception as e:
            self.send_response(500)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(str(e).encode())

    def log_message(self, fmt, *args):
        pass  # 로그 출력 억제

if __name__ == '__main__':
    print('서버 시작: http://localhost:5500')
    HTTPServer(('', 5500), Handler).serve_forever()
