prompt [migration 2026-05-20-038] warehouse topology master data - apply

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
  ensure_table('RRL_WAREHOUSE_TOPOLOGY', q'[
    create table RRL_WAREHOUSE_TOPOLOGY (
      TOPOLOGY_ID number not null,
      WARE_ID number not null,
      TOPOLOGY_CODE varchar2(80) not null,
      TOPOLOGY_NAME varchar2(200),
      VERSION_NO number default 1 not null,
      STATUS varchar2(20) default 'DRAFT' not null,
      VALID_FROM date,
      VALID_TO date,
      SOURCE_TOPOLOGY_ID number,
      COMMENT_TEXT varchar2(1000),
      CREATED_AT date default sysdate not null,
      CREATED_BY varchar2(50),
      UPDATED_AT date default sysdate not null,
      UPDATED_BY varchar2(50),
      PUBLISHED_AT date,
      PUBLISHED_BY varchar2(50),
      constraint RRL_WH_TOPOLOGY_PK primary key (TOPOLOGY_ID),
      constraint RRL_WH_TOPOLOGY_U1 unique (WARE_ID, TOPOLOGY_CODE),
      constraint RRL_WH_TOPOLOGY_CHK1 check (STATUS in ('DRAFT', 'VALIDATED', 'PUBLISHED', 'ARCHIVED'))
    )
  ]');

  ensure_table('RRL_TOPOLOGY_ZONE', q'[
    create table RRL_TOPOLOGY_ZONE (
      TOPOLOGY_ZONE_ID number not null,
      TOPOLOGY_ID number not null,
      ZONE_CODE varchar2(40) not null,
      ZONE_NAME varchar2(200),
      ZONE_KIND varchar2(40) default 'PICKING' not null,
      TEMPERATURE_CLASS varchar2(40),
      RESOURCE_AREA_CODE varchar2(40),
      X number default 0 not null,
      Y number default 0 not null,
      WIDTH number default 10 not null,
      HEIGHT number default 10 not null,
      ACTIVE number(1) default 1 not null,
      CREATED_AT date default sysdate not null,
      CREATED_BY varchar2(50),
      UPDATED_AT date default sysdate not null,
      UPDATED_BY varchar2(50),
      constraint RRL_TOPOLOGY_ZONE_PK primary key (TOPOLOGY_ZONE_ID),
      constraint RRL_TOPOLOGY_ZONE_FK1 foreign key (TOPOLOGY_ID) references RRL_WAREHOUSE_TOPOLOGY (TOPOLOGY_ID),
      constraint RRL_TOPOLOGY_ZONE_U1 unique (TOPOLOGY_ID, ZONE_CODE),
      constraint RRL_TOPOLOGY_ZONE_CHK1 check (ACTIVE in (0, 1))
    )
  ]');

  ensure_table('RRL_TOPOLOGY_AISLE', q'[
    create table RRL_TOPOLOGY_AISLE (
      TOPOLOGY_AISLE_ID number not null,
      TOPOLOGY_ID number not null,
      ZONE_CODE varchar2(40),
      AISLE_CODE varchar2(40) not null,
      AISLE_NAME varchar2(200),
      AISLE_KIND varchar2(40) default 'PICK_AISLE' not null,
      DIRECTION_CODE varchar2(20) default 'BOTH' not null,
      X1 number default 0 not null,
      Y1 number default 0 not null,
      X2 number default 0 not null,
      Y2 number default 0 not null,
      WIDTH_M number default 3 not null,
      ALLOW_PICKER number(1) default 1 not null,
      ALLOW_REACHTRUCK number(1) default 1 not null,
      ACTIVE number(1) default 1 not null,
      CREATED_AT date default sysdate not null,
      CREATED_BY varchar2(50),
      UPDATED_AT date default sysdate not null,
      UPDATED_BY varchar2(50),
      constraint RRL_TOPOLOGY_AISLE_PK primary key (TOPOLOGY_AISLE_ID),
      constraint RRL_TOPOLOGY_AISLE_FK1 foreign key (TOPOLOGY_ID) references RRL_WAREHOUSE_TOPOLOGY (TOPOLOGY_ID),
      constraint RRL_TOPOLOGY_AISLE_U1 unique (TOPOLOGY_ID, AISLE_CODE),
      constraint RRL_TOPOLOGY_AISLE_CHK1 check (ACTIVE in (0, 1))
    )
  ]');

  ensure_table('RRL_TOPOLOGY_CELL', q'[
    create table RRL_TOPOLOGY_CELL (
      TOPOLOGY_CELL_ID number not null,
      TOPOLOGY_ID number not null,
      WARE_ID number not null,
      CELL_CODE varchar2(80) not null,
      LEGACY_CELL_CODE varchar2(80),
      ZONE_CODE varchar2(40),
      SECTION_CODE varchar2(40),
      AISLE_CODE varchar2(40),
      RACK_CODE varchar2(40),
      BAY_NO number,
      LEVEL_NO number,
      POSITION_NO number,
      SIDE_CODE varchar2(20) default 'CENTER' not null,
      CELL_KIND varchar2(40) default 'STORAGE' not null,
      ACCESS_LEVEL number,
      STORAGE_AREA_CODE varchar2(40),
      RESOURCE_AREA_CODE varchar2(40),
      CELL_SIZE_CODE varchar2(40),
      MAX_VOLUME_M3 number,
      MAX_WEIGHT_KG number,
      X number default 0 not null,
      Y number default 0 not null,
      Z number default 0 not null,
      WIDTH number default 1 not null,
      DEPTH number default 1 not null,
      HEIGHT number default 1 not null,
      ANGLE_DEG number default 0 not null,
      ACTIVE number(1) default 1 not null,
      CREATED_AT date default sysdate not null,
      CREATED_BY varchar2(50),
      UPDATED_AT date default sysdate not null,
      UPDATED_BY varchar2(50),
      constraint RRL_TOPOLOGY_CELL_PK primary key (TOPOLOGY_CELL_ID),
      constraint RRL_TOPOLOGY_CELL_FK1 foreign key (TOPOLOGY_ID) references RRL_WAREHOUSE_TOPOLOGY (TOPOLOGY_ID),
      constraint RRL_TOPOLOGY_CELL_U1 unique (TOPOLOGY_ID, CELL_CODE),
      constraint RRL_TOPOLOGY_CELL_CHK1 check (SIDE_CODE in ('LEFT', 'RIGHT', 'CENTER')),
      constraint RRL_TOPOLOGY_CELL_CHK2 check (ACTIVE in (0, 1))
    )
  ]');

  ensure_table('RRL_TOPOLOGY_RECOMMENDATION', q'[
    create table RRL_TOPOLOGY_RECOMMENDATION (
      RECOMMENDATION_ID number not null,
      WARE_ID number not null,
      TOPOLOGY_ID number,
      PICK_ROUTE_ID number,
      PERIOD_FROM date,
      PERIOD_TO date,
      RECOMMENDATION_KIND varchar2(60) not null,
      SEVERITY varchar2(20) default 'INFO' not null,
      TITLE varchar2(200) not null,
      DETAIL_TEXT varchar2(2000),
      EVIDENCE_JSON clob,
      STATUS varchar2(20) default 'NEW' not null,
      CREATED_AT date default sysdate not null,
      CREATED_BY varchar2(50),
      DECIDED_AT date,
      DECIDED_BY varchar2(50),
      constraint RRL_TOPO_REC_PK primary key (RECOMMENDATION_ID),
      constraint RRL_TOPO_REC_CHK1 check (STATUS in ('NEW', 'ACCEPTED', 'REJECTED', 'APPLIED'))
    )
  ]');

  ensure_table('RRL_TOPOLOGY_CHANGE_LOG', q'[
    create table RRL_TOPOLOGY_CHANGE_LOG (
      CHANGE_ID number not null,
      TOPOLOGY_ID number not null,
      ENTITY_KIND varchar2(40) not null,
      ENTITY_ID number,
      CHANGE_KIND varchar2(40) not null,
      OLD_VALUE_JSON clob,
      NEW_VALUE_JSON clob,
      REASON_TEXT varchar2(1000),
      CREATED_AT date default sysdate not null,
      CREATED_BY varchar2(50),
      constraint RRL_TOPO_CHANGE_LOG_PK primary key (CHANGE_ID)
    )
  ]');

  ensure_sequence('RRL_WH_TOPOLOGY_SQ',
    'create sequence RRL_WH_TOPOLOGY_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_TOPOLOGY_ZONE_SQ',
    'create sequence RRL_TOPOLOGY_ZONE_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_TOPOLOGY_AISLE_SQ',
    'create sequence RRL_TOPOLOGY_AISLE_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_TOPOLOGY_CELL_SQ',
    'create sequence RRL_TOPOLOGY_CELL_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_TOPO_REC_SQ',
    'create sequence RRL_TOPO_REC_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_TOPO_CHANGE_LOG_SQ',
    'create sequence RRL_TOPO_CHANGE_LOG_SQ start with 1 increment by 1 nocache');

  ensure_column('RRL_PICK_ROUTE', 'TOPOLOGY_ID',
    'alter table RRL_PICK_ROUTE add TOPOLOGY_ID number');
  ensure_column('RRL_PICK_ROUTE', 'ROUTE_PATTERN',
    q'[alter table RRL_PICK_ROUTE add ROUTE_PATTERN varchar2(30) default 'LINEAR' not null]');
  ensure_column('RRL_PICK_ROUTE', 'START_POINT_CODE',
    'alter table RRL_PICK_ROUTE add START_POINT_CODE varchar2(80)');
  ensure_column('RRL_PICK_ROUTE', 'END_POINT_CODE',
    'alter table RRL_PICK_ROUTE add END_POINT_CODE varchar2(80)');
  ensure_column('RRL_PICK_ROUTE', 'STRICT_SEQUENCE',
    'alter table RRL_PICK_ROUTE add STRICT_SEQUENCE number(1) default 1 not null');
  ensure_column('RRL_PICK_ROUTE', 'STATUS',
    q'[alter table RRL_PICK_ROUTE add STATUS varchar2(20) default 'DRAFT' not null]');
  ensure_column('RRL_PICK_ROUTE', 'PUBLISHED_AT',
    'alter table RRL_PICK_ROUTE add PUBLISHED_AT date');
  ensure_column('RRL_PICK_ROUTE', 'PUBLISHED_BY',
    'alter table RRL_PICK_ROUTE add PUBLISHED_BY varchar2(50)');
  ensure_column('RRL_PICK_ROUTE', 'COMMENT_TEXT',
    'alter table RRL_PICK_ROUTE add COMMENT_TEXT varchar2(1000)');
  ensure_column('RRL_PICK_ROUTE', 'ZONE_CODE',
    'alter table RRL_PICK_ROUTE add ZONE_CODE varchar2(40)');

  ensure_column('RRL_PICK_ROUTE_CELL', 'TOPOLOGY_CELL_ID',
    'alter table RRL_PICK_ROUTE_CELL add TOPOLOGY_CELL_ID number');
  ensure_column('RRL_PICK_ROUTE_CELL', 'SECTION_CODE',
    'alter table RRL_PICK_ROUTE_CELL add SECTION_CODE varchar2(40)');
  ensure_column('RRL_PICK_ROUTE_CELL', 'BAY_NO',
    'alter table RRL_PICK_ROUTE_CELL add BAY_NO number');
  ensure_column('RRL_PICK_ROUTE_CELL', 'DIRECTION_CODE',
    'alter table RRL_PICK_ROUTE_CELL add DIRECTION_CODE varchar2(20)');
  ensure_column('RRL_PICK_ROUTE_CELL', 'VISIT_GROUP_NO',
    'alter table RRL_PICK_ROUTE_CELL add VISIT_GROUP_NO number');
  ensure_column('RRL_PICK_ROUTE_CELL', 'PATH_SEGMENT_NO',
    'alter table RRL_PICK_ROUTE_CELL add PATH_SEGMENT_NO number');
  ensure_column('RRL_PICK_ROUTE_CELL', 'DISTANCE_FROM_PREV_M',
    'alter table RRL_PICK_ROUTE_CELL add DISTANCE_FROM_PREV_M number');
  ensure_column('RRL_PICK_ROUTE_CELL', 'TURN_COST_SEC',
    'alter table RRL_PICK_ROUTE_CELL add TURN_COST_SEC number');

  ensure_index('RRL_TOPOLOGY_CELL_I1',
    'create index RRL_TOPOLOGY_CELL_I1 on RRL_TOPOLOGY_CELL (TOPOLOGY_ID, AISLE_CODE, BAY_NO, SIDE_CODE, ACTIVE)');
  ensure_index('RRL_TOPOLOGY_CELL_I2',
    'create index RRL_TOPOLOGY_CELL_I2 on RRL_TOPOLOGY_CELL (WARE_ID, CELL_CODE, ACTIVE)');
  ensure_index('RRL_PICK_ROUTE_I2',
    'create index RRL_PICK_ROUTE_I2 on RRL_PICK_ROUTE (TOPOLOGY_ID, STATUS, ACTIVE)');
  ensure_index('RRL_PICK_ROUTE_CELL_I3',
    'create index RRL_PICK_ROUTE_CELL_I3 on RRL_PICK_ROUTE_CELL (TOPOLOGY_CELL_ID, ACTIVE)');
end;
/

merge into RIGHTS d
using (
  select 'GLOBAL_ADMIN' USER_GROUP, 'WAREHOUSE_TOPOLOGY_VIEW' RIGHT1, 'View warehouse topology administration' DESCR from dual
  union all select 'GLOBAL_ADMIN', 'WAREHOUSE_TOPOLOGY_EDIT', 'Edit warehouse topology administration' from dual
  union all select 'GLOBAL_ADMIN', 'WAREHOUSE_TOPOLOGY_PUBLISH', 'Publish warehouse topology versions' from dual
  union all select 'GLOBAL_ADMIN', 'PICK_ROUTE_ADMIN_VIEW', 'View pick route administration' from dual
  union all select 'GLOBAL_ADMIN', 'PICK_ROUTE_ADMIN_EDIT', 'Edit pick route administration' from dual
  union all select 'GLOBAL_ADMIN', 'PICK_ROUTE_ADMIN_PUBLISH', 'Publish pick routes' from dual
) s
on (d.USER_GROUP = s.USER_GROUP and d.RIGHT1 = s.RIGHT1)
when not matched then insert (USER_GROUP, RIGHT1, DESCR)
values (s.USER_GROUP, s.RIGHT1, s.DESCR);

merge into RRL_SCHEMA_MIGRATIONS d
using (
  select '2026-05-20-038-warehouse-topology-master-data' migration_id,
         'Versioned warehouse topology master-data tables, pick-route topology links, and administration rights' description,
         '038_apply.sql' script_name,
         '038_rollback.sql' rollback_script
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

prompt [migration 2026-05-20-038] apply done
