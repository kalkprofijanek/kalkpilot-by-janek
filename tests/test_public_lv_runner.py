"""Pinned downloads and archive handling, using synthetic files only."""
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from run_public_lv_check import prepare_sources, unpack_download, validate_sources


class PublicLVRunner(unittest.TestCase):
    def source(self, name='A', filename='a.x83'):
        data=b'<GAEB><Item RNoPart="1"/></GAEB>'
        return {'name':name, 'fileName':filename, 'expectedItems':1,
            'sha256':hashlib.sha256(data).hexdigest(),
            'sourceUrl':'https://example.invalid/public-notice',
            'downloadUrl':'https://example.invalid/public-lv'}, data

    def test_changed_or_error_page_download_cannot_pass_as_pinned_lv(self):
        source, data=self.source()
        self.assertEqual(unpack_download(data,source),data)
        with self.assertRaisesRegex(ValueError,'checksum'):
            unpack_download(b'<html>Expired notice</html>',source)

    def test_archive_selects_exact_lv_without_extracting_other_entries(self):
        source,data=self.source()
        content=io.BytesIO()
        with ZipFile(content,'w') as archive:
            archive.writestr('Leistungsverzeichnis/a.x83',data)
            archive.writestr('../unrelated.txt',b'Never extract this')
        self.assertEqual(unpack_download(content.getvalue(),source),data)
        source['archiveEntry']='Leistungsverzeichnis/a.x83'
        self.assertEqual(unpack_download(content.getvalue(),source),data)

    def test_ambiguous_archive_and_unsafe_manifest_are_rejected(self):
        source,data=self.source()
        content=io.BytesIO()
        with ZipFile(content,'w') as archive:
            archive.writestr('v1/a.x83',data)
            archive.writestr('v2/a.x83',data)
        with self.assertRaisesRegex(ValueError,'exactly one'):
            unpack_download(content.getvalue(),source)
        second,_=self.source('B','b.x83')
        validate_sources([source,second])
        for change in [{'fileName':'../a.x83'}, {'fileName':'..'},
                {'downloadUrl':'https://user:password@example.invalid/x83'},
                {'sha256':'not-pinned'}, {'name':'B'}]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate_sources([{**source,**change},second])

    def test_existing_sources_prepare_manifest_with_verified_local_files(self):
        with tempfile.TemporaryDirectory(prefix='kalkpilot-pinned-') as folder:
            folder=Path(folder);local=folder/'sources';local.mkdir()
            a,data=self.source();b,_=self.source('B','b.x83')
            for source in [a,b]:(local/source['fileName']).write_bytes(data)
            manifest=prepare_sources([a,b],folder/'run',local)
            rows=json.loads(manifest.read_text())
            self.assertEqual([r['name'] for r in rows],['A','B'])
            for row in rows:self.assertEqual(Path(row['file']).read_bytes(),data)
            self.assertFalse((folder/'run/summary.json').exists())


if __name__=='__main__':
    unittest.main()
