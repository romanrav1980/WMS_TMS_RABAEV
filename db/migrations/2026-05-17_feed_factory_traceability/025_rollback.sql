prompt [migration 2026-05-17-025] MES raw supply Oracle API - rollback

begin
  execute immediate 'drop package RRL_MES_RAW_SUPPLY_API';
exception
  when others then
    if sqlcode <> -4043 then
      raise;
    end if;
end;
/

delete from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-17-025-mes-raw-supply-api';

commit;

prompt RRL_MES_RAW_* data and RRL_STOCK_RESERVATION rows are intentionally preserved.
prompt [migration 2026-05-17-025] rollback done
