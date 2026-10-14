merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-280-route-material-source-v3'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Original address date and order in time-route sourceV3',sysdate,user,
'db/migrations/2026-10-11_ni081_route_material_v3/001_body.sql','db/migrations/2026-10-11_ni081_route_material_v3/rollback.sql','APPLIED',
'Livebody no spec change; currentADDR/STDATE/ORD hash, oldV2decisions preserved stale, no physicalrollback. Actualown33564 two members address/ordinal perturbations rollbackexact; SQL0.820ms5/20buf P20H20.');
commit;
