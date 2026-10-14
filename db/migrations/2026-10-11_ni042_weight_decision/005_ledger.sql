merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-192-weight-tolerance-decision'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Explicit signed original order weight decision in existing CASE short approval root',sysdate,user,
'db/migrations/2026-10-11_ni042_weight_decision/apply.sql','db/migrations/2026-10-11_ni042_weight_decision/rollback.sql','APPLIED',
'CASE1070 short20 exact9.6/10/15 percent frozen metadata/no false inventory/P20H9.6/SHORT_PICKED; rollback outbox+decision+H passed; concurrent identical result/stale409/immutable proof/current scopes. Pool return-aware waiver next.');
commit;
