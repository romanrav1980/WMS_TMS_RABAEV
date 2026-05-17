prompt [migration 2026-05-17-023] Common stock reservation model - apply

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
  ensure_table('RRL_STOCK_RESERVATION', q'[
    create table RRL_STOCK_RESERVATION (
      RESERVATION_ID number not null,
      RESERVATION_KIND varchar2(10) not null,
      RESERVATION_SCOPE varchar2(20) default 'QTY' not null,
      RESERVATION_DOMAIN varchar2(30) not null,
      SOURCE_DOC_TYPE varchar2(40) not null,
      SOURCE_DOC_ID number not null,
      SOURCE_LINE_ID number,
      TASK_ID number,
      CUSTOMER_ID number,
      CUSTOMER_ORDER_ID number,
      PRODUCTION_ORDER_ID number,
      PICK_PLAN_ID number,
      PICK_PLAN_LINE_ID number,
      PICK_WAVE_ID number,
      PICK_WAVE_LINE_ID number,
      ARTICUL varchar2(40) not null,
      QTY number not null,
      UNIT_CODE varchar2(20),
      WARE_ID number,
      CELL varchar2(80),
      BATCH_ID varchar2(100),
      PROD_BATCH_ID number,
      UID_PALLET varchar2(128),
      SSCC varchar2(64),
      STATUS varchar2(20) default 'ACTIVE' not null,
      PRIORITY number default 100 not null,
      LOCK_OWNER varchar2(100),
      LOCKED_AT timestamp,
      CREATED_AT timestamp default systimestamp not null,
      CREATED_BY varchar2(100),
      RELEASED_AT timestamp,
      RELEASED_BY varchar2(100),
      RELEASE_REASON varchar2(1000),
      CONSUMED_AT timestamp,
      CONSUMED_BY varchar2(100),
      LAST_ERROR varchar2(2000),
      constraint RRL_STOCK_RESERVATION_PK primary key (RESERVATION_ID),
      constraint RRL_STOCK_RES_KIND_CHK check (RESERVATION_KIND in ('SOFT', 'HARD')),
      constraint RRL_STOCK_RES_SCOPE_CHK check (RESERVATION_SCOPE in ('PALLET', 'QTY')),
      constraint RRL_STOCK_RES_STATUS_CHK check (STATUS in ('ACTIVE', 'ALLOCATED', 'PICKING', 'CONSUMED', 'RELEASED', 'CANCELLED', 'EXPIRED')),
      constraint RRL_STOCK_RES_DOMAIN_CHK check (RESERVATION_DOMAIN in ('MES_RAW', 'PICKING', 'WAVE', 'SHIPMENT')),
      constraint RRL_STOCK_RES_QTY_CHK check (QTY >= 0),
      constraint RRL_STOCK_RES_SOFT_CHK check (
        RESERVATION_KIND <> 'SOFT'
        or (WARE_ID is null and CELL is null and BATCH_ID is null and PROD_BATCH_ID is null and UID_PALLET is null and SSCC is null)
      ),
      constraint RRL_STOCK_RES_HARD_CHK check (
        RESERVATION_KIND <> 'HARD'
        or (WARE_ID is not null and CELL is not null and (UID_PALLET is not null or BATCH_ID is not null or PROD_BATCH_ID is not null))
      )
    )
  ]');

  ensure_sequence('RRL_STOCK_RESERVATION_SQ',
    'create sequence RRL_STOCK_RESERVATION_SQ start with 1 increment by 1 nocache');

  ensure_index('RRL_STOCK_RESERVATION_I1',
    'create index RRL_STOCK_RESERVATION_I1 on RRL_STOCK_RESERVATION (RESERVATION_DOMAIN, SOURCE_DOC_TYPE, SOURCE_DOC_ID, STATUS)');
  ensure_index('RRL_STOCK_RESERVATION_I2',
    'create index RRL_STOCK_RESERVATION_I2 on RRL_STOCK_RESERVATION (ARTICUL, STATUS, RESERVATION_KIND)');
  ensure_index('RRL_STOCK_RESERVATION_I3',
    'create index RRL_STOCK_RESERVATION_I3 on RRL_STOCK_RESERVATION (WARE_ID, CELL, ARTICUL, STATUS)');
  ensure_index('RRL_STOCK_RESERVATION_I4',
    'create index RRL_STOCK_RESERVATION_I4 on RRL_STOCK_RESERVATION (UID_PALLET, STATUS, RESERVATION_KIND)');
  ensure_index('RRL_STOCK_RESERVATION_I5',
    'create index RRL_STOCK_RESERVATION_I5 on RRL_STOCK_RESERVATION (BATCH_ID, ARTICUL, STATUS)');
  ensure_index('RRL_STOCK_RESERVATION_I6',
    'create index RRL_STOCK_RESERVATION_I6 on RRL_STOCK_RESERVATION (PRODUCTION_ORDER_ID, STATUS)');
  ensure_index('RRL_STOCK_RESERVATION_I7',
    'create index RRL_STOCK_RESERVATION_I7 on RRL_STOCK_RESERVATION (PICK_PLAN_ID, STATUS)');
  ensure_index('RRL_STOCK_RESERVATION_I8',
    'create index RRL_STOCK_RESERVATION_I8 on RRL_STOCK_RESERVATION (PICK_WAVE_ID, STATUS)');
  ensure_index('RRL_STOCK_RESERVATION_U1',
    q'[create unique index RRL_STOCK_RESERVATION_U1 on RRL_STOCK_RESERVATION (
      case
        when RESERVATION_KIND = 'HARD'
         and RESERVATION_SCOPE = 'PALLET'
         and STATUS in ('ACTIVE', 'ALLOCATED', 'PICKING')
         and UID_PALLET is not null
        then UID_PALLET
      end
    )]');
end;
/

insert into RIGHTS (RIGHT1, USER_GROUP, ID, DESCR)
select s.RIGHT1,
       'GLOBAL_ADMIN',
       (select nvl(max(ID), 0) from RIGHTS) + row_number() over (order by s.RIGHT1),
       s.DESCR
  from (
    select 'STOCK_RESERVATION_VIEW' RIGHT1, 'View common soft/hard stock reservations' DESCR from dual
    union all
    select 'STOCK_RESERVATION_EDIT' RIGHT1, 'Manage common soft/hard stock reservations' DESCR from dual
  ) s
 where not exists (
   select 1
     from RIGHTS r
    where r.USER_GROUP = 'GLOBAL_ADMIN'
      and upper(r.RIGHT1) = s.RIGHT1
 );

merge into RRL_SCHEMA_MIGRATIONS d
using (
  select '2026-05-17-023-common-stock-reservation' migration_id,
         'Common table for SOFT demand and HARD WMS stock reservations' description,
         '023_apply.sql' script_name,
         '023_rollback.sql' rollback_script
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

prompt [migration 2026-05-17-023] done
