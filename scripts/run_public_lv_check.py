"""Download pinned public LVs and run the actual import and cross-project review.

Original files and full reports are written outside the repository. summary.json
contains only provenance and counts and is suitable for the CI artifact.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import urlparse
from urllib.request import urlopen
from zipfile import ZipFile, is_zipfile

from llm_matching_cloud import ROOT

DOWNLOAD_LIMIT = 30 * 1024 * 1024
XML_LIMIT = 8 * 1024 * 1024


def validate_sources(sources):
    if not isinstance(sources, list) or len(sources) < 2:
        raise ValueError('At least two pinned public source projects are required.')
    names, filenames = set(), set()
    for source in sources:
        name, filename = source.get('name'), source.get('fileName', '')
        if not name or name in names or not filename or filename in filenames:
            raise ValueError('Source project names and filenames must be unique.')
        if (Path(filename).name != filename or '/' in filename or '\\' in filename
                or Path(filename).suffix.lower() != '.x83'):
            raise ValueError('Source filename must be a plain X83 filename without a path.')
        if not re.fullmatch(r'[a-f0-9]{64}', source.get('sha256', '')):
            raise ValueError('Each source needs a pinned SHA-256.')
        if not isinstance(source.get('expectedItems'), int) or source['expectedItems'] < 1:
            raise ValueError('Each source needs a positive expectedItems count.')
        for key in ['sourceUrl', 'downloadUrl']:
            url = urlparse(source.get(key, ''))
            if url.scheme != 'https' or not url.hostname or url.username or url.password:
                raise ValueError('Public sources must use HTTPS URLs without credentials.')
        names.add(name)
        filenames.add(filename)


def unpack_download(data, source):
    if len(data) > DOWNLOAD_LIMIT:
        raise ValueError('Public download exceeds the configured size limit.')
    if is_zipfile(io.BytesIO(data)):
        with ZipFile(io.BytesIO(data)) as archive:
            name = source.get('archiveEntry')
            if not name:
                matches = [i.filename for i in archive.infolist()
                    if Path(i.filename).name == source['fileName']]
                if len(matches) != 1:
                    raise ValueError('Download must contain exactly one expected LV file.')
                name = matches[0]
            if archive.getinfo(name).file_size > XML_LIMIT:
                raise ValueError('LV inside the archive exceeds the XML size limit.')
            data = archive.read(name)
    if len(data) > XML_LIMIT:
        raise ValueError('LV exceeds the XML size limit.')
    if hashlib.sha256(data).hexdigest() != source['sha256']:
        raise ValueError('LV checksum changed. Review the source version before updating the manifest.')
    return data


def prepare_sources(sources, output, source_dir=None):
    validate_sources(sources)
    originals = output / 'originale'
    originals.mkdir(parents=True, exist_ok=True)
    manifest = []
    for source in sources:
        print(f"Preparing public source: {source['name']}", flush=True)
        if source_dir:
            path = source_dir / source['fileName']
            if path.stat().st_size > XML_LIMIT:
                raise ValueError('Local source exceeds the XML size limit.')
            data = path.read_bytes()
        else:
            with urlopen(source['downloadUrl'], timeout=60) as response:
                data = response.read(DOWNLOAD_LIMIT + 1)
        data = unpack_download(data, source)
        path = originals / source['fileName']
        path.write_bytes(data)
        manifest.append({'name': source['name'], 'file': str(path), 'sourceUrl': source['sourceUrl']})
    path = output / 'manifest.json'
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources', type=Path, default=ROOT / 'config/public-lv-sources.json')
    parser.add_argument('--source-dir', type=Path, help='Use existing original files instead of network downloads.')
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if output == ROOT or ROOT in output.parents:
        parser.error('Originals and reports must be written outside the repository.')
    output.mkdir(parents=True, exist_ok=True)
    # Do not leave a success summary from a previous run after a failed retry.
    (output / 'summary.json').unlink(missing_ok=True)
    sources = json.loads(args.sources.read_text(encoding='utf-8-sig'))
    manifest = prepare_sources(sources, output, args.source_dir)

    def run(script, *arguments):
        subprocess.run([sys.executable, str(ROOT / 'scripts' / script), *map(str, arguments)],
            cwd=ROOT, check=True)

    run('public_lv_review_cloud.py', '--manifest', manifest, '--output-dir', output / 'audit')
    audits = json.loads((output / 'audit/import-audit.json').read_text())
    if len(audits) != len(sources):
        raise RuntimeError('Import audit is incomplete.')
    for source, audit in zip(sources, audits):
        if not audit['passed'] or audit['importedItems'] != source['expectedItems']:
            raise RuntimeError('Pinned LV import does not match the expected source version.')
    refs = output / 'audit/textreferenzen.json'
    run('matching_originals_cloud.py', '--references', refs, '--output-dir', output / 'rankings',
        '--review-count', 60)
    run('prepare_original_review_cloud.py', '--references', refs,
        '--rankings', output / 'rankings/holdout-rankings.json', '--output-dir', output / 'pakete',
        '--count', 60)
    rankings = json.loads((output / 'rankings/holdout-rankings.json').read_text())
    packets = json.loads((output / 'pakete/uebersicht.json').read_text())
    summary = {'schema': 'kalkpilot.public-lv-check', 'passed': True,
        'projects': [{key: source[key] for key in ['name', 'sourceUrl', 'sha256', 'expectedItems']}
            for source in sources],
        'positions': rankings['positions'], 'pairs': rankings['pairsPerPhase'],
        'reviewCases': sum(p['targets'] for p in packets), 'expertConfirmed': 0,
        'priceApproval': False,
        'limitation': 'Import and rule workflow only; no independent expert accuracy or external model run.'}
    (output / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
