prompt [migration 2026-05-19-036] warehouse task stock move ledger - apply

declare
  procedure ensure_table(p_table varchar2, p_sql clob) is
    n number;
  begin
    select count(*) into n from user_tables where table_name = upper(p_table);
    if n = 0 then
      execute immediate p_sql;
    end if;
  end;

  procedure ensure_sequence(p_name varchar2, p_sql varchar2) is
    n number;
  begin
    select count(*) into n from user_sequences where sequence_name = upper(p_name);
    if n = 0 then
      execute immediate p_sql;
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
  ensure_table('RRL_WAREHOUSE_TASK_STOCK_MOVE', q'[
    create table RRL_WAREHOUSE_TASK_STOCK_MOVE (
      STOCK_MOVE_ID number not null,
      TASK_ID number not null,
      TASK_SOURCE varchar2(40) not null,
      TASK_TYPE varchar2(40) not null,
      SOURCE_DOC_TYPE varchar2(40),
      SOURCE_DOC_ID number,
      SOURCE_TASK_ID number,
      UID_PALLET varchar2(200) not null,
      FROM_CELL varchar2(80) not null,
      TO_CELL varchar2(80) not null,
      QTY number not null,
      CREATED_AT timestamp default systimestamp not null,
      CREATED_BY varchar2(100),
      constraint RRL_WH_TASK_STOCK_MOVE_PK primary key (STOCK_MOVE_ID),
      constraint RRL_WH_TASK_STOCK_MOVE_U1 unique (TASK_ID),
      constraint RRL_WH_TASK_STOCK_MOVE_FK1 foreign key (TASK_ID) references RRL_WAREHOUSE_TASK (TASK_ID),
      constraint RRL_WH_TASK_STOCK_MOVE_CHK1 check (QTY > 0)
    )
  ]');

  ensure_sequence('RRL_WH_TASK_STOCK_MOVE_SQ',
    'create sequence RRL_WH_TASK_STOCK_MOVE_SQ start with 1 increment by 1 nocache');

  ensure_index('RRL_WH_TASK_STOCK_MOVE_I1',
    'create index RRL_WH_TASK_STOCK_MOVE_I1 on RRL_WAREHOUSE_TASK_STOCK_MOVE (TASK_SOURCE, TASK_TYPE, SOURCE_DOC_TYPE, SOURCE_DOC_ID)');
  ensure_index('RRL_WH_TASK_STOCK_MOVE_I2',
    'create index RRL_WH_TASK_STOCK_MOVE_I2 on RRL_WAREHOUSE_TASK_STOCK_MOVE (UID_PALLET, FROM_CELL, TO_CELL)');
end;
/

merge into RRL_SCHEMA_MIGRATIONS d
using (
  select '2026-05-19-036-warehouse-task-stock-move-ledger' migration_id,
         'Warehouse task stock move ledger for idempotent RRL_REMAINS application from completed TSD warehouse-task facts' description,
         '036_apply.sql' script_name,
         '036_rollback.sql' rollback_script
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

prompt [migration 2026-05-19-036] done
