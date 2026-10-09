declare n number;v varchar2(20);begin
 select STATE into v from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if v!='PREPARED' then raise_application_error(-20808,'DORMANT_LEDGER_REQUIRES_PREPARED');end if;
 select count(*) into n from USER_OBJECTS where STATUS!='VALID' and
  OBJECT_NAME in('RRL_STOCK_CHANGE_AUDIT','RRL_STOCK_INVENTORY_BIRTH','RRL_STOCK_RESERVATION_CMD','RRL_STOCK_POSTING_API','RRL_ADD_INV_LINE');
 if n>0 then raise_application_error(-20808,'CURRENT_COMMAND_PACKAGES_INVALID');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-043-stock-change-audit' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Outbox v3: stock snapshots and changed unit/reservation composition; dormant code',sysdate,user,'123_stock_change_payload_apply.sql','123_stock_change_payload_rollback.sql','APPLIED');
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-044-inventory-birth' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Initial inventory via existing native import and declared inventory lot; dormant code',sysdate,user,'127_inventory_import_apply.sql','127_inventory_import_rollback.sql','APPLIED');
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-045-inventory-duplicate-guard' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Existing positive SKU/cell requires measured count; no duplicate inventory receipt',sysdate,user,'128_inventory_duplicate_guard_apply.sql','128_inventory_duplicate_guard_rollback.sql','APPLIED');
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-046-reservation-base-policy' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Reservation input conversion separated from canonical balance base policy',sysdate,user,'129_reservation_base_policy_apply.sql','129_reservation_base_policy_rollback.sql','APPLIED');
update RRL_SCHEMA_MIGRATIONS set SCRIPT_NAME='123_stock_change_payload_apply.sql',ROLLBACK_SCRIPT='123_stock_change_payload_rollback.sql' where MIGRATION_ID='2026-10-08-043-stock-change-audit';
commit;
