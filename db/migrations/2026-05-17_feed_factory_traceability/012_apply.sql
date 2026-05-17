prompt [migration 2026-05-17-012] WMS warehouse settings - apply

declare
  procedure ensure_column(p_table varchar2, p_column varchar2, p_sql varchar2) is
    n number;
  begin
    select count(*)
      into n
      from user_tab_columns
     where table_name = upper(p_table)
       and column_name = upper(p_column);

    if n = 0 then
      execute immediate 'alter table ' || p_table || ' add (' || p_sql || ')';
    end if;
  end;

  procedure ensure_index(p_name varchar2, p_sql varchar2) is
    n number;
  begin
    select count(*) into n from user_indexes where index_name = upper(p_name);
    if n = 0 then
      begin
        execute immediate p_sql;
      exception
        when others then
          if sqlcode = -1408 then
            null;
          else
            raise;
          end if;
      end;
    end if;
  end;
begin
  ensure_column('RRL_WARES', 'FLAG_RAW_MATERIAL', q'[FLAG_RAW_MATERIAL number(1) default 0]');
  ensure_column('RRL_WARES', 'FLAG_PRODUCTION', q'[FLAG_PRODUCTION number(1) default 0]');
  ensure_column('RRL_WARES', 'FLAG_PRODUCTION_BUFFER', q'[FLAG_PRODUCTION_BUFFER number(1) default 0]');
  ensure_column('RRL_WARES', 'FLAG_FINISHED_GOODS', q'[FLAG_FINISHED_GOODS number(1) default 0]');
  ensure_column('RRL_WARES', 'MES_ENABLED', q'[MES_ENABLED number(1) default 0]');
  ensure_column('RRL_WARES', 'DEFAULT_RECEIVE_CELL', q'[DEFAULT_RECEIVE_CELL varchar2(20)]');
  ensure_column('RRL_WARES', 'DEFAULT_ISSUE_CELL', q'[DEFAULT_ISSUE_CELL varchar2(20)]');
  ensure_column('RRL_WARES', 'WARE_COMMENT', q'[WARE_COMMENT varchar2(1000)]');

  ensure_index('RRL_WARES_I_MES_FLAGS', 'create index RRL_WARES_I_MES_FLAGS on RRL_WARES (MES_ENABLED, FLAG_RAW_MATERIAL, FLAG_PRODUCTION, FLAG_PRODUCTION_BUFFER, FLAG_FINISHED_GOODS, ID)');
end;
/

insert into RIGHTS (RIGHT1, USER_GROUP, ID, DESCR)
select s.RIGHT1,
       'GLOBAL_ADMIN',
       (select nvl(max(ID), 0) from RIGHTS) + row_number() over (order by s.RIGHT1),
       s.DESCR
  from (
    select 'WAREHOUSE_SETTINGS_VIEW' RIGHT1, 'View WMS warehouse type settings' DESCR from dual
    union all
    select 'WAREHOUSE_SETTINGS_EDIT', 'Edit WMS warehouse type settings' from dual
  ) s
 where not exists (
   select 1
     from RIGHTS r
    where r.USER_GROUP = 'GLOBAL_ADMIN'
      and upper(r.RIGHT1) = s.RIGHT1
 );

merge into RRL_SCHEMA_MIGRATIONS d
using (
  select '2026-05-17-012-wms-warehouse-settings' migration_id,
         'Warehouse role flags for raw, production, production buffer, and finished goods warehouses' description,
         '012_apply.sql' script_name,
         '012_rollback.sql' rollback_script
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

prompt [migration 2026-05-17-012] done
