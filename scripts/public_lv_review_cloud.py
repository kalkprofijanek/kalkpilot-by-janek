"""Audit local public X83 files through the real upload flow and prepare text references.

No network access or model calls. Source files and all outputs stay outside Git.
The resulting references contain tender texts, never invented calculation data.
"""
import argparse
from collections import Counter
from decimal import Decimal
from functools import partial
import hashlib
from http.server import ThreadingHTTPServer
import json
import os
from pathlib import Path
import shutil
from threading import Thread
import xml.etree.ElementTree as ET

from playwright.sync_api import sync_playwright
from llm_matching_cloud import ROOT, QuietHandler


def local(element):
    return element.tag.rsplit('}', 1)[-1]


def normalized(value):
    return ' '.join(str(value or '').split())


def plain_text(element):
    """Keep block and explicit line-break boundaries, including compact GAEB XML."""
    if element is None:
        return ''
    def collect(node):
        chunks = [node.text or '']
        for child in node:
            block = local(child).lower() in {'p', 'div', 'br', 'tr', 'td', 'li'}
            if block:
                chunks.append(' ')
            chunks.append(collect(child))
            if block:
                chunks.append(' ')
            chunks.append(child.tail or '')
        return ''.join(chunks)
    return normalized(collect(element))


def source_positions(path):
    root = ET.parse(path).getroot()
    if local(root) != 'GAEB':
        raise ValueError('Expected a GAEB XML document.')
    parents = {child: parent for parent in root.iter() for child in parent}

    def first(element, tag):
        return next((child for child in element.iter() if local(child) == tag), None)

    rows = []
    for item in root.iter():
        if local(item) != 'Item':
            continue
        parts = [item.attrib.get('RNoPart', '').strip()]
        titles = []
        parent = parents.get(item)
        while parent is not None:
            if local(parent) == 'BoQCtgy':
                parts.insert(0, parent.attrib.get('RNoPart', '').strip())
                label = next((c for c in parent if local(c) == 'LblTx'), None)
                if plain_text(label):
                    titles.insert(0, plain_text(label))
            parent = parents.get(parent)
        short = plain_text(first(item, 'OutlineText'))
        long = plain_text(first(item, 'DetailTxt'))
        qty = first(item, 'Qty')
        unit = first(item, 'QU')
        rows.append({'originalXref': item.attrib.get('ID'),
            'oz': ' '.join(p for p in parts if p), 'titlePath': ' > '.join(titles),
            'kurztext': short or (long[:80] + '...' if len(long) > 80 else long),
            'langtext': long or short,
            'menge': float(Decimal(normalized(qty.text if qty is not None else '0').replace(',', '.'))),
            'me': normalized(unit.text if unit is not None else '')})
    return rows


def compare_import(expected, actual):
    mismatches = []
    if len(expected) != len(actual):
        mismatches.append({'field': 'positions', 'expected': len(expected), 'actual': len(actual)})
    for index, (source, imported) in enumerate(zip(expected, actual)):
        for field in ['originalXref', 'oz', 'titlePath', 'kurztext', 'langtext', 'menge', 'me']:
            value = source[field]
            if field == 'me':
                value = {'m²': 'm2', 'm³': 'm3', 'mü': 'm3', 'mu': 'm3'}.get(value, value)
            if imported.get(field) != value:
                mismatches.append({'index': index, 'oz': source['oz'], 'field': field,
                    'expected': value, 'actual': imported.get(field)})
    return mismatches


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', required=True, type=Path,
        help='JSON list with unique name, absolute file path and sourceUrl for each project.')
    parser.add_argument('--output-dir', required=True, type=Path)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if output == ROOT or ROOT in output.parents:
        parser.error('Public source texts and outputs must remain outside the repository.')
    manifest = json.loads(args.manifest.read_text(encoding='utf-8-sig'))
    if not isinstance(manifest, list) or not manifest:
        parser.error('Manifest must be a nonempty JSON list.')
    names = set()
    for entry in manifest:
        if not entry.get('name') or entry['name'] in names or not entry.get('sourceUrl'):
            parser.error('Each project needs a unique name and a sourceUrl.')
        names.add(entry['name'])
        path = Path(entry['file']).resolve()
        if not path.is_file() or path == ROOT or ROOT in path.parents:
            parser.error('Source X83 files must exist outside the repository.')
        entry['file'] = str(path)
    output.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT)))
    Thread(target=server.serve_forever, daemon=True).start()
    os.environ.setdefault('PLAYWRIGHT_BROWSERS_PATH', str(ROOT / '.cache/ms-playwright'))
    reports, projects = [], []
    try:
        with sync_playwright() as playwright:
            executable = os.environ.get('KALKPILOT_CHROMIUM') or shutil.which('chromium')
            browser = playwright.chromium.launch(**({'executable_path': executable} if executable else {}))
            try:
                for entry in manifest:
                    path = Path(entry['file'])
                    expected = source_positions(path)
                    context = browser.new_context()
                    page = context.new_page()
                    errors = []
                    page.on('pageerror', lambda error: errors.append(str(error)))
                    base = f'http://127.0.0.1:{server.server_port}'
                    page.route('**/*', lambda route: route.continue_() if
                        route.request.url.startswith(base + '/') else route.abort())
                    page.goto(base + '/KalkPilot_by_Janek.html')
                    page.evaluate('referenceStorageReady')
                    page.locator('#fNew').set_input_files(str(path))
                    page.wait_for_function("S.newLV.length > 0 || document.getElementById('lvImportStatus').textContent.startsWith('Fehler')", timeout=60000)
                    actual = page.evaluate('S.newLV')
                    mismatches = compare_import(expected, actual)
                    counts = Counter(normalized(p['oz']) for p in actual)
                    report = {**entry, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                        'xmlItems': len(expected), 'importedItems': len(actual),
                        'checkedFieldsPerItem': 7, 'mismatches': mismatches, 'browserErrors': errors,
                        'duplicateOZ': [oz for oz, count in counts.items() if count > 1],
                        'emptyShortTexts': sum(not p['kurztext'] for p in actual),
                        'emptyLongTexts': sum(not p['langtext'] for p in actual),
                        'missingUnits': sum(not p['me'] for p in actual),
                        'categories': dict(Counter(page.evaluate('rows => rows.map(positionCategory)', actual))),
                        'priceApproval': False}
                    report['passed'] = bool(expected) and not (mismatches or errors or report['duplicateOZ'])
                    reports.append(report)
                    projects.append({'name': entry['name'], 'active': True,
                        'positions': [{**p, 'source': entry['name']} for p in actual]})
                    (output / 'import-audit.json').write_text(json.dumps(reports, ensure_ascii=False, indent=2))
                    print(json.dumps({k: report[k] for k in ['name', 'xmlItems', 'importedItems', 'passed', 'categories']}, ensure_ascii=False), flush=True)
                    context.close()
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
    if not all(report['passed'] for report in reports):
        raise SystemExit('Import audit failed; inspect import-audit.json before preparing comparisons.')
    (output / 'textreferenzen.json').write_text(json.dumps(projects, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
