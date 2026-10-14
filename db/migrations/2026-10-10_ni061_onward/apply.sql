@@001_schema.sql
@@002_helper.sql
@@003_shipping.sql
@@004_guards.sql
declare n number;begin select count(*)into n from user_objects where OBJECT_NAME in('RRL_STOCK_INTERWARE_NEXT','RRL_STOCK_SHIPPING_CORE','RRL_INTERWARE_ONWARD_BIND_GUARD','RRL_INTERWARE_ONWARD_FACT_GUARD','RRL_INTERWARE_ONWARD_ST_GUARD','RRL_INTERWARE_ONWARD_ROW_GUARD')and STATUS!='VALID';if n!=0 then raise_application_error(-20899,'INTERWARE122_INVALID_OBJECTS');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-122-existing-onward-st-original-ownership' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Existing ordinary ST constructor/rows and exact source-pinned second shoulder loading, original customer ownership retained without new fulfillment',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
