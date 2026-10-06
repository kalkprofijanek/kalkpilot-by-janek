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


class OriginalBenchmark(unittest.TestCase):
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
                self.assertEqual(entry['expertConfirmed'],0)
                labels=json.loads((case/'fachpruefung.json').read_text())
                self.assertEqual(labels[0]['reviewStatus'],'unreviewed')
                self.assertIsNone(labels[0]['expectedStatus'])
                self.assertEqual((case/'copilot-auftrag.xlsx').read_bytes()[:2],b'PK')
