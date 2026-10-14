declare n number;begin
 select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_ELIGIBILITY','RRL_STOCK_RESERVE_CORE','RRL_STOCK_WAVE_CMD','RRL_STOCK_WAVE_LAUNCH_CMD','RRL_STOCK_CASE_PICK_CMD','RRL_STOCK_TASK_CORE','RRL_PICKING_API') and STATUS!='VALID';
 if n>0 then raise_application_error(-20808,'ELIGIBILITY_OBJECT_INVALID');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-09-007-stock-source-eligibility' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'NI03.1 shared stock source eligibility for picking/wave and locked execution',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
