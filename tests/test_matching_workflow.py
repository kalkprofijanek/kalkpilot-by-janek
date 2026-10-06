"""Quality cases and native Microsoft 365 workbook exchange, with synthetic data only."""
import io
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED
import test_browser as browser_tests

ROOT = Path(__file__).resolve().parents[1]


class MatchingWorkflow(unittest.TestCase):
    setUpClass = classmethod(browser_tests.BrowserRegression.setUpClass.__func__)
    tearDownClass = classmethod(browser_tests.BrowserRegression.tearDownClass.__func__)
    setUp = browser_tests.BrowserRegression.setUp
    tearDown = browser_tests.BrowserRegression.tearDown
    import_projects = browser_tests.BrowserRegression.import_projects

    def test_quality_cases_reject_conflicts_but_keep_valid_minimums(self):
        cases = json.loads((ROOT / 'tests/fixtures/matching-quality.json').read_text())
        rows = self.page.evaluate('''cases => cases.map(c => {
          const check=KPLLMMatching.compareRequirements(c.a,c.b), result=calcScore(c.a,c.b);
          return {name:c.name,expected:c.expected,score:result.score,conflicts:check.conflicts,missing:check.missing};
        })''', cases)
        for row in rows:
            with self.subTest(case=row['name']):
                if row['expected'] == 'conflict':
                    self.assertTrue(row['conflicts'], row)
                    self.assertLessEqual(row['score'], 45)
                elif row['expected'] == 'incomplete':
                    self.assertFalse(row['conflicts'], row)
                    self.assertTrue(row['missing'], row)
                    self.assertLessEqual(row['score'], 68)
                else:
                    self.assertFalse(row['conflicts'], row)
                    self.assertFalse(row['missing'], row)
                    self.assertGreaterEqual(row['score'], 80)

    def test_plan_reference_does_not_turn_construction_into_document_work(self):
        result=self.page.evaluate("""()=>{
          const a={kurztext:'Bauzaun liefern und aufstellen',langtext:'Wie auf Plan A7 dargestellt, verzinkten Bauzaun mit Betonfüßen aufstellen.',me:'m'};
          const b={kurztext:'Bauzaun aufstellen',langtext:'Verzinkten Bauzaun mit Betonfüßen aufstellen.',me:'m'};
          const plan={kurztext:'Bauzeitenplan erstellen',langtext:'Bauzeitenplan erstellen und aktualisieren.',me:'psch'};
          const caps=calcScore(a,b).debug.hardCapsApplied;
          return {construction:getMatchProfile(a).docLike,document:getMatchProfile(plan).docLike,caps,
            documentCaps:calcScore(a,plan).debug.hardCapsApplied};
        }""")
        self.assertFalse(result['construction'])
        self.assertTrue(result['document'])
        self.assertNotIn('Dokumenttyp unpassend',result['caps'])
        self.assertTrue(result['documentCaps'])

    def test_profile_cache_updates_after_text_changes(self):
        result=self.page.evaluate("""()=>{
          const p={kurztext:'Bauzaun aufstellen',langtext:'Bauzaun aufstellen',me:'m'};
          const before=getMatchProfile(p);
          p.kurztext='Bauzeitenplan erstellen';p.langtext='Bauzeitenplan erstellen und aktualisieren';p.me='psch';
          const after=getMatchProfile(p);
          return {changed:before!==after,document:after.docLike,unit:after.unitNorm,
            serialized:JSON.stringify(p)};
        }""")
        self.assertTrue(result['changed'])
        self.assertTrue(result['document'])
        self.assertEqual(result['unit'],'psch')
        self.assertNotIn('__matchProfile',result['serialized'])

    def prepare(self):
        self.import_projects([{'name':'Synthetic','active':True,'positions':[
            {'oz':'R1','kurztext':'Rohr PE100 liefern','langtext':'Rohr PE100 da 75 SDR 11 liefern',
             'me':'m','menge':1,'kosten':[{'typ':'L','menge':1,'preis':1}]}]}])
        self.page.evaluate("S.newLV=[{oz:'T1',kurztext:'Rohr PE100 liefern',langtext:'Rohr PE100 da 75 SDR 11 liefern',me:'m',menge:30}];checkRunBtn();switchTab('t2')")
        return self.page.evaluate('async () => (await getLLMMatchingContext()).request')

    def test_text_evidence_is_verified_and_never_approves_price(self):
        request = self.prepare()
        response = {'schema':'kalkpilot.llm-matches','schemaVersion':1,'requestId':request['requestId'],
            'matches':[{'targetId':'t1','status':'matched','referenceIds':['r1'],'confidence':'high',
                'reason':'Rohrwerkstoff, Außendurchmesser und SDR stimmen überein.','differences':[],
                'missingInformation':[],'evidence':[{'referenceId':'r1','targetQuote':'PE100 da 75 SDR 11',
                                                   'referenceQuote':'PE100 da 75 SDR 11'}]}]}
        result = self.page.evaluate('''async response=>{
          await importLLMMatches(new File([JSON.stringify(response)],'reply.json'));
          return {accepted:S.results[0].accepted,verdict:S.results[0].matches[0].debug.llmAudit.verdict,
            status:document.getElementById('llmMatchingStatus').textContent};
        }''', response)
        self.assertFalse(result['accepted'])
        self.assertEqual(result['verdict'], 'consistent')
        response['matches'][0]['evidence'][0]['referenceQuote'] = 'Erfundener völlig anderer Rohrtext'
        rejected = self.page.evaluate('''async response=>{
          const before=S.results;await importLLMMatches(new File([JSON.stringify(response)],'reply.json'));
          return {same:before===S.results,status:document.getElementById('llmMatchingStatus').textContent};
        }''', response)
        self.assertTrue(rejected['same'])
        self.assertIn('Textbeleg steht nicht', rejected['status'])

    def test_xlsx_workbook_is_valid_and_deflated_answer_imports(self):
        request = self.prepare()
        with self.page.expect_download() as info:
            self.page.locator('#llmRequestBtn').click()
        downloaded = info.value.path()
        with ZipFile(downloaded) as archive:
            files = {name:archive.read(name) for name in archive.namelist()}
        self.assertIn('Antwort', files['xl/workbook.xml'].decode())
        self.assertIn('Referenzen', files['xl/workbook.xml'].decode())
        self.assertNotIn('Liefere eine JSON-Datei',files['xl/worksheets/sheet1.xml'].decode())
        self.assertIn('vollständig lesen kannst',files['xl/worksheets/sheet1.xml'].decode())
        for name, content in files.items():
            if name.endswith('.xml') or name.endswith('.rels'):
                ET.fromstring(content)
        ns = {'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        answer = ET.fromstring(files['xl/worksheets/sheet4.xml'])
        row = answer.find('s:sheetData', ns)[1]
        values = [request['requestId'],'t1','matched','r1','high','Rohrdimension und Werkstoff stimmen.','','',
                  'PE100 da 75 SDR 11','PE100 da 75 SDR 11']
        for cell, value in zip(row, values):
            cell.find('s:is/s:t', ns).text = value
        files['xl/worksheets/sheet4.xml'] = ET.tostring(answer,encoding='utf-8',xml_declaration=True)
        data=io.BytesIO()
        with ZipFile(data,'w',ZIP_DEFLATED) as archive:
            for name,content in files.items(): archive.writestr(name,content)
        result=self.page.evaluate('''async bytes=>{
          await importLLMMatches(new File([new Uint8Array(bytes)],'copilot-answer.xlsx'));
          return {accepted:S.results[0]?.accepted,verdict:S.results[0]?.matches[0]?.debug.llmAudit.verdict,
            status:document.getElementById('llmMatchingStatus').textContent};
        }''', list(data.getvalue()))
        self.assertEqual(result['verdict'],'consistent',result)
        self.assertFalse(result['accepted'])
        # Excel formula results are not trusted as typed matching data.
        ET.SubElement(row[5],'{'+ns['s']+'}f').text='"Formula reason"'
        files['xl/worksheets/sheet4.xml']=ET.tostring(answer,encoding='utf-8')
        data=io.BytesIO()
        with ZipFile(data,'w',ZIP_DEFLATED) as archive:
            for name,content in files.items():archive.writestr(name,content)
        result=self.page.evaluate('''async bytes=>{
          const before=S.results;await importLLMMatches(new File([new Uint8Array(bytes)],'answer.xlsx'));
          return {unchanged:before===S.results,status:document.getElementById('llmMatchingStatus').textContent};
        }''',list(data.getvalue()))
        self.assertTrue(result['unchanged'])
        self.assertIn('Formeln',result['status'])

    def test_pasted_copilot_table_and_missing_targets(self):
        request=self.prepare()
        text='\t'.join(['requestId','ZielID','Status','ReferenzIDs','Sicherheit','Begründung','Unterschiede','FehlendeAngaben'])+'\n'
        text+='\t'.join([request['requestId'],'t1','passend','r1','hoch','Gleiche Rohrleistung.','',''])
        result=self.page.evaluate('''async text=>{
          await importLLMMatches(new File([text],'answer.tsv'));
          return {verdict:S.results[0].matches[0].debug.llmAudit.verdict,accepted:S.results[0].accepted};
        }''',text)
        self.assertEqual(result['verdict'],'incomplete')
        self.assertFalse(result['accepted'])
        text += '\n'+ '\t'.join([request['requestId'],'t1','passend','r1','hoch','Doppelte Zielposition.','',''])
        result=self.page.evaluate('''async text=>{
          const before=S.results;await importLLMMatches(new File([text],'answer.tsv'));
          return {same:before===S.results,status:document.getElementById('llmMatchingStatus').textContent};
        }''',text)
        self.assertTrue(result['same'])
        self.assertIn('nicht übernommen',result['status'])

    def test_long_text_is_preserved_across_excel_columns_and_formula_text_is_literal(self):
        text='Lange Leistungsbeschreibung 🏗 '+('Vollständiger Text. '*4000)
        result=self.page.evaluate('''async text=>{
          const request=await KPLLMMatching.buildRequest({version:APP_VERSION,
            targets:[{oz:'1',kurztext:'=1+1',langtext:text,me:'m'}],
            references:[{oz:'2',kurztext:'=1+1',langtext:text,me:'m'}]});
          return Array.from(new Uint8Array(await KPCopilotExchange.exportRequest(request).arrayBuffer()));
        }''',text)
        with ZipFile(io.BytesIO(bytes(result))) as archive:
            data=ET.fromstring(archive.read('xl/worksheets/sheet2.xml'))
        ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        rows=data.find('s:sheetData',ns)
        labels=[cell.find('s:is/s:t',ns).text for cell in rows[0]]
        values=[cell.find('s:is/s:t',ns).text or '' for cell in rows[1]]
        restored=''.join(value for label,value in zip(labels,values) if label.startswith('Langtext '))
        self.assertEqual(restored,text)
        self.assertEqual(values[labels.index('Kurztext')],'=1+1')
        self.assertEqual(data.findall('.//s:f',ns),[])

    def test_markdown_table_checks_all_targets_before_import(self):
        request=self.prepare()
        header='| '+' | '.join(['requestId','ZielID','Status','ReferenzIDs','Sicherheit','Begründung','Unterschiede','FehlendeAngaben','Zielbeleg','Referenzbeleg'])+' |\n'
        table=header+'| '+ ' | '.join(['---']*10)+' |\n'
        table+='| '+' | '.join([f'`{request["requestId"]}`','`t1`','passend','r1','hoch','Gleiche Rohrleistung.','','','PE100 da 75 SDR 11','PE100 da 75 SDR 11'])+' |'
        result=self.page.evaluate('''async text=>{
          await importLLMMatches(new File([text],'answer.txt'));
          return {verdict:S.results[0]?.matches[0]?.debug.llmAudit.verdict,accepted:S.results[0]?.accepted};
        }''',table)
        self.assertEqual(result['verdict'],'consistent')
        self.assertFalse(result['accepted'])
        # A changed LV makes the previous answer stale; no partial adoption.
        result=self.page.evaluate('''async text=>{
          S.newLV.push({oz:'T2',kurztext:'Weitere Rohrleistung',langtext:'Rohr PE100 da 75 SDR 11 liefern',me:'m'});
          const before=S.results;await importLLMMatches(new File([text],'answer.txt'));
          return {same:before===S.results,status:document.getElementById('llmMatchingStatus').textContent};
        }''',table)
        self.assertTrue(result['same'])
        self.assertIn('nicht übernommen',result['status'])

    def test_corrupt_excel_preserves_previous_matching(self):
        request=self.prepare()
        data=self.page.evaluate('''async request=>Array.from(new Uint8Array(await KPCopilotExchange.exportRequest(request).arrayBuffer()))''',request)
        damaged=bytearray(data)
        marker=b'<workbook '
        at=damaged.index(marker)
        damaged[at+1]=ord('X')
        result=self.page.evaluate('''async bytes=>{
          const before=S.results;await importLLMMatches(new File([new Uint8Array(bytes)],'answer.xlsx'));
          return {same:before===S.results,status:document.getElementById('llmMatchingStatus').textContent};
        }''',list(damaged))
        self.assertTrue(result['same'])
        self.assertIn('beschädigt',result['status'])
