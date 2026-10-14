from pathlib import Path
import json
d=Path("db/migrations/2026-10-12_ni062_return_profile_matrix");out={};t=Path("tmp/388_before_return.sql").read_text()
out[(d/"000_before_core.sql").as_posix()]=t
t=t.replace("a RRL_STORE_RETURN_APPROVAL%rowtype;n number;","a RRL_STORE_RETURN_APPROVAL%rowtype;profile_count number;matched number;parts json_array_t;part json_object_t;n number;",1)
t=t.replace("case when SCAN_MODE='UNIT'then","case when SCAN_MODE in('UNIT','UNIT_OR_AGGREGATION')then",1)
t=t.replace("   into eligible,bad,profiles from RRL_SKU_RECEIPT_PROFILE where ARTICUL=a.ARTICLE;","   into eligible,bad,profiles from RRL_SKU_RECEIPT_PROFILE where ARTICUL=a.ARTICLE;profile_count:=eligible;",1)
needle="  proof:=json_object_t();proof.put('units',json_array_t.parse(units));"
new="""  select count(distinct u.PHYSICAL_UNIT_KEY||':'||code.SYSTEM_CODE||':'||decoded.CODE_PROFILE)into matched
  from RRL_STORE_RETURN_UNIT b join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=b.PHYSICAL_UNIT_KEY
  join RRL_WMS_RECEIPT_CODE code on code.UID_PALLET=u.UID_PALLET and code.UNIT_ID=u.UNIT_ID
  ,json_table(code.PROFILES_JSON,'$[*]'columns(CODE_PROFILE varchar2(80)path '$.profile',CODE_VERSION varchar2(40)path '$.version'))decoded
  ,RRL_SKU_RECEIPT_PROFILE card
  where b.APPROVAL_OPERATION_ID=p_approval and card.ARTICUL=a.ARTICLE and card.SYSTEM_CODE=code.SYSTEM_CODE
  and card.PROFILE_CODE=decoded.CODE_PROFILE and card.PROFILE_VERSION=decoded.CODE_VERSION;
  if matched!=n*profile_count then raise_application_error(-20886,'RETURN_CURRENT_SAVED_CODE_PROFILE_VERSION_REQUIRED');end if;
  parts:=json_array_t.parse(units);
  for i in 0..parts.get_size-1 loop part:=treat(parts.get(i)as json_object_t);
   part.put('lot_uid',a.LOT_UID);part.put('article',a.ARTICLE);part.put('profiles',json_array_t.parse(profiles));parts.put(i,part,true);
  end loop;
  proof:=json_object_t();proof.put('units',parts);"""
assert needle in t;t=t.replace(needle,new,1)
t=t.replace("proof json_object_t;qty number;lines json_array_t","proof json_object_t;qty number;lot_value varchar2(200);lines json_array_t",1)
t=t.replace("proof:=json_object_t.parse(wire);select BASE_QTY into qty from RRL_STORE_RETURN_APPROVAL","proof:=json_object_t.parse(wire);select BASE_QTY,LOT_UID into qty,lot_value from RRL_STORE_RETURN_APPROVAL",1)
t=t.replace("  x.put('accepted',RRL_STOCK_PLAN_HELPER.decimal_text(qty));","  x.put('lot_uid',lot_value);x.put('accepted',RRL_STOCK_PLAN_HELPER.decimal_text(qty));",1)
out[(d/"001_core.sql").as_posix()]=t
out[(d/"002_recompile.sql").as_posix()]=Path("db/migrations/2026-10-12_ni053_marked_case_receipt/003_recompile.sql").read_text()
out[(d/"003_ledger.sql").as_posix()]="merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-388-return-current-profile-matrix' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Existing return owner bridges approved unit/lot/profile matrix to shared disposition resolver; flexible UNIT accepted, current saved profile versions checked',sysdate,user,'apply.sql','rollback.sql','APPLIED');\ncommit;\n"
out[(d/"apply.sql").as_posix()]="@@001_core.sql\n@@002_recompile.sql\n@@003_ledger.sql\n"
out[(d/"rollback.sql").as_posix()]="@@000_before_core.sql\n@@002_recompile.sql\n"
out[(d/"verify.sql").as_posix()]="select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME='RRL_STORE_RETURN_UNIT_CORE';\n"
print(json.dumps(out))
