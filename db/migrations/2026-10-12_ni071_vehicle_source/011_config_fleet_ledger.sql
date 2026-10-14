merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-564-config-fleet-permission' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Allow actual transport_fleet_edit through existing configuration fence without granting warehouse settings rights',sysdate,user,'apply_config_fleet.sql','rollback_config_fleet.sql','APPLIED');
/
