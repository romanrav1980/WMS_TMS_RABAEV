whenever sqlerror exit failure rollback
declare begin if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;end;
/
-- Only package bodies change and no data is created. Restoring the before bodies brings back TRADE_TOPUP_COMMON_POOL_UNSUPPORTED;
-- holds already taken over by a wave stay as they are (the old launch refuses new pool top-ups, it does not touch adopted ones).
@@before_rrl_trade_topup_adopt.sql
@@before_rrl_stock_pool_cmd.sql
@@before_rrl_stock_pool_read.sql
@@rollback_verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-23-trade-topup-common-pool' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when matched then update set STATUS='ROLLED_BACK',APPLIED_AT=sysdate,APPLIED_BY=user;
commit;
