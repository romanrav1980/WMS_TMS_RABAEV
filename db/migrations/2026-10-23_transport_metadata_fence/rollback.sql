whenever sqlerror exit failure rollback
@@verify.sql
declare n number;begin select count(*)into n from USER_DEPENDENCIES where REFERENCED_OWNER=user and REFERENCED_NAME='RRL_STOCK_METADATA_TX'and NAME not in('RRL_ASSEMBLY_SCALE_API','RRL_INTERWARE_INCIDENT_API','RRL_SAP_STORE_ADMISSION_API','RRL_STOCK_METADATA_TX','RRL_STORE_CALENDAR_API','RRL_ST_DEFER_API','RRL_ST_DEFER_WAIT_API','RRL_TT_ROUTE_API','RRL_TT_TIME_API','RRL_UPDATE_PALLET_ROW2','RRL_UPDATE_PALLET_ROW3','RRL_WARE_DEPOT_API','RRL_WAVE_TIME_API','RRL_WORKLOAD_CONFIG_API');if n<>0 then raise_application_error(-20999,'TRANSPORT_FENCE_NEW_DEPENDENTS');end if;end;
/
@@before.sql
@@recompile.sql
@@rollback_verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-23-transport-metadata-fence' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)when matched then update set STATUS='ROLLED_BACK',APPLIED_AT=sysdate,APPLIED_BY=user when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Assigned transport dispatcher under existing metadata fence',sysdate,user,'apply.sql','rollback.sql','ROLLED_BACK');
commit;
