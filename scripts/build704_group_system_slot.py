from pathlib import Path
import json,hashlib
d="db/migrations/2026-10-12_ni061_group_system_target"
before=Path("tmp/703_slot_before.sql").read_text(encoding="utf-8")
body=before[before.index("create or replace package body"):]
old="  if nvl(c.IS_SYSTEM,0)!=0 then"
assert body.count(old)==1
new="""  if nvl(c.IS_SYSTEM,0)!=0 and m.get_string('group_receipt_operation_id') is not null then
   declare v_receipt varchar2(100):=m.get_string('group_receipt_operation_id');v_root varchar2(200):=j.get_string('root_uid');v_from varchar2(60):=j.get_string('cell');v_ware number:=j.get_number('warehouse');v_match number;
   begin
    select count(*)into v_match from RRL_IW_GROUP_RECEIPT r join RRL_IW_GROUP_PLAN p on p.OPERATION_ID=r.PLAN_OPERATION_ID
     where r.OPERATION_ID=v_receipt and r.ROOT_UID=v_root and r.WARE_ID=v_ware and r.RECEIVE_CELL=v_from and p.OUTBOUND_DOCK=v_cell
     and not exists(select 1 from RRL_IW_GROUP_PLACEMENT done where done.RECEIPT_OPERATION_ID=r.OPERATION_ID);
    if v_match!=1 then raise_application_error(-20886,'HU_GROUP_EXACT_RECEIVED_OUTBOUND_REQUIRED');end if;
    z.put('target_role','INTERWARE_GROUP_OUTBOUND');
   end;
  elsif nvl(c.IS_SYSTEM,0)!=0 then"""
body=body.replace(old,new)
ledger="""merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-704-group-system-target'MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Existing received whole HU group may use its immutable outbound dock; normal system-cell restrictions retained',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
"""
out={d+"/000_before.sql":before,d+"/001_slot.sql":body,d+"/apply.sql":"@@001_slot.sql\n@@002_ledger.sql\n",d+"/002_ledger.sql":ledger,d+"/rollback.sql":"@@000_before.sql\n",d+"/verify.sql":"select OBJECT_NAME,OBJECT_TYPE,STATUS from USER_OBJECTS where OBJECT_NAME='RRL_STOCK_HU_SLOT';\nselect LINE,POSITION,TEXT from USER_ERRORS where NAME='RRL_STOCK_HU_SLOT';\n",d+"/checkpoint.json":json.dumps({"schema":"RABAEV","service":"orcl","before_sha256":hashlib.sha256(before.encode()).hexdigest(),"recovery":"restore captured package; no data rebuild","authorization":"owner full RETAILCASE implementation in isolated dev"},indent=2)}
print(json.dumps(out,ensure_ascii=True))
