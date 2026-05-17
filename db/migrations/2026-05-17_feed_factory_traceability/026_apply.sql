prompt [migration 2026-05-17-026] warehouse reachtruck tasks - apply

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
  ensure_table('RRL_WAREHOUSE_TASK', q'[
    create table RRL_WAREHOUSE_TASK (
      TASK_ID number not null,
      TASK_TYPE varchar2(40) not null,
      TASK_SOURCE varchar2(40) not null,
      SOURCE_TASK_ID number,
      SOURCE_MOVEMENT_ID number,
      SOURCE_DOC_TYPE varchar2(40),
      SOURCE_DOC_ID number,
      PRODUCTION_ORDER_ID number,
      PROD_BATCH_ID number,
      RAW_ARTICUL varchar2(40),
      TARGET_ARTICUL varchar2(40),
      UID_PALLET varchar2(200),
      SSCC varchar2(64),
      FROM_WARE_ID number,
      FROM_CELL varchar2(80),
      TO_WARE_ID number,
      TO_CELL varchar2(80) not null,
      QTY number default 0 not null,
      UNIT_CODE varchar2(20),
      PRIORITY number default 100 not null,
      STATUS varchar2(20) default 'PLANNED' not null,
      ASSIGNED_TO varchar2(100),
      CREATED_AT timestamp default systimestamp not null,
      CREATED_BY varchar2(100),
      STARTED_AT timestamp,
      FINISHED_AT timestamp,
      CANCELLED_AT timestamp,
      CANCELLED_BY varchar2(100),
      LAST_ERROR varchar2(2000),
      constraint RRL_WAREHOUSE_TASK_PK primary key (TASK_ID),
      constraint RRL_WAREHOUSE_TASK_CHK1 check (TASK_TYPE in ('RAW_TO_PRODUCTION', 'FG_TO_STORAGE', 'REPLENISHMENT', 'PICKING_MOVE', 'OTHER')),
      constraint RRL_WAREHOUSE_TASK_CHK2 check (TASK_SOURCE in ('MES_RAW_SUPPLY', 'MES_COMPLETION', 'PICKING', 'WAVE', 'MANUAL')),
      constraint RRL_WAREHOUSE_TASK_CHK3 check (STATUS in ('PLANNED', 'ASSIGNED', 'IN_PROGRESS', 'DONE', 'CANCELLED', 'ERROR')),
      constraint RRL_WAREHOUSE_TASK_CHK4 check (QTY >= 0)
    )
  ]');

  ensure_sequence('RRL_WAREHOUSE_TASK_SQ',
    'create sequence RRL_WAREHOUSE_TASK_SQ start with 1 increment by 1 nocache');

  ensure_index('RRL_WAREHOUSE_TASK_I1',
    'create index RRL_WAREHOUSE_TASK_I1 on RRL_WAREHOUSE_TASK (STATUS, PRIORITY, CREATED_AT)');
  ensure_index('RRL_WAREHOUSE_TASK_I2',
    'create index RRL_WAREHOUSE_TASK_I2 on RRL_WAREHOUSE_TASK (TASK_TYPE, STATUS)');
  ensure_index('RRL_WAREHOUSE_TASK_I3',
    'create index RRL_WAREHOUSE_TASK_I3 on RRL_WAREHOUSE_TASK (PRODUCTION_ORDER_ID, STATUS)');
  ensure_index('RRL_WAREHOUSE_TASK_I4',
    'create index RRL_WAREHOUSE_TASK_I4 on RRL_WAREHOUSE_TASK (UID_PALLET, STATUS)');
  ensure_index('RRL_WAREHOUSE_TASK_U1',
    'create unique index RRL_WAREHOUSE_TASK_U1 on RRL_WAREHOUSE_TASK (TASK_SOURCE, nvl(SOURCE_TASK_ID, -1), nvl(SOURCE_MOVEMENT_ID, -1), TASK_TYPE)');
end;
/

insert into RIGHTS (RIGHT1, USER_GROUP, ID, DESCR)
select s.RIGHT1,
       'GLOBAL_ADMIN',
       (select nvl(max(ID), 0) from RIGHTS) + row_number() over (order by s.RIGHT1),
       s.DESCR
  from (
    select 'WAREHOUSE_TASK_VIEW' RIGHT1, 'View warehouse reachtruck tasks' DESCR from dual
    union all select 'WAREHOUSE_TASK_EXECUTE', 'Assign, start, complete and cancel warehouse reachtruck tasks' from dual
  ) s
 where not exists (
   select 1
     from RIGHTS r
    where r.USER_GROUP = 'GLOBAL_ADMIN'
      and upper(r.RIGHT1) = s.RIGHT1
 );

merge into RRL_SCHEMA_MIGRATIONS d
using (
  select '2026-05-17-026-warehouse-tasks' migration_id,
         'Common warehouse reachtruck tasks for MES raw supply and finished goods storage' description,
         '026_apply.sql' script_name,
         '026_rollback.sql' rollback_script
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

prompt [migration 2026-05-17-026] done
