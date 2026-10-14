@@001_schema.sql
@@002_placement.sql
@@003_unpack.sql
@@004_hu_command.sql
@@005_move_slot.sql
@@006_slot.sql
@@007_guards.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_HU_PLACEMENT_CORE','RRL_STOCK_HU_UNPACK_CMD','RRL_STOCK_HU_CMD','RRL_STOCK_HU_SLOT_MOVE_CMD','RRL_STOCK_HU_SLOT') and OBJECT_TYPE in('PACKAGE','PACKAGE BODY') and STATUS='VALID';
if n!=10 then raise_application_error(-20808,'STOCK_LEAF_PLACEMENT_INVALID');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-074-stock-leaf-placement' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Stock leaf physical unpack and empty outer carrier; measured claim bound to monotonic stock composition and physical members',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
