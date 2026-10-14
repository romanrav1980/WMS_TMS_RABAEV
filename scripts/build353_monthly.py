from pathlib import Path
import json
d=Path("db/migrations/2026-10-12_ni071_monthly_rate");out={}
out[(d/"001_columns.sql").as_posix()]="""declare n number;begin
 select count(*)into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_LOGISTICS_RATE_HISTORY'and COLUMN_NAME='COMPONENTS_JSON';
 if n=0 then execute immediate 'alter table RRL_LOGISTICS_RATE_HISTORY add(COMPONENTS_JSON clob check(COMPONENTS_JSON is json))';end if;
end;
/
"""
old=Path("db/migrations/2026-10-10_ni071_box_cost/002_guards.sql").read_text(encoding="utf-8").split("create or replace trigger RRL_LOG_COST_RUN_GUARD")[0]
out[(d/"000_before_history_guard.sql").as_posix()]=old
new=old.replace("declare n number;","declare n number;j json_object_t;base_value number;common_amount number;boxes number;share number;total_rate number;month_text varchar2(7);",1)
marker=" if n!=1 then raise_application_error(-20882,'LOGISTICS_RATE_CURRENT_BOUND_FINANCE_REQUIRED');end if;"
assert marker in new
new=new.replace(marker,marker+"""
 if :new.COMPONENTS_JSON is not null then
  j:=json_object_t.parse(:new.COMPONENTS_JSON);base_value:=j.get_number('picking_rate');common_amount:=j.get_number('common_work_amount');boxes:=j.get_number('basis_boxes');share:=j.get_number('common_work_rate');total_rate:=j.get_number('combined_rate');month_text:=j.get_string('month');
  if j.get_size!=7 or base_value is null or common_amount is null or boxes is null or share is null or total_rate is null or month_text is null or j.get_string('basis_provenance')is null or j.get_string('basis_provenance')!='DECLARED_MONTHLY_BOX_BASE'
   or base_value<0 or common_amount<0 or common_amount!=round(common_amount,2)or boxes<=0 or boxes!=trunc(boxes)or boxes>999999999999 or share!=round(common_amount/boxes,9)or total_rate!=base_value+share or total_rate!=:new.RATE_VALUE or total_rate>=1e18
   or month_text!=to_char(:new.EFFECTIVE_FROM,'YYYY-MM')or :new.EFFECTIVE_FROM!=trunc(:new.EFFECTIVE_FROM,'MM')then raise_application_error(-20886,'LOGISTICS_MONTHLY_RATE_EXACT_COMPONENTS_REQUIRED');end if;
 end if;
""")
out[(d/"002_history_guard.sql").as_posix()]=new
out[(d/"003_ledger.sql").as_posix()]="merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-353-monthly-shared-box-rate' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Existing immutable BOX rate includes explicit monthly common work components and declared box base, without second extra charge',sysdate,user,'apply.sql','rollback.sql','APPLIED');\ncommit;\n"
out[(d/"apply.sql").as_posix()]="@@001_columns.sql\n@@002_history_guard.sql\n@@003_ledger.sql\n"
out[(d/"rollback.sql").as_posix()]="declare n number;begin select count(*)into n from RRL_LOGISTICS_RATE_HISTORY where COMPONENTS_JSON is not null;if n>0 then raise_application_error(-20899,'MONTHLY_RATE_HISTORY_REQUIRES_FORWARD_RECOVERY');end if;end;\n/\n@@000_before_history_guard.sql\n"
out[(d/"verify.sql").as_posix()]="select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME='RRL_LOG_RATE_HISTORY_GUARD';\nselect RATE_KEY,VERSION_NO,EFFECTIVE_FROM,RATE_VALUE,COMPONENTS_JSON from RRL_LOGISTICS_RATE_HISTORY where COMPONENTS_JSON is not null;\n"
print(json.dumps(out))
