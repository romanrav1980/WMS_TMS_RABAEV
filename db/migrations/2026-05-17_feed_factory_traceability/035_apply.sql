prompt [migration 2026-05-19-035] case-pick TSD runtime foundation - apply

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
begin
  ensure_table('RRL_PALLET_TYPE', q'[
    create table RRL_PALLET_TYPE (
      PALLET_TYPE_ID number not null,
      PALLET_TYPE_CODE varchar2(50) not null,
      PALLET_TYPE_NAME varchar2(160) not null,
      LOAD_UNIT_CLASS varchar2(20) default 'PALLET' not null,
      DEFAULT_VOLUME_M3 number,
      DEFAULT_WEIGHT_KG number,
      LENGTH_MM number,
      WIDTH_MM number,
      HEIGHT_MM number,
      DEFAULT_MAX_CLIENT_PALLETS number default 1 not null,
      ACTIVE number(1) default 1 not null,
      CREATED_AT timestamp default systimestamp not null,
      CREATED_BY varchar2(100),
      UPDATED_AT timestamp,
      UPDATED_BY varchar2(100),
      constraint RRL_PALLET_TYPE_PK primary key (PALLET_TYPE_ID),
      constraint RRL_PALLET_TYPE_U1 unique (PALLET_TYPE_CODE),
      constraint RRL_PALLET_TYPE_CHK1 check (LOAD_UNIT_CLASS in ('PALLET', 'TROLLEY', 'CONTAINER')),
      constraint RRL_PALLET_TYPE_CHK2 check (ACTIVE in (0, 1))
    )
  ]');

  ensure_table('RRL_CUSTOMER_PALLET_TYPE_RULE', q'[
    create table RRL_CUSTOMER_PALLET_TYPE_RULE (
      CUSTOMER_PALLET_TYPE_RULE_ID number not null,
      CUSTOMER_ID number not null,
      CUSTOMER_ADDRESS_ID number,
      CUSTOMER_STORE_MAP_ID number,
      PALLET_TYPE_ID number not null,
      IS_DEFAULT number(1) default 0 not null,
      ACTIVE number(1) default 1 not null,
      VALID_FROM date default trunc(sysdate) not null,
      VALID_TO date,
      CREATED_AT timestamp default systimestamp not null,
      CREATED_BY varchar2(100),
      UPDATED_AT timestamp,
      UPDATED_BY varchar2(100),
      constraint RRL_CUST_PALLET_RULE_PK primary key (CUSTOMER_PALLET_TYPE_RULE_ID),
      constraint RRL_CUST_PALLET_RULE_FK1 foreign key (CUSTOMER_ID) references RRL_CUSTOMER (CUSTOMER_ID),
      constraint RRL_CUST_PALLET_RULE_FK2 foreign key (CUSTOMER_ADDRESS_ID) references RRL_CUSTOMER_ADDRESS (CUSTOMER_ADDRESS_ID),
      constraint RRL_CUST_PALLET_RULE_FK3 foreign key (CUSTOMER_STORE_MAP_ID) references RRL_CUSTOMER_STORE_MAP (CUSTOMER_STORE_MAP_ID),
      constraint RRL_CUST_PALLET_RULE_FK4 foreign key (PALLET_TYPE_ID) references RRL_PALLET_TYPE (PALLET_TYPE_ID),
      constraint RRL_CUST_PALLET_RULE_CHK1 check (IS_DEFAULT in (0, 1)),
      constraint RRL_CUST_PALLET_RULE_CHK2 check (ACTIVE in (0, 1)),
      constraint RRL_CUST_PALLET_RULE_CHK3 check (VALID_TO is null or VALID_TO >= VALID_FROM)
    )
  ]');

  ensure_table('RRL_CASE_PICK_SETTING', q'[
    create table RRL_CASE_PICK_SETTING (
      WARE_ID number not null,
      SCAN_CELL_REQUIRED number(1) default 1 not null,
      SCAN_PRODUCT_REQUIRED number(1) default 1 not null,
      SCAN_BOX_REQUIRED number(1) default 0 not null,
      SCAN_CONTAINER_REQUIRED number(1) default 1 not null,
      QTY_CONFIRM_MODE varchar2(30) default 'ALWAYS' not null,
      SHORTAGE_BEHAVIOR varchar2(40) default 'WAIT_REPLENISHMENT' not null,
      ALLOW_MANUAL_ORDER_CHANGE number(1) default 0 not null,
      PALLET_COMPLETE_STAGE varchar2(40) default 'AFTER_CONTROL' not null,
      CONTROL_MODE varchar2(30) default 'WEIGHT_OR_AUDIT' not null,
      LABEL_PRINT_STAGE varchar2(30) default 'AFTER_PICKING' not null,
      AUTO_INVENTORY_ON_SHORT number(1) default 1 not null,
      INVENTORY_ASSIGNMENT_MODE varchar2(40) default 'RESOURCE_ROLE' not null,
      INVENTORY_RESOURCE_TYPE varchar2(40) default 'INVENTORY' not null,
      OFFLINE_ENABLED number(1) default 1 not null,
      OFFLINE_SCOPE varchar2(40) default 'ISSUED_TASKS_ONLY' not null,
      ACTIVE number(1) default 1 not null,
      CREATED_AT timestamp default systimestamp not null,
      CREATED_BY varchar2(100),
      UPDATED_AT timestamp,
      UPDATED_BY varchar2(100),
      constraint RRL_CASE_PICK_SETTING_PK primary key (WARE_ID),
      constraint RRL_CASE_PICK_SETTING_CHK1 check (QTY_CONFIRM_MODE in ('ALWAYS', 'ONLY_DEVIATION', 'SCAN_INCREMENT')),
      constraint RRL_CASE_PICK_SETTING_CHK2 check (SHORTAGE_BEHAVIOR in ('WAIT_REPLENISHMENT', 'SKIP_AND_RETURN', 'PARTIAL_PICK', 'CLOSE_SHORT', 'CALL_REACHTRUCK')),
      constraint RRL_CASE_PICK_SETTING_CHK3 check (PALLET_COMPLETE_STAGE in ('LINES_PICKED', 'PICKER_CLOSED', 'CONSOLIDATION', 'AFTER_CONTROL')),
      constraint RRL_CASE_PICK_SETTING_CHK4 check (CONTROL_MODE in ('NONE', 'AUDIT', 'WEIGHT', 'WEIGHT_OR_AUDIT')),
      constraint RRL_CASE_PICK_SETTING_CHK5 check (LABEL_PRINT_STAGE in ('AFTER_PICKING', 'AFTER_CONTROL', 'MANUAL')),
      constraint RRL_CASE_PICK_SETTING_CHK6 check (SCAN_CELL_REQUIRED in (0, 1) and SCAN_PRODUCT_REQUIRED in (0, 1) and SCAN_BOX_REQUIRED in (0, 1) and SCAN_CONTAINER_REQUIRED in (0, 1) and ALLOW_MANUAL_ORDER_CHANGE in (0, 1) and AUTO_INVENTORY_ON_SHORT in (0, 1) and OFFLINE_ENABLED in (0, 1) and ACTIVE in (0, 1))
    )
  ]');

  ensure_table('RRL_CASE_PICK_TASK', q'[
    create table RRL_CASE_PICK_TASK (
      CASE_PICK_TASK_ID number not null,
      PICK_WAVE_ID number not null,
      PICK_PLAN_ID number,
      CUSTOMER_ORDER_ID number not null,
      CUSTOMER_ID number,
      CUSTOMER_ADDRESS_ID number,
      CUSTOMER_STORE_MAP_ID number,
      SSCC varchar2(64) not null,
      PALLET_TYPE_ID number,
      PALLET_NO number default 1 not null,
      STATUS varchar2(30) default 'NEW' not null,
      ASSIGNED_RESOURCE_ID number,
      RESOURCE_SESSION_ID number,
      EQUIPMENT_ID number,
      ASSIGNED_TO varchar2(100),
      WARE_ID number,
      ZONE_CODE varchar2(60),
      TOTAL_LINES number default 0 not null,
      PICKED_LINES number default 0 not null,
      PLANNED_QTY number default 0 not null,
      PICKED_QTY number default 0 not null,
      OFFLINE_STATE varchar2(30),
      CREATED_AT timestamp default systimestamp not null,
      CREATED_BY varchar2(100),
      STARTED_AT timestamp,
      CLOSED_AT timestamp,
      DONE_AT timestamp,
      UPDATED_AT timestamp,
      UPDATED_BY varchar2(100),
      TRANSFERRED_AT timestamp,
      TRANSFERRED_BY varchar2(100),
      TRANSFER_REASON varchar2(1000),
      constraint RRL_CASE_PICK_TASK_PK primary key (CASE_PICK_TASK_ID),
      constraint RRL_CASE_PICK_TASK_U1 unique (PICK_WAVE_ID, CUSTOMER_ORDER_ID, PALLET_NO),
      constraint RRL_CASE_PICK_TASK_U2 unique (SSCC),
      constraint RRL_CASE_PICK_TASK_FK1 foreign key (PICK_WAVE_ID) references RRL_PICK_WAVE (PICK_WAVE_ID),
      constraint RRL_CASE_PICK_TASK_FK2 foreign key (CUSTOMER_ORDER_ID) references RRL_CUSTOMER_ORDER (CUSTOMER_ORDER_ID),
      constraint RRL_CASE_PICK_TASK_FK3 foreign key (PALLET_TYPE_ID) references RRL_PALLET_TYPE (PALLET_TYPE_ID),
      constraint RRL_CASE_PICK_TASK_CHK1 check (STATUS in ('NEW', 'ASSIGNED', 'IN_PROGRESS', 'WAIT_REPLENISHMENT', 'PARTIAL', 'PICKED', 'WAIT_CONTROL', 'CONTROL_IN_PROGRESS', 'CONTROLLED', 'READY_TO_SHIP', 'SYNC_CONFLICT', 'CANCELLED', 'FAILED')),
      constraint RRL_CASE_PICK_TASK_CHK2 check (OFFLINE_STATE is null or OFFLINE_STATE in ('ONLINE', 'LOCAL_PICKED', 'SYNC_CONFLICT'))
    )
  ]');

  ensure_table('RRL_CASE_PICK_LINE', q'[
    create table RRL_CASE_PICK_LINE (
      CASE_PICK_LINE_ID number not null,
      CASE_PICK_TASK_ID number not null,
      PICK_WAVE_ID number not null,
      PICK_WAVE_TASK_ID number,
      PICK_TASK_ID number,
      PICK_PLAN_LINE_ID number,
      CUSTOMER_ORDER_ID number not null,
      CUSTOMER_ID number,
      ARTICUL varchar2(40) not null,
      PRODUCT_NAME varchar2(255),
      CELL_CODE varchar2(80),
      PICK_FACE_ID number,
      PICK_ROUTE_CELL_ID number,
      PICK_SEQUENCE number,
      PLANNED_QTY number default 0 not null,
      PICKED_QTY number default 0 not null,
      STATUS varchar2(30) default 'NEW' not null,
      REQUIRED_SCAN_MODE varchar2(200),
      LAST_OFFLINE_EVENT_ID varchar2(100),
      CREATED_AT timestamp default systimestamp not null,
      CREATED_BY varchar2(100),
      STARTED_AT timestamp,
      DONE_AT timestamp,
      UPDATED_AT timestamp,
      UPDATED_BY varchar2(100),
      constraint RRL_CASE_PICK_LINE_PK primary key (CASE_PICK_LINE_ID),
      constraint RRL_CASE_PICK_LINE_U1 unique (CASE_PICK_TASK_ID, PICK_WAVE_TASK_ID),
      constraint RRL_CASE_PICK_LINE_FK1 foreign key (CASE_PICK_TASK_ID) references RRL_CASE_PICK_TASK (CASE_PICK_TASK_ID),
      constraint RRL_CASE_PICK_LINE_FK2 foreign key (PICK_WAVE_ID) references RRL_PICK_WAVE (PICK_WAVE_ID),
      constraint RRL_CASE_PICK_LINE_CHK1 check (STATUS in ('NEW', 'ACTIVE', 'SKIPPED', 'WAIT_REPLENISHMENT', 'PARTIAL', 'PICKED', 'SHORT_PICKED', 'SYNC_CONFLICT', 'CANCELLED', 'FAILED'))
    )
  ]');

  ensure_table('RRL_CASE_PICK_SHORT', q'[
    create table RRL_CASE_PICK_SHORT (
      CASE_PICK_SHORT_ID number not null,
      PICK_WAVE_ID number,
      CASE_PICK_TASK_ID number,
      CASE_PICK_LINE_ID number,
      PICK_WAVE_TASK_ID number,
      CUSTOMER_ORDER_ID number,
      CUSTOMER_ID number,
      ARTICUL varchar2(40) not null,
      CELL_CODE varchar2(80),
      PLANNED_QTY number default 0 not null,
      PICKED_QTY number default 0 not null,
      SHORT_QTY number default 0 not null,
      REASON_CODE varchar2(80) default 'SHIFT_LEAD_CONFIRMATION_REQUIRED' not null,
      REASON_TEXT varchar2(1000),
      STATUS varchar2(30) default 'PENDING_APPROVAL' not null,
      INVENTORY_TASK_ID number,
      OFFLINE_EVENT_ID varchar2(100),
      CREATED_AT timestamp default systimestamp not null,
      CREATED_BY varchar2(100),
      APPROVED_AT timestamp,
      APPROVED_BY varchar2(100),
      CANCELLED_AT timestamp,
      CANCELLED_BY varchar2(100),
      PAYLOAD_JSON clob,
      constraint RRL_CASE_PICK_SHORT_PK primary key (CASE_PICK_SHORT_ID),
      constraint RRL_CASE_PICK_SHORT_FK1 foreign key (CASE_PICK_TASK_ID) references RRL_CASE_PICK_TASK (CASE_PICK_TASK_ID),
      constraint RRL_CASE_PICK_SHORT_FK2 foreign key (CASE_PICK_LINE_ID) references RRL_CASE_PICK_LINE (CASE_PICK_LINE_ID),
      constraint RRL_CASE_PICK_SHORT_CHK1 check (STATUS in ('CREATED', 'PENDING_APPROVAL', 'ACCEPTED', 'REJECTED', 'CANCELLED', 'SHORT_CLOSED'))
    )
  ]');

  ensure_table('RRL_INVENTORY_TASK', q'[
    create table RRL_INVENTORY_TASK (
      INVENTORY_TASK_ID number not null,
      TASK_TYPE varchar2(40) default 'INVENTORY_CHECK' not null,
      TASK_SOURCE varchar2(40) default 'CASE_PICK_SHORT' not null,
      SOURCE_DOC_TYPE varchar2(40) default 'CASE_PICK_SHORT' not null,
      SOURCE_DOC_ID number not null,
      STATUS varchar2(30) default 'NEW' not null,
      WARE_ID number,
      CELL_CODE varchar2(80),
      ARTICUL varchar2(40),
      PLANNED_QTY number,
      FACT_QTY number,
      ASSIGNED_RESOURCE_TYPE varchar2(40),
      ASSIGNED_RESOURCE_ID number,
      ASSIGNED_TO varchar2(100),
      CREATED_AT timestamp default systimestamp not null,
      CREATED_BY varchar2(100),
      ASSIGNED_AT timestamp,
      STARTED_AT timestamp,
      DONE_AT timestamp,
      UPDATED_AT timestamp,
      UPDATED_BY varchar2(100),
      COMMENT_TEXT varchar2(1000),
      constraint RRL_INVENTORY_TASK_PK primary key (INVENTORY_TASK_ID),
      constraint RRL_INVENTORY_TASK_CHK1 check (TASK_TYPE in ('INVENTORY_CHECK')),
      constraint RRL_INVENTORY_TASK_CHK2 check (STATUS in ('NEW', 'ASSIGNED', 'IN_PROGRESS', 'DONE', 'CANCELLED', 'FAILED'))
    )
  ]');

  ensure_table('RRL_CASE_PICK_EVENT', q'[
    create table RRL_CASE_PICK_EVENT (
      CASE_PICK_EVENT_ID number not null,
      CASE_PICK_TASK_ID number,
      CASE_PICK_LINE_ID number,
      EVENT_TYPE varchar2(60) not null,
      OFFLINE_EVENT_ID varchar2(100),
      RESOURCE_ID number,
      RESOURCE_SESSION_ID number,
      EQUIPMENT_ID number,
      MESSAGE_TEXT varchar2(1000),
      PAYLOAD_JSON clob,
      CREATED_AT timestamp default systimestamp not null,
      CREATED_BY varchar2(100),
      constraint RRL_CASE_PICK_EVENT_PK primary key (CASE_PICK_EVENT_ID)
    )
  ]');

  ensure_column('RRL_PICK_WAVE_TASK', 'CASE_PICK_TASK_ID',
    'alter table RRL_PICK_WAVE_TASK add CASE_PICK_TASK_ID number');
  ensure_column('RRL_PICK_WAVE_TASK', 'CASE_PICK_LINE_ID',
    'alter table RRL_PICK_WAVE_TASK add CASE_PICK_LINE_ID number');
  ensure_column('RRL_PICK_TASK', 'CASE_PICK_TASK_ID',
    'alter table RRL_PICK_TASK add CASE_PICK_TASK_ID number');
  ensure_column('RRL_PICK_TASK', 'CASE_PICK_LINE_ID',
    'alter table RRL_PICK_TASK add CASE_PICK_LINE_ID number');

  ensure_sequence('RRL_PALLET_TYPE_SQ', 'create sequence RRL_PALLET_TYPE_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_CUST_PALLET_TYPE_RULE_SQ', 'create sequence RRL_CUST_PALLET_TYPE_RULE_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_CASE_PICK_TASK_SQ', 'create sequence RRL_CASE_PICK_TASK_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_CASE_PICK_LINE_SQ', 'create sequence RRL_CASE_PICK_LINE_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_CASE_PICK_SHORT_SQ', 'create sequence RRL_CASE_PICK_SHORT_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_INVENTORY_TASK_SQ', 'create sequence RRL_INVENTORY_TASK_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_CASE_PICK_EVENT_SQ', 'create sequence RRL_CASE_PICK_EVENT_SQ start with 1 increment by 1 nocache');

  ensure_index('RRL_CUST_PALLET_RULE_I1', 'create index RRL_CUST_PALLET_RULE_I1 on RRL_CUSTOMER_PALLET_TYPE_RULE (CUSTOMER_ID, CUSTOMER_ADDRESS_ID, ACTIVE, IS_DEFAULT)');
  ensure_index('RRL_CASE_PICK_TASK_I1', 'create index RRL_CASE_PICK_TASK_I1 on RRL_CASE_PICK_TASK (STATUS, WARE_ID, ASSIGNED_RESOURCE_ID)');
  ensure_index('RRL_CASE_PICK_TASK_I2', 'create index RRL_CASE_PICK_TASK_I2 on RRL_CASE_PICK_TASK (PICK_WAVE_ID, STATUS)');
  ensure_index('RRL_CASE_PICK_LINE_I1', 'create index RRL_CASE_PICK_LINE_I1 on RRL_CASE_PICK_LINE (CASE_PICK_TASK_ID, STATUS, PICK_SEQUENCE)');
  ensure_index('RRL_CASE_PICK_LINE_I2', 'create index RRL_CASE_PICK_LINE_I2 on RRL_CASE_PICK_LINE (PICK_WAVE_ID, ARTICUL, STATUS)');
  ensure_index('RRL_CASE_PICK_SHORT_I1', 'create index RRL_CASE_PICK_SHORT_I1 on RRL_CASE_PICK_SHORT (STATUS, CREATED_AT)');
  ensure_index('RRL_INVENTORY_TASK_I1', 'create index RRL_INVENTORY_TASK_I1 on RRL_INVENTORY_TASK (STATUS, TASK_SOURCE, SOURCE_DOC_ID)');
  ensure_index('RRL_CASE_PICK_EVENT_I1', 'create index RRL_CASE_PICK_EVENT_I1 on RRL_CASE_PICK_EVENT (CASE_PICK_TASK_ID, CREATED_AT)');
  ensure_index('RRL_CASE_PICK_EVENT_U1',
    q'[create unique index RRL_CASE_PICK_EVENT_U1 on RRL_CASE_PICK_EVENT (
      case when OFFLINE_EVENT_ID is not null then OFFLINE_EVENT_ID end
    )]');
end;
/

merge into RRL_PALLET_TYPE d
using (
  select 'EURO_PALLET' PALLET_TYPE_CODE, 'Европоддон' PALLET_TYPE_NAME, 'PALLET' LOAD_UNIT_CLASS, 1.6 DEFAULT_VOLUME_M3, 1 DEFAULT_MAX_CLIENT_PALLETS from dual
  union all select 'AMERICAN_PALLET', 'Американский поддон', 'PALLET', 1.9, 1 from dual
  union all select 'TROLLEY', 'Тележка', 'TROLLEY', 1.6, 1 from dual
) s
on (d.PALLET_TYPE_CODE = s.PALLET_TYPE_CODE)
when matched then update set
  d.PALLET_TYPE_NAME = s.PALLET_TYPE_NAME,
  d.LOAD_UNIT_CLASS = s.LOAD_UNIT_CLASS,
  d.DEFAULT_VOLUME_M3 = s.DEFAULT_VOLUME_M3,
  d.DEFAULT_MAX_CLIENT_PALLETS = s.DEFAULT_MAX_CLIENT_PALLETS,
  d.ACTIVE = 1,
  d.UPDATED_AT = systimestamp,
  d.UPDATED_BY = '035_apply'
when not matched then insert (
  PALLET_TYPE_ID, PALLET_TYPE_CODE, PALLET_TYPE_NAME, LOAD_UNIT_CLASS,
  DEFAULT_VOLUME_M3, DEFAULT_MAX_CLIENT_PALLETS, ACTIVE, CREATED_AT, CREATED_BY
) values (
  RRL_PALLET_TYPE_SQ.nextval, s.PALLET_TYPE_CODE, s.PALLET_TYPE_NAME, s.LOAD_UNIT_CLASS,
  s.DEFAULT_VOLUME_M3, s.DEFAULT_MAX_CLIENT_PALLETS, 1, systimestamp, '035_apply'
);

merge into RRL_CASE_PICK_SETTING d
using (
  select nvl(min(ID), 1) WARE_ID
    from RRL_WARES
) s
on (d.WARE_ID = s.WARE_ID)
when not matched then insert (
  WARE_ID, CREATED_AT, CREATED_BY
) values (
  s.WARE_ID, systimestamp, '035_apply'
);

merge into RRL_RESOURCE_TYPE d
using (
  select 'INVENTORY' RESOURCE_TYPE,
         'PERSON' RESOURCE_CLASS,
         'Инвентаризация' RESOURCE_NAME,
         'INVENTORY_CHECK' DEFAULT_TASK_TYPES
    from dual
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
    select 'CASE_PICK_VIEW' RIGHT1, 'View case-pick TSD tasks and settings' DESCR from dual
    union all select 'CASE_PICK_EXECUTE', 'Execute case-pick TSD tasks' from dual
    union all select 'CASE_PICK_MANAGE', 'Manage case-pick assignment, transfer, and settings' from dual
    union all select 'CASE_PICK_SHORT_APPROVE', 'Approve case-pick shorts/write-offs' from dual
    union all select 'INVENTORY_TASK_VIEW', 'View inventory check tasks' from dual
    union all select 'INVENTORY_TASK_EXECUTE', 'Execute inventory check tasks' from dual
  ) s
 where not exists (
   select 1
     from RIGHTS r
    where r.USER_GROUP = 'GLOBAL_ADMIN'
      and upper(r.RIGHT1) = s.RIGHT1
 );

merge into RRL_SCHEMA_MIGRATIONS d
using (
  select '2026-05-19-035-case-pick-tsd-runtime' migration_id,
         'Case-pick TSD runtime foundation: pallet type, address rules, picker pallet tasks, lines, shorts, inventory tasks, offline events' description,
         '035_apply.sql' script_name,
         '035_rollback.sql' rollback_script
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

prompt [migration 2026-05-19-035] done
