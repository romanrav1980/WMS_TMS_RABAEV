from pathlib import Path
f=Path("db/migrations/2026-10-12_ni062_return_aggregation")
p=f/"002_return_unit_core.sql";v=p.read_text(encoding="utf-8")
a="  if aggregation_count>0 then\n   input_wire"
b="""  if aggregation_count>0 then
   input_wire:=normalized.get_array('aggregation_scans').to_clob;
   select count(*)into bad_direct from json_table(input_wire,'$[*]'columns(L varchar2(10)path '$.level'))where L='PALLET';
   if bad_direct!=0 then raise_application_error(-20886,'RETURN_PALLET_AGGREGATION_REQUIRES_PRESERVED_CONTAINER_IDENTITY');end if;
   input_wire"""
assert a in v;v=v.replace(a,b);p.write_text(v,encoding="utf-8")
(f/"apply_pallet_scope_guard.sql").write_text("@@002_return_unit_core.sql\n",encoding="utf-8")
p=Path("scripts/case624_aggregate_reuse.py");v=p.read_text(encoding="utf-8")
v=v.replace('aggregation_scans=[dict(system_code="CRPT",profile_code="TOBACCO",level="PALLET",code=origin["lot"]),\n                    dict(system_code="EGAIS",profile_code="ALCOHOL",level="BOX",code="EGAIS.B:"+tag)]',
'''aggregation_scans=[dict(system_code="EGAIS",profile_code="ALCOHOL",level="BOX",code="EGAIS.B:"+tag)]
 scans=[code for unit in origin["units"]for code in unit["codes"]if code["system_code"]=="CRPT"]''')
v=v.replace("when 'CRPT'then 'PALLET'else 'BOX'","when 'CRPT'then 'UNIT'else 'BOX'")
v=v.replace('"aggregation_scans":aggregation_scans','"scans":scans,"aggregation_scans":aggregation_scans')
a=' if "handover"not in saved:saved["handover"]=call(admin,"POST","/api/delivery/store-return-custody/handover",hand);save()'
b=''' if "handover"not in saved:
  all_units=[code for unit in origin["units"]for code in unit["codes"]]
  call(admin,"POST","/api/delivery/store-return-custody/handover",{**hand,"operation_id":hand["operation_id"]+".BAD.UNIT","aggregation_scans":[],"scans":all_units},409)
  saved["handover"]=call(admin,"POST","/api/delivery/store-return-custody/handover",hand);save()'''
assert a in v;v=v.replace(a,b)
v=v.replace("aggregate-only registered CRPT PALLET/EGAIS BOX;","mixed configured CRPT UNIT/EGAIS BOX-only;")
p.write_text(v,encoding="utf-8")
print("626 new-pallet return cannot reuse original PALLET code; BOX-only profile remains registered resolver path, no unit fallback. Existing fresh622 used for mixed exact-profile case.")
