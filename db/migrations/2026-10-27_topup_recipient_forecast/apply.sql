@@before.sql
@@rrl_trade_topup_cmd_package_body.sql
@@compile_dependents.sql
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-27-topup-recipient-forecast' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)when matched then update set STATUS='APPLIED',APPLIED_AT=sysdate,APPLIED_BY=user when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Recipient-enabled movement forecast and horizon checked before hold',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
