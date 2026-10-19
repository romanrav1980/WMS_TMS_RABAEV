whenever sqlerror exit failure rollback
alter table RRL_TRADE_BUYOUT drop constraint RRL_TRADE_BUYOUT_EXT_UK drop index;
create unique index RRL_TRADE_BUYOUT_DOC_UK on RRL_TRADE_BUYOUT(
 case when EXTERNAL_DOCUMENT_ID is not null then WARE_ID end,
 case when EXTERNAL_DOCUMENT_ID is not null then SKM_ID end,
 EXTERNAL_DOCUMENT_ID
);
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-19-tradecase-buyout-external-key'MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(x.MIGRATION_ID,'Unique external document only after its ID exists; permit multiple independent pending buyouts',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
