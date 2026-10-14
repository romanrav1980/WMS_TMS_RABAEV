merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-254-warehouse-task-finish-instant'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Future warehouse task completion clock and same-snapshot operational day counts',sysdate,user,
'db/migrations/2026-10-11_ni072_task_finish_time/apply.sql','db/migrations/2026-10-11_ni072_task_finish_time/rollback.sql','APPLIED',
'Own4ecffb36dd/task979/WARE5265051/native awarestart/TASK_COMPLETE3 rootlate rollback/restored clock+quantity/fixedID repeat samefinish; nativeQC6/load-depart33569/same3units6codes/sourceP0/target33570 pending. OldDONE953 nobackfill/currentclockimmutable20863/dayaware start1finish1/HTTP/no closedday/nativeVALID/protected20-20. Architecture5750cycles76/JS.');
commit;
