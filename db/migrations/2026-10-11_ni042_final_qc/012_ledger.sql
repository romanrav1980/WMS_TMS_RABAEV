merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-205-final-scale-qc-use'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Existing native QC mandatory addressed whole CASE weight and once-use',sysdate,user,
'db/migrations/2026-10-11_ni042_final_qc/apply.sql','db/migrations/2026-10-11_ni042_final_qc/rollback.sql','APPLIED',
'Own QPB205F0C461FA/type12/CASE6/SSCC090000000000000100/gross.400/tare.100/net.300: native late rollback, distinct concurrentOP one winner, sameOP replay, manual bypass403/409, current WARE before saved native replay, immutable use, original source14/nativecleanup13520/20. Existing root/QC/gate reused; TEST visible in result/UI, no real hardware claim.');
commit;
