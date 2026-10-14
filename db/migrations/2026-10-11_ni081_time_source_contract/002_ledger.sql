merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-256-material-transport-time-source'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Plan-only source contract and explicit full loaded plan review',sysdate,user,
'db/migrations/2026-10-11_ni081_time_source_contract/apply.sql','db/migrations/2026-10-11_ni081_time_source_contract/rollback.sql','APPLIED',
'Original254-255 same3units6codes/TT33570 loaded; specialunload refusedwithoutbypass; explicitloadedreview currentallmemberproof/defaultdenied/V2fullplan/replay; no rebirth/stockeffect fromreview. Combined255same snapshot phasescomplete/native actualdepart thenphaseblocked/actualOPSfact does not invalidate plan/protected20-20/nativeVALID/5770cycles76TS. OldV1history retainedLEGACY_SOURCE_CONTRACT.');
commit;
