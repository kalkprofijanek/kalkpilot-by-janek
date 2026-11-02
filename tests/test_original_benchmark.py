"""Holdout isolation and balanced review preparation, with synthetic data only."""
from collections import Counter
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from matching_originals_cloud import choose_review
from public_lv_review_cloud import source_positions, compare_import, plain_text
import xml.etree.ElementTree as ET


class OriginalBenchmark(unittest.TestCase):
    def test_public_import_audit_detects_lost_content_and_preserves_xml_decimals(self):
        xml='''<GAEB xmlns="http://www.gaeb.de/GAEB_DA_XML/DA83/3.2"><BoQCtgy RNoPart="01">
          <LblTx><p>Synthetic drainage</p></LblTx><Item RNoPart="0010" ID="synthetic-id">
          <Qty>123.456</Qty><QU>m³</QU><Description><CompleteText>
          <OutlineText><OutlTxt><TextOutlTxt><p>Drainage pipe</p></TextOutlTxt></OutlTxt></OutlineText>
          <DetailTxt><Text><p>Pipe <span>PE </span><span>100</span></p><p>da 75 mm</p></Text></DetailTxt>
          </CompleteText></Description></Item></BoQCtgy></GAEB>'''
        with tempfile.TemporaryDirectory(prefix='kalkpilot-public-audit-') as folder:
            path=Path(folder)/'synthetic.x83';path.write_text(xml)
            rows=source_positions(path)
        self.assertEqual(rows[0]['menge'],123.456)
        self.assertEqual(rows[0]['oz'],'01 0010')
        self.assertEqual(rows[0]['langtext'],'Pipe PE 100 da 75 mm')
        self.assertEqual(rows[0]['titlePath'],'Synthetic drainage')
        actual=[{**rows[0],'me':'m3'}]
        self.assertEqual(compare_import(rows,actual),[])
        actual[0]['langtext']='Pipe PE 100'
        self.assertEqual(compare_import(rows,actual)[0]['field'],'langtext')
        self.assertEqual(compare_import(rows,[])[0]['field'],'positions')
        self.assertEqual(plain_text(ET.fromstring('<Text><p>A<br/>B</p><p>C</p></Text>')),'A B C')

    def test_public_x83_upload_audit_produces_text_only_references(self):
        with tempfile.TemporaryDirectory(prefix='kalkpilot-public-review-') as folder:
            folder=Path(folder);source=folder/'sample.x83';manifest=folder/'manifest.json';out=folder/'out'
            source.write_text('''<GAEB xmlns="http://www.gaeb.de/GAEB_DA_XML/DA83/3.2">
              <BoQCtgy RNoPart="01"><LblTx>Drainage</LblTx><Item RNoPart="0010" ID="synthetic-id">
              <Qty>123.456</Qty><QU>m³</QU><Description><CompleteText>
              <OutlineText><OutlTxt><TextOutlTxt><p>Synthetic pipe</p></TextOutlTxt></OutlTxt></OutlineText>
              <DetailTxt><Text><p>Synthetic pipe da 75 mm</p></Text></DetailTxt>
              </CompleteText></Description></Item></BoQCtgy></GAEB>''')
            manifest.write_text(json.dumps([{'name':'Synthetic public project','file':str(source),
                'sourceUrl':'https://example.invalid/public-notice'}]))
            run=subprocess.run([sys.executable,str(ROOT/'scripts/public_lv_review_cloud.py'),
                '--manifest',str(manifest),'--output-dir',str(out)],cwd=ROOT,
                capture_output=True,text=True,timeout=60)
            self.assertEqual(run.returncode,0,run.stdout+run.stderr)
            audit=json.loads((out/'import-audit.json').read_text())[0]
            self.assertTrue(audit['passed'])
            self.assertEqual(audit['xmlItems'],audit['importedItems'])
            self.assertFalse(audit['priceApproval'])
            pos=json.loads((out/'textreferenzen.json').read_text())[0]['positions'][0]
            self.assertEqual(pos['kosten'],[])
            self.assertFalse(pos['matchedXML'])
            self.assertEqual(pos['menge'],123.456)
            self.assertEqual(pos['originalXref'],'synthetic-id')

    def test_large_project_does_not_dominate_review_set(self):
        rows=[{'id':f'{project}-{i}','project':project,'category':['ROHR','ERDBAU'][i%2]}
            for project,size in [('A',1114),('B',108),('C',167),('D',138)] for i in range(size)]
        chosen=choose_review(rows,200)
        self.assertEqual(Counter(r['project'] for r in chosen),{'A':50,'B':50,'C':50,'D':50})
        self.assertEqual(len({r['id'] for r in chosen}),200)
        self.assertEqual(Counter(r['category'] for r in chosen),{'ROHR':100,'ERDBAU':100})

    def test_original_tools_exclude_self_project_and_prepare_unreviewed_packets(self):
        with tempfile.TemporaryDirectory(prefix='kalkpilot-review-') as folder:
            folder=Path(folder);source=folder/'refs.json';out=folder/'ranks';pack=folder/'pack'
            source.write_text(json.dumps([{'name':project,'active':True,'positions':[
                {'oz':'1','kurztext':'Baufacharbeiter','langtext':'Baufacharbeiter','me':'h','menge':1,
                 'titlePath':'Synthetic project > Labour',
                 'kosten':[{'typ':'L','nameCoC':'LOHN','identifyKey':'LOHN-KEY','menge':1,'preis':0}]}]}
                for project in ['A','B']]))
            run=subprocess.run([sys.executable,str(ROOT/'scripts/matching_originals_cloud.py'),
                '--references',str(source),'--output-dir',str(out),'--review-count','2'],
                cwd=ROOT,capture_output=True,text=True,timeout=60)
            self.assertEqual(run.returncode,0,run.stdout+run.stderr)
            report=json.loads((out/'holdout-rankings.json').read_text())
            self.assertEqual(report['pairsPerPhase'],2)
            for row in report['results']['current']:
                self.assertEqual(row['references'],1)
                self.assertNotEqual(row['project'],row['top'][0]['project'])
                self.assertNotEqual(row['id'],row['top'][0]['id'])
            run=subprocess.run([sys.executable,str(ROOT/'scripts/prepare_original_review_cloud.py'),
                '--references',str(source),'--rankings',str(out/'holdout-rankings.json'),
                '--output-dir',str(pack),'--count','2'],cwd=ROOT,capture_output=True,text=True,timeout=60)
            self.assertEqual(run.returncode,0,run.stdout+run.stderr)
            summary=json.loads((pack/'uebersicht.json').read_text())
            self.assertEqual(sum(s['targets'] for s in summary),2)
            for entry in summary:
                case=pack/entry['folder']
                request=json.loads((case/'matching-auftrag.json').read_text())
                self.assertTrue(all(r['projekt']!=entry['project'] for r in request['referenzen']))
                self.assertEqual(request['zielpositionen'][0]['titelkontext'],'Synthetic project > Labour')
                self.assertEqual(request['zielpositionen'][0]['oz'],'1')
                self.assertEqual(entry['expertConfirmed'],0)
                labels=json.loads((case/'fachpruefung.json').read_text())
                self.assertEqual(labels[0]['reviewStatus'],'unreviewed')
                self.assertIsNone(labels[0]['expectedStatus'])
                self.assertEqual((case/'copilot-auftrag.xlsx').read_bytes()[:2],b'PK')
