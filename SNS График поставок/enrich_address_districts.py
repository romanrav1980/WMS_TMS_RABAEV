from pathlib import Path
import re,json,csv,collections
root=Path(__file__).parent

def find_district(address,city):
    text=' '.join((address or '').split())
    if not text:return '', 'адрес отсутствует'
    patterns=[r'([А-Яа-яЁё-]+(?:ский|ской|цкий|ской|ский))\s+(?:муниципальный\s+)?(?:м\.\s*)?р\s*[-.]?\s*(?:н|он)\b',r'([А-Яа-яЁё-]+(?:ский|цкий))\s+(?:муниципальный\s+)?район\b',r'муниципальный\s+район\s+([А-Яа-яЁё-]+(?:ский|цкий))\b',r'муниципальный\s+округ\s+([А-Яа-яЁё-]+(?:ский|цкий))\s+район']
    for pattern in patterns:
        m=re.search(pattern,text,re.I)
        if m:return m.group(1).capitalize()+' район','район указан в адресе'
    if city=='Санкт-Петербург':
        if re.search(r'шушар',text,re.I):return 'Пушкинский район','населённый пункт Шушары'
        if re.search(r'парголов',text,re.I):return 'Выборгский район','населённый пункт Парголово'
        if re.search(r'ям[- ]ижор|тельмана|\bтосно\b',text,re.I) and re.search(r'ленинградск',text,re.I):return 'Тосненский район','населённый пункт Ленинградской области'
    return '', 'район не указан в адресе'

def enrich():
    directory_path=root/'data'/'rc_districts.json';directory=json.loads(directory_path.read_text(encoding='utf8'));reviewed=json.loads((root/'data'/'district_reviewed_rules.json').read_text(encoding='utf8'));office_file=root/'data'/'office_district_candidates.json';offices=json.loads(office_file.read_text(encoding='utf8')) if office_file.exists() else []
    records=json.loads((root/'data'/'october.json').read_text(encoding='utf8'))['records']
    norm=lambda v:re.sub(r'\s+',' ',str(v or '').strip()).lower().replace('ё','е')
    index={(x['chain'],x['receiver'],x['address']):x for x in directory}
    for r in records:
        if r.get('chain') not in ('drinks','tobacco') or not r.get('receiver') or not (r.get('recipient_id') or r.get('address')):continue
        key=(r['chain'],norm(r.get('receiver')),norm(r.get('address')))
        if key not in index:
            entry={'chain':key[0],'receiver':key[1],'address':key[2],'city':r.get('destination') or 'Город не указан','source_city':r.get('destination') or '', 'district':'','method':'','moscow_region':False,'order':9000}
            index[key]=entry
        entry=index[key];matches=[x for x in reviewed if x['city']==entry['city'] and re.search(x['pattern'],norm(r.get('address')),re.I)];
        if len(matches)==1 and not entry.get('district'):
            entry['district']=matches[0]['district'];entry['method']='географический источник';entry['source_url']=matches[0]['source']
        found,method=find_district(r.get('address'),entry['city'])
        if found and not entry.get('district'):entry['district']=found;entry['method']=method
    # Адреса официальных офисов СНС используются как адреса складов по указанию владельца.
    def normal(v):return str(v or '').lower().replace('ё','е')
    for e in index.values():
        if e.get('district') or e.get('address'):continue
        city=normal(e['city']);receiver=normal(e['receiver'])
        if receiver not in (city+'_ф','снс - '+city,'снс-'+city):continue
        candidates={(normal(o.get('office_address')),normal(o.get('district'))):o for o in offices if normal(o.get('city'))==city and o.get('district') and o.get('geocoded')}
        if len(candidates)!=1:continue
        o=next(iter(candidates.values()));a=o['geocoded'];road=normal(a.get('road'));office=normal(o.get('office_address'))
        words=[w for w in re.findall(r'[а-яa-z0-9-]+',road) if len(w)>=4 and w not in ('улица','проспект','шоссе','проезд','трасса','дорога','улицы')]
        house=re.search(r'\d+',a.get('house_number',''))
        if not words or not any(w in office for w in words) or not house or not re.search(r'(?<!\d)'+house.group()+r'(?!\d)',office):continue
        district=a.get('city_district') or (a.get('suburb') if re.search(r'район|округ',a.get('suburb',''),re.I) else '') or a.get('county','')
        if not district:continue
        e['district']=district;e['method']='адрес филиала СНС и OpenStreetMap';e['source_url']=o['source'];e['office_address']=o['office_address'];e['geo_source_url']=o['geo_source']
    directory=list(index.values());directory_path.write_text(json.dumps(directory,ensure_ascii=False,separators=(',',':')),encoding='utf8')
    report=root/'reports'/'address-districts.csv'
    with report.open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.writer(f,delimiter=';');writer.writerow(['Цепь','Город','Район','Получатель','Адрес','Источник района','Ссылка','Адрес филиала СНС','Карта'])
        for x in sorted(directory,key=lambda x:(x['chain'],x['city'],x['district'],x['address'])):writer.writerow([x['chain'],x['city'],x.get('district') or 'Не определён',x['receiver'],x['address'],x.get('method') or ('адрес отсутствует' if not x['address'] else 'не определён'),x.get('source_url',''),x.get('office_address',''),x.get('geo_source_url','')])
    print('directory',len(directory),'identified',sum(bool(x.get('district')) for x in directory),'unidentified',sum(not x.get('district') for x in directory),'missing_address',sum(not x.get('address') for x in directory))
if __name__=='__main__':enrich()
