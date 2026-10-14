merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-186-shared-scale-packet'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'One pure scale packet validator reused by original store archive and forthcoming warehouse post',sysdate,user,
'db/migrations/2026-10-11_ni042_scale_packet/apply.sql','db/migrations/2026-10-11_ni042_scale_packet/rollback.sql','APPLIED',
'Fresh store source/checkpoint/paired rollback;7 statements0errors/helpers VALID; existing authenticated store capture author scenario PASS stable10KG/replay/unstable/zero/stale/capacity/version/foreign/current archive/no P/H; warehouse archiving remains next');
commit;
