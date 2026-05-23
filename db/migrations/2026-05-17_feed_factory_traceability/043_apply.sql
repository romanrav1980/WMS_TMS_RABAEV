prompt [migration 2026-05-23-043] warehouse map operation idempotency keys - apply

declare
  procedure ensure_column(p_table varchar2, p_column varchar2, p_sql varchar2) is
    n number;
  begin
    select count(*) into n
      from user_tab_columns
     where table_name = upper(p_table)
       and column_name = upper(p_column);
    if n = 0 then
      execute immediate p_sql;
    end if;
  end;

  procedure ensure_index(p_name varchar2, p_sql varchar2) is
    n number;
  begin
    select count(*) into n from user_indexes where index_name = upper(p_name);
    if n = 0 then
      execute immediate p_sql;
    end if;
  end;
begin
  ensure_column('RRL_WAREHOUSE_MAP_CANVAS', 'IDEMPOTENCY_KEY',
    'alter table RRL_WAREHOUSE_MAP_CANVAS add IDEMPOTENCY_KEY varchar2(120)');
  ensure_column('RRL_WAREHOUSE_MAP_CANVAS', 'PUBLISH_IDEMPOTENCY_KEY',
    'alter table RRL_WAREHOUSE_MAP_CANVAS add PUBLISH_IDEMPOTENCY_KEY varchar2(120)');
  ensure_column('RRL_WAREHOUSE_TOPOLOGY', 'IDEMPOTENCY_KEY',
    'alter table RRL_WAREHOUSE_TOPOLOGY add IDEMPOTENCY_KEY varchar2(120)');
  ensure_column('RRL_PICK_ROUTE', 'IDEMPOTENCY_KEY',
    'alter table RRL_PICK_ROUTE add IDEMPOTENCY_KEY varchar2(120)');

  ensure_index('RRL_WH_MAP_CANVAS_UX_IDEMP',
    q'[create unique index RRL_WH_MAP_CANVAS_UX_IDEMP on RRL_WAREHOUSE_MAP_CANVAS (
       case when ACTIVE = 1 and IDEMPOTENCY_KEY is not null then WARE_ID end,
       case when ACTIVE = 1 and IDEMPOTENCY_KEY is not null then upper(IDEMPOTENCY_KEY) end
    )]');
  ensure_index('RRL_WH_MAP_CANVAS_UX_PUBIDEMP',
    q'[create unique index RRL_WH_MAP_CANVAS_UX_PUBIDEMP on RRL_WAREHOUSE_MAP_CANVAS (
       case when ACTIVE = 1 and PUBLISH_IDEMPOTENCY_KEY is not null then WARE_ID end,
       case when ACTIVE = 1 and PUBLISH_IDEMPOTENCY_KEY is not null then upper(PUBLISH_IDEMPOTENCY_KEY) end
    )]');
  ensure_index('RRL_WH_TOPOLOGY_UX_IDEMP',
    q'[create unique index RRL_WH_TOPOLOGY_UX_IDEMP on RRL_WAREHOUSE_TOPOLOGY (
       case when STATUS <> 'ARCHIVED' and IDEMPOTENCY_KEY is not null then WARE_ID end,
       case when STATUS <> 'ARCHIVED' and IDEMPOTENCY_KEY is not null then upper(IDEMPOTENCY_KEY) end
    )]');
  ensure_index('RRL_PICK_ROUTE_UX_IDEMP',
    q'[create unique index RRL_PICK_ROUTE_UX_IDEMP on RRL_PICK_ROUTE (
       case when ACTIVE = 1 and STATUS <> 'ARCHIVED' and IDEMPOTENCY_KEY is not null then TOPOLOGY_ID end,
       case when ACTIVE = 1 and STATUS <> 'ARCHIVED' and IDEMPOTENCY_KEY is not null then upper(IDEMPOTENCY_KEY) end
    )]');
end;
/

merge into RRL_SCHEMA_MIGRATIONS d
using (
  select '2026-05-23-043-warehouse-map-operation-idempotency' migration_id,
         'Warehouse map canvas, projection, route, and publish operation idempotency keys' description,
         '043_apply.sql' script_name,
         '043_rollback.sql' rollback_script
    from dual
) s
on (d.MIGRATION_ID = s.MIGRATION_ID)
when matched then update set
  d.DESCRIPTION = s.DESCRIPTION,
  d.SCRIPT_NAME = s.SCRIPT_NAME,
  d.ROLLBACK_SCRIPT = s.ROLLBACK_SCRIPT,
  d.APPLIED_AT = sysdate,
  d.APPLIED_BY = user
when not matched then insert (
  MIGRATION_ID, DESCRIPTION, SCRIPT_NAME, ROLLBACK_SCRIPT, APPLIED_AT, APPLIED_BY
) values (
  s.MIGRATION_ID, s.DESCRIPTION, s.SCRIPT_NAME, s.ROLLBACK_SCRIPT, sysdate, user
);

commit;

prompt [migration 2026-05-23-043] apply done
