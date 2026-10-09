declare n number;v varchar2(100);begin
 select count(*) into n from USER_OBJECTS where OBJECT_NAME like 'RRL_STOCK_%' and OBJECT_TYPE in('PACKAGE','PACKAGE BODY','TRIGGER') and STATUS!='VALID';
 if n>0 then raise_application_error(-20808,'STOCK_BRIDGE_MES_NOT_VALID');end if;
 select SETTING_VALUE into v from RRL_SYSTEM_SETTINGS where SETTING_KEY='STOCK_LEGACY_TRIGGER_ENABLED';
 if v!='0' then raise_application_error(-20808,'COMPATIBILITY_MUST_STAY_OFF_DURING_PREPARATION');end if;
 select STATE into v from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if v!='PREPARED' then raise_application_error(-20808,'CUTOVER_NOT_AUTHORIZED_BY_THIS_INSTALL');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-035-mes-supply-core' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Existing native MES allocation and raw task confirm/cancel through command core; exact P-H, document metadata and warehouse tasks',sysdate,user,'083_mes_supply_acl_apply.sql','082_mes_supply_rollback.sql','APPLIED');
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-036-event-bridge' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Explicit journal bypasses legacy double effect; prepared compatibility whole unmarked manual move; DB-wide default OFF audited setting',sysdate,user,'093_event_bridge_apply.sql','093_event_bridge_rollback.sql','APPLIED');
commit;
