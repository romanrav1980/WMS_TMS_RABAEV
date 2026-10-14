declare n number;begin select count(*)into n from RRL_LOGISTICS_EXPENSE where COST_CORRECTION_OF_OP is not null;
 if n!=0 then raise_application_error(-20886,'NORMATIVE_CORRECTION_FACTS_REQUIRE_FORWARD_REPAIR');end if;end;
/
@@000_before_rrl_log_exp_decision_guard.sql
@@000_before_rrl_log_expense_guard.sql
drop package RRL_NORM_COST_CORRECTION;
drop index RRL_LOG_EXP_COST_CORR_IDX;
alter table RRL_LOGISTICS_EXPENSE drop column COST_CORRECTION_OF_OP;
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-12-598-normative-cost-correction';
