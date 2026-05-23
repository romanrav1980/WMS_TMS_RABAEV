prompt [migration 2026-05-23-043] warehouse map operation idempotency keys - rollback

declare
  procedure drop_index_if_exists(p_name varchar2) is
    n number;
  begin
    select count(*) into n from user_indexes where index_name = upper(p_name);
    if n > 0 then
      execute immediate 'drop index ' || p_name;
    end if;
  end;
begin
  drop_index_if_exists('RRL_PICK_ROUTE_UX_IDEMP');
  drop_index_if_exists('RRL_WH_TOPOLOGY_UX_IDEMP');
  drop_index_if_exists('RRL_WH_MAP_CANVAS_UX_PUBIDEMP');
  drop_index_if_exists('RRL_WH_MAP_CANVAS_UX_IDEMP');
end;
/

delete from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-23-043-warehouse-map-operation-idempotency';

commit;

prompt [migration 2026-05-23-043] rollback done
