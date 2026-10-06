"""Check application content and all browser dependencies on the development server."""
import argparse
import os
from urllib.request import urlopen

CHECKS = {
    '/': 'KalkPilot_by_Janek.html',
    '/KalkPilot_by_Janek.html': 'downloadBrowserReview',
    '/KalkPilot_Referenzpaket_Builder.html': 'KalkPilot Referenzpaket Builder',
    '/vendor/dexie/dexie.js': 'Dexie',
    '/js/reference-store.js': 'KPReferenceStore',
    '/js/gaeb-encoding.js': 'KPGaebEncoding',
    '/js/browser-review.js': 'KPBrowserReview',
    '/js/llm-matching.js': 'KPLLMMatching',
    '/js/copilot-exchange.js': 'KPCopilotExchange',
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='http://127.0.0.1:' + os.environ.get('KALKPILOT_PORT', '8000'))
    args = parser.parse_args()
    for path, expected in CHECKS.items():
        with urlopen(args.url.rstrip('/') + path, timeout=10) as response:
            if response.status != 200 or expected not in response.read().decode('utf-8'):
                raise SystemExit(f'Application readiness failed: {path}')
    print(f'Application readiness passed: {len(CHECKS)} content checks')


if __name__ == '__main__':
    main()
