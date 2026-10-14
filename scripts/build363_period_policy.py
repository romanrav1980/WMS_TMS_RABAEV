from pathlib import Path
import json
out={};d=Path("db/migrations/2026-10-12_ni071_period_policy")
out[(d/"001_schema.sql").as_posix()]="""begin execute immediate q'[create table RRL_LOG_COST_PERIOD_HEAD(WARE_ID number primary key,VERSION_NO number(19)not null check(VERSION_NO>0))]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate q'[create table RRL_LOG_COST_PERIOD_HISTORY(
 WARE_ID number not null references RRL_LOG_COST_PERIOD_HEAD(WARE_ID),VERSION_NO number(19)not null,
 OPERATION_ID varchar2(100)not null unique,PAYLOAD_HASH raw(32)not null,
 PERIOD_MODE varchar2(20)not null check(PERIOD_MODE in('LOADED_UTC','CASE_ASSEMBLY')),
 TIME_ZONE varchar2(64),ACTOR nvarchar2(50)not null,REASON_TEXT varchar2(2000 byte)not null,DECISION_REFERENCE varchar2(255 byte)not null,
 CREATED_AT timestamp with time zone default systimestamp not null,RESULT_JSON clob not null check(RESULT_JSON is json),
 primary key(WARE_ID,VERSION_NO),check((PERIOD_MODE='LOADED_UTC'and TIME_ZONE is null)or(PERIOD_MODE='CASE_ASSEMBLY'and TIME_ZONE is not null))
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
declare n number;begin select count(*)into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_LOGISTICS_COST_LINE'and COLUMN_NAME='RATE_DATE';
 if n=0 then execute immediate 'alter table RRL_LOGISTICS_COST_LINE add(RATE_DATE date,PERIOD_MODE varchar2(20),PERIOD_TIME_ZONE varchar2(64),PERIOD_POLICY_VERSION number(19))';end if;
end;
/
"""
out[(d/"002_policy_guard.sql").as_posix()]="""create or replace trigger RRL_LOG_COST_PERIOD_HEAD_G before update or delete on RRL_LOG_COST_PERIOD_HEAD for each row
begin
 if deleting or :new.WARE_ID!=:old.WARE_ID or :new.VERSION_NO!=:old.VERSION_NO+1 then raise_application_error(-20863,'COST_PERIOD_HEAD_VERSION_REQUIRED');end if;
end;
/
create or replace trigger RRL_LOG_COST_PERIOD_HISTORY_G before insert or update or delete on RRL_LOG_COST_PERIOD_HISTORY for each row
declare n number;z varchar2(64);begin
 if not inserting then raise_application_error(-20863,'COST_PERIOD_HISTORY_IMMUTABLE');end if;
 select count(*)into n from RRL_LOG_COST_PERIOD_HEAD h join RUSERS u on u.ID=:new.ACTOR and nvl(u.DELETED,0)=0
 where h.WARE_ID=:new.WARE_ID and h.VERSION_NO=:new.VERSION_NO and RRL_HAS_WRIGHT(u.ID,'create_tt_price')=1
 and(u.WARE_ID=h.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN')and 1=(select count(*)from RRL_WARES where ID=h.WARE_ID);
 if n!=1 then raise_application_error(-20882,'COST_PERIOD_CURRENT_BOUND_FINANCE_REQUIRED');end if;
 if :new.PERIOD_MODE='CASE_ASSEMBLY'then select to_char(systimestamp at time zone(:new.TIME_ZONE),'TZR')into z from dual;end if;
end;
/
"""
out[(d/"004_ledger.sql").as_posix()]="""merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-363-warehouse-financial-period' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Versioned explicit warehouse BOX financial period; aware CASE source or preserved loaded UTC, immutable source proof and rate date',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
"""
out[(d/"apply.sql").as_posix()]="@@001_schema.sql\n@@002_policy_guard.sql\n@@003_cost_guard.sql\n@@004_ledger.sql\n"
out[(d/"rollback.sql").as_posix()]="declare n number;begin select count(*)into n from RRL_LOG_COST_PERIOD_HISTORY;if n>0 then raise_application_error(-20899,'FINANCIAL_PERIOD_HISTORY_REQUIRES_FORWARD_RECOVERY');end if;end;\n/\n"
out[(d/"verify.sql").as_posix()]="select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME like 'RRL_LOG_COST_PERIOD%'or NAME='RRL_LOG_COST_LINE_GUARD';\nselect WARE_ID,VERSION_NO,PERIOD_MODE,TIME_ZONE from RRL_LOG_COST_PERIOD_HISTORY;\n"
print(json.dumps(out))
