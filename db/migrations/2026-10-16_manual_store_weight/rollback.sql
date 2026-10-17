@@after_sources.sql
declare n number;begin
 if user!='RABAEV'or lower(sys_context('USERENV','SERVICE_NAME'))!='orcl'then raise_application_error(-20886,'PACKAGE_KIT_TARGET');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'PACKAGE_KIT_INVALID');end if;
 select count(*)into n from USER_ERRORS where NAME not like 'BIN$%';if n!=0 then raise_application_error(-20886,'PACKAGE_KIT_ERRORS');end if;
end;
/

@@schema_after.sql
declare n number;begin select count(*)into n from RRL_STORE_RECEIPT_WEIGHT where MEASUREMENT_ORIGIN!='SCALE_CAPTURE'or CAPTURE_KEY is null;
 if n!=0 then raise_application_error(-20886,'MANUAL_WEIGHT_ROLLBACK_HISTORY_EXISTS');end if;end;
/
alter table RRL_STORE_RECEIPT_WEIGHT drop constraint RRL_STORE_WEIGHT_ORIGIN_CK;
alter table RRL_STORE_RECEIPT_WEIGHT modify CAPTURE_KEY not null;
alter table RRL_STORE_RECEIPT_WEIGHT drop column MEASUREMENT_ORIGIN;
@@restore_rrl_stock_store_weight_core_package_body.sql
@@compile_dependents.sql
@@before_sources.sql
declare n number;begin
 if user!='RABAEV'or lower(sys_context('USERENV','SERVICE_NAME'))!='orcl'then raise_application_error(-20886,'PACKAGE_KIT_TARGET');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'PACKAGE_KIT_INVALID');end if;
 select count(*)into n from USER_ERRORS where NAME not like 'BIN$%';if n!=0 then raise_application_error(-20886,'PACKAGE_KIT_ERRORS');end if;
end;
/

update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-16-manual-store-weight';
commit;

@@schema_before.sql
