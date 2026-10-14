alter table RRL_TRANSPORT_COST_DETAIL add constraint SYS_C0018737 check(AMOUNT=QUANTITY*round(RATE_VALUE,2));
alter table RRL_TRANSPORT_COST_DETAIL drop constraint RRL_TRAN_COST_AMOUNT_CK;
@@000_before_api.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-12-594-transport-article-rounding';
