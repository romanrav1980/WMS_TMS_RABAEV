whenever sqlerror exit failure rollback
declare n number;begin
 if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;
 -- Taken-over holds are wave HARD reservations with history: they are never silently dropped.
 select count(*)into n from RRL_TRADE_TOPUP_ADOPTION;if n<>0 then raise_application_error(-20999,'ADOPTION_HISTORY_PRESENT');end if;
end;
/
@@before_rrl_trade_pick_context.sql
@@before_rrl_stock_wave_launch_cmd.sql
@@before_rrl_picking_api.sql
@@before_rrl_stock_reserve_core.sql
@@before_rrl_stock_reserve_core_spec.sql
drop package RRL_TRADE_TOPUP_ADOPT;
drop table RRL_TRADE_TOPUP_ADOPTION purge;
begin dbms_utility.compile_schema(user,false);end;
/
@@rollback_verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-22-trade-topup-wave-adoption' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when matched then update set STATUS='ROLLED_BACK',APPLIED_AT=sysdate,APPLIED_BY=user
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(x.MIGRATION_ID,'Atomic take-over of a top-up HARD hold by its own SAP order wave; planning sees only its own hold',sysdate,user,'apply.sql','rollback.sql','ROLLED_BACK');
commit;
