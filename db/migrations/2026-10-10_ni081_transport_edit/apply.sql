@@001_api.sql
@@002_loaded_guard.sql
declare n number;begin select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_TRANSPORT_EDIT_API','RRL_TT_PHYSICAL_DEPART_GUARD','RRL_STOCK_POSTING_API')and STATUS!='VALID';
 if n!=0 then raise_application_error(-20899,'TRANSPORT_EDIT137_INVALID');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-137-current-vehicle-trip-edit' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Existing manual trip edit vehicle ordering/shared capacity/current actor; loaded shipment date-time-type guard',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
