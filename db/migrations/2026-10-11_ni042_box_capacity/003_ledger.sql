merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-184-weight-box-volume-budget'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Existing pick-face capacity uses physical weighted box volumes; conservative prospective KG upper bound, no BOX-to-KG average',sysdate,user,
'db/migrations/2026-10-11_ni042_box_capacity/apply.sql','db/migrations/2026-10-11_ni042_box_capacity/rollback.sql','APPLIED',
'Own weighted wave417 CASE1057 actual storage19.6KG/two boxes/.06m3 -> existing full replenishment/pick-face.2m3/HARD9.8/CASE9.8/replay/native cleanup; no BOX conversion; current malformed GS1409/manual fact422/foreign403; helpers VALID; bounded200 lots/10000 units, not industrial certification');
commit;
