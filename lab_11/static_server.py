import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HOST = "127.0.0.1"
PORT = 8080
MAX_AGE = 3600
ROOT = Path(__file__).resolve().parent / "static"


# Локальная имитация CDN: отдельный сервер статического контента
# с заголовками Cache-Control, ETag и поддержкой условных запросов (304).
class CdnHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        self._etag = None
        file_path = self.translate_path(self.path)
        if os.path.isfile(file_path):
            stat = os.stat(file_path)
            self._etag = f'"{int(stat.st_mtime)}-{stat.st_size}"'
            if self.headers.get("If-None-Match") == self._etag:
                self.send_response(304)
                self.send_header("ETag", self._etag)
                self.send_header("Cache-Control", f"public, max-age={MAX_AGE}")
                self.end_headers()
                return
        super().do_GET()

    def end_headers(self):
        self.send_header("Cache-Control", f"public, max-age={MAX_AGE}")
        self.send_header("X-CDN-Node", "local-edge-1")
        if getattr(self, "_etag", None):
            self.send_header("ETag", self._etag)
        super().end_headers()

    def log_message(self, fmt, *args):
        print(f"[CDN] {self.address_string()} {fmt % args}", flush=True)


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), CdnHandler)
    print(f"CDN-сервер запущен на http://{HOST}:{PORT}/", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    main()
