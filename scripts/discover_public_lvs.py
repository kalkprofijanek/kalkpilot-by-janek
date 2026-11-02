"""Find public LV source candidates in the official OCDS daily export.

Writes notice metadata and document-page links, not expert labels or GAEB files.
The API does not supply the GAEB files themselves. No model calls or login.
"""
import argparse
import csv
from datetime import date, datetime, timedelta
import io
import json
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import urlopen
from zipfile import ZipFile
from zoneinfo import ZoneInfo

from llm_matching_cloud import ROOT

API = 'https://www.oeffentlichevergabe.de/api/notice-exports'
KEYWORDS = ['tiefbau', 'erdarbeiten', 'erdbau', 'rohrleitung', 'kanalbau', 'entwässerung', 'boden']
CPV_PREFIXES = ['4511', '4523']
DOWNLOAD_LIMIT = 30 * 1024 * 1024
UNPACKED_LIMIT = 150 * 1024 * 1024


def dicts(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from dicts(child)
    elif isinstance(value, list):
        for child in value:
            yield from dicts(child)


def public_url(value):
    if not isinstance(value, str):
        return False
    try:
        parsed = urlparse(value)
    except ValueError:
        return False
    return parsed.scheme in {'http', 'https'} and bool(parsed.hostname) and not (parsed.username or parsed.password)


def read_export(data):
    if len(data) > DOWNLOAD_LIMIT:
        raise ValueError('Daily export exceeds the download limit.')
    payloads = []
    with ZipFile(io.BytesIO(data)) as archive:
        members = [m for m in archive.infolist() if m.filename.endswith('.json')]
        if len(members) > 20000 or sum(m.file_size for m in members) > UNPACKED_LIMIT:
            raise ValueError('Daily export exceeds the unpacked size limit.')
        for member in members:
            payload = json.loads(archive.read(member))
            if not isinstance(payload, dict) or not isinstance(payload.get('releases'), list):
                raise ValueError('Unexpected OCDS export structure.')
            payloads.append(payload)
    return payloads


def select_candidates(payloads, keywords, cpv_prefixes, excluded_ocids=(), limit=40):
    latest = {}
    scanned = 0
    for payload in payloads:
        uri = payload.get('uri', '')
        version = parse_qs(urlparse(uri).query).get('noticeVersion', ['0'])[0]
        version = int(version) if version.isdigit() else 0
        for release in payload['releases']:
            scanned += 1
            key = release.get('ocid') or release.get('id')
            if not key:
                continue
            rank = (str(release.get('date', '')), version, str(release.get('id', '')))
            if key not in latest or rank > latest[key][0]:
                latest[key] = (rank, release, uri)
    candidates = []
    excluded = 0
    for key, (_, release, uri) in latest.items():
        if key in excluded_ocids:
            excluded += 1
            continue
        tender = release.get('tender') or {}
        text = ' '.join(str(part.get(field, '')) for part in [tender, *(tender.get('lots') or [])]
            for field in ['title', 'description']).casefold()
        cpv = sorted({str(part['id']) for part in dicts(tender)
            if part.get('scheme') == 'CPV' and part.get('id')})
        words = [word for word in keywords if word.casefold() in text]
        codes = [code for code in cpv if any(code.startswith(prefix) for prefix in cpv_prefixes)]
        if not words and not codes:
            continue
        links = sorted({doc['url'] for part in dicts(tender)
            for doc in (part.get('documents') or []) if isinstance(doc, dict) and public_url(doc.get('url'))})
        if not links:
            continue
        candidates.append({'projectKey': key, 'noticeId': release.get('id'),
            'title': ' '.join(str(tender.get('title', '')).split()),
            'publicationDate': release.get('date'), 'noticeUrl': uri if public_url(uri) else None,
            'documentPages': links, 'cpv': cpv, 'matchedKeywords': words, 'matchedCPV': codes,
            'reviewStatus': 'source_unverified', 'split': 'unassigned',
            'gaebAvailability': 'unknown', 'expertConfirmed': False})
    candidates.sort(key=lambda row: (-len(row['matchedKeywords']), row['title'], row['projectKey']))
    return {'noticesScanned': scanned, 'uniqueProjects': len(latest),
        'excludedKnownProjects': excluded, 'eligibleProjects': len(candidates),
        'candidates': candidates[:limit]}


def csv_cell(value):
    value = str(value or '')
    return "'" + value if value.lstrip().startswith(('=', '+', '-', '@')) else value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--day', type=date.fromisoformat,
        default=datetime.now(ZoneInfo('Europe/Berlin')).date() - timedelta(days=1))
    parser.add_argument('--keywords', default=','.join(KEYWORDS))
    parser.add_argument('--cpv-prefixes', default=','.join(CPV_PREFIXES))
    parser.add_argument('--limit', type=int, default=40)
    parser.add_argument('--export-file', type=Path, help='Use a previously downloaded OCDS ZIP.')
    parser.add_argument('--known-sources', type=Path, default=ROOT / 'config/public-lv-sources.json')
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.limit <= 1000:
        parser.error('Limit must be between 1 and 1000.')
    output = args.output_dir.resolve()
    if output == ROOT or ROOT in output.parents:
        parser.error('Discovery results must remain outside the repository.')
    keywords = [s.strip().casefold() for s in args.keywords.split(',') if s.strip()]
    prefixes = [s.strip() for s in args.cpv_prefixes.split(',') if s.strip()]
    if not keywords and not prefixes:
        parser.error('At least one keyword or CPV prefix is required.')
    url = API + '?' + urlencode({'pubDay': args.day.isoformat(), 'format': 'ocds.zip'})
    if args.export_file:
        if args.export_file.stat().st_size > DOWNLOAD_LIMIT:
            parser.error('Export file exceeds the download limit.')
        data = args.export_file.read_bytes()
    else:
        with urlopen(url, timeout=60) as response:
            data = response.read(DOWNLOAD_LIMIT + 1)
    known = json.loads(args.known_sources.read_text())
    result = select_candidates(read_export(data), keywords, prefixes,
        {source['ocid'] for source in known if source.get('ocid')}, args.limit)
    result.update({'schema': 'kalkpilot.public-lv-discovery', 'schemaVersion': 1,
        'publicationDay': args.day.isoformat(), 'apiUrl': url, 'keywords': keywords,
        'cpvPrefixes': prefixes, 'expertConfirmed': 0,
        'limitation': 'Notice metadata only. Document access, GAEB availability, duplicates across other project identifiers and independent test suitability require review.'})
    output.mkdir(parents=True, exist_ok=True)
    (output / 'candidates.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    with (output / 'candidates.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.writer(stream, delimiter=';')
        writer.writerow(['Projekt-ID', 'Titel', 'CPV', 'Unterlagenlinks', 'GAEB-Verfügbarkeit', 'Prüfstatus', 'Datenaufteilung'])
        for row in result['candidates']:
            writer.writerow([csv_cell(value) for value in [row['projectKey'], row['title'],
                ', '.join(row['cpv']), ' | '.join(row['documentPages']),
                row['gaebAvailability'], row['reviewStatus'], row['split']]])
    print(json.dumps({key: result[key] for key in ['publicationDay', 'noticesScanned', 'uniqueProjects',
        'excludedKnownProjects', 'eligibleProjects']}, ensure_ascii=False))
    print(f"Selected source candidates: {len(result['candidates'])}; GAEB availability and expert labels unverified.")


if __name__ == '__main__':
    main()
