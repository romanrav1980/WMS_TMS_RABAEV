declare n number;begin select count(*)into n from RRL_IW_GROUP_UNLOAD;if n!=0 then raise_application_error(-20899,'GROUP_PHYSICAL_FACTS_REQUIRE_FORWARD_RECOVERY');end if;end;
/
@@000_before_rec.sql
@@000_before_units.sql
drop trigger RRL_IW_GROUP_REC_LINE_GUARD;
drop trigger RRL_IW_GROUP_RECEIPT_GUARD;
drop trigger RRL_IW_GROUP_UNLOAD_GUARD;
drop package RRL_IW_GROUP_FACT_GUARD;
drop package RRL_IW_GROUP_REC;
drop table RRL_IW_GROUP_RECEIPT_LINE;
drop table RRL_IW_GROUP_RECEIPT;
drop table RRL_IW_GROUP_UNLOAD;
alter package RRL_STOCK_POSTING_API compile body;
delete from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-12-409-grouped-interware-receipt';
commit;
