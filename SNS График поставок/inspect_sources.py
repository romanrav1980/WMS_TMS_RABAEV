import json, zipfile, xml.etree.ElementTree as ET, re, os, sys
from pathlib import Path

ROOT = Path(__file__).parent
MAIN = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
REL = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'

def analyze(path):
    result = {'file': path.name, 'bytes': path.stat().st_size, 'sheets': []}
    with zipfile.ZipFile(path) as z:
        book = ET.fromstring(z.read('xl/workbook.xml'))
        rels = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
        targets = {r.get('Id'): r.get('Target') for r in rels}
        strings = []
        if 'xl/sharedStrings.xml' in z.namelist():
            with z.open('xl/sharedStrings.xml') as f:
                for _, el in ET.iterparse(f, events=('end',)):
                    if el.tag == MAIN+'si':
                        strings.append(''.join(t.text or '' for t in el.iter(MAIN+'t')))
                        el.clear()
        result['shared_strings'] = len(strings)
        for s in book.find(MAIN+'sheets'):
            target = targets.get(s.get(REL+'id'), '')
            target = target.lstrip('/') if target.startswith('/') else 'xl/'+target
            target = target.replace('xl/xl/', 'xl/')
            item = {'name': s.get('name'), 'state': s.get('state','visible'), 'rows': 0, 'cells': 0, 'formulas': 0, 'sample': []}
            if target not in z.namelist():
                item['error']='sheet target unavailable: '+target; result['sheets'].append(item); continue
            with z.open(target) as f:
                for _, row in ET.iterparse(f,events=('end',)):
                    if row.tag != MAIN+'row': continue
                    item['rows'] += 1
                    sample = []
                    for c in row.findall(MAIN+'c'):
                        item['cells'] += 1
                        if c.find(MAIN+'f') is not None: item['formulas'] += 1
                        if len(item['sample']) >= 16: continue
                        v = c.find(MAIN+'v'); t = c.get('t'); value = v.text if v is not None else None
                        if t == 's' and value is not None:
                            i=int(value); value=strings[i] if i < len(strings) else '[missing string]'
                        if t == 'inlineStr': value=''.join(x.text or '' for x in c.iter(MAIN+'t'))
                        if value is not None and len(sample)<50: sample.append([c.get('r'),str(value)[:180]])
                    if sample and len(item['sample'])<16: item['sample'].append(sample)
                    row.clear()
            result['sheets'].append(item)
    return result

files = [ROOT / arg for arg in sys.argv[1:]] if len(sys.argv) > 1 else sorted({p for p in ROOT.iterdir() if p.suffix.lower() == '.xlsx'})
for p in files:
    try:
        data=analyze(p)
        print(json.dumps(data,ensure_ascii=False),flush=True)
    except Exception as exc:
        print(json.dumps({'file':p.name,'error':str(exc)},ensure_ascii=False),flush=True)
