"""Check standalone print questionnaire and rasterize every Word-rendered page."""
from pathlib import Path
import json,re,zipfile
import fitz
from docx import Document
from docx.opc.constants import RELATIONSHIP_TYPE as RT
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'wiki/requirements/tobacco_regional_hubs/supplier_questionnaire_v2'
QA=ROOT/'tmp/tobacco-questionnaire-v2-qa'

def main():
    data=json.loads((ROOT/'tools/tobacco_questionnaire_v2_data.json').read_text(encoding='utf-8'))
    md=(SRC/'questionnaire.md').read_text(encoding='utf-8')
    assert not re.search(r'\[[^\]]+\]\([^)]+\)|https?://|TH-\d|<!--',md)
    rows=[x for x in md.splitlines() if re.match(r'^\| \d{3}\*? \|',x)]
    assert len(rows)==100
    for q,line in zip(data['rows'],rows):
        cols=[c.strip() for c in line.strip('|').split('|')]
        assert cols[0]==q['id']+('*' if q['critical'] else '') and cols[2]==q['question']
        assert float(cols[3].strip('%').replace(',','.'))==q['weight']
    assert sum(q['weight'] for q in data['rows'])==100
    path=SRC/'questionnaire.docx'
    with zipfile.ZipFile(path) as z:assert z.testzip() is None
    d=Document(path)
    assert not any(r.reltype==RT.HYPERLINK for r in d.part.rels.values())
    for t in d.tables:
        assert t.rows[0]._tr.xpath('./w:trPr/w:tblHeader')
        assert t._tbl.tblPr.xpath('./w:tblBorders')
    pdf=QA/'questionnaire.pdf'
    assert pdf.stat().st_mtime>=path.stat().st_mtime
    out=QA/'pages';out.mkdir(exist_ok=True)
    rendered=fitz.open(pdf);items=[];text=''
    for i,page in enumerate(rendered,1):
        words=page.get_text('words');text+=page.get_text()
        outside=[w[:5] for w in words if w[0]<15 or w[1]<10 or w[2]>page.rect.width-15 or w[3]>page.rect.height-10]
        assert words and not outside,(i,outside)
        img=out/f'page-{i:03}.png';page.get_pixmap(dpi=105,alpha=False).save(img)
        items.append({'page':i,'image':str(img),'words':len(words)})
    for q in data['rows']:assert re.search(r'(?m)^'+q['id']+r'\*?(?=\s|$)',text),q['id']
    report={'questions':100,'areas':15,'weight':100,'external_links':0,'pages':len(rendered),'images':items}
    (QA/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='images'},ensure_ascii=False))

if __name__=='__main__':main()
