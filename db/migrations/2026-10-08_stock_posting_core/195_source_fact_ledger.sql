declare n number;s varchar2(20);begin
 select STATE into s from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if s!='PREPARED' then raise_application_error(-20808,'DORMANT_LEDGER_REQUIRES_PREPARED');end if;
 select count(*) into n from USER_OBJECTS where STATUS!='VALID' and OBJECT_NAME in
 ('RRL_STOCK_SHIPPING_CORE','RRL_STOCK_CASE_PICK_CMD','RRL_STOCK_INV_ENTRY','RRL_REVIZION_CELL','RRL_REVIZION_CELL_SP_OLD');
 if n>0 then raise_application_error(-20808,'CURRENT_COMPONENT_INVALID');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-084-source-fact-guards' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Freeze CASE fact pending shortage decision; reject supplier/customer source conflict',sysdate,user,
 '192_source_fact_guards_apply.sql','192_source_fact_guards_rollback.sql','APPLIED');
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-085-revision-cell-each' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Measured EA inventory through explicit core; ambiguous lots require UID',sysdate,user,
 '193_revision_cell_each_apply.sql','196_revision_cell_each_rollback.sql','APPLIED');
commit;
