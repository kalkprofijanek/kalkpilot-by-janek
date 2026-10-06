"""Build balanced held-out original LV excerpts and full-reference Copilot workbooks.

Prepares review cases, not expert-confirmed answers. No model invocation or uploads.
"""
import argparse
import base64
from functools import partial
from http.server import ThreadingHTTPServer
import json
import os
from pathlib import Path
import shutil
from threading import Thread
import xml.etree.ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED
from playwright.sync_api import sync_playwright
from llm_matching_cloud import ROOT, QuietHandler
from matching_originals_cloud import choose_review


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--references',required=True,type=Path)
    parser.add_argument('--rankings',required=True,type=Path)
    parser.add_argument('--output-dir',required=True,type=Path)
    parser.add_argument('--count',type=int,default=200)
    args=parser.parse_args();out=args.output_dir.resolve()
    if out==ROOT or ROOT in out.parents:parser.error('Outputs must be outside Git.')
    if args.count<1:parser.error('Count must be positive.')
    for path in [args.references,args.rankings]:
        if not path.is_file():parser.error(f'File does not exist: {path}')
    ranks=json.loads(args.rankings.read_text())
    selected=choose_review(ranks['results']['current'],args.count)
    projects=json.loads(args.references.read_text(encoding='utf-8-sig'))
    if not isinstance(projects,list):parser.error('Expected reference-project JSON list.')
    out.mkdir(parents=True,exist_ok=True)
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(ROOT)))
    Thread(target=server.serve_forever,daemon=True).start()
    os.environ.setdefault('PLAYWRIGHT_BROWSERS_PATH',str(ROOT/'.cache/ms-playwright'))
    try:
        with sync_playwright() as p:
            exe=os.environ.get('KALKPILOT_CHROMIUM') or shutil.which('chromium')
            browser=p.chromium.launch(**({'executable_path':exe} if exe else {}))
            try:
                page=browser.new_page();base=f'http://127.0.0.1:{server.server_port}'
                errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
                page.route('**/*',lambda r:r.continue_() if r.request.url.startswith(base+'/') else r.abort())
                page.goto(base+'/KalkPilot_by_Janek.html');page.evaluate('referenceStorageReady')
                page.evaluate('async text=>importRefFromJSON(new File([text],"all.json"))',args.references.read_text(encoding='utf-8-sig'))
                sources=page.evaluate('''()=>{
                  const active=new Set(getActiveRef());
                  const positions=S.refProjects.flatMap(project=>(project.positions || []).filter(p=>active.has(p))
                    .map(p=>({...p,source:project.name})));
                  return positions.map((p,i)=>({id:'r'+(i+1),project:p.source,oz:p.oz,
                  kurztext:p.kurztext,langtext:[...new Set([p.langtext,p.outlineSpecs,p.linkedD83?.langtext].filter(Boolean))].join('\\n\\n'),
                  me:p.linkedD83?.me || p.me,menge:p.linkedD83?.menge ?? p.menge}));}''')
                source_map={s['id']:s for s in sources}
                for row in selected:
                    source=source_map[row['id']]
                    if (source['project'],source['oz'],source['kurztext'])!=(row['project'],row['oz'],row['short']):
                        raise RuntimeError('Rankings and source database do not describe the same positions.')
                summary=[]
                for index,project in enumerate(sorted({r['project'] for r in selected}),1):
                    folder=out/f'projekt-{index}';folder.mkdir(exist_ok=True)
                    rows=[r for r in selected if r['project']==project]
                    holds=[{**pr,'active':True,'positions':[{**p,'source':pr['name']} for p in pr['positions']]}
                        for pr in projects if pr['name']!=project]
                    (folder/'referenzen-ohne-zielprojekt.json').write_text(json.dumps(holds,ensure_ascii=False))
                    gaeb=ET.Element('GAEB');body=ET.SubElement(gaeb,'BoQBody')
                    itemlist=ET.SubElement(body,'Itemlist')
                    for row in rows:
                        source=source_map[row['id']]
                        item=ET.SubElement(itemlist,'Item',{'RNoPart':source['oz']})
                        ET.SubElement(item,'Qty').text=str(source['menge'] if source['menge'] is not None else 0)
                        ET.SubElement(item,'QU').text=source['me']
                        desc=ET.SubElement(item,'Description')
                        ET.SubElement(desc,'S').text=source['kurztext']
                        ET.SubElement(desc,'L').text=source['langtext']
                    xml=ET.tostring(gaeb,encoding='unicode')
                    (folder/'pruef-lv.x83').write_text(xml,encoding='utf-8')
                    # Re-import the generated excerpt so the request uses exactly the
                    # same whitespace, text and ID conventions as the user's browser.
                    page.evaluate('async text=>importRefFromJSON(new File([text],"holdout.json"))',json.dumps(holds,ensure_ascii=False))
                    page.evaluate('''({xml,project})=>{S.refProjects=S.refProjects.filter(p=>p.name!==project);S.newLV=parseGAEBXML(xml,'pruef-lv.x83');}''',{'xml':xml,'project':project})
                    request=page.evaluate('async ()=>(await getLLMMatchingContext()).request')
                    if len(request['zielpositionen'])!=len(rows):raise RuntimeError('Review excerpt lost target positions.')
                    if any(p['projekt']==project for p in request['referenzen']):raise RuntimeError('Target project leaked into references.')
                    (folder/'matching-auftrag.json').write_text(json.dumps(request,ensure_ascii=False,indent=2))
                    encoded=page.evaluate('''request=>new Promise((resolve,reject)=>{const reader=new FileReader();reader.onload=()=>resolve(reader.result.split(',')[1]);reader.onerror=()=>reject(new Error('Workbook cannot be read'));reader.readAsDataURL(KPCopilotExchange.exportRequest(request));})''',request)
                    workbook=base64.b64decode(encoded,validate=True)
                    (folder/'copilot-auftrag.xlsx').write_bytes(bytes(workbook))
                    mapping=[{'targetId':request['zielpositionen'][i]['id'],'originalId':r['id'],
                        'project':project,'oz':r['oz'],'category':r['category'],'expectedStatus':None,
                        'expectedReferenceIds':[],'reviewStatus':'unreviewed','reason':''} for i,r in enumerate(rows)]
                    (folder/'fachpruefung.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2))
                    summary.append({'folder':folder.name,'project':project,'targets':len(rows),
                        'references':len(request['referenzen']),'requestId':request['requestId'],
                        'workbookBytes':len(workbook),'expertConfirmed':0})
                if errors:raise RuntimeError('; '.join(errors))
                (out/'uebersicht.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
                (out/'README.txt').write_text('Private Originaldaten-Prüfpakete, keine bestätigten Musterlösungen.\n'
                    'Pro Projekt: Referenzen-ohne-Zielprojekt.json in KalkPilot laden, andere Projekte deaktivieren.\n'
                    'Pruef-lv.x83 als neues LV laden. Copilot-auftrag.xlsx oder Matching-auftrag.json in der KI bearbeiten.\n'
                    'Antwort in KalkPilot importieren. Fachpruefung.json erst nach unabhängiger fachlicher Prüfung ausfüllen.\n'
                    'Das Prüfauszug-XML dient ausschließlich diesem App-Prüflauf; kein zertifizierter Original-GAEB-Export.\n'
                    'Die Referenz-IDs sind lokal je Auftrag, nicht die globalen IDs des Ranglistenberichts.\n'
                    'Keine Preise freigegeben. Stammdatenpreise und Leistungsansätze werden in i2 berechnet.\n')
                with ZipFile(out/'Originaldaten-Pruefpakete.zip','w',ZIP_DEFLATED) as z:
                    for file in sorted(out.rglob('*')):
                        if file.is_file() and file.suffix!='.zip':z.write(file,file.relative_to(out))
                print(json.dumps({'cases':sum(s['targets'] for s in summary),'projects':summary,'expertConfirmed':0},ensure_ascii=False),flush=True)
            finally:browser.close()
    finally:server.shutdown();server.server_close()


if __name__=='__main__':main()
