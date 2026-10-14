merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-183-physical-box-dimensions'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Per-physical-unit declared gross KG, volume, measurement reference and original GS1 label; exact net quantity unchanged',sysdate,user,
'db/migrations/2026-10-11_ni042_weight_box_dimensions/apply.sql','db/migrations/2026-10-11_ni042_weight_box_dimensions/rollback.sql','APPLIED',
'Own weighted marked4.25KG/4.5gross/.03volume/code1/no legal ACK; own marked CASE1056 actual9.8KG/gross10.1/.03volume/current unit QR/no-QR409/replay/composition evidence/native cleanup; original135 P20H20 unchanged; additive columns/constraint/recompile0errors');
commit;
