prompt [migration 2026-05-17-027] warehouse task quantity mode - apply

declare
  procedure ensure_column(p_table varchar2, p_column varchar2, p_sql varchar2) is
    n number;
  begin
    select count(*)
      into n
      from user_tab_cols
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
  ensure_column('RRL_WAREHOUSE_TASK', 'QTY_MODE',
    q'[alter table RRL_WAREHOUSE_TASK add QTY_MODE varchar2(20) default 'BOX' not null]');
  ensure_column('RRL_WAREHOUSE_TASK', 'FACT_QTY',
    q'[alter table RRL_WAREHOUSE_TASK add FACT_QTY number]');
  ensure_column('RRL_WAREHOUSE_TASK', 'PARENT_TASK_ID',
    q'[alter table RRL_WAREHOUSE_TASK add PARENT_TASK_ID number]');

  execute immediate q'[
    update RRL_WAREHOUSE_TASK
       set QTY_MODE = case
                        when TASK_TYPE = 'FG_TO_STORAGE' then 'PALLET'
                        else nvl(QTY_MODE, 'BOX')
                      end
     where QTY_MODE is null
        or (TASK_TYPE = 'FG_TO_STORAGE' and QTY_MODE <> 'PALLET')
  ]';

  execute immediate q'[
    update RRL_WAREHOUSE_TASK
       set FACT_QTY = QTY
     where STATUS = 'DONE'
       and FACT_QTY is null
  ]';

  ensure_index('RRL_WAREHOUSE_TASK_I5',
    'create index RRL_WAREHOUSE_TASK_I5 on RRL_WAREHOUSE_TASK (QTY_MODE, STATUS)');
  ensure_index('RRL_WAREHOUSE_TASK_I6',
    'create index RRL_WAREHOUSE_TASK_I6 on RRL_WAREHOUSE_TASK (PARENT_TASK_ID)');
end;
/

merge into RRL_SCHEMA_MIGRATIONS d
using (
  select '2026-05-17-027-warehouse-task-qty-mode' migration_id,
         'Warehouse task quantity mode and residual task links' description,
         '027_apply.sql' script_name,
         '027_rollback.sql' rollback_script
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

prompt [migration 2026-05-17-027] done
