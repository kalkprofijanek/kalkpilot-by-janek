"""Start the static application inside Codex Cloud, Claude Code Web or Codespaces."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


class DevelopmentHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # Development must display current files after an edit.
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def send_head(self):
        path = unquote(urlsplit(self.path).path)
        if any(part.startswith('.') for part in path.split('/')):
            self.send_error(404)
            return None
        return super().send_head()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', default=os.environ.get('KALKPILOT_HOST', '0.0.0.0'))
    parser.add_argument('--port', type=int, default=int(os.environ.get('KALKPILOT_PORT', '8000')))
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), partial(DevelopmentHandler, directory=str(ROOT)))
    print(f'KalkPilot development server: port {server.server_port}; root {ROOT}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
