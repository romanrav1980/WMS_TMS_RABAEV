-- POSTED exists only through the TRADE_QUALITY_WRITE_OFF posting kind (real stock effect in the same transaction).
alter table RRL_TRADE_QUALITY_CASE add(POSTED_BY varchar2(50),POSTED_AT timestamp with time zone,POST_OPERATION_ID varchar2(100));
alter table RRL_TRADE_QUALITY_CASE drop constraint RRL_TRADE_QUALITY_CASE_STATE;
alter table RRL_TRADE_QUALITY_CASE drop constraint RRL_TRADE_QUALITY_CASE_FACTS;
alter table RRL_TRADE_QUALITY_CASE add constraint RRL_TRADE_QUALITY_CASE_STATE check(STATE in('OPEN','DEFECT','RELEASED','WAITING_POSTING','POSTED'));
alter table RRL_TRADE_QUALITY_CASE add constraint RRL_TRADE_QUALITY_CASE_FACTS check((STATE='OPEN'and DECIDED_AT is null and APPROVED_AT is null and POSTED_AT is null)
  or(STATE in('DEFECT','RELEASED')and DECIDED_AT is not null and DECIDED_BY is not null and APPROVED_AT is null and POSTED_AT is null)
  or(STATE='WAITING_POSTING'and DECIDED_AT is not null and APPROVED_AT is not null and APPROVED_BY is not null and POSTED_AT is null)
  or(STATE='POSTED'and APPROVED_AT is not null and POSTED_AT is not null and POSTED_BY is not null and POST_OPERATION_ID is not null));
-- A posted case no longer holds its pallet: the stock is gone.
drop index RRL_TRADE_QUALITY_CASE_ACTIVE_UK;
create unique index RRL_TRADE_QUALITY_CASE_ACTIVE_UK on RRL_TRADE_QUALITY_CASE(case when STATE not in('RELEASED','POSTED')then PALLET_UID end);
create unique index RRL_TRADE_QUALITY_CASE_POST_UK on RRL_TRADE_QUALITY_CASE(POST_OPERATION_ID);
