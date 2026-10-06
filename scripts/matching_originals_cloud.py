"""Compare every imported position to other projects and prepare an unlabelled review set.

This exercises the real browser rules. It does not call a model or claim LLM accuracy.
Customer outputs must remain outside Git. Reference prices never affect ranking.
"""
import argparse
from collections import Counter, defaultdict, deque
import csv
from functools import partial
from http.server import ThreadingHTTPServer
import json
import os
from pathlib import Path
import shutil
import subprocess
from threading import Thread
from playwright.sync_api import sync_playwright
from llm_matching_cloud import ROOT, QuietHandler


def choose_review(rows, count):
    """Round robin over projects and categories, not the largest project's best scores."""
    groups=defaultdict(lambda:defaultdict(deque))
    for row in rows:
        groups[row['project']][row['category']].append(row)
    chosen=[]
    while groups and len(chosen)<count:
        for project in list(sorted(groups)):
            categories=groups[project]
            category=next(iter(categories))
            chosen.append(categories[category].popleft())
            queue=categories.pop(category)
            if queue:categories[category]=queue
            if not categories:del groups[project]
            if len(chosen)==count:break
    return chosen


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--references',required=True,type=Path)
    parser.add_argument('--output-dir',required=True,type=Path)
    parser.add_argument('--baseline-ref')
    parser.add_argument('--review-count',type=int,default=200)
    args=parser.parse_args()
    output=args.output_dir.resolve()
    if output==ROOT or ROOT in output.parents:parser.error('Customer outputs must be outside the repository.')
    if not args.references.is_file():parser.error('Reference JSON does not exist.')
    if args.review_count<1:parser.error('Review count must be positive.')
    output.mkdir(parents=True,exist_ok=True)
    current=(ROOT/'js/llm-matching.js').read_text()
    baseline=subprocess.run(['git','show',args.baseline_ref+':js/llm-matching.js'],cwd=ROOT,
        capture_output=True,text=True,check=True).stdout if args.baseline_ref else None
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(ROOT)))
    Thread(target=server.serve_forever,daemon=True).start()
    os.environ.setdefault('PLAYWRIGHT_BROWSERS_PATH',str(ROOT/'.cache/ms-playwright'))
    try:
        with sync_playwright() as p:
            executable=os.environ.get('KALKPILOT_CHROMIUM') or shutil.which('chromium')
            browser=p.chromium.launch(**({'executable_path':executable} if executable else {}))
            try:
                page=browser.new_page();base=f'http://127.0.0.1:{server.server_port}'
                errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
                page.route('**/*',lambda r:r.continue_() if r.request.url.startswith(base+'/') else r.abort())
                page.goto(base+'/KalkPilot_by_Janek.html');page.evaluate('referenceStorageReady')
                page.evaluate('async text=>importRefFromJSON(new File([text],"references.json"))',args.references.read_text(encoding='utf-8-sig'))
                meta=page.evaluate('''()=>{
                  // Disable learnt and built-in choices: test only the held-out texts.
                  getAllTopMatchEntries=()=>[];getAllLearningEntries=()=>[];getAllRejectedEntries=()=>[];
                  const active=new Set(getActiveRef());
                  const positions=S.refProjects.flatMap(project=>(project.positions || []).filter(pos=>active.has(pos))
                    .map(pos=>({...pos,source:project.name})));
                  window.originalPositions=positions.map((pos,i)=>({id:'r'+(i+1),project:pos.source,pos,
                    target:{oz:pos.oz,kurztext:pos.kurztext,
                      langtext:[...new Set([pos.langtext,pos.outlineSpecs,pos.linkedD83?.langtext].filter(Boolean))].join('\\n\\n'),
                      me:pos.linkedD83?.me || pos.me,menge:pos.linkedD83?.menge ?? pos.menge}}));
                  return originalPositions.map(p=>({id:p.id,project:p.project,category:positionCategory(p.target)}));
                }''')
                if len({r['project'] for r in meta})<2:raise RuntimeError('At least two projects are needed for a holdout.')
                results={}
                for phase,source in ([('baseline',baseline)] if baseline else [])+[('current',current)]:
                    page.evaluate('source=>(0,eval)(source)',source)
                    rows=[]
                    for start in range(0,len(meta),25):
                        rows+=page.evaluate('''({start,end})=>originalPositions.slice(start,end).map(target=>{
                          const refs=originalPositions.filter(r=>r.project!==target.project);
                          const scored=refs.map(ref=>{
                            const score=calcScore(target.target,ref.pos,{isTextOnly:!(ref.pos.kosten || []).some(c=>c.typ!=='S')});
                            return {id:ref.id,project:ref.project,oz:ref.pos.oz,short:ref.pos.kurztext,
                              score:score.score,conflicts:score.debug.technicalCheck.conflicts,missing:score.debug.technicalCheck.missing};
                          }).sort((a,b)=>b.score-a.score || a.id.localeCompare(b.id));
                          return {id:target.id,project:target.project,oz:target.pos.oz,short:target.pos.kurztext,
                            category:positionCategory(target.target),references:refs.length,top:scored.slice(0,3)};
                        })''',{'start':start,'end':start+25})
                        print(f'{phase}: {len(rows)}/{len(meta)} positions',flush=True)
                    results[phase]=rows
                selected=choose_review(results['current'],min(args.review_count,len(meta)))
                packets=page.evaluate('''ids=>ids.map(id=>{
                  const row=originalPositions.find(p=>p.id===id);
                  const data=p=>({...p.target,project:p.project,
                    technical:KPLLMMatching.technicalProfile(p.pos),resources:KPBrowserReview.resourceContext(p.pos)});
                  return {id, target:data(row)};
                })''',[r['id'] for r in selected])
                packets={p['id']:p for p in packets}
                for row in selected:
                    packet=packets[row['id']]
                    packet.update({'category':row['category'],'referenceCount':row['references'],
                        'candidates':row['top'],'expectedStatus':None,'expectedReferenceIds':[],
                        'reviewStatus':'unreviewed','reviewReason':'','priceApproval':False})
                ref_ids=sorted({c['id'] for row in selected for c in row['top']})
                candidate_texts=page.evaluate('''ids=>ids.map(id=>{
                  const p=originalPositions.find(p=>p.id===id);
                  return {id,project:p.project,...p.target,
                    resources:KPBrowserReview.resourceContext(p.pos)};
                })''',ref_ids)
                report={'schema':'kalkpilot.original-holdout','version':1,'positions':len(meta),
                    'projects':dict(Counter(r['project'] for r in meta)),
                    'pairsPerPhase':sum(r['references'] for r in results['current']),
                    'baselineRef':args.baseline_ref,'results':results,
                    'limitation':'Rule rankings only; expectations are unreviewed, not an LLM or expert accuracy benchmark.'}
                (output/'holdout-rankings.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
                review={'schema':'kalkpilot.matching-review-set','version':1,
                    'instructions':['Confirm expected status and references using the complete source texts.',
                        'Identical text is not automatic ground truth. Exclude the target project.',
                        'Master-data prices and performance factors are separate from semantic equivalence.'],
                    'cases':list(packets.values()),'candidateTexts':candidate_texts}
                (output/'review-set.json').write_text(json.dumps(review,ensure_ascii=False,indent=2))
                with (output/'review-sheet.csv').open('w',encoding='utf-8-sig',newline='') as f:
                    writer=csv.writer(f,delimiter=';')
                    writer.writerow(['ZielID','Projekt','OZ','Kurztext','Kategorie','Kandidaten','Erwarteter Status','Erwartete Referenzen','Fachlicher Grund','Prüfstatus'])
                    for row in selected:writer.writerow([row['id'],row['project'],row['oz'],row['short'],row['category'],
                        ' | '.join(c['id']+' '+c['short'] for c in row['top']),'','','','unreviewed'])
                if errors:raise RuntimeError('; '.join(errors))
                print(json.dumps({'positions':len(meta),'projects':report['projects'],
                    'pairsPerPhase':report['pairsPerPhase'],'reviewCases':len(selected),'expertConfirmed':0}),flush=True)
            finally:browser.close()
    finally:server.shutdown();server.server_close()


if __name__=='__main__':main()
