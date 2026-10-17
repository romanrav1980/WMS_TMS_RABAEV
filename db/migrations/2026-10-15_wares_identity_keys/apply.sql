-- Explicit owner decision: physical ID is the relational key; NAME is the business key.
-- No row is deleted, merged, renamed or renumbered.
@@before.sql
alter table RRL_WARES add constraint RRL_WARES_PK primary key(ID) enable validate;
alter table RRL_WARES modify(NAME constraint RRL_WARES_NAME_NN not null);
alter table RRL_WARES add constraint RRL_WARES_NAME_UK unique(NAME) enable validate;
@@verify.sql
insert into RRL_SCHEMA_MIGRATIONS(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values('2026-10-15-wares-identity-keys','Warehouse ID primary key and exact NAME mandatory unique business key; no row changes',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
