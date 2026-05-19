prompt [migration 2026-05-17-028] warehouse task domain sync - apply

declare
  procedure ensure_table(p_name varchar2, p_sql varchar2) is
    n number;
  begin
    select count(*) into n from user_tables where table_name = upper(p_name);
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
      execute immediate p_sql;
    end if;
  end;
begin
  ensure_table('RRL_WAREHOUSE_TASK_SYNC', q'[
    create table RRL_WAREHOUSE_TASK_SYNC (
      SYNC_ID number not null,
      TASK_ID number not null,
      TASK_SOURCE varchar2(40) not null,
      TASK_TYPE varchar2(40) not null,
      SOURCE_DOC_TYPE varchar2(40),
      SOURCE_DOC_ID number,
      SOURCE_TASK_ID number,
      SOURCE_MOVEMENT_ID number,
      SYNC_KEY varchar2(240) not null,
      SYNC_STATUS varchar2(30) default 'PENDING' not null,
      SYNC_ATTEMPT number default 0 not null,
      LAST_ERROR varchar2(2000),
      CREATED_AT timestamp default systimestamp not null,
      UPDATED_AT timestamp,
      SYNCED_AT timestamp,
      UPDATED_BY varchar2(100),
      constraint RRL_WH_TASK_SYNC_PK primary key (SYNC_ID),
      constraint RRL_WH_TASK_SYNC_CHK1 check (SYNC_STATUS in ('PENDING', 'IN_PROGRESS', 'SYNCED', 'ERROR', 'RETRY_PENDING'))
    )
  ]');

  ensure_sequence('RRL_WH_TASK_SYNC_SQ',
    'create sequence RRL_WH_TASK_SYNC_SQ start with 1 increment by 1 nocache');

  ensure_index('RRL_WH_TASK_SYNC_U1',
    'create unique index RRL_WH_TASK_SYNC_U1 on RRL_WAREHOUSE_TASK_SYNC (SYNC_KEY)');
  ensure_index('RRL_WH_TASK_SYNC_I1',
    'create index RRL_WH_TASK_SYNC_I1 on RRL_WAREHOUSE_TASK_SYNC (TASK_ID)');
  ensure_index('RRL_WH_TASK_SYNC_I2',
    'create index RRL_WH_TASK_SYNC_I2 on RRL_WAREHOUSE_TASK_SYNC (SYNC_STATUS, UPDATED_AT)');
  ensure_index('RRL_WH_TASK_SYNC_I3',
    'create index RRL_WH_TASK_SYNC_I3 on RRL_WAREHOUSE_TASK_SYNC (TASK_SOURCE, SOURCE_DOC_TYPE, SOURCE_DOC_ID)');
end;
/

merge into RRL_SCHEMA_MIGRATIONS d
using (
  select '2026-05-17-028-warehouse-task-domain-sync' migration_id,
         'Warehouse task domain sync queue and retry status' description,
         '028_apply.sql' script_name,
         '028_rollback.sql' rollback_script
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

prompt [migration 2026-05-17-028] done
