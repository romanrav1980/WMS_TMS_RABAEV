prompt [migration 2026-05-17-002] Feed factory traceability API - rollback
prompt WARNING: this script drops package RRL_PRODUCTION_API only. It does not drop tables.

begin
  execute immediate 'drop package RRL_PRODUCTION_API';
exception
  when others then
    if sqlcode != -4043 then
      raise;
    end if;
end;
/

delete from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-17-002-feed-factory-traceability-api';

commit;

prompt [migration 2026-05-17-002] Rollback finished. Run 002_verify.sql.
