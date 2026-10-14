create index RRL_ST_DEFER_ORIG_DAY_I on RRL_ST_DEFER_DECISION(WARE_ID,json_value(RESULT_JSON,'$.original_shipping_date'returning varchar2(10)),ST_NUMBER);
/
merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-652-deferred-original-day-register'MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Indexed existing immutable deferral origin day preserves NULL-date ST members in original daily register',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
