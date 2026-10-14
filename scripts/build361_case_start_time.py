from pathlib import Path
import json
d=Path("db/migrations/2026-10-12_ni033_case_start_instant");out={}
out[(d/"001_columns.sql").as_posix()]="""declare n number;begin
 select count(*)into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_CASE_PICK_TASK'and COLUMN_NAME='STARTED_AT_INSTANT';
 if n=0 then execute immediate 'alter table RRL_CASE_PICK_TASK add(STARTED_AT_INSTANT timestamp with time zone,STARTED_SHIFT_TIME_ZONE varchar2(64))';end if;
end;
/
"""
out[(d/"002_guard.sql").as_posix()]="""create or replace trigger RRL_CASE_START_TIME_GUARD before insert or update of STARTED_AT_INSTANT,STARTED_SHIFT_TIME_ZONE on RRL_CASE_PICK_TASK for each row
declare n number;zone_text varchar2(64);
begin
 if inserting then
  if :new.STARTED_AT_INSTANT is not null or :new.STARTED_SHIFT_TIME_ZONE is not null then raise_application_error(-20863,'CASE_START_TIME_EXPLICIT_START_REQUIRED');end if;return;
 end if;
 if :old.STARTED_AT_INSTANT is not null then
  if :new.STARTED_AT_INSTANT is null or :new.STARTED_AT_INSTANT!=:old.STARTED_AT_INSTANT or nvl(:new.STARTED_SHIFT_TIME_ZONE,'~')!=nvl(:old.STARTED_SHIFT_TIME_ZONE,'~')then raise_application_error(-20863,'CASE_ACTUAL_START_TIME_IMMUTABLE');end if;return;
 end if;
 if :new.STARTED_AT_INSTANT is null then
  if :new.STARTED_SHIFT_TIME_ZONE is not null then raise_application_error(-20886,'CASE_START_ZONE_WITHOUT_INSTANT');end if;return;
 end if;
 RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
 if :old.STARTED_AT is not null then raise_application_error(-20886,'LEGACY_CASE_START_REQUIRES_ORIGINAL_TIME_EVIDENCE');end if;
 if :new.STARTED_AT is null or :new.STARTED_AT_INSTANT<systimestamp-interval '5'second or :new.STARTED_AT_INSTANT>systimestamp+interval '5'second then raise_application_error(-20886,'CASE_START_CURRENT_SERVER_INSTANT_REQUIRED');end if;
 select count(*)into n from RUSERS u join RRL_PICK_WAVE w on w.PICK_WAVE_ID=:new.PICK_WAVE_ID
 where u.ID=:new.UPDATED_BY and nvl(u.DELETED,0)=0 and RRL_HAS_WRIGHT(u.ID,'case_pick_execute')=1 and(u.WARE_ID=w.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN');
 if n!=1 then raise_application_error(-20882,'CASE_START_CURRENT_BOUND_ACTOR_REQUIRED');end if;
 if nvl(zone_text,'~')!=nvl(:new.STARTED_SHIFT_TIME_ZONE,'~')then raise_application_error(-20886,'CASE_START_ORIGINAL_SHIFT_ZONE_REQUIRED');end if;
end;
/
"""
out[(d/"003_recompile.sql").as_posix()]=Path("db/migrations/2026-10-12_ni061_nested_receiving/009_recompile.sql").read_text(encoding="utf-8")
out[(d/"004_ledger.sql").as_posix()]="merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-361-case-actual-aware-start' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Existing CASE START captures immutable actual server instant with unknown legacy shift zone kept NULL; legacy naive starts not guessed',sysdate,user,'apply.sql','rollback.sql','APPLIED');\ncommit;\n"
out[(d/"apply.sql").as_posix()]="@@001_columns.sql\n@@002_guard.sql\n@@003_recompile.sql\n@@004_ledger.sql\n"
out[(d/"rollback.sql").as_posix()]="declare n number;begin select count(*)into n from RRL_CASE_PICK_TASK where STARTED_AT_INSTANT is not null;if n>0 then raise_application_error(-20899,'ACTUAL_CASE_START_HISTORY_REQUIRES_FORWARD_RECOVERY');end if;end;\n/\ndrop trigger RRL_CASE_START_TIME_GUARD;\n"
out[(d/"verify.sql").as_posix()]="select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME='RRL_CASE_START_TIME_GUARD';\nselect CASE_PICK_TASK_ID,STARTED_AT_INSTANT,STARTED_SHIFT_TIME_ZONE from RRL_CASE_PICK_TASK where STARTED_AT_INSTANT is not null;\n"
p=Path("api/wms_api_server/app/modules/resources/infrastructure/case_actions.py");s=p.read_text(encoding="utf-8");out["tmp/361_before_case_actions.py"]=s
start=s.index("    def start_task(");end=s.index("    def transfer_task(",start)
piece=s[start:end].replace("update RRL_CASE_PICK_TASK","update RRL_CASE_PICK_TASK t",1)
piece=piece.replace("                   STARTED_AT = nvl(STARTED_AT, systimestamp),","                   STARTED_AT = nvl(STARTED_AT, systimestamp),\n                   STARTED_AT_INSTANT = systimestamp,\n                   STARTED_SHIFT_TIME_ZONE = null,",1)
s=s[:start]+piece+s[end:];out[p.as_posix()]=s
print(json.dumps(out))
