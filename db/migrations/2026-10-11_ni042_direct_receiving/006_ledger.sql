merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-199-direct-receiving-pick-plan'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Existing DIRECT SAP source planning and atomic placement handoff',sysdate,user,
'db/migrations/2026-10-11_ni042_direct_receiving/apply.sql','db/migrations/2026-10-11_ni042_direct_receiving/rollback.sql','APPLIED',
'Own QPB1999A1F92AB wave444 SAP20 to original store orders12/8; wait before birth/current IN_PROGRESS refusal/no target or replenishment/current HARD/native CASE picks/replay; outer rollback restores putaway and HARD0; original taskQTY retained; narrow planned native SAP CASE clone trigger; native cleanup/original13520/20.');
commit;
