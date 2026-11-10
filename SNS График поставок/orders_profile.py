import zipfile, xml.etree.ElementTree as ET, json, collections, datetime
from pathlib import Path

root=Path(__file__).parent
M='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
path=root/'EXPORT1.XLSX'
with zipfile.ZipFile(path) as z:
    strings=[]
    with z.open('xl/sharedStrings.xml') as f:
        for _,e in ET.iterparse(f,events=('end',)):
            if e.tag==M+'si': strings.append(''.join(t.text or '' for t in e.iter(M+'t')));e.clear()
    book=ET.fromstring(z.read('xl/workbook.xml')); rels=ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    targets={r.get('Id'):r.get('Target') for r in rels}
    rid='{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'
    sheet=next(s for s in book.find(M+'sheets') if s.get('name')=='Sheet1')
    target=targets[sheet.get(rid)].lstrip('/'); target=target if target.startswith('xl/') else 'xl/'+target
    rows=[]
    with z.open(target) as f:
        for _,e in ET.iterparse(f,events=('end',)):
            if e.tag!=M+'row':continue
            row={}
            for c in e.findall(M+'c'):
                col=''.join(x for x in c.get('r','') if x.isalpha());v=c.find(M+'v'); val=v.text if v is not None else ''
                if c.get('t')=='s' and val:val=strings[int(val)]
                row[col]=val
            if row: rows.append(row)
            e.clear()
header=rows[0]; data=rows[1:]
def counts(col):return collections.Counter(r.get(col,'') for r in data)
def dates(col):
    vals=[]
    for r in data:
        try: vals.append((datetime.datetime(1899,12,30)+datetime.timedelta(days=float(r.get(col,'')))).strftime('%Y-%m-%d'))
        except (ValueError,OverflowError):pass
    return {'min':min(vals,default=None),'max':max(vals,default=None),'valid':len(vals),'months':dict(collections.Counter(x[:7] for x in vals).most_common(15))}
def show(col,n=12):return counts(col).most_common(n)
out={'header':header,'rows':len(data),'date_order':dates('A'),'date_requested':dates('C'),'date_goods_fact':dates('AF'),
     'unique_edi':len({r.get('O') for r in data if r.get('O')}),'unique_ynor':len({r.get('S') for r in data if r.get('S')}),
     'unique_blc':len({r.get('AO') for r in data if r.get('AO')}),'unique_transport':len({r.get('AN') for r in data if r.get('AN')}),
     'edi_blank':counts('O').get('',0),'ynor_blank':counts('S').get('',0),'top_customers':show('G'),'categories':show('AH'),
     'hub':show('AL'),'hub_flag':show('AK'),'cancelled':show('AQ'),'status':show('U'),'box_sum_raw':sum(float(r.get('R') or 0) for r in data),
     'duplicate_edi_rows':sum(n for k,n in counts('O').items() if k and n>1),'duplicate_ynor_rows':sum(n for k,n in counts('S').items() if k and n>1)}
(root/'orders_profile.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(out,ensure_ascii=False))
