from pathlib import Path
import json,re,time,urllib.request,urllib.parse,sys
sys.stdout.reconfigure(encoding='utf8');path=Path(__file__).parent/'reports/address-geocode-review.json';rows=json.loads(path.read_text(encoding='utf8'));queries=[]
for row in rows:
 if row.get('results'):continue
 city=row['city'];addr=row['address'];parts=[x.strip() for x in addr.split(',') if x.strip()];road=None;number=''
 for i,part in enumerate(parts):
  if re.search(r'\b(ул\.?|улица|шоссе|ш\.?|тракт|проезд|пр-д)\b',part):
   road=re.sub(r'^\s*\d{6}\s*','',part);number=parts[i+1] if i+1<len(parts) and re.match(r'^(?:д[. ]|зд[. ]|стр[. ]|\d)',parts[i+1]) else '';break
 m=re.search(r'(?:^|,)\s*([а-яё-]+)\s+г\s*[.,]',addr,re.I)
 if m:city=m.group(1)
 if not city or not road:continue
 query=', '.join([city,road,number]).strip(', ');queries.append((row,query))
print('повторных запросов',len(queries),flush=True)
for i,(row,query) in enumerate(queries,1):
 params=urllib.parse.urlencode({'q':query,'format':'jsonv2','addressdetails':1,'limit':3,'accept-language':'ru'});req=urllib.request.Request('https://nominatim.openstreetmap.org/search?'+params,headers={'User-Agent':'SNS-address-review/1.0 (local address directory quality review)'})
 try:
  with urllib.request.urlopen(req,timeout=12) as r: result=json.load(r)
  row['query2']=query;row['results2']=[{'display_name':x.get('display_name'),'address':x.get('address'),'lat':x.get('lat'),'lon':x.get('lon'),'type':x.get('type')} for x in result]
 except Exception as e:row['error2']=str(e)
 path.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
 if i%10==0:print(f'{i}/{len(queries)} найдено {sum(bool(r.get("results2")) for r in rows)}',flush=True)
 time.sleep(1.1)
