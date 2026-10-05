"""Browser regression tests with synthetic data; customer files never enter Git."""
import json
import os
from pathlib import Path
import threading
import unittest
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


class BrowserRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT)))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f'http://127.0.0.1:{cls.server.server_port}'
        cls.playwright = sync_playwright().start()
        options = {'headless': True}
        if os.environ.get('KALKPILOT_CHROMIUM'):
            options['executable_path'] = os.environ['KALKPILOT_CHROMIUM']
        cls.browser = cls.playwright.chromium.launch(**options)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        self.errors = []
        self.external_requests = []
        self.page.on('pageerror', lambda error: self.errors.append(str(error)))

        def route(request):
            if request.request.url.startswith(self.url + '/'):
                request.continue_()
            else:
                self.external_requests.append(request.request.url)
                request.abort()

        self.page.route('**/*', route)
        self.page.goto(self.url + '/')
        self.page.wait_for_url('**/KalkPilot_by_Janek.html')
        self.page.evaluate('referenceStorageReady')

    def tearDown(self):
        self.assertEqual(self.errors, [])
        self.assertEqual(self.external_requests, [])
        self.context.close()

    def import_projects(self, projects):
        return self.page.evaluate('''async projects => {
          await importRefFromJSON(new File([JSON.stringify(projects)], 'references.json'));
          return S.refProjects.length;
        }''', projects)

    def test_existing_self_tests(self):
        for function in ('runMatchingSelfTest', 'runExportFormatSelfTest',
                         'runMatchMemoryMergeSelfTest', 'runStoredDecisionSelfTest'):
            with self.subTest(function=function):
                result = self.page.evaluate(f'{function}()')
                self.assertTrue(all(row['ok'] for row in result) if isinstance(result, list) else result['ok'])

    def test_d83_numbering_and_structural_records(self):
        result = self.page.evaluate(r'''() => {
          const text = '2101 01   1NNN         00000001000psch\n25Baustelle einrichten\n31 1 1\n' +
            '2101 01   2NNN         00000002000m3\n25Boden ausheben\n32 42';
          return parseD83(text, 'synthetic.d83');
        }''')
        self.assertEqual([r['oz'] for r in result], ['01 01   1', '01 01   2'])
        self.assertEqual([r['menge'] for r in result], [1, 2])
        self.assertTrue(all(r['ep'] == 0 and r['kosten'] == [] for r in result))

    def test_duplicate_and_unknown_d83_rejected(self):
        for text in ('2101 01   1NNN         00000001000psch\n25One\n' * 2,
                     '21unrecognized position\n25One'):
            with self.subTest(text=text):
                result = self.page.evaluate('''text => {
                  try {parseD83(text,'synthetic.d83'); return false;} catch (_) {return true;}
                }''', text)
                self.assertTrue(result)

    def test_encoding_and_override(self):
        for encoding in ('cp850', 'cp1252', 'utf-8'):
            with self.subTest(encoding=encoding):
                data = list('25Baustelle räumen\n2101 01   1NNN         00000001000m²'.encode(encoding))
                text = self.page.evaluate('bytes => KPGaebEncoding.decode(Uint8Array.from(bytes).buffer)', data)
                self.assertIn('räumen', text)
                self.assertIn('m²', text)
        forced = self.page.evaluate("bytes => KPGaebEncoding.decode(Uint8Array.from(bytes).buffer,'cp850')",
                                    list('Ä Ö Ü ß m³'.encode('cp850')))
        self.assertEqual(forced, 'Ä Ö Ü ß m³')

    def test_x83_compatibility_text(self):
        rows = self.page.evaluate('''() => parseGAEBXML(
          '<GAEB xmlns="http://www.gaeb.de/GAEB_DA_XML/DA83/3.3"><BoQCtgy RNoPart="01">' +
          '<Item RNoPart="010"><Qty>12.5</Qty><QU>m3</QU><Description><S>Boden ausheben</S>' +
          '<L><P>Boden lösen und laden; Tiefe 2 m.</P></L></Description></Item></BoQCtgy></GAEB>',
          'synthetic.x83')''')
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['kurztext'], 'Boden ausheben')
        self.assertIn('Tiefe 2 m', rows[0]['langtext'])
        self.assertEqual(rows[0]['menge'], 12.5)

    def test_linked_longtext_detects_disposal_conflict(self):
        result = self.page.evaluate('''() => {
          const a={kurztext:'Boden entsorgen',me:'t',langtext:'Boden entsorgen',
            linkedD83:{langtext:'Entsorgung Boden BM-0 AVV 170504'}};
          const b={kurztext:'Boden entsorgen',me:'t',langtext:'Boden entsorgen',
            linkedD83:{langtext:'Entsorgung Boden BM-F3 AVV 170506'}};
          return {a:getMatchProfile(a).fullRaw, b:getMatchProfile(b).fullRaw,
            caps:calcScore(a,b).debug.hardCapsApplied};
        }''')
        self.assertIn('BM-0', result['a'])
        self.assertIn('BM-F3', result['b'])
        self.assertTrue(result['caps'], result)

    def test_large_references_survive_reload(self):
        # More than localStorage's practical quota; exercises real IndexedDB persistence.
        projects = [{'name': 'Synthetic', 'active': True, 'positions': [
            {'oz': str(i), 'kurztext': 'Synthetic position', 'langtext': 'x' * 8000,
             'kosten': [], 'me': 'm3', 'menge': i + 1} for i in range(1500)]}]
        self.assertEqual(self.import_projects(projects), 1)
        self.page.reload()
        self.page.evaluate('referenceStorageReady')
        result = self.page.evaluate('({count:S.refProjects[0].positions.length,last:S.refProjects[0].positions[1499].menge})')
        self.assertEqual(result, {'count': 1500, 'last': 1500})

    def test_direct_link_preserves_disposal_cap_in_actual_matching(self):
        result = self.page.evaluate('''async () => {
          const np={oz:'01.001',kurztext:'Boden entsorgen',me:'t',menge:10,
            langtext:'Entsorgung Boden BM-0 AVV 170504'};
          const rp={...np,source:'Synthetic',matchedXML:true,matchedD83:true,
            kosten:[{typ:'L',menge:1,preis:12}],ep:12,
            linkedD83:{...np,langtext:'Entsorgung Boden BM-F0'}};
          S.newLV=[np]; S.refProjects=[{name:'Synthetic',active:true,positions:[rp]}];
          document.getElementById('thresh').value='35';
          const evaluated=calcScore(np,rp);
          await runMatch();
          const row=S.results[0], match=row.matches[0];
          showDetail(0);
          return {base:evaluated.score,direct:linkedD83MatchScore(np,rp),
            score:match.score,debug:match.debug,accepted:row.accepted,
            details:document.getElementById('dBody').textContent};
        }''')
        self.assertEqual(result['direct'], 1)
        self.assertTrue(result['debug']['hardCapsApplied'])
        self.assertEqual(result['score'], result['base'])
        self.assertEqual(result['debug']['finalScore'], result['score'])
        self.assertFalse(result['accepted'])
        self.assertIn('Prüfschritte · BETA', result['details'])
        self.assertIn('keine Wahrscheinlichkeit', result['details'])

    def test_project_bonus_preserves_caps_in_both_manual_searches(self):
        result = self.page.evaluate('''() => {
          const np={oz:'01',kurztext:'Boden entsorgen',me:'t',menge:10,
            langtext:'Entsorgung Boden BM-0 AVV 170504'};
          const rp={...np,source:'Synthetic',matchedXML:true,
            langtext:'Entsorgung Boden BM-F3 AVV 170506',kosten:[{typ:'L',menge:1,preis:12}]};
          const target={newPos:np,matches:[],sel:0,accepted:false};
          S.refProjects=[{name:'Synthetic',active:true,positions:[rp]}];
          S.results=[target,{newPos:np,matches:[{pos:rp,kind:'CALC',score:90}],accepted:true}];
          resetManualCache();
          const pool=getManualRefPool(true);
          const sync=computeManualCandidateRowsSync(target,pool.refs,pool)[0];
          const global=getGlobalManualSearchRows(target,true,'boden',['boden'])[0];
          return {base:calcScore(np,rp).score,sync,global};
        }''')
        for path in ('sync', 'global'):
            row = result[path]
            self.assertGreater(row['debug']['requestedProjectBoost'], 0)
            self.assertEqual(row['debug']['projectBoost'], 0)
            self.assertEqual(row['score'], result['base'])
            self.assertEqual(row['debug']['finalScore'], row['score'])

    def test_review_package_reports_missing_prices_and_inspection_steps(self):
        self.page.evaluate('''() => {
          const np={oz:'01',kurztext:'Boden lösen',me:'m3',menge:12};
          const pos={...np,source:'Synthetic',kosten:[{typ:'L',menge:1,preis:null}]};
          S.newLV=[np]; S.results=[{newPos:np,matches:[{pos,score:90,kind:'CALC',
            debug:{unitScore:100,categoryScore:100}}],sel:0,accepted:false}];
        }''')
        with self.page.expect_download() as info:
            self.page.evaluate('downloadBrowserReview()')
        payload = json.loads(Path(info.value.path()).read_text())
        candidate = payload['positionen'][0]['kandidaten'][0]
        quality = candidate['datenqualitaet']
        self.assertIn('Langtext', quality['fehlendeLeistungsdaten'])
        self.assertIn('Menge oder Preis im Ansatz fehlt oder ist ungültig', quality['kalkulationshinweise'])
        self.assertEqual(len(candidate['pruefschritte']), 5)
        self.assertIn('Nicht bestätigt', quality['preispruefung'])
        self.assertIsNone(candidate['kostenansaetze'][0]['historischerPreis'])

    def test_invalid_import_keeps_existing_data(self):
        self.import_projects([{'name': 'Retain', 'positions': []}])
        self.page.on('dialog', lambda dialog: dialog.dismiss())
        self.import_projects([{'name': 'Invalid', 'positions': 'not a list'}])
        self.assertEqual(self.page.evaluate('S.refProjects[0].name'), 'Retain')
        self.page.reload()
        self.page.evaluate('referenceStorageReady')
        self.assertEqual(self.page.evaluate('S.refProjects[0].name'), 'Retain')

    def test_failed_save_keeps_committed_data(self):
        self.import_projects([{'name': 'Retain', 'positions': []}])
        self.page.evaluate('''() => {KPReferenceStore.save=async () => {throw new Error('Simulated quota');};}''')
        self.import_projects([{'name': 'Do not replace', 'positions': []}])
        self.assertEqual(self.page.evaluate('S.refProjects[0].name'), 'Retain')
        self.assertIn('fehlgeschlagen', self.page.locator('#referenceStorageStatus').inner_text())
        self.page.reload()
        self.page.evaluate('referenceStorageReady')
        self.assertEqual(self.page.evaluate('S.refProjects[0].name'), 'Retain')

    def test_legacy_storage_migration(self):
        self.context.close()
        self.context = self.browser.new_context()
        # Find the actual versioned key without copying any browser data.
        source = (ROOT / 'KalkPilot_by_Janek.html').read_text()
        import re
        key = re.search(r"const STORAGE_KEY='([^']+)'", source).group(1)
        self.context.add_init_script(f"localStorage.setItem({json.dumps(key)},JSON.stringify([{{name:'Legacy',positions:[]}}]))")
        self.page = self.context.new_page()
        self.page.goto(self.url + '/KalkPilot_by_Janek.html')
        self.page.evaluate('referenceStorageReady')
        self.assertEqual(self.page.evaluate('S.refProjects[0].name'), 'Legacy')
        self.assertEqual(self.page.evaluate('async () => (await KPReferenceStore.load())[0].name'), 'Legacy')
        self.assertIsNotNone(self.page.evaluate('key => localStorage.getItem(key)', key))

    def test_unresolved_assembly_prevents_auto_accept(self):
        result = self.page.evaluate('''() => {
          const pos={kurztext:'Boden lösen',me:'m3',kosten:[{typ:'B',isAssembly:true,menge:1,preis:0}]};
          const match={pos,score:100,kind:'CALC',debug:{unitScore:100,categoryScore:100}};
          const row={newPos:{kurztext:'Boden lösen',me:'m3'},matches:[match],sel:0};
          return {accepted:canAutoAcceptMatch(row,match),risks:getMatchRiskReasons(row,match)};
        }''')
        self.assertFalse(result['accepted'])
        self.assertIn('Bausteinpreis nicht aufgelöst', result['risks'])

    def test_manual_chatgpt_download(self):
        self.page.evaluate('''() => {
          S.newLV=[{oz:'01',kurztext:'Synthetic excavation',langtext:'Depth 2m',menge:12,me:'m3'}];
          S.results=[];
        }''')
        with self.page.expect_download() as info:
            self.page.evaluate('downloadBrowserReview()')
        payload = json.loads(Path(info.value.path()).read_text())
        self.assertEqual(payload['schema'], 'kalkpilot.browser-review')
        self.assertIn('BETA', payload['status'])
        self.assertEqual(payload['positionen'][0]['ziel']['menge'], 12)
        self.assertEqual(payload['positionen'][0]['kandidaten'], [])
        self.assertEqual(self.page.locator('#llmApiKey').count(), 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
