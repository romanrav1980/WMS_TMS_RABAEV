from pathlib import Path
import json,urllib.request,urllib.parse,time,re,sys
sys.stdout.reconfigure(encoding='utf8')
root=Path(__file__).parent;entries=json.loads((root/'data/rc_districts.json').read_text(encoding='utf8'))
queries=sorted({(e['city'],e['address']) for e in entries if not e.get('district') and e['address']})
out=root/'reports/address-geocode-review.json';found=[]
for i,(city,address) in enumerate(queries,1):
 parts=[x.strip() for x in address.split(',') if x.strip()];parts=[re.sub(r'^\s*\d{6}\s*','',x) for x in parts];parts=[x for x in parts if x];
 query=', '.join(parts[:6]);query=re.sub(r'\b(респ|обл)\b',lambda m: {'респ':'республика','обл':'область'}[m.group(1)],query);query=re.sub(r'\b(ул|г|д)\s*,',r'\1,',query)
 params=urllib.parse.urlencode({'q':query,'format':'jsonv2','addressdetails':1,'limit':3,'accept-language':'ru'});req=urllib.request.Request('https://nominatim.openstreetmap.org/search?'+params,headers={'User-Agent':'SNS-address-review/1.0 (local address directory quality review)'})
 try:
  with urllib.request.urlopen(req,timeout=12) as response: result=json.load(response)
  found.append({'city':city,'address':address,'query':query,'results':[{'display_name':x.get('display_name'),'address':x.get('address'),'lat':x.get('lat'),'lon':x.get('lon'),'type':x.get('type')} for x in result]})
 except Exception as e:found.append({'city':city,'address':address,'query':query,'error':str(e)})
 out.write_text(json.dumps(found,ensure_ascii=False,indent=2),encoding='utf8')
 if i%10==0:print(f'{i}/{len(queries)}; найдено {sum(bool(x.get("results")) for x in found)}',flush=True)
 time.sleep(1.1)
