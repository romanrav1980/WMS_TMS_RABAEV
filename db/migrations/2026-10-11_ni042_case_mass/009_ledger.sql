merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-207-case-measured-mass-manifest'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Measured CASE mass frozen in original HU load and store manifest',sysdate,user,
'db/migrations/2026-10-11_ni042_case_mass/apply.sql','db/migrations/2026-10-11_ni042_case_mass/rollback.sql','APPLIED',
'Own QPB2075AB68DD7/type17/6EA/SSCC090000000000000209/.400-.100=.300; existing HU outer1+.4=1.4; native rollback, fake CASE manual mass refused, load replay and departure without second stock, store frozen proof/tolerance. Original13520/20; TEST only.');
commit;
