whenever sqlerror exit failure rollback
@@000_preflight.sql
@@001_allow_many_cases_per_st.sql
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d
using (select '2026-10-29-root-hu-shipment-bind' migration_id from dual) x
   on (d.MIGRATION_ID=x.migration_id)
when matched then update set STATUS='APPLIED', APPLIED_AT=sysdate, APPLIED_BY=user
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(x.migration_id,'Allow one root HU with multiple CASE children to bind to one ST',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
