"""API source discovery uses metadata, never self-confirmed matching labels."""
import io
from pathlib import Path
import sys
import unittest
from zipfile import ZipFile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from discover_public_lvs import csv_cell, public_url, read_export, select_candidates


class PublicLVDiscovery(unittest.TestCase):
    def payload(self, key='project-a', version=1, title='Synthetic Tiefbau', cpv='45000000'):
        return {'uri':f'https://example.invalid/api/notices/{key}?noticeVersion={version}',
            'releases':[{'ocid':key,'id':f'notice-{version}','date':'2026-10-30T00:00:00Z',
                'tender':{'title':title,'items':[{'classification':{'scheme':'CPV','id':cpv}}],
                    'documents':[{'url':'https://example.invalid/documents'}]}}]}

    def test_latest_notice_per_project_and_known_project_exclusion(self):
        old=self.payload(version=1);new=self.payload(version=2,title='New Tiefbau')
        known=self.payload(key='known-project')
        result=select_candidates([old,new,known],['tiefbau'],[],{'known-project'})
        self.assertEqual(result['noticesScanned'],3)
        self.assertEqual(result['uniqueProjects'],2)
        self.assertEqual(result['excludedKnownProjects'],1)
        self.assertEqual(len(result['candidates']),1)
        row=result['candidates'][0]
        self.assertEqual(row['title'],'New Tiefbau')
        self.assertEqual(row['gaebAvailability'],'unknown')
        self.assertEqual(row['reviewStatus'],'source_unverified')
        self.assertEqual(row['split'],'unassigned')
        self.assertFalse(row['expertConfirmed'])

    def test_cpv_and_lot_descriptions_can_find_relevant_sources(self):
        a=self.payload(key='a',title='Project A',cpv='45112000')
        b=self.payload(key='b',title='Project B',cpv='99999999')
        b['releases'][0]['tender']['lots']=[{'title':'Synthetic Rohrleitungsbau'}]
        rows=select_candidates([a,b],['rohrleitung'],['4511'])['candidates']
        self.assertEqual({row['projectKey'] for row in rows},{'a','b'})

    def test_no_documents_or_irrelevant_sources_are_not_lv_candidates(self):
        a=self.payload(key='a');a['releases'][0]['tender']['documents']=None
        b=self.payload(key='b',title='Synthetic office supplies')
        self.assertEqual(select_candidates([a,b],['tiefbau'],[])['candidates'],[])

    def test_document_links_are_deduplicated_and_credentials_are_rejected(self):
        a=self.payload();a['releases'][0]['tender']['lots']=[{'documents':[
            {'url':'https://example.invalid/documents'},
            {'url':'https://user:password@example.invalid/secret'},
            {'url':'javascript:alert(1)'}, {'url':'http://['}]}]
        row=select_candidates([a],['tiefbau'],[])['candidates'][0]
        self.assertEqual(row['documentPages'],['https://example.invalid/documents'])
        self.assertFalse(public_url('http://['))

    def test_empty_export_and_malformed_payload_are_distinguished(self):
        empty=io.BytesIO()
        with ZipFile(empty,'w'):pass
        self.assertEqual(read_export(empty.getvalue()),[])
        bad=io.BytesIO()
        with ZipFile(bad,'w') as archive:archive.writestr('a.json','{}')
        with self.assertRaisesRegex(ValueError,'OCDS'):read_export(bad.getvalue())

    def test_result_limit_and_csv_formula_text(self):
        rows=[self.payload(key=str(i)) for i in range(4)]
        result=select_candidates(rows,['tiefbau'],[],limit=2)
        self.assertEqual(result['eligibleProjects'],4)
        self.assertEqual(len(result['candidates']),2)
        self.assertEqual(csv_cell('=SUM(1;2)'),"'=SUM(1;2)")
        self.assertEqual(csv_cell('Normal title'),'Normal title')


if __name__=='__main__':unittest.main()
