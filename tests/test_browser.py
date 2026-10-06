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

    def test_uploaded_lv_enables_start_after_reference_import(self):
        self.page.locator('#fNew').set_input_files({
            'name': 'new.d83', 'mimeType': 'application/octet-stream',
            'buffer': b'2101 01   1NNN         00000001000psch\n25Baustelle einrichten\n'})
        self.page.wait_for_function('S.newLV.length === 1')
        self.assertTrue(self.page.locator('#runBtn').is_disabled())
        self.assertIn('Referenzdatenbank', self.page.locator('#matchStartStatus').inner_text())
        self.assertTrue(self.page.locator('#matchStartHelp').is_visible())
        self.import_projects([{'name': 'Synthetic', 'active': True, 'positions': [
            {'oz': '01.001', 'kurztext': 'Baustelle einrichten', 'menge': 1, 'me': 'psch',
             'kosten': [{'typ': 'L', 'menge': 1, 'preis': 12}]}]}])
        self.assertTrue(self.page.locator('#runBtn').is_enabled())
        self.page.locator('#ruleComparisonOptions > summary').click()
        self.page.locator('#runBtn').click()
        self.page.wait_for_function('!S.matching && S.results.length === 1')
        self.assertGreater(self.page.evaluate('S.results[0].matches.length'), 0)
        self.page.evaluate('selectAllProj(false)')
        self.page.wait_for_function('getActiveRef().length === 0')
        self.assertTrue(self.page.locator('#runBtn').is_disabled())
        self.assertIn('deaktiviert', self.page.locator('#matchStartStatus').inner_text())

    def test_active_text_references_enable_start_when_toggled(self):
        payload = {'name': 'synthetic.d83', 'mimeType': 'application/octet-stream',
                   'buffer': b'2101 01   1NNN         00000001000psch\n25Baustelle einrichten\n'}
        self.page.locator('#fileD83').set_input_files(payload)
        self.page.wait_for_function('P.d83Pos.length === 1')
        self.page.locator('#addProjBtn').click()
        self.page.wait_for_function('getActiveRef().length === 1')
        self.page.locator('#fNew').set_input_files(payload)
        self.page.wait_for_function('S.newLV.length === 1')
        self.page.locator('#d83RefFilter').uncheck()
        self.assertTrue(self.page.locator('#runBtn').is_disabled())
        self.assertIn('Textreferenzen', self.page.locator('#matchStartStatus').inner_text())
        self.page.locator('#d83RefFilter').check()
        self.assertTrue(self.page.locator('#runBtn').is_enabled())
        self.assertIn('ohne Preise', self.page.locator('#matchStartStatus').inner_text())
        self.page.locator('#ruleComparisonOptions > summary').click()
        self.page.locator('#runBtn').click()
        self.page.wait_for_function('!S.matching && S.results.length === 1')
        self.assertEqual(self.page.evaluate('S.results[0].matches[0].kind'), 'TEXT_ONLY')
        self.assertFalse(self.page.evaluate('S.results[0].accepted'))

    def test_prefixed_x83_upload_without_xml_declaration(self):
        xml = ('<g:GAEB xmlns:g="http://www.gaeb.de/GAEB_DA_XML/DA83/3.3">'
               '<g:BoQCtgy RNoPart="01"><g:Item RNoPart="010"><g:Qty>12.5</g:Qty>'
               '<g:QU>m3</g:QU><g:Description><g:S>Boden ausheben</g:S>'
               '</g:Description></g:Item></g:BoQCtgy></g:GAEB>')
        self.page.locator('#fNew').set_input_files({
            'name': 'prefix.x83', 'mimeType': 'application/xml', 'buffer': xml.encode()})
        self.page.wait_for_function('S.newLV.length === 1')
        self.assertIn('1 Positionen', self.page.locator('#lvLoadedTxt').inner_text())
        self.page.locator('#fNew').set_input_files({
            'name': 'empty.x83', 'mimeType': 'application/xml', 'buffer': b'<GAEB/>'})
        self.page.wait_for_function("document.getElementById('lvImportStatus').textContent.includes('Keine LV-Positionen')")
        self.assertIn('bisherige LV', self.page.locator('#lvImportStatus').inner_text())
        self.assertEqual(self.page.evaluate('S.newLV[0].menge'), 12.5)

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
        self.assertEqual(quality['teilkosten']['masterDataCount'],1)
        self.assertNotIn('Menge oder Preis im Ansatz fehlt oder ist ungültig',quality['kalkulationshinweise'])
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

    def test_llm_buttons_are_accessible_on_work_laptop_screen(self):
        self.page.evaluate("switchTab('t2')")
        for width in (1366, 1024):
            self.page.set_viewport_size({'width': width, 'height': 768})
            result = self.page.evaluate("""() => {
              const button=document.getElementById('llmRequestBtn');const rect=button.getBoundingClientRect();
              const hit=document.elementFromPoint(rect.x+rect.width/2,rect.y+rect.height/2);
              return {visible:rect.y>=0&&rect.bottom<=innerHeight,hit:hit===button||button.contains(hit),
                optional:document.getElementById('ruleComparisonOptions').open};
            }""")
            self.assertTrue(result['visible'])
            self.assertTrue(result['hit'])
            self.assertFalse(result['optional'])

    def test_technical_conflicts_override_identical_short_text(self):
        result = self.page.evaluate("""() => {
          const pair=(text,a,b,unit='m')=>({a:{kurztext:text,langtext:a,me:unit},b:{kurztext:text,langtext:b,me:unit}});
          return [
            pair('PE100 Rohr liefern und einbauen','PE100 da 75 SDR 11','PE100 da 315 SDR 11'),
            pair('PE100 Rohr liefern und einbauen','PE100 da 75 SDR 11','PE100 da 75 SDR 17'),
            pair('Kunststoffrohr liefern und einbauen','Rohr PE100 da 75','Rohr PE80 da 75'),
            pair('Altholz entsorgen','AVV 170204* Altholz A IV','AVV 170201 nicht gefährliches Altholz','t'),
            pair('Abfälle entsorgen','AVV 170204*','AVV 170204','t'),
            pair('Kiessand einbauen','Unterhalb der Grundwasseroberfläche einbauen','Trocken oberhalb des Grundwassers einbauen','m3')
          ].map(p=>calcScore(p.a,p.b));
        }""")
        for row in result:
            self.assertLessEqual(row['score'], 45)
            self.assertTrue(row['debug']['technicalCheck']['conflicts'])

    def test_llm_request_contains_requirements_and_unknown_is_not_equal(self):
        result = self.page.evaluate("""async () => {
          const a={kurztext:'PE100 Rohr liefern und einbauen',langtext:'PE100 da 75 SDR 11',me:'m'};
          const b={...a,langtext:'PE 100 Außendurchmesser 75 mm SDR11'};
          const unknown={kurztext:'Rohr liefern und einbauen',me:'m'};
          const dn={...a,langtext:'PE100 DN 75 SDR 11'};
          const request=await KPLLMMatching.buildRequest({version:APP_VERSION,targets:[a],references:[b]});
          return {request,positive:KPLLMMatching.compareRequirements(a,b),unknown:calcScore(a,unknown),
            dn:KPLLMMatching.compareRequirements(a,dn)};
        }""")
        self.assertEqual(result['request']['zielpositionen'][0]['fachmerkmale']['aussendurchmesser'], ['75'])
        self.assertEqual(result['request']['referenzen'][0]['fachmerkmale']['sdr'], ['11'])
        self.assertEqual(result['positive']['conflicts'], [])
        self.assertEqual(result['positive']['missing'], [])
        self.assertLessEqual(result['unknown']['score'], 68)
        self.assertTrue(result['unknown']['debug']['technicalCheck']['missing'])
        self.assertEqual(result['dn']['conflicts'], [])
        self.assertTrue(result['dn']['missing'])

    def test_partial_costs_separate_master_data_and_i2_factor_rows(self):
        result = self.page.evaluate("""() => {
          const pos={menge:1,me:'m2',kosten:[
            {descr:'Vlies',menge:1.15,preis:.68},
            {descr:'Lohn',menge:1,preis:54.79,factor:400,factorIsPerformanceFactor:1},
            {descr:'Gerät',menge:1,preis:0,isAssembly:true},
            {descr:'Nullpreis',menge:1,preis:0},
            {descr:'deaktiviert',menge:100,preis:100,sItemDisabled:1},
            {descr:'ungenutzt',menge:0,preis:0,isAssembly:true}
          ]};
          const before=JSON.stringify(pos);const result=KPBrowserReview.calculateKnownCosts(pos);
          return {...result,unchanged:before===JSON.stringify(pos)};
        }""")
        self.assertAlmostEqual(result['knownSubtotal'], .782)
        self.assertEqual(result['knownCount'], 1)
        self.assertEqual(result['openCount'], 0)
        self.assertEqual(result['masterDataCount'], 2)
        self.assertEqual(result['requiresI2Count'], 1)
        self.assertEqual(result['excludedCount'], 2)
        self.assertFalse(result['complete'])
        self.assertFalse(result['priceApproved'])
        self.assertIsNone(result['unitPrice'])
        self.assertTrue(result['unchanged'])

    def test_partial_costs_distinguish_simple_costs_from_lump_sum(self):
        result = self.page.evaluate("""() => {
          const basic={menge:1,me:'h',kosten:[{menge:2,preis:60},{menge:1,preis:-5}]};
          const lump={...basic,subItems:[{sItemLSum:1}],linkedD83:{menge:1188,me:'m'}};
          const invalid={...basic,kosten:[{menge:1,preis:null},{menge:1,preis:10,curCoC:'USD'}]};
          return [basic,lump,invalid].map(p=>KPBrowserReview.calculateKnownCosts(p));
        }""")
        self.assertEqual(result[0]['knownSubtotal'], 115)
        self.assertTrue(result[0]['complete'])
        self.assertFalse(result[0]['priceApproved'])
        self.assertFalse(result[1]['complete'])
        self.assertTrue(result[1]['basisReasons'])
        self.assertIsNone(result[1]['unitPrice'])
        self.assertIsNone(result[2]['knownSubtotal'])
        self.assertEqual(result[2]['openCount'], 0)
        self.assertEqual(result[2]['masterDataCount'], 1)
        self.assertEqual(result[2]['requiresI2Count'], 1)

    def test_missing_resource_keys_prevent_automatic_reference_acceptance(self):
        result = self.page.evaluate("""() => {
          return [
            {kosten:[{typ:'L',menge:1,preis:50,factor:400,factorIsPerformanceFactor:1}]},
            {kosten:[{typ:'M',menge:1,preis:0}]},
            {kosten:[{typ:'G',menge:1,preis:100}],subItems:[{sItemLSum:1}]}
          ].map(data=>{
            const pos={kurztext:'Boden lösen',me:'m3',...data};
            const match={pos,score:100,kind:'CALC',debug:{unitScore:100,categoryScore:100}};
            const row={newPos:{kurztext:'Boden lösen',me:'m3'},matches:[match],sel:0};
            return {auto:canAutoAcceptMatch(row,match),risks:getMatchRiskReasons(row,match),status:KPBrowserReview.priceStatus(pos)};
          });
        }""")
        for row in result:
            self.assertFalse(row['auto'])
            self.assertTrue(row['risks'])
            self.assertFalse(row['status']['approved'])

    def test_reference_comparison_shows_price_basis_without_changing_prices(self):
        result = self.page.evaluate("""() => {
          const a={oz:'1',source:'A',kurztext:'Baufacharbeiter',langtext:'Baufacharbeiter',me:'h',menge:1,ep:60,kosten:[{typ:'L',menge:1,preis:60}]};
          const b={...a,oz:'2',source:'<img src=x onerror=alert(1)>',me:'Std',ep:75,kosten:[{typ:'L',menge:1,preis:75}]};
          const bad={...a,oz:'3',me:'m3',ep:900};
          S.refProjects=[{name:'A',active:true,positions:[a,b,bad]}];
          _refPreviewCache=[a];showRefDetail(0);
          const peers=KPBrowserReview.referencePeers(a,getActiveRef());
          return {peers:peers.map(p=>p.oz),text:document.getElementById('dBody').textContent,
            injected:document.querySelector('#dBody img')!==null,prices:[a.ep,b.ep],costs:[a.kosten[0].preis,b.kosten[0].preis]};
        }""")
        self.assertEqual(result['peers'], ['2'])
        self.assertIn('Preis ungeprüft', result['text'])
        self.assertIn('Referenzen vergleichen', result['text'])
        self.assertIn('60.00', result['text'])
        self.assertIn('75.00', result['text'])
        self.assertFalse(result['injected'])
        self.assertEqual(result['prices'], [60, 75])
        self.assertEqual(result['costs'], [60, 75])

    def test_missing_device_key_prevents_auto_accept(self):
        result = self.page.evaluate('''() => {
          const pos={kurztext:'Boden lösen',me:'m3',kosten:[{typ:'B',isAssembly:true,menge:1,preis:0}]};
          const match={pos,score:100,kind:'CALC',debug:{unitScore:100,categoryScore:100}};
          const row={newPos:{kurztext:'Boden lösen',me:'m3'},matches:[match],sel:0};
          return {accepted:canAutoAcceptMatch(row,match),risks:getMatchRiskReasons(row,match)};
        }''')
        self.assertFalse(result['accepted'])
        self.assertIn('Kostenarten-/Gerätekennung fehlt', result['risks'])
        self.assertNotIn('Bausteinpreis nicht aufgelöst', result['risks'])

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

    def prepare_llm_case(self):
        self.import_projects([{'name': 'Synthetic', 'active': True, 'positions': [
            {'oz': 'R.01', 'kurztext': 'Boden entsorgen', 'langtext': 'Entsorgung Boden BM-F3',
             'menge': 10, 'me': 't', 'kosten': [{'typ': 'L', 'menge': 1, 'preis': 12}]},
            {'oz': 'R.02', 'kurztext': 'Boden entsorgen', 'langtext': 'Entsorgung Boden BM-0',
             'menge': 10, 'me': 't', 'kosten': [{'typ': 'L', 'menge': 1, 'preis': 20}]}]}])
        self.page.evaluate('''() => {
          S.newLV=[{oz:'N.01',kurztext:'Boden entsorgen',langtext:'Entsorgung Boden BM-0',menge:10,me:'t'}];
          switchTab('t2');checkRunBtn();
        }''')
        with self.page.expect_download() as info:
            self.page.locator('#llmProvider').select_option('cloud')
            self.page.locator('#llmRequestBtn').click()
        request = json.loads(Path(info.value.path()).read_text())
        self.assertEqual(request['schema'], 'kalkpilot.llm-matching-request')
        self.assertEqual(len(request['referenzen']), 2)
        return {'schema': 'kalkpilot.llm-matches', 'schemaVersion': 1,
                'requestId': request['requestId'], 'matches': [
                    {'targetId': 't1', 'status': 'matched', 'referenceIds': ['r2'],
                     'confidence': 'high', 'reason': '<img src=x onerror=alert(1)> Die Materialklasse BM-0 passt.',
                     'differences': [], 'missingInformation': [], 'preis': 999999}]}

    def load_llm_response(self, response):
        self.page.locator('#fileLLMMatches').set_input_files({
            'name': 'llm.json', 'mimeType': 'application/json',
            'buffer': json.dumps(response).encode()})
        self.page.wait_for_function("document.getElementById('llmMatchingStatus').textContent.includes('eingelesen') || document.getElementById('llmMatchingStatus').textContent.includes('nicht übernommen')")

    def test_llm_file_roundtrip_selects_reference_without_approving_price(self):
        response = self.prepare_llm_case()
        self.load_llm_response(response)
        result = self.page.evaluate('''() => {const r=S.results[0],m=r.matches[0];
          return {oz:m.pos.oz,ep:m.pos.ep,accepted:r.accepted,
            auto:canAutoAcceptMatch(r,m),reason:m.debug.reasonText};}''')
        self.assertEqual(result['oz'], 'R.02')
        self.assertEqual(result['ep'], 20)
        self.assertFalse(result['accepted'])
        self.assertFalse(result['auto'])
        self.assertIn('BM-0', result['reason'])
        self.assertIn('LLM', self.page.locator('#mTbl').inner_text())
        self.assertEqual(self.page.locator('#mTbl img').count(), 0)

    def test_invalid_and_stale_llm_results_keep_previous_selection(self):
        response = self.prepare_llm_case()
        self.load_llm_response(response)
        for variant in ('unknown_ref', 'duplicate_target', 'stale', 'changed_data'):
            invalid = json.loads(json.dumps(response))
            if variant == 'unknown_ref':
                invalid['matches'][0]['referenceIds'] = ['invented']
            elif variant == 'duplicate_target':
                invalid['matches'] *= 2
            elif variant == 'stale':
                invalid['requestId'] = 'old'
            else:
                self.page.evaluate("S.newLV[0].langtext='Entsorgung Boden BM-F3'")
            self.page.evaluate("document.getElementById('llmMatchingStatus').textContent='' ")
            self.load_llm_response(invalid)
            self.assertIn('nicht übernommen', self.page.locator('#llmMatchingStatus').inner_text())
            self.assertEqual(self.page.evaluate('S.results[0].matches[0].pos.oz'), 'R.02')

    def test_llm_choice_obeys_conflict_caps_and_no_match_has_visible_reason(self):
        response = self.prepare_llm_case()
        response['matches'][0]['referenceIds'] = ['r1']
        self.load_llm_response(response)
        result = self.page.evaluate('''() => ({score:S.results[0].matches[0].score,
          caps:S.results[0].matches[0].debug.hardCapsApplied,
          accepted:S.results[0].accepted})''')
        self.assertLess(result['score'], 40)
        self.assertTrue(result['caps'])
        self.assertFalse(result['accepted'])
        response['matches'][0].update(status='no_match', referenceIds=[], reason='Keine fachlich belastbare Referenz.')
        self.page.evaluate("document.getElementById('llmMatchingStatus').textContent='' ")
        self.load_llm_response(response)
        self.assertEqual(self.page.evaluate('S.results[0].matches.length'), 0)
        self.assertIn('Keine fachlich belastbare Referenz.', self.page.locator('#mTbl').inner_text())


if __name__ == '__main__':
    unittest.main(verbosity=2)
