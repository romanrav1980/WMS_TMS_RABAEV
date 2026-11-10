from pathlib import Path
import json,collections,re
p=Path(__file__).with_name('build_analysis.py');d={'__file__':str(p.resolve())};exec(p.read_text(encoding='utf8').split('trips={};details=')[0],d)
b=collections.defaultdict(lambda:{'end':set(),'net':set()}); n=0
for r in d['read_sheet']('SAP октябрь опер BLC.xlsx','ДАННЫЕ'):
 leg=r.get('AH','');trip=r.get('T','');delivery=r.get('F','');recipient=r.get('S','');net=r.get('U','');end=d['date'](r.get('R',''))
 if not re.search(r'[-–—]\s*сеть\s*$',leg,re.I) or not trip or not delivery or not recipient or not net:continue
 x=b[(trip,delivery,recipient)];x['net'].add(net)
 if end:x['end'].add(end)
 n+=1
o=collections.defaultdict(lambda:{'plan':set(),'receipt':set()});orows=0
for r in d['read_sheet']('EXPORT1.XLSX','Sheet1'):
 k=(r.get('AN',''),r.get('Z',''),r.get('L',''));cancel=(r.get('AQ','') or '').strip().lower()
 if k not in b or cancel not in ('','нет','no','0'):continue
 x=o[k];plan=d['date'](r.get('C',''));receipt=d['date'](r.get('AG',''))
 if plan:x['plan'].add(plan)
 if receipt:x['receipt'].add(receipt)
 orows+=1
results=collections.defaultdict(lambda:collections.Counter());examples={}
for key,x in b.items():
 if len(x['net'])!=1:continue
 network=next(iter(x['net']));stat=results[network];stat['blc']+=1
 if key not in o:continue
 stat['linked']+=1;y=o[key]
 for label,left,right in [('p_b',y['plan'],x['end']),('p_r',y['plan'],y['receipt']),('b_r',x['end'],y['receipt'])]:
  if len(left)==len(right)==1:
   stat[label+'_n']+=1
   if next(iter(left))==next(iter(right)):stat[label+'_eq']+=1
  elif len(left)>1 or len(right)>1:stat[label+'_ambiguous']+=1
print(json.dumps({'blc_rows':n,'blc_keys':len(b),'orders_matched_rows':orows,'rows':[{ 'network':k,**v} for k,v in sorted(results.items(),key=lambda x:-x[1]['linked'])]},ensure_ascii=False))
