prompt [migration 2026-05-17-024] MES raw supply planning and transfer tasks - apply

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
  ensure_table('RRL_MES_RAW_DEMAND', q'[
    create table RRL_MES_RAW_DEMAND (
      DEMAND_ID number not null,
      PRODUCTION_ORDER_ID number not null,
      ORDER_LINE_ID number,
      BOM_ID number,
      BOM_LINE_ID number,
      RAW_ARTICUL varchar2(40) not null,
      REQUIRED_QTY number not null,
      ISSUED_QTY number default 0 not null,
      OPEN_QTY number default 0 not null,
      UNIT_CODE varchar2(20),
      SOFT_RESERVATION_ID number,
      STATUS varchar2(20) default 'OPEN' not null,
      CALCULATED_AT timestamp default systimestamp not null,
      CALCULATED_BY varchar2(100),
      constraint RRL_MES_RAW_DEMAND_PK primary key (DEMAND_ID),
      constraint RRL_MES_RAW_DEMAND_CHK1 check (STATUS in ('OPEN', 'COVERED', 'SHORT', 'CANCELLED')),
      constraint RRL_MES_RAW_DEMAND_CHK2 check (REQUIRED_QTY >= 0 and ISSUED_QTY >= 0 and OPEN_QTY >= 0)
    )
  ]');

  ensure_table('RRL_MES_RAW_SUPPLY_CANDIDATE', q'[
    create table RRL_MES_RAW_SUPPLY_CANDIDATE (
      CANDIDATE_ID number not null,
      DEMAND_ID number not null,
      PRODUCTION_ORDER_ID number not null,
      RAW_ARTICUL varchar2(40) not null,
      UID_PALLET varchar2(128),
      BATCH_ID varchar2(100),
      RAW_BATCH_ID number,
      SSCC varchar2(64),
      FROM_WARE_ID number,
      FROM_CELL varchar2(80),
      PHYSICAL_QTY number default 0 not null,
      HARD_RESERVED_QTY number default 0 not null,
      AVAILABLE_QTY number default 0 not null,
      SUGGESTED_QTY number default 0 not null,
      EXPIRY_DATE date,
      QUALITY_STATUS varchar2(30),
      SORT_ORDER number,
      CREATED_AT timestamp default systimestamp not null,
      constraint RRL_MES_RAW_SUPPLY_CAND_PK primary key (CANDIDATE_ID),
      constraint RRL_MES_RAW_SUPPLY_CAND_CHK1 check (
        PHYSICAL_QTY >= 0 and HARD_RESERVED_QTY >= 0 and AVAILABLE_QTY >= 0 and SUGGESTED_QTY >= 0
      )
    )
  ]');

  ensure_table('RRL_MES_RAW_SHORTAGE', q'[
    create table RRL_MES_RAW_SHORTAGE (
      SHORTAGE_ID number not null,
      PRODUCTION_ORDER_ID number not null,
      DEMAND_ID number,
      RAW_ARTICUL varchar2(40) not null,
      REQUIRED_QTY number default 0 not null,
      ISSUED_QTY number default 0 not null,
      AVAILABLE_QTY number default 0 not null,
      SHORTAGE_QTY number default 0 not null,
      UNIT_CODE varchar2(20),
      STATUS varchar2(20) default 'OPEN' not null,
      CREATED_AT timestamp default systimestamp not null,
      RESOLVED_AT timestamp,
      constraint RRL_MES_RAW_SHORTAGE_PK primary key (SHORTAGE_ID),
      constraint RRL_MES_RAW_SHORTAGE_CHK1 check (STATUS in ('OPEN', 'RESOLVED', 'CANCELLED')),
      constraint RRL_MES_RAW_SHORTAGE_CHK2 check (
        REQUIRED_QTY >= 0 and ISSUED_QTY >= 0 and AVAILABLE_QTY >= 0 and SHORTAGE_QTY >= 0
      )
    )
  ]');

  ensure_table('RRL_MES_RAW_TRANSFER_TASK', q'[
    create table RRL_MES_RAW_TRANSFER_TASK (
      TASK_ID number not null,
      PRODUCTION_ORDER_ID number not null,
      ORDER_LINE_ID number,
      BOM_ID number,
      BOM_LINE_ID number,
      RAW_ARTICUL varchar2(40) not null,
      RAW_BATCH_ID number,
      BATCH_ID varchar2(100),
      UID_PALLET varchar2(128),
      SSCC varchar2(64),
      FROM_WARE_ID number not null,
      FROM_CELL varchar2(80) not null,
      TO_WARE_ID number,
      TO_CELL varchar2(80) not null,
      REQUIRED_QTY number default 0 not null,
      TASK_QTY number default 0 not null,
      FACT_QTY number,
      UNIT_CODE varchar2(20),
      RESERVATION_ID number,
      TASK_STATUS varchar2(20) default 'PLANNED' not null,
      PRIORITY number default 100 not null,
      ASSIGNED_TO varchar2(100),
      CREATED_AT timestamp default systimestamp not null,
      CREATED_BY varchar2(100),
      STARTED_AT timestamp,
      FINISHED_AT timestamp,
      CANCELLED_AT timestamp,
      CANCELLED_BY varchar2(100),
      LAST_ERROR varchar2(2000),
      constraint RRL_MES_RAW_TRANSFER_TASK_PK primary key (TASK_ID),
      constraint RRL_MES_RAW_TRANSFER_TASK_CHK1 check (TASK_STATUS in ('PLANNED', 'IN_PROGRESS', 'DONE', 'CANCELLED', 'ERROR')),
      constraint RRL_MES_RAW_TRANSFER_TASK_CHK2 check (REQUIRED_QTY >= 0 and TASK_QTY >= 0 and nvl(FACT_QTY, 0) >= 0)
    )
  ]');

  ensure_sequence('RRL_MES_RAW_DEMAND_SQ',
    'create sequence RRL_MES_RAW_DEMAND_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_MES_RAW_SUPPLY_CANDIDATE_SQ',
    'create sequence RRL_MES_RAW_SUPPLY_CANDIDATE_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_MES_RAW_SHORTAGE_SQ',
    'create sequence RRL_MES_RAW_SHORTAGE_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_MES_RAW_TRANSFER_TASK_SQ',
    'create sequence RRL_MES_RAW_TRANSFER_TASK_SQ start with 1 increment by 1 nocache');

  ensure_index('RRL_MES_RAW_DEMAND_I1',
    'create index RRL_MES_RAW_DEMAND_I1 on RRL_MES_RAW_DEMAND (PRODUCTION_ORDER_ID, STATUS)');
  ensure_index('RRL_MES_RAW_DEMAND_I2',
    'create index RRL_MES_RAW_DEMAND_I2 on RRL_MES_RAW_DEMAND (RAW_ARTICUL, STATUS)');
  ensure_index('RRL_MES_RAW_SUPPLY_CAND_I1',
    'create index RRL_MES_RAW_SUPPLY_CAND_I1 on RRL_MES_RAW_SUPPLY_CANDIDATE (PRODUCTION_ORDER_ID, DEMAND_ID)');
  ensure_index('RRL_MES_RAW_SUPPLY_CAND_I2',
    'create index RRL_MES_RAW_SUPPLY_CAND_I2 on RRL_MES_RAW_SUPPLY_CANDIDATE (RAW_ARTICUL, FROM_WARE_ID, FROM_CELL)');
  ensure_index('RRL_MES_RAW_SHORTAGE_I1',
    'create index RRL_MES_RAW_SHORTAGE_I1 on RRL_MES_RAW_SHORTAGE (PRODUCTION_ORDER_ID, STATUS)');
  ensure_index('RRL_MES_RAW_TRANSFER_TASK_I1',
    'create index RRL_MES_RAW_TRANSFER_TASK_I1 on RRL_MES_RAW_TRANSFER_TASK (PRODUCTION_ORDER_ID, TASK_STATUS)');
  ensure_index('RRL_MES_RAW_TRANSFER_TASK_I2',
    'create index RRL_MES_RAW_TRANSFER_TASK_I2 on RRL_MES_RAW_TRANSFER_TASK (RESERVATION_ID)');
  ensure_index('RRL_MES_RAW_TRANSFER_TASK_I3',
    'create index RRL_MES_RAW_TRANSFER_TASK_I3 on RRL_MES_RAW_TRANSFER_TASK (UID_PALLET, TASK_STATUS)');
end;
/

insert into RIGHTS (RIGHT1, USER_GROUP, ID, DESCR)
select s.RIGHT1,
       'GLOBAL_ADMIN',
       (select nvl(max(ID), 0) from RIGHTS) + row_number() over (order by s.RIGHT1),
       s.DESCR
  from (
    select 'MES_RAW_SUPPLY_VIEW' RIGHT1, 'View MES raw material demand, supply and transfer tasks' DESCR from dual
    union all select 'MES_RAW_SUPPLY_CALCULATE', 'Calculate MES raw material demand and soft reservations' from dual
    union all select 'MES_RAW_TRANSFER_CREATE', 'Release production order to raw material transfer tasks' from dual
    union all select 'MES_RAW_TRANSFER_CONFIRM', 'Confirm raw material transfer tasks into MES issue movements' from dual
    union all select 'MES_RAW_TRANSFER_CANCEL', 'Cancel raw material transfer tasks and reservations' from dual
  ) s
 where not exists (
   select 1
     from RIGHTS r
    where r.USER_GROUP = 'GLOBAL_ADMIN'
      and upper(r.RIGHT1) = s.RIGHT1
 );

merge into RRL_SCHEMA_MIGRATIONS d
using (
  select '2026-05-17-024-mes-raw-supply' migration_id,
         'MES raw supply demand, candidates, shortages and transfer tasks linked to common reservations' description,
         '024_apply.sql' script_name,
         '024_rollback.sql' rollback_script
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

prompt [migration 2026-05-17-024] done
