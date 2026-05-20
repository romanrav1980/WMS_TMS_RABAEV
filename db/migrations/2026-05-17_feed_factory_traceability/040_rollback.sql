prompt [migration 2026-05-20-040] linear pick route order invariants - rollback

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
  drop_index_if_exists('RRL_PICK_ROUTE_CELL_UX_CELL');
  drop_index_if_exists('RRL_PICK_ROUTE_CELL_UX_SEQ');
  drop_index_if_exists('RRL_PICK_ROUTE_UX_ACTIVE_TOPO');
end;
/

delete from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-20-040-linear-pick-route-order';

commit;

prompt [migration 2026-05-20-040] rollback done
