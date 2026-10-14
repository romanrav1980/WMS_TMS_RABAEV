@@001_schema.sql
@@002_helper.sql
@@004_effect.sql
@@003_shipping.sql
@@005_guards.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_SUP_RETURN','RRL_STOCK_SHIPPING_CORE','RRL_STOCK_EFFECT_CORE','RRL_SUP_RETURN_BIND_GUARD','RRL_SUP_RETURN_DISPATCH_GUARD')and STATUS='INVALID';if n!=0 then raise_application_error(-20808,'SUP_RETURN_DISPATCH_INVALID');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-108-supplier-return-existing-loading' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Existing PALL_SPLITTER supplier ST pins actual placed store return; existing single physical load/current QC/core consumes exactly one segregated pallet and records dispatch, not supplier receipt',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
