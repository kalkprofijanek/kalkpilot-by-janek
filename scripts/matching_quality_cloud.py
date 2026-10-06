"""Measure curated synthetic matching cases; this is not an LLM accuracy benchmark."""
import argparse
from functools import partial
from http.server import ThreadingHTTPServer
import json
import os
from pathlib import Path
import shutil
import subprocess
from threading import Thread
from playwright.sync_api import sync_playwright
from llm_matching_cloud import ROOT, QuietHandler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',required=True,type=Path)
    parser.add_argument('--baseline-ref',help='Optional local Git revision for technical-profile comparison')
    args=parser.parse_args()
    out=args.output_dir.resolve()
    if out==ROOT or ROOT in out.parents:
        parser.error('Output must be outside the repository.')
    out.mkdir(parents=True,exist_ok=True)
    cases=json.loads((ROOT/'tests/fixtures/matching-quality.json').read_text())
    source=(ROOT/'js/llm-matching.js').read_text()
    baseline=None
    if args.baseline_ref:
        baseline=subprocess.run(['git','show',args.baseline_ref+':js/llm-matching.js'],cwd=ROOT,
            capture_output=True,text=True,check=True).stdout
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(ROOT)))
    Thread(target=server.serve_forever,daemon=True).start()
    os.environ.setdefault('PLAYWRIGHT_BROWSERS_PATH',str(ROOT/'.cache/ms-playwright'))
    try:
        with sync_playwright() as playwright:
            executable=os.environ.get('KALKPILOT_CHROMIUM') or shutil.which('chromium')
            browser=playwright.chromium.launch(**({'executable_path':executable} if executable else {}))
            try:
                page=browser.new_page();base=f'http://127.0.0.1:{server.server_port}'
                errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
                page.route('**/*',lambda route:route.continue_() if route.request.url.startswith(base+'/') else route.abort())
                page.goto(base+'/KalkPilot_by_Janek.html');page.evaluate('referenceStorageReady')
                def measure(script):
                    page.evaluate('source => (0,eval)(source)',script)
                    rows=page.evaluate('''cases=>cases.map(c=>{
                      const check=KPLLMMatching.compareRequirements(c.a,c.b),scored=calcScore(c.a,c.b);
                      const observed=check.conflicts.length?'conflict':check.missing.length?'incomplete':'consistent';
                      return {name:c.name,expected:c.expected,observed,ok:observed===c.expected,
                        score:scored.score,conflicts:check.conflicts,missing:check.missing};
                    })''',cases)
                    return {'correct':sum(row['ok'] for row in rows),'total':len(rows),'rows':rows}
                report={'kind':'curated-synthetic-regression','baselineRef':args.baseline_ref,
                    'baseline':measure(baseline) if baseline else None,'current':measure(source),
                    'limitation':'Technical requirement checks on curated cases; not independent expert validation or LLM accuracy.'}
                if errors:raise RuntimeError('; '.join(errors))
                (out/'matching-quality.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
                for key in ['baseline','current']:
                    if report[key]:print(f'{key}: {report[key]["correct"]}/{report[key]["total"]} correct classifications')
                if not all(row['ok'] for row in report['current']['rows']):raise SystemExit('Matching quality cases failed')
            finally:browser.close()
    finally:server.shutdown();server.server_close()


if __name__=='__main__':main()
