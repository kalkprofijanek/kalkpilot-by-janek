"""Prepare and validate LLM matching files by running the real app in a cloud browser.

The Codex/Claude Code agent makes the semantic decisions between these commands.
This script does not invoke a model or replace those decisions with a text score.
"""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import shutil
from threading import Thread

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['prepare', 'check'])
    parser.add_argument('--references', required=True, type=Path)
    parser.add_argument('--lv', required=True, type=Path)
    parser.add_argument('--output-dir', required=True, type=Path)
    parser.add_argument('--response', type=Path)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if output == ROOT or ROOT in output.parents:
        parser.error('Output must be outside the repository; customer files must not enter Git.')
    for path in [args.references, args.lv] + ([args.response] if args.response else []):
        if not path.is_file():
            parser.error(f'File does not exist: {path}')
    if args.action == 'check' and not args.response:
        parser.error('check requires --response')
    output.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault('PLAYWRIGHT_BROWSERS_PATH', str(ROOT / '.cache/ms-playwright'))
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT)))
    Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as playwright:
            executable = os.environ.get('KALKPILOT_CHROMIUM') or shutil.which('chromium')
            browser = playwright.chromium.launch(**({'executable_path': executable} if executable else {}))
            try:
                page = browser.new_page()
                base = f'http://127.0.0.1:{server.server_port}'
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.route('**/*', lambda route: route.continue_() if
                           route.request.url.startswith(base + '/') else route.abort())
                page.goto(base + '/KalkPilot_by_Janek.html')
                page.evaluate('referenceStorageReady')
                # Await the actual import function rather than a timing-dependent UI event.
                ref_text = args.references.read_text(encoding='utf-8-sig')
                page.evaluate('async text => importRefFromJSON(new File([text], "references.json"))', ref_text)
                if not page.evaluate('getActiveRef().length'):
                    raise RuntimeError('No active reference positions imported.')
                page.locator('#fNew').set_input_files(str(args.lv.resolve()))
                page.wait_for_function("document.getElementById('lvImportStatus').textContent !== 'LV wird eingelesen …'", timeout=60000)
                if not page.evaluate('S.newLV.length'):
                    raise RuntimeError(page.locator('#lvImportStatus').inner_text() or 'No LV positions imported.')
                if args.action == 'prepare':
                    request = page.evaluate('async () => (await getLLMMatchingContext()).request')
                    if errors:
                        raise RuntimeError('Browser errors: ' + '; '.join(errors))
                    request_path = output / 'matching-request.json'
                    request_path.write_text(json.dumps(request, ensure_ascii=False, indent=2), encoding='utf-8')
                    print(f'Request: {request_path}')
                    print(f'Targets: {len(request["zielpositionen"])}; references: {len(request["referenzen"])}')
                else:
                    response_text = args.response.read_text(encoding='utf-8-sig')
                    page.evaluate('async text => importLLMMatches(new File([text], "response.json"))', response_text)
                    status = page.locator('#llmMatchingStatus').inner_text()
                    if status.startswith('LLM-Ergebnis nicht übernommen:'):
                        raise RuntimeError(status)
                    if errors:
                        raise RuntimeError('Browser errors: ' + '; '.join(errors))
                    summary = page.evaluate('''() => ({
                      positions:S.results.length,
                      suggested:S.results.filter(r=>r.matches.length).length,
                      accepted:S.results.filter(r=>r.accepted).length,
                      priceApproval:false
                    })''')
                    (output / 'validation.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
                    destination = output / 'verified-response.json'
                    if args.response.resolve() != destination:
                        shutil.copyfile(args.response, destination)
                    print(f'Validated response: {destination}')
                    print(json.dumps(summary))
                if errors:
                    raise RuntimeError('Browser errors: ' + '; '.join(errors))
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()


if __name__ == '__main__':
    main()
