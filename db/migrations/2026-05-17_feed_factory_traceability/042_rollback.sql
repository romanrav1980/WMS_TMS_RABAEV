prompt [migration 2026-05-22-042] warehouse map draft publish API - rollback

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
  drop_index_if_exists('RRL_PICK_ROUTE_CELL_UX_SLOT');
end;
/

drop package RRL_WAREHOUSE_MAP_API;

delete from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-22-042-warehouse-map-draft-publish-api';

commit;

prompt [migration 2026-05-22-042] rollback done
