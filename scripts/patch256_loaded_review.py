from pathlib import Path
import json
out={};p=Path("db/migrations/2026-10-11_ni081_time_source_contract/001_api.sql");s=p.read_text(encoding="utf-8")
s=s.replace("v_zone varchar2(50);v_reason nvarchar2(500);","v_zone varchar2(50);v_reason nvarchar2(500);v_phase varchar2(40);")
old="  if n>0 then raise_application_error(-20886,'TT_TIME_PHYSICAL_EXECUTION_FROZEN');end if;"
assert s.count(old)==1
s=s.replace(old,"""  v_phase:=nvl(b.get_string('approval_phase'),'BEFORE_LOADING');
  if v_phase not in('BEFORE_LOADING','AFTER_LOADING_REVIEW')then raise_application_error(-20886,'TT_TIME_APPROVAL_PHASE_REQUIRED');end if;
  if n>0 then
   if v_phase!='AFTER_LOADING_REVIEW'then raise_application_error(-20886,'TT_TIME_PHYSICAL_EXECUTION_FROZEN');end if;
   select count(*)into n from RRL_SBORKA_PALLETS p where p.TRANSTASK_ID=v_trip
    and(nvl(p.CONDITION,-1)!=2 or(select count(*)from RRL_TT_HU_LOAD_ST m
      join RRL_TT_HU_LOAD_FACT l on l.LOAD_OPERATION_ID=m.LOAD_OPERATION_ID
      join RRL_STOCK_OPERATION op on op.OPERATION_ID=l.LOAD_OPERATION_ID
      join RRL_TR_VEHICLE vehicle on vehicle.ID=l.VEHICLE_ID and vehicle.NUM=w.TRANSPORT
      where m.SBORKA_PALLET_ID=p.ID and m.ACTIVE_FLAG=1 and l.TT_ID=v_trip
       and l.STATUS='LOADED'and l.VEHICLE_NUMBER=w.TRANSPORT and l.DOCK=w.DOCK
       and l.CUSTODY_RELEASED_AT is null and op.STATE='APPLIED')!=1);
   if n>0 then raise_application_error(-20886,'TT_TIME_ALL_CURRENT_MEMBERS_LOADED_PROOF_REQUIRED');end if;
   select count(*)into n from RRL_SBORKA_PALLETS where TRANSTASK_ID=v_trip;
   if n<1 then raise_application_error(-20886,'TT_TIME_CURRENT_MEMBERS_REQUIRED');end if;
  elsif v_phase='AFTER_LOADING_REVIEW'then raise_application_error(-20886,'TT_TIME_REVIEW_REQUIRES_ACTUAL_LOAD');end if;""")
needle="  result.put('source_contract_version',2);"
assert s.count(needle)==1;s=s.replace(needle,"  result.put('approval_phase',v_phase);\n"+needle)
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
