whenever sqlerror exit failure rollback
declare n number;begin
 if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;
 -- A posted write-off is a real stock fact with an outgoing document; the posting owner is never removed under it.
 select count(*)into n from RRL_TRADE_QUALITY_CASE where STATE='POSTED';if n<>0 then raise_application_error(-20999,'QUALITY_POSTINGS_PRESENT');end if;
 select count(*)into n from RRL_STOCK_OPERATION where COMMAND_TYPE='TRADE_QUALITY_WRITE_OFF';if n<>0 then raise_application_error(-20999,'QUALITY_POSTING_OPERATIONS_PRESENT');end if;
end;
/
-- Restore the shared owners first (they reference the write-off package), then drop it, then the case version and columns.
@@before_rrl_stock_posting_api.sql
@@before_rrl_trade_stock_guard.sql
@@before_rrl_regulatory_stock_outbox.sql
@@before_rrl_stock_effect_core_spec.sql
@@before_rrl_stock_effect_core.sql
drop package RRL_STOCK_QUALITY_WRITEOFF;
@@before_rrl_trade_quality_case_api.sql
drop index RRL_TRADE_QUALITY_CASE_POST_UK;
drop index RRL_TRADE_QUALITY_CASE_ACTIVE_UK;
create unique index RRL_TRADE_QUALITY_CASE_ACTIVE_UK on RRL_TRADE_QUALITY_CASE(case when STATE<>'RELEASED'then PALLET_UID end);
alter table RRL_TRADE_QUALITY_CASE drop constraint RRL_TRADE_QUALITY_CASE_FACTS;
alter table RRL_TRADE_QUALITY_CASE drop constraint RRL_TRADE_QUALITY_CASE_STATE;
alter table RRL_TRADE_QUALITY_CASE drop(POSTED_BY,POSTED_AT,POST_OPERATION_ID);
alter table RRL_TRADE_QUALITY_CASE add constraint RRL_TRADE_QUALITY_CASE_STATE check(STATE in('OPEN','DEFECT','RELEASED','WAITING_POSTING'));
alter table RRL_TRADE_QUALITY_CASE add constraint RRL_TRADE_QUALITY_CASE_FACTS check((STATE='OPEN'and DECIDED_AT is null and APPROVED_AT is null)
  or(STATE in('DEFECT','RELEASED')and DECIDED_AT is not null and DECIDED_BY is not null and APPROVED_AT is null)
  or(STATE='WAITING_POSTING'and DECIDED_AT is not null and APPROVED_AT is not null and APPROVED_BY is not null));
@@recompile_dependents.sql
@@rollback_verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-23-trade-quality-posting' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when matched then update set STATUS='ROLLED_BACK',APPLIED_AT=sysdate,APPLIED_BY=user
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(x.MIGRATION_ID,'TRADECASE quality write-off posting kind and native quality hold enforcement',sysdate,user,'apply.sql','rollback.sql','ROLLED_BACK');
commit;
