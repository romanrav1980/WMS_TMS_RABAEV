import zipfile,xml.etree.ElementTree as ET,json,collections,datetime,re
from pathlib import Path

ROOT=Path(__file__).parent
NS='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
REL='{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'

def read_sheet(filename,sheet_name):
    with zipfile.ZipFile(ROOT/filename) as z:
        strings=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            with z.open('xl/sharedStrings.xml') as f:
                for _,e in ET.iterparse(f,events=('end',)):
                    if e.tag==NS+'si':strings.append(''.join(t.text or '' for t in e.iter(NS+'t')));e.clear()
        book=ET.fromstring(z.read('xl/workbook.xml'))
        rels={r.get('Id'):r.get('Target') for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        sheet=next(s for s in book.find(NS+'sheets') if s.get('name')==sheet_name)
        path=rels[sheet.get(REL)].lstrip('/');path=path if path.startswith('xl/') else 'xl/'+path
        with z.open(path) as f:
            for _,e in ET.iterparse(f,events=('end',)):
                if e.tag!=NS+'row':continue
                row={}
                for c in e.findall(NS+'c'):
                    col=''.join(x for x in c.get('r','') if x.isalpha());v=c.find(NS+'v');value=v.text if v is not None else ''
                    if c.get('t')=='s' and value:value=strings[int(value)]
                    row[col]=value
                if row:yield row
                e.clear()

def date(v):
    try:return (datetime.datetime(1899,12,30)+datetime.timedelta(days=float(v))).date().isoformat()
    except (ValueError,OverflowError,TypeError):return ''
def num(v):
    try:return float(str(v).replace(',','.'))
    except (ValueError,TypeError):return None

trips={};details=collections.defaultdict(lambda:{'goods':[],'orders':[]});main_rows=0
for r in read_sheet('SAP октябрь.XLSX','Sheet1'):
    if r.get('AA')=='№ транспортировки':continue
    main_rows+=1;key=r.get('AA','')
    if not key:continue
    details[key]['goods'].append({'delivery':r.get('F',''),'operation':r.get('AH',''),'material':r.get('B',''),'name':r.get('C',''),'quantity':num(r.get('AQ')),'uom':r.get('AR',''),'weight':num(r.get('AE')),'origin_id':r.get('G',''),'origin':r.get('H',''),'destination_id':r.get('I',''),'destination':r.get('J',''),'client':r.get('O',''),'address':r.get('AF',''),'document':r.get('E','')})
    t=trips.setdefault(key,{'costs':set(),'distances':set(),'operations':set(),'origins':set(),'destinations':set(),'routes':set(),'route_names':set(),'rows':0})
    t['rows']+=1
    if r.get('AC') and r.get('T'):t['route_names'].add((r['AC'],r['T']))
    for key2,col in [('costs','S'),('distances','AO')]:
        n=num(r.get(col));
        if n is not None and n>0:t[key2].add(n)
    for key2,col in [('operations','AH'),('origins','G'),('destinations','I'),('routes','AC')]:
        if r.get(col):t[key2].add(r[col])

rows=[];unclassified=collections.Counter()
for r in read_sheet('SAP октябрь опер BLC.xlsx','ДАННЫЕ'):
    if r.get('Z')=='Номер операции BLC':continue
    cat=r.get('AG','');low=cat.lower()
    if 'gfd' in low or 'напит' in low:chain='drinks'
    elif any(x in low for x in ('сигар','табак','itms','стик','ths','thd','vape','зажиг','гло','glo')):chain='tobacco'
    else:unclassified[cat]+=1;chain='unclassified'
    trip=r.get('T','');t=trips.get(trip);cost=None;km=None
    if t and len(t['costs'])==1:cost=next(iter(t['costs']))
    if t and len(t['distances'])==1:km=next(iter(t['distances']))
    rows.append({'chain':chain,'operation':r.get('Z',''),'trip':trip,'origin':r.get('AI',''),'destination':r.get('AJ',''),
                 'sender':r.get('H',''),'receiver':r.get('U',''),'recipient_id':r.get('S','') or r.get('L',''),
                 'address':r.get('X',''),'leg':r.get('AH',''),
                 'start':date(r.get('K','')),'end':date(r.get('R','')),'status':r.get('J',''),
                 'weight':num(r.get('AL')),'volume':num(r.get('AM')),'qty':num(r.get('AK')),'uom':r.get('AE',''),
                 'trip_cost':cost,'distance':km,'capacity':r.get('AC',''), 'sap_routes':sorted(t['routes']) if t else [], 'sap_route_names':{code:sorted(name for route,name in t['route_names'] if route==code) for code in t['routes']} if t else {}})

# Compute allocations across all categories in a trip before filtering the UI.
# A missing operation, duplicate operation, missing boxes or missing distance makes
# the denominator incomplete: do not silently distribute the whole fare.
by_trip=collections.defaultdict(list)
for row in rows:
    if row['trip']:by_trip[row['trip']].append(row)
allocated=0
for trip,group in by_trip.items():
    info=trips.get(trip); ids=[r['operation'] for r in group]
    if not info or len(info['costs'])!=1 or not ids or any(not x for x in ids):continue
    if len(set(ids))!=len(ids) or set(ids)!=info['operations']:continue
    if any(r['uom'].strip().upper() not in ('КОР','КОРОБ','КОРОБКА') or not r['qty'] or r['qty']<=0 or not r['distance'] or r['distance']<=0 for r in group):continue
    denominator=sum(r['qty']*r['distance'] for r in group)
    for r in group:
        r['allocated_cost']=r['trip_cost']*r['qty']*r['distance']/denominator
        r['cost_method']='распределено: короба × расстояние'
        allocated+=1

for r in read_sheet('EXPORT1.XLSX','Sheet1'):
    if r.get('AN')=='№ транспортировки':continue
    trip=r.get('AN','')
    if trip and trip in details:
        details[trip]['orders'].append({'edi':r.get('O',''),'ynor':r.get('S',''),'package':r.get('T',''),'document':r.get('Y',''),'delivery':r.get('Z',''),'operation':r.get('AO',''),'recipient_id':r.get('L',''),'recipient':r.get('M',''),'boxes':num(r.get('R')),'status':r.get('U',''),'cancelled':r.get('AQ','')})

out={'source':'SAP октябрь опер BLC.xlsx / ДАННЫЕ + SAP октябрь.XLSX / Sheet1',
     'limits':'Классификация по тексту категории; неизвестные строки учитываются в распределении расходов. Распределение только для полного уникального состава операций с коробами и расстоянием; цена доли оценочная. Расстояние — значение транспортировки, не обязательно отдельного адреса. Объёмы/веса строк BLC не подтверждены как уникальный груз.',
     'main_rows':main_rows,'trips':len(trips),'cost_multiple':sum(len(t['costs'])>1 for t in trips.values()),
     'trip_multiple_operations':sum(len(t['operations'])>1 for t in trips.values()),
     'unclassified':unclassified.most_common(),'records':rows}
from required_delivery import fill_required_dates, planned_rows
fill_required_dates(rows, details)
(ROOT/'data').mkdir(exist_ok=True)
(ROOT/'data'/'october.json').write_text(json.dumps(out,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
(ROOT/'data'/'trip_details.json').write_text(json.dumps(details,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
(ROOT/'data'/'planned_delivery.json').write_text(json.dumps(planned_rows(details),ensure_ascii=False,separators=(',',':')),encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k!='records'}|{'records':len(rows),'cost_enriched':sum(r['trip_cost'] is not None for r in rows),'allocations':allocated},ensure_ascii=False))
