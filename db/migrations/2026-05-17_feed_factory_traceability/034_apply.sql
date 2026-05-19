prompt [migration 2026-05-19-034] resource management foundation - apply

declare
  procedure ensure_table(p_table varchar2, p_sql clob) is
    n number;
  begin
    select count(*)
      into n
      from user_tables
     where table_name = upper(p_table);
    if n = 0 then
      execute immediate p_sql;
    end if;
  end;

  procedure ensure_sequence(p_name varchar2, p_sql varchar2) is
    n number;
  begin
    select count(*)
      into n
      from user_sequences
     where sequence_name = upper(p_name);
    if n = 0 then
      execute immediate p_sql;
    end if;
  end;

  procedure ensure_index(p_name varchar2, p_sql varchar2) is
    n number;
  begin
    select count(*)
      into n
      from user_indexes
     where index_name = upper(p_name);
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

  procedure ensure_column(p_table varchar2, p_column varchar2, p_sql varchar2) is
    n number;
  begin
    select count(*)
      into n
      from user_tab_columns
     where table_name = upper(p_table)
       and column_name = upper(p_column);
    if n = 0 then
      execute immediate p_sql;
    end if;
  end;
begin
  ensure_table('RRL_RESOURCE_TYPE', q'[
    create table RRL_RESOURCE_TYPE (
      RESOURCE_TYPE varchar2(40) not null,
      RESOURCE_CLASS varchar2(40) not null,
      RESOURCE_NAME varchar2(120) not null,
      DEFAULT_TASK_TYPES varchar2(500),
      ACTIVE number(1) default 1 not null,
      CREATED_AT timestamp default systimestamp not null,
      UPDATED_AT timestamp,
      constraint RRL_RESOURCE_TYPE_PK primary key (RESOURCE_TYPE),
      constraint RRL_RESOURCE_TYPE_CHK1 check (RESOURCE_CLASS in ('WAREHOUSE_EQUIPMENT', 'PERSON', 'TEAM', 'PRODUCTION_EQUIPMENT')),
      constraint RRL_RESOURCE_TYPE_CHK2 check (ACTIVE in (0, 1))
    )
  ]');

  ensure_table('RRL_RESOURCE_EQUIPMENT', q'[
    create table RRL_RESOURCE_EQUIPMENT (
      EQUIPMENT_ID number not null,
      EQUIPMENT_CODE varchar2(60) not null,
      EQUIPMENT_TYPE varchar2(40) not null,
      EQUIPMENT_NAME varchar2(160),
      WARE_ID number,
      HOME_ZONE_CODE varchar2(60),
      CAPACITY_CLASS varchar2(60),
      SERVICE_STATUS varchar2(20) default 'ACTIVE' not null,
      ACTIVE number(1) default 1 not null,
      CREATED_AT timestamp default systimestamp not null,
      CREATED_BY varchar2(100),
      UPDATED_AT timestamp,
      UPDATED_BY varchar2(100),
      constraint RRL_RESOURCE_EQUIP_PK primary key (EQUIPMENT_ID),
      constraint RRL_RESOURCE_EQUIP_U1 unique (EQUIPMENT_CODE),
      constraint RRL_RESOURCE_EQUIP_FK1 foreign key (EQUIPMENT_TYPE) references RRL_RESOURCE_TYPE (RESOURCE_TYPE),
      constraint RRL_RESOURCE_EQUIP_CHK1 check (SERVICE_STATUS in ('ACTIVE', 'MAINTENANCE', 'CHARGING', 'BLOCKED', 'RETIRED')),
      constraint RRL_RESOURCE_EQUIP_CHK2 check (ACTIVE in (0, 1))
    )
  ]');

  ensure_table('RRL_RESOURCE', q'[
    create table RRL_RESOURCE (
      RESOURCE_ID number not null,
      RESOURCE_CODE varchar2(60) not null,
      RESOURCE_NAME varchar2(160) not null,
      RESOURCE_CLASS varchar2(40) not null,
      RESOURCE_TYPE varchar2(40) not null,
      EQUIPMENT_ID number,
      USER_ID varchar2(100),
      TEAM_CODE varchar2(60),
      WARE_ID number,
      ZONE_CODE varchar2(60),
      STATUS varchar2(20) default 'AVAILABLE' not null,
      ACTIVE number(1) default 1 not null,
      CREATED_AT timestamp default systimestamp not null,
      CREATED_BY varchar2(100),
      UPDATED_AT timestamp,
      UPDATED_BY varchar2(100),
      constraint RRL_RESOURCE_PK primary key (RESOURCE_ID),
      constraint RRL_RESOURCE_U1 unique (RESOURCE_CODE),
      constraint RRL_RESOURCE_FK1 foreign key (RESOURCE_TYPE) references RRL_RESOURCE_TYPE (RESOURCE_TYPE),
      constraint RRL_RESOURCE_FK2 foreign key (EQUIPMENT_ID) references RRL_RESOURCE_EQUIPMENT (EQUIPMENT_ID),
      constraint RRL_RESOURCE_CHK1 check (RESOURCE_CLASS in ('WAREHOUSE_EQUIPMENT', 'PERSON', 'TEAM', 'PRODUCTION_EQUIPMENT')),
      constraint RRL_RESOURCE_CHK2 check (STATUS in ('AVAILABLE', 'IN_WORK', 'IDLE', 'MAINTENANCE', 'UNAVAILABLE', 'CLOSED')),
      constraint RRL_RESOURCE_CHK3 check (ACTIVE in (0, 1))
    )
  ]');

  ensure_table('RRL_RESOURCE_SHIFT', q'[
    create table RRL_RESOURCE_SHIFT (
      SHIFT_ID number not null,
      SHIFT_CODE varchar2(60) not null,
      SHIFT_DATE date not null,
      WARE_ID number,
      SITE_CODE varchar2(60),
      START_AT timestamp not null,
      FINISH_AT timestamp not null,
      STATUS varchar2(20) default 'PLANNED' not null,
      CREATED_AT timestamp default systimestamp not null,
      CREATED_BY varchar2(100),
      UPDATED_AT timestamp,
      UPDATED_BY varchar2(100),
      constraint RRL_RESOURCE_SHIFT_PK primary key (SHIFT_ID),
      constraint RRL_RESOURCE_SHIFT_CHK1 check (STATUS in ('PLANNED', 'OPEN', 'CLOSED', 'CANCELLED')),
      constraint RRL_RESOURCE_SHIFT_CHK2 check (FINISH_AT > START_AT)
    )
  ]');

  ensure_table('RRL_RESOURCE_SESSION', q'[
    create table RRL_RESOURCE_SESSION (
      SESSION_ID number not null,
      SHIFT_ID number not null,
      RESOURCE_ID number not null,
      EQUIPMENT_ID number,
      OPERATOR_USER_ID varchar2(100),
      LOGIN_AT timestamp default systimestamp not null,
      LOGOUT_AT timestamp,
      STATUS varchar2(20) default 'ACTIVE' not null,
      CURRENT_TASK_ID number,
      LAST_HEARTBEAT_AT timestamp,
      TERMINAL_ID varchar2(100),
      ZONE_CODE varchar2(60),
      CREATED_BY varchar2(100),
      CLOSED_BY varchar2(100),
      constraint RRL_RESOURCE_SESSION_PK primary key (SESSION_ID),
      constraint RRL_RESOURCE_SESSION_FK1 foreign key (SHIFT_ID) references RRL_RESOURCE_SHIFT (SHIFT_ID),
      constraint RRL_RESOURCE_SESSION_FK2 foreign key (RESOURCE_ID) references RRL_RESOURCE (RESOURCE_ID),
      constraint RRL_RESOURCE_SESSION_FK3 foreign key (EQUIPMENT_ID) references RRL_RESOURCE_EQUIPMENT (EQUIPMENT_ID),
      constraint RRL_RESOURCE_SESSION_CHK1 check (STATUS in ('ACTIVE', 'PAUSED', 'CLOSED', 'ERROR')),
      constraint RRL_RESOURCE_SESSION_CHK2 check (LOGOUT_AT is null or LOGOUT_AT >= LOGIN_AT)
    )
  ]');

  ensure_table('RRL_RESOURCE_ASSIGNMENT', q'[
    create table RRL_RESOURCE_ASSIGNMENT (
      ASSIGNMENT_ID number not null,
      RESOURCE_ID number not null,
      SESSION_ID number,
      TASK_KIND varchar2(40) not null,
      TASK_ID number,
      SOURCE_DOC_TYPE varchar2(40),
      SOURCE_DOC_ID number,
      PLAN_START_AT timestamp,
      PLAN_FINISH_AT timestamp,
      FACT_START_AT timestamp,
      FACT_FINISH_AT timestamp,
      STATUS varchar2(20) default 'PLANNED' not null,
      PRIORITY number default 100 not null,
      CREATED_AT timestamp default systimestamp not null,
      CREATED_BY varchar2(100),
      UPDATED_AT timestamp,
      UPDATED_BY varchar2(100),
      constraint RRL_RESOURCE_ASSIGN_PK primary key (ASSIGNMENT_ID),
      constraint RRL_RESOURCE_ASSIGN_FK1 foreign key (RESOURCE_ID) references RRL_RESOURCE (RESOURCE_ID),
      constraint RRL_RESOURCE_ASSIGN_FK2 foreign key (SESSION_ID) references RRL_RESOURCE_SESSION (SESSION_ID),
      constraint RRL_RESOURCE_ASSIGN_CHK1 check (STATUS in ('PLANNED', 'DISPATCHED', 'ASSIGNED', 'IN_PROGRESS', 'DONE', 'CANCELLED', 'ERROR')),
      constraint RRL_RESOURCE_ASSIGN_CHK2 check (PLAN_FINISH_AT is null or PLAN_START_AT is null or PLAN_FINISH_AT >= PLAN_START_AT),
      constraint RRL_RESOURCE_ASSIGN_CHK3 check (FACT_FINISH_AT is null or FACT_START_AT is null or FACT_FINISH_AT >= FACT_START_AT)
    )
  ]');

  ensure_table('RRL_RESOURCE_FACT_EVENT', q'[
    create table RRL_RESOURCE_FACT_EVENT (
      EVENT_ID number not null,
      ASSIGNMENT_ID number,
      TASK_ID number,
      SESSION_ID number,
      RESOURCE_ID number,
      EVENT_TYPE varchar2(40) not null,
      EVENT_AT timestamp default systimestamp not null,
      EVENT_BY varchar2(100),
      PAYLOAD_JSON clob,
      constraint RRL_RESOURCE_FACT_EVENT_PK primary key (EVENT_ID),
      constraint RRL_RESOURCE_FACT_EVENT_FK1 foreign key (ASSIGNMENT_ID) references RRL_RESOURCE_ASSIGNMENT (ASSIGNMENT_ID),
      constraint RRL_RESOURCE_FACT_EVENT_FK2 foreign key (SESSION_ID) references RRL_RESOURCE_SESSION (SESSION_ID),
      constraint RRL_RESOURCE_FACT_EVENT_FK3 foreign key (RESOURCE_ID) references RRL_RESOURCE (RESOURCE_ID),
      constraint RRL_RESOURCE_FACT_EVENT_CHK1 check (EVENT_TYPE in ('LOGIN', 'HEARTBEAT', 'PAUSE', 'RESUME', 'LOGOUT', 'ASSIGNED', 'STARTED', 'COMPLETED', 'CANCELLED', 'ERROR', 'REPLAN'))
    )
  ]');

  ensure_sequence('RRL_RESOURCE_EQUIPMENT_SQ', 'create sequence RRL_RESOURCE_EQUIPMENT_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_RESOURCE_SQ', 'create sequence RRL_RESOURCE_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_RESOURCE_SHIFT_SQ', 'create sequence RRL_RESOURCE_SHIFT_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_RESOURCE_SESSION_SQ', 'create sequence RRL_RESOURCE_SESSION_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_RESOURCE_ASSIGN_SQ', 'create sequence RRL_RESOURCE_ASSIGN_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_RESOURCE_FACT_EVENT_SQ', 'create sequence RRL_RESOURCE_FACT_EVENT_SQ start with 1 increment by 1 nocache');

  ensure_index('RRL_RESOURCE_I1', 'create index RRL_RESOURCE_I1 on RRL_RESOURCE (RESOURCE_TYPE, STATUS, ACTIVE)');
  ensure_index('RRL_RESOURCE_I2', 'create index RRL_RESOURCE_I2 on RRL_RESOURCE (WARE_ID, ZONE_CODE, STATUS)');
  ensure_index('RRL_RESOURCE_EQUIP_I1', 'create index RRL_RESOURCE_EQUIP_I1 on RRL_RESOURCE_EQUIPMENT (EQUIPMENT_TYPE, SERVICE_STATUS, ACTIVE)');
  ensure_index('RRL_RESOURCE_SHIFT_I1', 'create index RRL_RESOURCE_SHIFT_I1 on RRL_RESOURCE_SHIFT (SHIFT_DATE, WARE_ID, STATUS)');
  ensure_index('RRL_RESOURCE_SESSION_I1', 'create index RRL_RESOURCE_SESSION_I1 on RRL_RESOURCE_SESSION (SHIFT_ID, STATUS)');
  ensure_index('RRL_RESOURCE_SESSION_U1', q'[create unique index RRL_RESOURCE_SESSION_U1 on RRL_RESOURCE_SESSION (case when STATUS in ('ACTIVE', 'PAUSED') then RESOURCE_ID end)]');
  ensure_index('RRL_RESOURCE_SESSION_U2', q'[create unique index RRL_RESOURCE_SESSION_U2 on RRL_RESOURCE_SESSION (case when STATUS in ('ACTIVE', 'PAUSED') then EQUIPMENT_ID end)]');
  ensure_index('RRL_RESOURCE_SESSION_U3', q'[create unique index RRL_RESOURCE_SESSION_U3 on RRL_RESOURCE_SESSION (case when STATUS in ('ACTIVE', 'PAUSED') then upper(OPERATOR_USER_ID) end)]');
  ensure_index('RRL_RESOURCE_ASSIGN_I1', 'create index RRL_RESOURCE_ASSIGN_I1 on RRL_RESOURCE_ASSIGNMENT (RESOURCE_ID, STATUS, PLAN_START_AT)');
  ensure_index('RRL_RESOURCE_ASSIGN_I2', 'create index RRL_RESOURCE_ASSIGN_I2 on RRL_RESOURCE_ASSIGNMENT (TASK_KIND, TASK_ID)');
  ensure_index('RRL_RESOURCE_FACT_EVENT_I1', 'create index RRL_RESOURCE_FACT_EVENT_I1 on RRL_RESOURCE_FACT_EVENT (RESOURCE_ID, EVENT_AT)');

  ensure_column('RRL_WAREHOUSE_TASK', 'RESOURCE_ID',
    'alter table RRL_WAREHOUSE_TASK add RESOURCE_ID number');
  ensure_column('RRL_WAREHOUSE_TASK', 'RESOURCE_SESSION_ID',
    'alter table RRL_WAREHOUSE_TASK add RESOURCE_SESSION_ID number');
  ensure_column('RRL_WAREHOUSE_TASK', 'EQUIPMENT_ID',
    'alter table RRL_WAREHOUSE_TASK add EQUIPMENT_ID number');
  ensure_column('RRL_WAREHOUSE_TASK', 'PLANNED_START_AT',
    'alter table RRL_WAREHOUSE_TASK add PLANNED_START_AT timestamp');
  ensure_column('RRL_WAREHOUSE_TASK', 'PLANNED_FINISH_AT',
    'alter table RRL_WAREHOUSE_TASK add PLANNED_FINISH_AT timestamp');
  ensure_column('RRL_WAREHOUSE_TASK', 'DISPATCH_PRIORITY',
    'alter table RRL_WAREHOUSE_TASK add DISPATCH_PRIORITY number');

  ensure_index('RRL_WAREHOUSE_TASK_I9',
    'create index RRL_WAREHOUSE_TASK_I9 on RRL_WAREHOUSE_TASK (RESOURCE_ID, STATUS, PLANNED_START_AT)');
  ensure_index('RRL_WAREHOUSE_TASK_I10',
    'create index RRL_WAREHOUSE_TASK_I10 on RRL_WAREHOUSE_TASK (RESOURCE_SESSION_ID, STATUS)');
end;
/

merge into RRL_RESOURCE_TYPE d
using (
  select 'REACHTRUCK' resource_type, 'WAREHOUSE_EQUIPMENT' resource_class, 'Ричтрак' resource_name, 'REPLENISHMENT,PICKING_MOVE,FG_TO_STORAGE' default_task_types from dual
  union all select 'KIKA', 'WAREHOUSE_EQUIPMENT', 'KIKA', 'RAW_TO_PRODUCTION,OTHER' from dual
  union all select 'FORKLIFT', 'WAREHOUSE_EQUIPMENT', 'Погрузчик', 'PICKING_MOVE,FG_TO_STORAGE,RAW_TO_PRODUCTION' from dual
  union all select 'TROLLEY', 'WAREHOUSE_EQUIPMENT', 'Тележка', 'CASE_PICK' from dual
  union all select 'CASE_PICKER', 'PERSON', 'Комплектовщик', 'CASE_PICK' from dual
  union all select 'LOADING_TEAM', 'TEAM', 'Бригада погрузки', 'LOADING,PICKING_MOVE' from dual
  union all select 'COOKING', 'PRODUCTION_EQUIPMENT', 'Варка', 'MES_COOKING' from dual
  union all select 'PACKING', 'PRODUCTION_EQUIPMENT', 'Фасовка', 'MES_PACKING' from dual
) s
on (d.RESOURCE_TYPE = s.RESOURCE_TYPE)
when matched then update set
  d.RESOURCE_CLASS = s.RESOURCE_CLASS,
  d.RESOURCE_NAME = s.RESOURCE_NAME,
  d.DEFAULT_TASK_TYPES = s.DEFAULT_TASK_TYPES,
  d.ACTIVE = 1,
  d.UPDATED_AT = systimestamp
when not matched then insert (
  RESOURCE_TYPE, RESOURCE_CLASS, RESOURCE_NAME, DEFAULT_TASK_TYPES, ACTIVE, CREATED_AT
) values (
  s.RESOURCE_TYPE, s.RESOURCE_CLASS, s.RESOURCE_NAME, s.DEFAULT_TASK_TYPES, 1, systimestamp
);

insert into RIGHTS (RIGHT1, USER_GROUP, ID, DESCR)
select s.RIGHT1,
       'GLOBAL_ADMIN',
       (select nvl(max(ID), 0) from RIGHTS) + row_number() over (order by s.RIGHT1),
       s.DESCR
  from (
    select 'RESOURCE_MANAGEMENT_VIEW' RIGHT1, 'View warehouse and production resources' DESCR from dual
    union all select 'RESOURCE_MANAGEMENT_EDIT', 'Edit warehouse and production resources' from dual
    union all select 'RESOURCE_SHIFT_VIEW', 'View resource shifts' from dual
    union all select 'RESOURCE_SHIFT_EDIT', 'Edit resource shifts' from dual
    union all select 'RESOURCE_SESSION_VIEW', 'View active resource sessions' from dual
    union all select 'RESOURCE_SESSION_MANAGE', 'Manage resource sessions' from dual
    union all select 'RESOURCE_GANTT_VIEW', 'View resource plan-fact Gantt' from dual
    union all select 'RESOURCE_GANTT_REPLAN', 'Replan resource assignments' from dual
    union all select 'RESOURCE_DISPATCH_MANAGE', 'Manage resource dispatch' from dual
    union all select 'WAREHOUSE_TASK_FORCE_ASSIGN', 'Force assign warehouse task to resource' from dual
  ) s
 where not exists (
   select 1
     from RIGHTS r
    where r.USER_GROUP = 'GLOBAL_ADMIN'
      and upper(r.RIGHT1) = s.RIGHT1
 );

merge into RRL_SCHEMA_MIGRATIONS d
using (
  select '2026-05-19-034-resource-management-foundation' migration_id,
         'Resource-management foundation for warehouse equipment, pickers, production equipment, shifts, sessions, assignments, and plan-fact Gantt' description,
         '034_apply.sql' script_name,
         '034_rollback.sql' rollback_script
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

prompt [migration 2026-05-19-034] done
