merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-202-small-box-final-weight'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Per-carrier type mandatory child final weight with existing QC owner',sysdate,user,
'db/migrations/2026-10-11_ni042_small_final_weight/apply.sql','db/migrations/2026-10-11_ni042_small_final_weight/rollback.sql','APPLIED',
'Own QPB202E0AA707B small type7/customer-specific CASE6/original warehouse NONE but child WEIGHT; measured gross.400/wood.100/net.300/native QC/replay/source14 unchanged. Precise DTO/version/old omission preserveflag/rawwrite20863/current owner. Addressed hardware archive next; no measured-reference claim.');
commit;
