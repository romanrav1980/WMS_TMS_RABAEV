merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-264-store-calendar-exceptions'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Original store calendar date exceptions and retained held SAP demand',sysdate,user,
'db/migrations/2026-10-11_ni022_calendar/apply.sql','db/migrations/2026-10-11_ni022_calendar/rollback.sql','APPLIED',
'NativecurrentWARE/metadataCFGX narrowcustomer_rule_edit/exceptionimmutable/weeklywriteguard/version/replay/concurrentHTTP200-409/rollback. OriginalStoreMap0 andSAPOrders0 discovered; ownmap6 syntheticregistrationprecondition/existingcustomer-article heldqty1/newOPENqty1/pickplans0/stockunchanged. JSONnative reader/reservedRAWbind fixed. No realERP claim.');
commit;
