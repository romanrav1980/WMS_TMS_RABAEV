import json,hashlib
from pathlib import Path
root="db/migrations/2026-10-12_ni061_group_aggregation/"
live=Path("tmp/666_rrl_iw_group_rec.sql").read_text(encoding="utf-8")
before="create or replace "+live+"\n/\n"
s=before.replace(" or m.has('aggregation_scans')","")
anchor="scan_domain.put('legs',legs);"
if anchor not in s:raise RuntimeError("Current native anchor missing")
guard="""scan_domain.put('legs',legs);
  -- An aggregation on one lot must not enable direct unit fallback on another.
  select count(*)into n from
   json_table(m.to_clob,'$.unit_scans[*]'columns(S varchar2(40)path '$.system_code',P varchar2(80)path '$.profile_code',H varchar2(64)path '$.code_hash'))scan,
   json_table(scan_domain.to_clob,'$.legs[*]'columns(U varchar2(200)path '$.uid',A varchar2(160)path '$.article'))selected,
   RRL_WMS_RECEIPT_UNIT u,RRL_WMS_RECEIPT_CODE code,RRL_SKU_RECEIPT_PROFILE card,
   json_table(code.PROFILES_JSON,'$[*]'columns(P varchar2(80)path '$.profile'))decoded
  where u.CURRENT_UID=selected.U and code.UID_PALLET=u.UID_PALLET and code.UNIT_ID=u.UNIT_ID
   and code.SYSTEM_CODE=scan.S and code.CODE_HASH=scan.H and decoded.P=scan.P
   and card.ARTICUL=selected.A and card.SYSTEM_CODE=scan.S and card.PROFILE_CODE=scan.P
   and card.SCAN_MODE in('BOX','PALLET');
  if n>0 then raise_application_error(-20886,'INTERWARE_GROUP_AGGREGATE_ONLY_UNIT_FALLBACK_FORBIDDEN');end if;"""
s=s.replace(anchor,guard)
s=s.replace("elsif m.has('unit_scans')and m.get_array('unit_scans').get_size>0 then","elsif (m.has('unit_scans')and m.get_array('unit_scans').get_size>0)or (m.has('aggregation_scans')and m.get_array('aggregation_scans').get_size>0)then")
p=Path("api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py")
api=p.read_text(encoding="utf-8");old="class GroupReceive(PhysicalAction):\n    scan_cell:"
assert old in api
api=api.replace(old,"class GroupReceive(PhysicalAction):\n    aggregation_scans: list[AggregationScan]=Field(default_factory=list,max_length=1000)\n    scan_cell:")
files={root+"000_before_group_rec.sql":before,root+"001_group_rec.sql":s,str(p):api,
root+"002_ledger.sql":"""merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-667-group-aggregation-receiving'MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Existing whole group receipt accepts registered aggregate proof, per-lot aggregate-only direct scan fence',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
""",
root+"apply.sql":"@001_group_rec.sql\n@002_ledger.sql\n",
root+"rollback.sql":"@000_before_group_rec.sql\nupdate RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-12-667-group-aggregation-receiving';\n/\n",
root+"verify.sql":"select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME='RRL_IW_GROUP_REC';\nselect OBJECT_NAME,OBJECT_TYPE,STATUS from USER_OBJECTS where OBJECT_NAME='RRL_IW_GROUP_REC';\n",
root+"checkpoint.json":json.dumps({"schema":"RABAEV","service":"127.0.0.1:1521/orcl","migration":"2026-10-12-667-group-aggregation-receiving","before_sha256":hashlib.sha256(before.encode()).hexdigest(),"after_sha256":hashlib.sha256(s.encode()).hexdigest(),"recovery":"paired native package source rollback; no table or stock changes"},indent=2)}
print(json.dumps(files))
