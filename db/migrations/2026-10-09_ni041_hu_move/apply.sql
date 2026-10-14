@@001_read.sql
@@002_commands.sql
@@003_transfer.sql
@@004_posting.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_HU_READ','RRL_STOCK_HU_CMD','RRL_STOCK_TRANSFER_CORE','RRL_STOCK_POSTING_API') and OBJECT_TYPE in('PACKAGE','PACKAGE BODY') and STATUS='VALID';
if n!=8 then raise_application_error(-20808,'HU_MOVE_OBJECTS_INVALID');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-09-051-whole-hu-move' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Atomic top container move with whole leaf P/H and unit/reservation ownership; bounded empty unrestricted storage target until physical slot adapter',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
