from pathlib import Path
import json
files={}
for source,target in [('place392_cycle.py','place398_cycle.py'),('prepare392_cycle.py','prepare398_cycle.py'),('load393_cycle.py','load399_cycle.py'),('deliver393_cycle.py','deliver399_cycle.py')]:
 t=Path('scripts/'+source).read_text(encoding='utf-8').replace('context390','context396').replace('context392','context398').replace('IW392','IW398').replace('IH392','IH398').replace('DEV392','DEV398').replace('IW393','IW399').replace('STORE393','STORE399')
 if target=='prepare398_cycle.py':
  t=t.replace('len(ids)==(1 if index==0 else 2)','len(ids)==1')
 if target=='load399_cycle.py':
  t=t.replace('q.fetchone()==(1,2)','q.fetchone()==(1,1)').replace('gross_weight_kg="6"','gross_weight_kg="3"')
 if target=='deliver399_cycle.py':
  t=t.replace('physical_unit_count"]==3','physical_unit_count"]==2').replace('q.fetchone()==(3,1)','q.fetchone()==(2,1)').replace('quantity["accepted"]=="3"','quantity["accepted"]=="2"').replace('quantity["historical_transport_shortage"]=="2"','quantity["historical_transport_shortage"]=="1"').replace('quantity["recovered_transport_quantity"]=="2"','quantity["recovered_transport_quantity"]=="1"').replace('lot=source["lot"]','lot=source["old_birth_uid"]')
 files['scripts/'+target]=t
print(json.dumps(files,ensure_ascii=False))
