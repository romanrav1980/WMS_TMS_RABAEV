merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-259-trip-specific-route-estimate'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Scoped trip route duration estimate and original ARM regeneration',sysdate,user,
'db/migrations/2026-10-11_ni081_route_input/apply.sql','db/migrations/2026-10-11_ni081_route_input/rollback.sql','APPLIED',
'Original own empty33564 same12OPS IDs/duration45-50/outerrollback/customchainlatefailure rollback/concurrentHTTP200-409/replay/payload/foreign403/journalguard/materialchanges stale/newtimeV2/protected20-20. Estimate only/no routing-provider legal admission/nativeVALID. No goods birth.');
commit;
