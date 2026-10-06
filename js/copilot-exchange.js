/* Native XLSX exchange for user-initiated Microsoft 365 Copilot uploads. No network calls. */
(() => {
  'use strict';
  const encoder=new TextEncoder(), decoder=new TextDecoder('utf-8',{fatal:true});
  const limit=16*1024*1024;
  function crc32(bytes){let crc=0xffffffff;for(const byte of bytes){crc^=byte;for(let bit=0;bit<8;bit++)crc=(crc>>>1)^((crc&1)?0xedb88320:0);}return(crc^0xffffffff)>>>0;}
  const xml=value=>String(value??'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  function column(index){let result='';for(index++;index;index=Math.floor((index-1)/26))result=String.fromCharCode(65+(index-1)%26)+result;return result;}
  function sheet(rows){
    return '<?xml version="1.0" encoding="UTF-8"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>'+rows.map((row,i)=>'<row r="'+(i+1)+'">'+row.map((value,j)=>{
      const text=String(value??'');
      if(text.length>32767 || /[\x00-\x08\x0b\x0c\x0e-\x1f]/.test(text))throw new Error('Excel-Zelle enthält zu langen Text oder unzulässige Steuerzeichen.');
      return '<c r="'+column(j)+(i+1)+'" t="inlineStr"><is><t xml:space="preserve">'+xml(text)+'</t></is></c>';
    }).join('')+'</row>').join('')+'</sheetData></worksheet>';
  }
  function zip(files){
    const locals=[],centrals=[];let offset=0;
    for(const [name,content] of Object.entries(files)){
      const path=encoder.encode(name),data=encoder.encode(content),crc=crc32(data);
      const local=new Uint8Array(30+path.length+data.length),v=new DataView(local.buffer);
      v.setUint32(0,0x04034b50,true);v.setUint16(4,20,true);v.setUint16(6,0x800,true);v.setUint16(12,0x21,true);v.setUint32(14,crc,true);v.setUint32(18,data.length,true);v.setUint32(22,data.length,true);v.setUint16(26,path.length,true);
      local.set(path,30);local.set(data,30+path.length);locals.push(local);
      const central=new Uint8Array(46+path.length),c=new DataView(central.buffer);
      c.setUint32(0,0x02014b50,true);c.setUint16(4,20,true);c.setUint16(6,20,true);c.setUint16(8,0x800,true);c.setUint16(14,0x21,true);c.setUint32(16,crc,true);c.setUint32(20,data.length,true);c.setUint32(24,data.length,true);c.setUint16(28,path.length,true);c.setUint32(42,offset,true);central.set(path,46);centrals.push(central);offset+=local.length;
    }
    const size=centrals.reduce((sum,data)=>sum+data.length,0),end=new Uint8Array(22),e=new DataView(end.buffer);
    e.setUint32(0,0x06054b50,true);e.setUint16(8,centrals.length,true);e.setUint16(10,centrals.length,true);e.setUint32(12,size,true);e.setUint32(16,offset,true);
    return new Blob([...locals,...centrals,end],{type:'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'});
  }
  function workbook(sheets){
    const files={
      '_rels/.rels':'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>',
      'xl/workbook.xml':'<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>'+sheets.map((s,i)=>'<sheet name="'+xml(s.name)+'" sheetId="'+(i+1)+'" r:id="rId'+(i+1)+'"/>').join('')+'</sheets></workbook>',
      'xl/_rels/workbook.xml.rels':'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'+sheets.map((s,i)=>'<Relationship Id="rId'+(i+1)+'" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet'+(i+1)+'.xml"/>').join('')+'</Relationships>',
      '[Content_Types].xml':'<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'+sheets.map((s,i)=>'<Override PartName="/xl/worksheets/sheet'+(i+1)+'.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>').join('')+'</Types>'
    };
    sheets.forEach((s,i)=>files['xl/worksheets/sheet'+(i+1)+'.xml']=sheet(s.rows));return zip(files);
  }
  function chunks(text){const parts=[];let part='';for(const char of String(text||'')){if(part.length+char.length>32000){parts.push(part);part='';}part+=char;}parts.push(part);return parts;}
  function dataRows(positions,references=false){
    const parts=positions.map(p=>chunks(p.langtext)),count=parts.reduce((maximum,p)=>Math.max(maximum,p.length),1);
    const header=['ID',...(references?['Projekt']:[]),'OZ','Kurztext','Menge','Einheit','Titelkontext',...Array.from({length:count},(_,i)=>'Langtext '+(i+1)),'Fachmerkmale',...(references?['Kalkulationshinweise','Geräteansätze','Kostenarten und Leistungsansätze','Strukturhinweise']:[])];
    return [header,...positions.map((p,i)=>[p.id,...(references?[p.projekt]:[]),p.oz,p.kurztext,p.menge,p.einheit,p.titelkontext || '',...Array.from({length:count},(_,j)=>parts[i][j]||''),JSON.stringify(p.fachmerkmale),...(references?[(p.kalkulationshinweise||[]).join('\n'),JSON.stringify(p.geraeteansaetze || []),JSON.stringify(p.kalkulationsstruktur || []),(p.strukturhinweise || []).join('\n')]:[])])];
  }
  const headers=['requestId','ZielID','Status','ReferenzIDs','Sicherheit','Begründung','Unterschiede','FehlendeAngaben','Zielbeleg','Referenzbeleg','Preishinweise'];
  function exportRequest(request){
    const instructions=[...request.instructions.filter(value=>!value.startsWith('Liefere eine JSON-Datei') && !value.startsWith('Nenne für den ersten Referenzvorschlag')),
      'Lies alle Langtext-Spalten vollständig. Fachmerkmale sind Hilfen, nicht Ersatz für den Originaltext.',
      'Fülle das Blatt Antwort für jede ZielID aus. Status: matched, ambiguous oder no_match. Sicherheit: high, medium oder low. Mehrere ReferenzIDs durch | trennen.',
      'Preishinweise getrennt von der fachlichen Passung in die eigene Spalte schreiben. Unterschiede und FehlendeAngaben als Text mit Zeilenumbrüchen oder JSON-Arrays. Zielbeleg und Referenzbeleg sind wörtliche Auszüge für die erste ReferenzID. Belege mindestens 8 Zeichen lang, ohne Auslassungen; nicht erfinden.',
      'Wenn du nicht alle Zielpositionen und Referenzen vollständig lesen kannst, sage das ausdrücklich und liefere keine scheinbar vollständige Bewertung.',
      'Behalte requestId und ZielID unverändert. Liefere die Excel-Datei mit ausgefülltem Blatt Antwort oder dessen Tabelle als TSV/CSV. Ein fehlender Treffer ist ein zulässiges Ergebnis.'];
    return workbook([
      {name:'Auftrag',rows:[['Schlüssel','Wert'],['requestId',request.requestId],['AppVersion',request.appVersion],['Zielpositionen',request.zielpositionen.length],['Referenzen',request.referenzen.length],...instructions.map((value,i)=>['Schritt '+(i+1),value])]},
      {name:'Zielpositionen',rows:dataRows(request.zielpositionen)},
      {name:'Referenzen',rows:dataRows(request.referenzen,true)},
      {name:'Antwort',rows:[headers,...request.zielpositionen.map(p=>[request.requestId,p.id,'','','','','','','','',''])]}
    ]);
  }
  async function unzip(buffer){
    const bytes=new Uint8Array(buffer),v=new DataView(buffer);let end=-1;
    if(bytes.length>32*1024*1024)throw new Error('Excel-Datei ist größer als 32 MB.');
    for(let i=bytes.length-22;i>=Math.max(0,bytes.length-65557);i--)if(v.getUint32(i,true)===0x06054b50){end=i;break;}
    if(end<0 || end+22+v.getUint16(end+20,true)!==bytes.length || v.getUint16(end+8,true)!==v.getUint16(end+10,true) || v.getUint16(end+4,true) || v.getUint16(end+6,true))throw new Error('Keine unterstützte XLSX-Datei.');
    const count=v.getUint16(end+10,true),start=v.getUint32(end+16,true),size=v.getUint32(end+12,true);
    if(count>1000 || start+size>end)throw new Error('Excel-Archiv ist ungültig oder zu groß.');
    const entries=new Map();let pos=start;
    for(let i=0;i<count;i++){
      if(pos+46>end || v.getUint32(pos,true)!==0x02014b50)throw new Error('Ungültiges Excel-Archiv.');
      const nameLength=v.getUint16(pos+28,true),extra=v.getUint16(pos+30,true),comment=v.getUint16(pos+32,true),next=pos+46+nameLength+extra+comment;
      if(next>start+size)throw new Error('Ungültiger Excel-Dateieintrag.');
      const name=decoder.decode(bytes.slice(pos+46,pos+46+nameLength));
      if(name.startsWith('/') || name.includes('\\') || name.split('/').includes('..') || entries.has(name))throw new Error('Ungültiger oder doppelter Excel-Dateipfad.');
      entries.set(name,{flags:v.getUint16(pos+8,true),method:v.getUint16(pos+10,true),crc:v.getUint32(pos+16,true),compressed:v.getUint32(pos+20,true),size:v.getUint32(pos+24,true),offset:v.getUint32(pos+42,true)});pos=next;
    }
    return async name=>{
      const entry=entries.get(name);if(!entry)return null;
      if(entry.flags&1 || ![0,8].includes(entry.method) || entry.size>limit)throw new Error('Excel-Inhalt ist verschlüsselt, zu groß oder nicht unterstützt.');
      const p=entry.offset;if(p+30>start || v.getUint32(p,true)!==0x04034b50)throw new Error('Ungültiger Excel-Dateikopf.');
      const begin=p+30+v.getUint16(p+26,true)+v.getUint16(p+28,true);
      if(begin+entry.compressed>start)throw new Error('Ungültige Excel-Datenlänge.');
      let data=bytes.slice(begin,begin+entry.compressed);
      if(entry.method===8){
        if(typeof DecompressionStream==='undefined')throw new Error('Dieser Browser unterstützt den Excel-Import nicht. Antwort als Tabelle einfügen.');
        const reader=new Blob([data]).stream().pipeThrough(new DecompressionStream('deflate-raw')).getReader(),parts=[];let length=0;
        try{while(true){const {done,value}=await reader.read();if(done)break;length+=value.length;if(length>limit || length>entry.size){await reader.cancel();throw new Error('Entpackter Excel-Inhalt ist zu groß.');}parts.push(value);}}finally{reader.releaseLock();}
        data=new Uint8Array(length);let at=0;for(const part of parts){data.set(part,at);at+=part.length;}
      }
      if(data.length!==entry.size || crc32(data)!==entry.crc)throw new Error('Excel-Inhalt ist beschädigt.');
      return decoder.decode(data);
    };
  }
  function parseXML(text){if(!text || /<!DOCTYPE/i.test(text))throw new Error('Excel-XML fehlt oder wird nicht unterstützt.');const doc=new DOMParser().parseFromString(text,'application/xml');if(doc.getElementsByTagName('parsererror').length)throw new Error('Excel-XML ist ungültig.');return doc;}
  const nodes=(root,name)=>Array.from(root.getElementsByTagNameNS('*',name));
  const content=(root,name)=>nodes(root,name).map(n=>n.textContent).join('');
  function parseTable(text){
    if(text.trimStart().startsWith('|')){
      return text.trim().split(/\r?\n/).map(line=>line.trim().replace(/^\|/,'').replace(/\|$/,'')
        .split(/(?<!\\)\|/).map(cell=>cell.trim().replace(/\\\|/g,'|').replace(/<br\s*\/?>/gi,'\n')))
        .filter(row=>!row.every(cell=>/^:?-+:?$/.test(cell.replace(/\s/g,''))));
    }
    const first=text.slice(0,text.indexOf('\n')<0?text.length:text.indexOf('\n'));
    const separator=first.includes('\t')?'\t':first.includes(';')?';':',';
    const rows=[];let row=[],cell='',quoted=false,closed=false;
    for(let i=0;i<text.length;i++){
      const char=text[i];
      if(char==='"'){
        if(quoted && text[i+1]==='"'){cell+='"';i++;}
        else if(quoted){quoted=false;closed=true;}
        else if(!cell && !closed)quoted=true;
        else throw new Error('Ungültige Anführungszeichen in Antworttabelle.');
      }else if(!quoted && (char===separator || char==='\n' || char==='\r')){
        row.push(cell);cell='';closed=false;
        if(char!==separator){rows.push(row);row=[];if(char==='\r' && text[i+1]==='\n')i++;}
      }else {if(closed && char!==' ')throw new Error('Ungültige Antworttabelle.');if(!closed)cell+=char;}
    }
    if(quoted)throw new Error('Antworttabelle endet innerhalb eines Textfelds.');
    if(cell || row.length){row.push(cell);rows.push(row);}return rows;
  }
  function fromRows(rows){
    rows=rows.filter(row=>row.some(value=>String(value||'').trim()));
    if(rows.length<2)throw new Error('Antworttabelle ist leer.');
    const header=rows.shift().map(value=>String(value||'').replace(/^\ufeff/,'').trim().toLowerCase());
    const indices=headers.map(key=>header.indexOf(key.toLowerCase()));
    if(indices.slice(0,8).some(index=>index<0) || new Set(header).size!==header.length)throw new Error('Antworttabelle benötigt die unveränderten Spalten aus dem Blatt Antwort.');
    const list=value=>{const text=String(value||'').trim();if(!text)return [];if(text.startsWith('[')){const parsed=JSON.parse(text);if(!Array.isArray(parsed))throw new Error('Hinweise müssen eine Liste sein.');return parsed;}return text.split(/\r?\n/).map(s=>s.trim()).filter(Boolean);};
    let requestId=null;
    const matches=rows.map(row=>{
      const values=indices.map((index,i)=>{const value=String(row[index]??'').trim();return i<5?value.replace(/^`([^`]+)`$/,'$1'):value;});
      if(!requestId)requestId=values[0];if(!values[0] || values[0]!==requestId)throw new Error('Datenkennung fehlt oder unterscheidet sich zwischen den Antwortzeilen.');
      const ids=values[3]?values[3].split(/[|;,\s]+/).filter(Boolean):[];
      const result={targetId:values[1],status:({passend:'matched',teilweise:'ambiguous','kein treffer':'no_match'}[values[2].toLowerCase()]||values[2]),referenceIds:ids,
        confidence:({hoch:'high',mittel:'medium',niedrig:'low'}[values[4].toLowerCase()]||values[4]),reason:values[5],differences:list(values[6]),missingInformation:list(values[7]),priceInformation:list(values[10])};
      if(values[8] || values[9])result.evidence=[{referenceId:ids[0],targetQuote:values[8],referenceQuote:values[9]}];
      return result;
    });
    return {schema:'kalkpilot.llm-matches',schemaVersion:1,requestId,matches};
  }
  async function importWorkbook(buffer){
    const read=await unzip(buffer),book=parseXML(await read('xl/workbook.xml'));
    const answer=nodes(book,'sheet').find(node=>node.getAttribute('name')==='Antwort');if(!answer)throw new Error('Excel-Datei benötigt das Blatt Antwort.');
    const id=answer.getAttributeNS('http://schemas.openxmlformats.org/officeDocument/2006/relationships','id');
    const rels=parseXML(await read('xl/_rels/workbook.xml.rels')),rel=nodes(rels,'Relationship').find(node=>node.getAttribute('Id')===id);
    if(!rel || rel.getAttribute('TargetMode')==='External')throw new Error('Ungültige Verknüpfung zum Antwortblatt.');
    const target=rel.getAttribute('Target'),path=target.startsWith('/xl/')?target.slice(1):'xl/'+target;
    const sharedText=await read('xl/sharedStrings.xml'),shared=sharedText?nodes(parseXML(sharedText),'si').map(node=>content(node,'t')):[];
    const answerXML=parseXML(await read(path));const rows=nodes(answerXML,'row');if(rows.length>20000)throw new Error('Zu viele Antwortzeilen.');
    return fromRows(rows.map(row=>{
      const values=[];
      for(const cell of nodes(row,'c')){
        if(nodes(cell,'f').length)throw new Error('Formeln im Antwortblatt werden nicht importiert.');
        const address=cell.getAttribute('r')||'',match=/^([A-Z]+)\d+$/.exec(address);if(!match)throw new Error('Ungültige Zelladresse.');
        const index=[...match[1]].reduce((value,char)=>value*26+char.charCodeAt(0)-64,0)-1;if(index>511)throw new Error('Zu viele Antwortspalten.');
        const type=cell.getAttribute('t'),raw=content(cell,'v');let value;
        if(type==='s'){if(!/^\d+$/.test(raw) || Number(raw)>=shared.length)throw new Error('Ungültiger Excel-Textverweis.');value=shared[Number(raw)];}
        else value=type==='inlineStr'?content(cell,'t'):raw;
        if(values[index]!=null)throw new Error('Doppelte Antwortzelle.');values[index]=value;
      }
      return values;
    }));
  }
  function importText(text){if(text.length>10*1024*1024)throw new Error('Antworttext ist größer als 10 MB.');text=text.replace(/^\ufeff/,'').trim();if(text.startsWith('```'))text=text.replace(/^```(?:json|csv|tsv)?\s*/i,'').replace(/\s*```$/,'');return text.startsWith('{')?JSON.parse(text):fromRows(parseTable(text));}
  window.KPCopilotExchange={exportRequest,importWorkbook,importText,workbook,headers};
})();
