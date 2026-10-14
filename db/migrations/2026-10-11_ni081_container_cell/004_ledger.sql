merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-178-container-cell-sparse-index'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Sparse existing container-cell function index and matching predicates without virtual columns or stock writer changes',sysdate,user,
'db/migrations/2026-10-11_ni081_container_cell/apply.sql','db/migrations/2026-10-11_ni081_container_cell/rollback.sql','APPLIED',
'Index VALID84 rows; same READ ONLY snapshot seven cells old/new equivalent, author latency126.991->3.541ms; actual existing empty carrier native move/back no quantity journal; new native count0.825ms/4, not industrial capacity');
commit;
