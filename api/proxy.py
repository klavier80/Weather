from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import urllib.error
import ssl
import sys

API_HUB = 'https://apihub.kma.go.kr'
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            parsed = urllib.parse.urlparse(self.path)
            qs = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)

            path = qs.pop('path', ['/'])[0]
            query = urllib.parse.urlencode({k: v[0] for k, v in qs.items()})
            url = f"{API_HUB}{path}?{query}"

            print(f"[proxy] → {url}", file=sys.stderr)

            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=SSL_CTX, timeout=15) as r:
                body = r.read()

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(body)

        except urllib.error.HTTPError as e:
            body = e.fp.read() if hasattr(e, 'fp') else b'{}'
            print(f"[proxy] HTTPError {e.code}: {body[:200]}", file=sys.stderr)
            self.send_response(e.code)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(body)

        except Exception as e:
            print(f"[proxy] Exception: {e}", file=sys.stderr)
            msg = str(e).encode()
            self.send_response(500)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(msg)

    def log_message(self, fmt, *args):
        pass
