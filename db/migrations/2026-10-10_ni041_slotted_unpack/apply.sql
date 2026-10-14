@@001_slot.sql
@@002_hu_command.sql
@@003_reserve_acl.sql
@@004_unpack.sql
@@005_root.sql
@@006_guards.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_HU_UNPACK_CMD','RRL_STOCK_HU_SLOT','RRL_STOCK_HU_CMD','RRL_STOCK_POSTING_API','RRL_STOCK_RESERVE_CORE') and OBJECT_TYPE in('PACKAGE','PACKAGE BODY') and STATUS='VALID';
if n!=10 then raise_application_error(-20808,'SLOTTED_UNPACK_INVALID');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-069-slotted-hu-unpack' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Explicit nested-container extraction to separate slot; two fresh measurements/actual tasks/claims; same quantities/owner, reservation slot only',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
