from pathlib import Path
import json
out={}
out["scripts/source641_preserved_pallet.py"]=Path("scripts/source622_return_aggregate.py").read_text(encoding="utf-8").replace("622","641")
out["scripts/deliver642_preserved_pallet.py"]=Path("scripts/deliver623_return_aggregate_source.py").read_text(encoding="utf-8").replace("623","642").replace("622","641")
v=Path("scripts/case624_aggregate_reuse.py").read_text(encoding="utf-8").replace("624","643").replace("623","642").replace("622","641")
v=v.replace('aggregation_scans=[dict(system_code="EGAIS",profile_code="ALCOHOL",level="BOX",code="EGAIS.B:"+tag)]','aggregation_scans=[dict(system_code="CRPT",profile_code="TOBACCO",level="PALLET",code=origin["lot"]),dict(system_code="EGAIS",profile_code="ALCOHOL",level="BOX",code="EGAIS.B:"+tag)]')
v=v.replace('scans=[code for unit in origin["units"]for code in unit["codes"]if code["system_code"]=="CRPT"]','scans=[]')
v=v.replace("when 'CRPT'then 'UNIT'else 'BOX'","when 'CRPT'then 'PALLET'else 'BOX'")
v=v.replace('uid="REUSE643:"+tag;hand=', 'uid=origin["lot"];hand=')
a='  saved["handover"]=call(admin,"POST","/api/delivery/store-return-custody/handover",hand);save()'
b='  call(admin,"POST","/api/delivery/store-return-custody/handover",{**hand,"operation_id":hand["operation_id"]+".BAD.IDENTITY","pallet_identifier":"REPACK643:"+tag},409)\n'+a
assert a in v;v=v.replace(a,b)
v=v.replace("mixed configured CRPT UNIT/EGAIS BOX-only;","preserved original PALLET identity / CRPT PALLET-only + EGAIS BOX-only;")
out["scripts/case643_preserved_pallet_return.py"]=v
print(json.dumps(out,ensure_ascii=True))
