prompt Recompile unchanged objects invalidated by additive table DDL; preserve initial INVALID baseline
declare v_sql varchar2(1000);
begin
 for pass in 1..3 loop
  for r in(select OBJECT_NAME,OBJECT_TYPE from USER_OBJECTS where STATUS='INVALID'
   and OBJECT_NAME not in('RRL_SAP_RECEIPT_API','RRL_SAP_STORE_ROW_GUARD')
   and (OBJECT_NAME not like 'BIN$%' or OBJECT_NAME in(select TRIGGER_NAME from USER_TRIGGERS where STATUS='ENABLED'))
   and OBJECT_TYPE in('PACKAGE BODY','PACKAGE','FUNCTION','PROCEDURE','TRIGGER','VIEW')
   order by case OBJECT_TYPE when 'PACKAGE' then 0 when 'PACKAGE BODY' then 2 else 1 end,OBJECT_NAME) loop
   v_sql:='alter '||case when r.OBJECT_TYPE='PACKAGE BODY' then 'package' else r.OBJECT_TYPE end
    ||' "'||replace(r.OBJECT_NAME,'"','""')||'" compile'||case when r.OBJECT_TYPE='PACKAGE BODY' then ' body' else '' end;
   begin execute immediate v_sql;
   exception when others then
    if sqlcode!=-24344 then raise; end if;
   end;
  end loop;
 end loop;
end;
/
declare n number;
begin
 select count(*) into n from USER_OBJECTS where STATUS='INVALID'
  and OBJECT_NAME not in('RRL_SAP_RECEIPT_API','RRL_SAP_STORE_ROW_GUARD')
  and (OBJECT_NAME not like 'BIN$%' or OBJECT_NAME in(select TRIGGER_NAME from USER_TRIGGERS where STATUS='ENABLED'));
 if n>0 then raise_application_error(-20881,'Unresolved new compilation errors; inspect USER_ERRORS'); end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-014b-stock-dependent-compilation' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Unchanged dependent object compilation after additive stock DDL',sysdate,user,'014b_recompile.sql','014b_rollback.sql','APPLIED');
commit;