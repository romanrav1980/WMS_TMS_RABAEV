whenever sqlerror exit failure rollback
declare begin if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;end;
/
@@000_preflight.sql
alter table RRL_PALLET_TYPE add constraint RRL_PT_CLASS_BOX_TMP check (LOAD_UNIT_CLASS in ('PALLET', 'TROLLEY', 'CONTAINER', 'BOX'));
alter table RRL_PALLET_TYPE drop constraint RRL_PALLET_TYPE_CHK1;
alter table RRL_PALLET_TYPE rename constraint RRL_PT_CLASS_BOX_TMP to RRL_PALLET_TYPE_CHK1;
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-26-box-load-class'MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)when matched then update set STATUS='APPLIED',APPLIED_AT=sysdate,APPLIED_BY=user when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(x.MIGRATION_ID,'Allow independent BOX carrier class; preserve existing carrier values',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
