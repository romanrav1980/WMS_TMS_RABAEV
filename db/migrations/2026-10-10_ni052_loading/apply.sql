@@000_legacy_keys.sql
@@001_schema.sql
@@002_load_core.sql
@@003_departure.sql
@@004_hu_ship.sql
@@005_root.sql
@@006_guards.sql
@@007_indexes.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_HU_LOAD_CORE','RRL_STOCK_TRIP_DEPART_CMD','RRL_STOCK_HU_SHIP_CMD','RRL_STOCK_POSTING_API') and OBJECT_TYPE in('PACKAGE','PACKAGE BODY') and STATUS='VALID';
if n!=8 then raise_application_error(-20808,'PHYSICAL_LOADING_INVALID');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-077-physical-loading-departure' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Actual upper HU loading into existing vehicle/trip/dock atomic with stock shipment; separate root departure gate through all physically loaded assigned STs',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
