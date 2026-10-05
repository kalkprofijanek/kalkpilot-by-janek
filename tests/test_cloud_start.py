"""Exercise the documented cloud start command from outside the checkout."""
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]


class CloudStartTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.process = subprocess.Popen(
            [sys.executable, str(ROOT / 'scripts/dev.py'), '--host', '127.0.0.1', '--port', '0'],
            cwd=tempfile.gettempdir(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        first_line = cls.process.stdout.readline()
        match = re.search(r'port (\d+)', first_line)
        if not match:
            cls.process.terminate()
            cls.process.wait(timeout=5)
            raise RuntimeError('Development server did not report a port')
        cls.url = 'http://127.0.0.1:' + match.group(1)

    @classmethod
    def tearDownClass(cls):
        cls.process.terminate()
        cls.process.wait(timeout=5)
        cls.process.stdout.close()
        cls.process.stderr.close()

    def test_documented_healthcheck(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / 'scripts/check_ready.py'), '--url', self.url],
            cwd=tempfile.gettempdir(), capture_output=True, text=True, timeout=20,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('7 content checks', result.stdout)

    def test_current_static_assets_served(self):
        with urlopen(self.url + '/js/browser-review.js', timeout=10) as response:
            self.assertEqual(response.status, 200)
            self.assertIn('no-store', response.headers['Cache-Control'])
            self.assertIn('KPBrowserReview', response.read().decode())

    def test_hidden_repository_data_not_served(self):
        for path in ('/.git/config', '/%2egit/config'):
            for method in ('GET', 'HEAD'):
                with self.subTest(path=path, method=method):
                    with self.assertRaises(HTTPError) as result:
                        urlopen(Request(self.url + path, method=method), timeout=10)
                    self.assertEqual(result.exception.code, 404)


if __name__ == '__main__':
    unittest.main(verbosity=2)
