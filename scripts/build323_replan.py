from pathlib import Path
import json
d=Path("db/migrations/2026-10-12_ni061_nested_replan");out={}
old=Path("db/migrations/2026-10-12_ni061_nested_placement/002_put.sql").read_text(encoding="utf-8")
new=old.replace("nvl(t.SOURCE_DOC_TYPE,'~')!='INTERWARE'","nvl(t.SOURCE_DOC_TYPE,'~')not in('INTERWARE','WAREHOUSE_HU')",1)
begin=new.index("   if p_domain.has('physical_place_uid')then raise_application_error")
end=new.index("   p_domain.put('superseded_task_id'",begin)
new=new[:begin]+"""   if p_domain.has('physical_place_uid')then
    if t.SOURCE_DOC_TYPE!='WAREHOUSE_HU'or t.UID_PALLET!=p_domain.get_string('physical_place_uid')or t.HU_CONTENT_VERSION!=p_domain.get_number('hu_version')or t.FROM_CELL!=p_domain.get_string('from_cell')or t.QTY!=1 or t.UNIT_CODE!='HU'or t.QTY_MODE!='PALLET'then raise_application_error(-20886,'INTERWARE_HU_REPLAN_ORIGINAL_TASK_IDENTITY_REQUIRED');end if;
   else
    if t.SOURCE_DOC_TYPE!='INTERWARE'or t.UID_PALLET!=p_domain.get_string('uid')or t.FROM_CELL!=p_domain.get_string('from_cell')or t.QTY!=RRL_STOCK_MATH.quantity(p_domain.get_string('quantity'))or t.UNIT_CODE!=p_domain.get_string('base_uom')or t.QTY_MODE!='PALLET'then raise_application_error(-20886,'INTERWARE_REPLAN_ORIGINAL_TASK_IDENTITY_REQUIRED');end if;
   end if;
"""+new[end:]
assert new!=old
for n,t in {"000_before.sql":old,"001_put.sql":new,"apply.sql":"@@001_put.sql\n@@002_ledger.sql\n","rollback.sql":"@@000_before.sql\n","verify.sql":"select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME='RRL_STOCK_INTERWARE_PUT';\n","002_ledger.sql":"merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-323-nested-placement-replan' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Existing atomic cancel-replan extends exact unstarted one-HU task with preserved tree and original journals',sysdate,user,'apply.sql','rollback.sql','APPLIED');\ncommit;\n"}.items():out[(d/n).as_posix()]=t
print(json.dumps(out))
