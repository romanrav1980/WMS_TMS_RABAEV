from pathlib import Path
import json,urllib.request,urllib.parse,time,sys
sys.stdout.reconfigure(encoding='utf8');root=Path(__file__).parent;entries=json.loads((root/'reports/sns-office-candidates.json').read_text(encoding='utf8'));offices={e['city']:e['office'] for e in entries};out=[]
for i,(city,office) in enumerate(offices.items(),1):
 try:
  lat,lon=office['geo'].split(',');params=urllib.parse.urlencode({'lat':lat,'lon':lon,'format':'jsonv2','addressdetails':1,'accept-language':'ru'});req=urllib.request.Request('https://nominatim.openstreetmap.org/reverse?'+params,headers={'User-Agent':'SNS-address-review/1.0 (local address directory quality review)'})
  with urllib.request.urlopen(req,timeout=12) as response:data=json.load(response)
  address=data.get('address',{});district=address.get('city_district') or address.get('county') or ''
  out.append({'city':city,'office_address':office['address'],'district':district,'geocoded':address,'source':'https://sns.ru/contacts/','geo_source':'https://www.openstreetmap.org/?mlat='+lat+'&mlon='+lon})
 except Exception as e:out.append({'city':city,'error':str(e)})
 (root/'data/office_district_candidates.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
 if i%10==0:print(f'{i}/{len(offices)}; найден район {sum(bool(x.get("district")) for x in out)}',flush=True)
 time.sleep(1.1)
