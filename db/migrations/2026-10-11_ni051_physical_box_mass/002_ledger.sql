merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-185-actual-box-quality-mass'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Existing outgoing QC reads actual physical weighted-box gross masses, half-lightest actual box tolerance; normal SI policy retained',sysdate,user,
'db/migrations/2026-10-11_ni051_physical_box_mass/apply.sql','db/migrations/2026-10-11_ni051_physical_box_mass/rollback.sql','APPLIED',
'Actual marked CASE1059 net9.8/gross10.1/minhalf5.05; mismatched partial9.7 refused; existing closed carrier/ST binding/current independent controller native WEIGHT2 passes/replay, SCAN remains pending; native cleanup/original13520/20; SQL0.701ms/8');
commit;
