declare n number;begin select count(*)into n from RRL_INTERWARE_CUSTODY_PROOF;if n!=0 then raise_application_error(-20899,'INTERWARE121_FORWARD_ONLY_AFTER_FACTS');end if;end;
/
@@../2026-10-08_stock_posting_core/438_before121_root.sql
@@../2026-10-08_stock_posting_core/439_before121_load_fact_guard.sql
drop index RRL_TT_HU_LOAD_UID_U1;
create unique index RRL_TT_HU_LOAD_UID_U1 on RRL_TT_HU_LOAD_FACT(case when STATUS in('LOADED','DEPARTED')then ROOT_UID end);
drop table RRL_INTERWARE_CUSTODY_PROOF;
alter table RRL_TT_HU_LOAD_FACT drop(CUSTODY_RELEASED_AT,CUSTODY_RELEASE_OPERATION_ID);
drop package RRL_STOCK_INTERWARE_CUSTODY;
