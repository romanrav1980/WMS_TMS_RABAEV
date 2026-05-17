prompt [migration 2026-05-17-017] Pick face and pick route - apply

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
  ensure_table('RRL_PICK_ROUTE', q'[
    create table RRL_PICK_ROUTE (
      PICK_ROUTE_ID number not null,
      WARE_ID number not null,
      ROUTE_CODE varchar2(50) not null,
      ROUTE_NAME varchar2(255),
      ROUTE_KIND varchar2(20) default 'PICK' not null,
      ACTIVE number(1) default 1 not null,
      CREATED_AT date default sysdate not null,
      CREATED_BY varchar2(50),
      UPDATED_AT date,
      UPDATED_BY varchar2(50),
      constraint RRL_PICK_ROUTE_PK primary key (PICK_ROUTE_ID),
      constraint RRL_PICK_ROUTE_CHK1 check (ROUTE_KIND in ('PICK', 'REPLENISHMENT', 'MIXED')),
      constraint RRL_PICK_ROUTE_CHK2 check (ACTIVE in (0, 1))
    )
  ]');

  ensure_table('RRL_PICK_ROUTE_CELL', q'[
    create table RRL_PICK_ROUTE_CELL (
      PICK_ROUTE_CELL_ID number not null,
      PICK_ROUTE_ID number not null,
      WARE_ID number not null,
      CELL_CODE varchar2(60) not null,
      PICK_SEQUENCE number not null,
      ZONE_CODE varchar2(50),
      AISLE_CODE varchar2(50),
      SIDE_CODE varchar2(20),
      LEVEL_NO number,
      ACTIVE number(1) default 1 not null,
      CREATED_AT date default sysdate not null,
      CREATED_BY varchar2(50),
      UPDATED_AT date,
      UPDATED_BY varchar2(50),
      constraint RRL_PICK_ROUTE_CELL_PK primary key (PICK_ROUTE_CELL_ID),
      constraint RRL_PICK_ROUTE_CELL_FK1 foreign key (PICK_ROUTE_ID) references RRL_PICK_ROUTE (PICK_ROUTE_ID),
      constraint RRL_PICK_ROUTE_CELL_CHK1 check (ACTIVE in (0, 1))
    )
  ]');

  ensure_table('RRL_PICK_FACE', q'[
    create table RRL_PICK_FACE (
      PICK_FACE_ID number not null,
      WARE_ID number not null,
      CELL_CODE varchar2(60) not null,
      PICK_FACE_CODE varchar2(100),
      PICK_FACE_TYPE varchar2(20) default 'REGULAR' not null,
      PICK_ROUTE_ID number,
      PICK_ROUTE_CELL_ID number,
      PICK_SEQUENCE number,
      MIN_CASE_QTY number default 0,
      MAX_CASE_QTY number,
      REPLENISHMENT_TRIGGER_QTY number,
      MAX_WEIGHT number,
      MAX_VOLUME number,
      ALLOW_DYNAMIC_ASSIGNMENT number(1) default 0 not null,
      ACTIVE number(1) default 1 not null,
      COMMENT_TEXT varchar2(1000),
      CREATED_AT date default sysdate not null,
      CREATED_BY varchar2(50),
      UPDATED_AT date,
      UPDATED_BY varchar2(50),
      constraint RRL_PICK_FACE_PK primary key (PICK_FACE_ID),
      constraint RRL_PICK_FACE_FK1 foreign key (PICK_ROUTE_ID) references RRL_PICK_ROUTE (PICK_ROUTE_ID),
      constraint RRL_PICK_FACE_FK2 foreign key (PICK_ROUTE_CELL_ID) references RRL_PICK_ROUTE_CELL (PICK_ROUTE_CELL_ID),
      constraint RRL_PICK_FACE_CHK1 check (PICK_FACE_TYPE in ('REGULAR', 'DYNAMIC')),
      constraint RRL_PICK_FACE_CHK2 check (ALLOW_DYNAMIC_ASSIGNMENT in (0, 1)),
      constraint RRL_PICK_FACE_CHK3 check (ACTIVE in (0, 1))
    )
  ]');

  ensure_table('RRL_PICK_FACE_ARTICUL', q'[
    create table RRL_PICK_FACE_ARTICUL (
      PICK_FACE_ARTICUL_ID number not null,
      PICK_FACE_ID number not null,
      ARTICUL varchar2(40) not null,
      PRIORITY number default 100 not null,
      MIN_QTY number,
      MAX_QTY number,
      CASE_PICK_ENABLED number(1) default 1 not null,
      ACTIVE number(1) default 1 not null,
      VALID_FROM date default trunc(sysdate) not null,
      VALID_TO date,
      CREATED_AT date default sysdate not null,
      CREATED_BY varchar2(50),
      UPDATED_AT date,
      UPDATED_BY varchar2(50),
      constraint RRL_PICK_FACE_ARTICUL_PK primary key (PICK_FACE_ARTICUL_ID),
      constraint RRL_PICK_FACE_ARTICUL_FK1 foreign key (PICK_FACE_ID) references RRL_PICK_FACE (PICK_FACE_ID),
      constraint RRL_PICK_FACE_ARTICUL_CHK1 check (CASE_PICK_ENABLED in (0, 1)),
      constraint RRL_PICK_FACE_ARTICUL_CHK2 check (ACTIVE in (0, 1))
    )
  ]');

  ensure_sequence('RRL_PICK_ROUTE_SQ', 'create sequence RRL_PICK_ROUTE_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_PICK_ROUTE_CELL_SQ', 'create sequence RRL_PICK_ROUTE_CELL_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_PICK_FACE_SQ', 'create sequence RRL_PICK_FACE_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_PICK_FACE_ARTICUL_SQ', 'create sequence RRL_PICK_FACE_ARTICUL_SQ start with 1 increment by 1 nocache');

  ensure_column('RRL_PICK_TASK', 'PICK_FACE_ID', 'alter table RRL_PICK_TASK add PICK_FACE_ID number');
  ensure_column('RRL_PICK_TASK', 'PICK_ROUTE_CELL_ID', 'alter table RRL_PICK_TASK add PICK_ROUTE_CELL_ID number');

  ensure_index('RRL_PICK_ROUTE_I1', 'create index RRL_PICK_ROUTE_I1 on RRL_PICK_ROUTE (WARE_ID, ROUTE_CODE, ACTIVE)');
  ensure_index('RRL_PICK_ROUTE_CELL_I1', 'create index RRL_PICK_ROUTE_CELL_I1 on RRL_PICK_ROUTE_CELL (PICK_ROUTE_ID, PICK_SEQUENCE)');
  ensure_index('RRL_PICK_ROUTE_CELL_I2', 'create index RRL_PICK_ROUTE_CELL_I2 on RRL_PICK_ROUTE_CELL (WARE_ID, CELL_CODE, ACTIVE)');
  ensure_index('RRL_PICK_FACE_I1', 'create index RRL_PICK_FACE_I1 on RRL_PICK_FACE (WARE_ID, CELL_CODE, ACTIVE)');
  ensure_index('RRL_PICK_FACE_I2', 'create index RRL_PICK_FACE_I2 on RRL_PICK_FACE (PICK_ROUTE_ID, PICK_SEQUENCE)');
  ensure_index('RRL_PICK_FACE_ARTICUL_I1', 'create index RRL_PICK_FACE_ARTICUL_I1 on RRL_PICK_FACE_ARTICUL (ARTICUL, ACTIVE, PRIORITY)');
  ensure_index('RRL_PICK_TASK_I3', 'create index RRL_PICK_TASK_I3 on RRL_PICK_TASK (PICK_FACE_ID, STATUS)');
end;
/

create or replace package RRL_PICK_TOPOLOGY_API as
  function upsert_route(
    p_pick_route_id number default null,
    p_route_code    varchar2,
    p_route_name    varchar2 default null,
    p_ware_id       number,
    p_route_kind    varchar2 default 'PICK',
    p_active        number default 1,
    p_updated_by    varchar2 default null
  ) return number;

  function upsert_route_cell(
    p_pick_route_cell_id number default null,
    p_pick_route_id      number,
    p_cell_code          varchar2,
    p_pick_sequence      number,
    p_zone_code          varchar2 default null,
    p_aisle_code         varchar2 default null,
    p_side_code          varchar2 default null,
    p_level_no           number default null,
    p_active             number default 1,
    p_updated_by         varchar2 default null
  ) return number;

  function upsert_pick_face(
    p_pick_face_id             number default null,
    p_ware_id                  number,
    p_cell_code                varchar2,
    p_pick_face_code           varchar2 default null,
    p_pick_face_type           varchar2 default 'REGULAR',
    p_pick_route_id            number default null,
    p_pick_route_cell_id       number default null,
    p_pick_sequence            number default null,
    p_min_case_qty             number default null,
    p_max_case_qty             number default null,
    p_replenishment_trigger_qty number default null,
    p_max_weight               number default null,
    p_max_volume               number default null,
    p_allow_dynamic_assignment number default 0,
    p_active                   number default 1,
    p_comment_text             varchar2 default null,
    p_updated_by               varchar2 default null
  ) return number;

  function assign_articul(
    p_pick_face_articul_id number default null,
    p_pick_face_id         number,
    p_articul              varchar2,
    p_priority             number default 100,
    p_min_qty              number default null,
    p_max_qty              number default null,
    p_case_pick_enabled    number default 1,
    p_active               number default 1,
    p_valid_from           date default null,
    p_valid_to             date default null,
    p_updated_by           varchar2 default null
  ) return number;

  procedure resolve_pick_face(
    p_ware_id            number,
    p_articul            varchar2,
    p_target_cell        out varchar2,
    p_pick_sequence      out number,
    p_pick_face_id       out number,
    p_pick_route_cell_id out number
  );
end RRL_PICK_TOPOLOGY_API;
/

create or replace package body RRL_PICK_TOPOLOGY_API as
  function norm_active(p_active number) return number is
  begin
    if nvl(p_active, 1) = 0 then
      return 0;
    end if;
    return 1;
  end;

  function upsert_route(
    p_pick_route_id number default null,
    p_route_code    varchar2,
    p_route_name    varchar2 default null,
    p_ware_id       number,
    p_route_kind    varchar2 default 'PICK',
    p_active        number default 1,
    p_updated_by    varchar2 default null
  ) return number is
    v_id number;
    v_kind varchar2(20);
  begin
    if p_route_code is null or p_ware_id is null then
      raise_application_error(-20970, 'route_code and ware_id are required');
    end if;

    v_kind := upper(nvl(p_route_kind, 'PICK'));
    if v_kind not in ('PICK', 'REPLENISHMENT', 'MIXED') then
      raise_application_error(-20971, 'unsupported route kind');
    end if;

    if p_pick_route_id is not null then
      v_id := p_pick_route_id;
      update RRL_PICK_ROUTE
         set ROUTE_CODE = upper(substr(p_route_code, 1, 50)),
             ROUTE_NAME = substr(p_route_name, 1, 255),
             WARE_ID = p_ware_id,
             ROUTE_KIND = v_kind,
             ACTIVE = case when nvl(p_active, 1) = 0 then 0 else 1 end,
             UPDATED_AT = sysdate,
             UPDATED_BY = substr(p_updated_by, 1, 50)
       where PICK_ROUTE_ID = v_id;
      if sql%rowcount = 0 then
        raise_application_error(-20972, 'pick route not found');
      end if;
      return v_id;
    end if;

    begin
      select PICK_ROUTE_ID
        into v_id
        from RRL_PICK_ROUTE
       where WARE_ID = p_ware_id
         and upper(ROUTE_CODE) = upper(p_route_code)
         and rownum = 1;

      update RRL_PICK_ROUTE
         set ROUTE_NAME = substr(p_route_name, 1, 255),
             ROUTE_KIND = v_kind,
             ACTIVE = case when nvl(p_active, 1) = 0 then 0 else 1 end,
             UPDATED_AT = sysdate,
             UPDATED_BY = substr(p_updated_by, 1, 50)
       where PICK_ROUTE_ID = v_id;
      return v_id;
    exception
      when no_data_found then
        select RRL_PICK_ROUTE_SQ.nextval into v_id from dual;
        insert into RRL_PICK_ROUTE (
          PICK_ROUTE_ID, WARE_ID, ROUTE_CODE, ROUTE_NAME, ROUTE_KIND,
          ACTIVE, CREATED_AT, CREATED_BY
        ) values (
          v_id, p_ware_id, upper(substr(p_route_code, 1, 50)),
          substr(p_route_name, 1, 255), v_kind,
          case when nvl(p_active, 1) = 0 then 0 else 1 end, sysdate, substr(p_updated_by, 1, 50)
        );
        return v_id;
    end;
  end upsert_route;

  function upsert_route_cell(
    p_pick_route_cell_id number default null,
    p_pick_route_id      number,
    p_cell_code          varchar2,
    p_pick_sequence      number,
    p_zone_code          varchar2 default null,
    p_aisle_code         varchar2 default null,
    p_side_code          varchar2 default null,
    p_level_no           number default null,
    p_active             number default 1,
    p_updated_by         varchar2 default null
  ) return number is
    v_id number;
    v_ware_id number;
  begin
    if p_pick_route_id is null or p_cell_code is null or p_pick_sequence is null then
      raise_application_error(-20973, 'route, cell and sequence are required');
    end if;

    select WARE_ID into v_ware_id from RRL_PICK_ROUTE where PICK_ROUTE_ID = p_pick_route_id;

    if p_pick_route_cell_id is not null then
      v_id := p_pick_route_cell_id;
      update RRL_PICK_ROUTE_CELL
         set PICK_ROUTE_ID = p_pick_route_id,
             WARE_ID = v_ware_id,
             CELL_CODE = substr(p_cell_code, 1, 60),
             PICK_SEQUENCE = p_pick_sequence,
             ZONE_CODE = substr(p_zone_code, 1, 50),
             AISLE_CODE = substr(p_aisle_code, 1, 50),
             SIDE_CODE = substr(p_side_code, 1, 20),
             LEVEL_NO = p_level_no,
             ACTIVE = case when nvl(p_active, 1) = 0 then 0 else 1 end,
             UPDATED_AT = sysdate,
             UPDATED_BY = substr(p_updated_by, 1, 50)
       where PICK_ROUTE_CELL_ID = v_id;
      if sql%rowcount = 0 then
        raise_application_error(-20974, 'pick route cell not found');
      end if;
      return v_id;
    end if;

    begin
      select PICK_ROUTE_CELL_ID
        into v_id
        from RRL_PICK_ROUTE_CELL
       where PICK_ROUTE_ID = p_pick_route_id
         and upper(CELL_CODE) = upper(p_cell_code)
         and rownum = 1;

      update RRL_PICK_ROUTE_CELL
         set PICK_SEQUENCE = p_pick_sequence,
             ZONE_CODE = substr(p_zone_code, 1, 50),
             AISLE_CODE = substr(p_aisle_code, 1, 50),
             SIDE_CODE = substr(p_side_code, 1, 20),
             LEVEL_NO = p_level_no,
             ACTIVE = case when nvl(p_active, 1) = 0 then 0 else 1 end,
             UPDATED_AT = sysdate,
             UPDATED_BY = substr(p_updated_by, 1, 50)
       where PICK_ROUTE_CELL_ID = v_id;
      return v_id;
    exception
      when no_data_found then
        select RRL_PICK_ROUTE_CELL_SQ.nextval into v_id from dual;
        insert into RRL_PICK_ROUTE_CELL (
          PICK_ROUTE_CELL_ID, PICK_ROUTE_ID, WARE_ID, CELL_CODE, PICK_SEQUENCE,
          ZONE_CODE, AISLE_CODE, SIDE_CODE, LEVEL_NO, ACTIVE, CREATED_AT, CREATED_BY
        ) values (
          v_id, p_pick_route_id, v_ware_id, substr(p_cell_code, 1, 60), p_pick_sequence,
          substr(p_zone_code, 1, 50), substr(p_aisle_code, 1, 50),
          substr(p_side_code, 1, 20), p_level_no, case when nvl(p_active, 1) = 0 then 0 else 1 end,
          sysdate, substr(p_updated_by, 1, 50)
        );
        return v_id;
    end;
  end upsert_route_cell;

  function upsert_pick_face(
    p_pick_face_id             number default null,
    p_ware_id                  number,
    p_cell_code                varchar2,
    p_pick_face_code           varchar2 default null,
    p_pick_face_type           varchar2 default 'REGULAR',
    p_pick_route_id            number default null,
    p_pick_route_cell_id       number default null,
    p_pick_sequence            number default null,
    p_min_case_qty             number default null,
    p_max_case_qty             number default null,
    p_replenishment_trigger_qty number default null,
    p_max_weight               number default null,
    p_max_volume               number default null,
    p_allow_dynamic_assignment number default 0,
    p_active                   number default 1,
    p_comment_text             varchar2 default null,
    p_updated_by               varchar2 default null
  ) return number is
    v_id number;
    v_type varchar2(20);
    v_route_cell_sequence number;
  begin
    if p_ware_id is null or p_cell_code is null then
      raise_application_error(-20975, 'ware_id and cell_code are required');
    end if;

    v_type := upper(nvl(p_pick_face_type, 'REGULAR'));
    if v_type not in ('REGULAR', 'DYNAMIC') then
      raise_application_error(-20976, 'unsupported pick face type');
    end if;

    if p_pick_route_cell_id is not null then
      begin
        select PICK_SEQUENCE
          into v_route_cell_sequence
          from RRL_PICK_ROUTE_CELL
         where PICK_ROUTE_CELL_ID = p_pick_route_cell_id;
      exception
        when no_data_found then
          raise_application_error(-20977, 'pick route cell not found');
      end;
    end if;

    if p_pick_face_id is not null then
      v_id := p_pick_face_id;
      update RRL_PICK_FACE
         set WARE_ID = p_ware_id,
             CELL_CODE = substr(p_cell_code, 1, 60),
             PICK_FACE_CODE = substr(p_pick_face_code, 1, 100),
             PICK_FACE_TYPE = v_type,
             PICK_ROUTE_ID = p_pick_route_id,
             PICK_ROUTE_CELL_ID = p_pick_route_cell_id,
             PICK_SEQUENCE = nvl(p_pick_sequence, v_route_cell_sequence),
             MIN_CASE_QTY = nvl(p_min_case_qty, 0),
             MAX_CASE_QTY = p_max_case_qty,
             REPLENISHMENT_TRIGGER_QTY = p_replenishment_trigger_qty,
             MAX_WEIGHT = p_max_weight,
             MAX_VOLUME = p_max_volume,
             ALLOW_DYNAMIC_ASSIGNMENT = case when nvl(p_allow_dynamic_assignment, 0) = 0 then 0 else 1 end,
             ACTIVE = case when nvl(p_active, 1) = 0 then 0 else 1 end,
             COMMENT_TEXT = substr(p_comment_text, 1, 1000),
             UPDATED_AT = sysdate,
             UPDATED_BY = substr(p_updated_by, 1, 50)
       where PICK_FACE_ID = v_id;
      if sql%rowcount = 0 then
        raise_application_error(-20978, 'pick face not found');
      end if;
      return v_id;
    end if;

    select RRL_PICK_FACE_SQ.nextval into v_id from dual;
    insert into RRL_PICK_FACE (
      PICK_FACE_ID, WARE_ID, CELL_CODE, PICK_FACE_CODE, PICK_FACE_TYPE,
      PICK_ROUTE_ID, PICK_ROUTE_CELL_ID, PICK_SEQUENCE, MIN_CASE_QTY, MAX_CASE_QTY,
      REPLENISHMENT_TRIGGER_QTY, MAX_WEIGHT, MAX_VOLUME, ALLOW_DYNAMIC_ASSIGNMENT,
      ACTIVE, COMMENT_TEXT, CREATED_AT, CREATED_BY
    ) values (
      v_id, p_ware_id, substr(p_cell_code, 1, 60), substr(p_pick_face_code, 1, 100), v_type,
      p_pick_route_id, p_pick_route_cell_id, nvl(p_pick_sequence, v_route_cell_sequence),
      nvl(p_min_case_qty, 0), p_max_case_qty, p_replenishment_trigger_qty,
      p_max_weight, p_max_volume, case when nvl(p_allow_dynamic_assignment, 0) = 0 then 0 else 1 end,
      case when nvl(p_active, 1) = 0 then 0 else 1 end, substr(p_comment_text, 1, 1000), sysdate, substr(p_updated_by, 1, 50)
    );
    return v_id;
  end upsert_pick_face;

  function assign_articul(
    p_pick_face_articul_id number default null,
    p_pick_face_id         number,
    p_articul              varchar2,
    p_priority             number default 100,
    p_min_qty              number default null,
    p_max_qty              number default null,
    p_case_pick_enabled    number default 1,
    p_active               number default 1,
    p_valid_from           date default null,
    p_valid_to             date default null,
    p_updated_by           varchar2 default null
  ) return number is
    v_id number;
  begin
    if p_pick_face_id is null or p_articul is null then
      raise_application_error(-20979, 'pick_face_id and articul are required');
    end if;

    if p_pick_face_articul_id is not null then
      v_id := p_pick_face_articul_id;
      update RRL_PICK_FACE_ARTICUL
         set PICK_FACE_ID = p_pick_face_id,
             ARTICUL = upper(substr(p_articul, 1, 40)),
             PRIORITY = nvl(p_priority, 100),
             MIN_QTY = p_min_qty,
             MAX_QTY = p_max_qty,
             CASE_PICK_ENABLED = case when nvl(p_case_pick_enabled, 1) = 0 then 0 else 1 end,
             ACTIVE = case when nvl(p_active, 1) = 0 then 0 else 1 end,
             VALID_FROM = nvl(p_valid_from, trunc(sysdate)),
             VALID_TO = p_valid_to,
             UPDATED_AT = sysdate,
             UPDATED_BY = substr(p_updated_by, 1, 50)
       where PICK_FACE_ARTICUL_ID = v_id;
      if sql%rowcount = 0 then
        raise_application_error(-20980, 'pick face articul row not found');
      end if;
      return v_id;
    end if;

    begin
      select PICK_FACE_ARTICUL_ID
        into v_id
        from RRL_PICK_FACE_ARTICUL
       where PICK_FACE_ID = p_pick_face_id
         and upper(ARTICUL) = upper(p_articul)
         and rownum = 1;

      update RRL_PICK_FACE_ARTICUL
         set PRIORITY = nvl(p_priority, 100),
             MIN_QTY = p_min_qty,
             MAX_QTY = p_max_qty,
             CASE_PICK_ENABLED = case when nvl(p_case_pick_enabled, 1) = 0 then 0 else 1 end,
             ACTIVE = case when nvl(p_active, 1) = 0 then 0 else 1 end,
             VALID_FROM = nvl(p_valid_from, trunc(sysdate)),
             VALID_TO = p_valid_to,
             UPDATED_AT = sysdate,
             UPDATED_BY = substr(p_updated_by, 1, 50)
       where PICK_FACE_ARTICUL_ID = v_id;
      return v_id;
    exception
      when no_data_found then
        select RRL_PICK_FACE_ARTICUL_SQ.nextval into v_id from dual;
        insert into RRL_PICK_FACE_ARTICUL (
          PICK_FACE_ARTICUL_ID, PICK_FACE_ID, ARTICUL, PRIORITY, MIN_QTY, MAX_QTY,
          CASE_PICK_ENABLED, ACTIVE, VALID_FROM, VALID_TO, CREATED_AT, CREATED_BY
        ) values (
          v_id, p_pick_face_id, upper(substr(p_articul, 1, 40)), nvl(p_priority, 100),
      p_min_qty, p_max_qty, case when nvl(p_case_pick_enabled, 1) = 0 then 0 else 1 end, case when nvl(p_active, 1) = 0 then 0 else 1 end,
          nvl(p_valid_from, trunc(sysdate)), p_valid_to, sysdate, substr(p_updated_by, 1, 50)
        );
        return v_id;
    end;
  end assign_articul;

  procedure resolve_pick_face(
    p_ware_id            number,
    p_articul            varchar2,
    p_target_cell        out varchar2,
    p_pick_sequence      out number,
    p_pick_face_id       out number,
    p_pick_route_cell_id out number
  ) is
  begin
    p_target_cell := null;
    p_pick_sequence := null;
    p_pick_face_id := null;
    p_pick_route_cell_id := null;

    select PICK_FACE_ID,
           CELL_CODE,
           PICK_SEQUENCE,
           PICK_ROUTE_CELL_ID
      into p_pick_face_id,
           p_target_cell,
           p_pick_sequence,
           p_pick_route_cell_id
      from (
        select pf.PICK_FACE_ID,
               pf.CELL_CODE,
               nvl(rc.PICK_SEQUENCE, pf.PICK_SEQUENCE) PICK_SEQUENCE,
               pf.PICK_ROUTE_CELL_ID
          from RRL_PICK_FACE_ARTICUL pfa
          join RRL_PICK_FACE pf
            on pf.PICK_FACE_ID = pfa.PICK_FACE_ID
          left join RRL_PICK_ROUTE_CELL rc
            on rc.PICK_ROUTE_CELL_ID = pf.PICK_ROUTE_CELL_ID
           and rc.ACTIVE = 1
         where pfa.ACTIVE = 1
           and pfa.CASE_PICK_ENABLED = 1
           and pf.ACTIVE = 1
           and upper(pfa.ARTICUL) = upper(p_articul)
           and (p_ware_id is null or pf.WARE_ID = p_ware_id)
           and trunc(sysdate) between trunc(pfa.VALID_FROM) and nvl(trunc(pfa.VALID_TO), date '2999-12-31')
         order by pfa.PRIORITY, nvl(rc.PICK_SEQUENCE, pf.PICK_SEQUENCE) nulls last, pf.PICK_FACE_ID
      )
     where rownum = 1;
  exception
    when no_data_found then
      p_target_cell := null;
      p_pick_sequence := null;
      p_pick_face_id := null;
      p_pick_route_cell_id := null;
  end resolve_pick_face;
end RRL_PICK_TOPOLOGY_API;
/

create or replace package RRL_PICKING_API as
  function create_plan(
    p_customer_order_id number,
    p_plan_strategy     varchar2 default 'FEFO',
    p_created_by        varchar2 default null
  ) return number;

  procedure cancel_plan(
    p_pick_plan_id number,
    p_updated_by   varchar2 default null
  );
end RRL_PICKING_API;
/

create or replace package body RRL_PICKING_API as
  function active_reserved_qty(
    p_pallet_uid varchar2,
    p_articul    varchar2
  ) return number is
    v_qty number;
  begin
    select nvl(sum(RESERVED_QTY), 0)
      into v_qty
      from RRL_PICK_RESERVATION
     where RESERVATION_STATUS = 'ACTIVE'
       and PALLET_UID = p_pallet_uid
       and upper(ARTICUL) = upper(p_articul);
    return v_qty;
  end active_reserved_qty;

  procedure log_decision(
    p_pick_plan_id      number,
    p_pick_plan_line_id number,
    p_decision_type     varchar2,
    p_message_text      varchar2,
    p_payload_json      clob default null,
    p_created_by        varchar2 default null
  ) is
  begin
    insert into RRL_PICK_DECISION_LOG (
      PICK_DECISION_ID, PICK_PLAN_ID, PICK_PLAN_LINE_ID,
      DECISION_TYPE, MESSAGE_TEXT, PAYLOAD_JSON, CREATED_AT, CREATED_BY
    ) values (
      RRL_PICK_DECISION_LOG_SQ.nextval, p_pick_plan_id, p_pick_plan_line_id,
      substr(p_decision_type, 1, 50), substr(p_message_text, 1, 1000),
      p_payload_json, sysdate, substr(p_created_by, 1, 50)
    );
  end log_decision;

  function create_plan(
    p_customer_order_id number,
    p_plan_strategy     varchar2 default 'FEFO',
    p_created_by        varchar2 default null
  ) return number is
    v_order RRL_CUSTOMER_ORDER%rowtype;
    v_pick_plan_id number;
    v_line_id number;
    v_task_id number;
    v_remaining number;
    v_candidate_available number;
    v_reserved_by_other number;
    v_reserve_qty number;
    v_requested_total number := 0;
    v_planned_total number := 0;
    v_shortage_total number := 0;
    v_line_planned number;
    v_line_shortage number;
    v_task_type varchar2(30);
    v_strategy varchar2(30);
    v_status varchar2(30);
    v_target_cell varchar2(60);
    v_pick_sequence number;
    v_pick_face_id number;
    v_pick_route_cell_id number;
  begin
    v_strategy := upper(nvl(p_plan_strategy, 'FEFO'));
    if v_strategy not in ('FEFO', 'FIFO') then
      raise_application_error(-20980, 'unsupported picking strategy');
    end if;

    select *
      into v_order
      from RRL_CUSTOMER_ORDER
     where CUSTOMER_ORDER_ID = p_customer_order_id;

    select RRL_PICK_PLAN_SQ.nextval into v_pick_plan_id from dual;

    insert into RRL_PICK_PLAN (
      PICK_PLAN_ID, CUSTOMER_ORDER_ID, CUSTOMER_ID, WARE_ID, ROUTE_ID, DOCK_ID,
      STATUS, PLAN_STRATEGY, CREATED_AT, CREATED_BY
    ) values (
      v_pick_plan_id, v_order.CUSTOMER_ORDER_ID, v_order.CUSTOMER_ID, v_order.WARE_ID,
      v_order.ROUTE_ID, v_order.DOCK_ID, 'DRAFT', v_strategy, sysdate, substr(p_created_by, 1, 50)
    );

    for l in (
      select *
        from RRL_CUSTOMER_ORDER_ROW
       where CUSTOMER_ORDER_ID = p_customer_order_id
         and STATUS <> 'CANCELLED'
       order by LINE_NO, CUSTOMER_ORDER_ROW_ID
    ) loop
      select RRL_PICK_PLAN_LINE_SQ.nextval into v_line_id from dual;
      v_remaining := nvl(l.ORDER_QTY, 0);
      v_line_planned := 0;
      v_reserved_by_other := 0;
      v_requested_total := v_requested_total + nvl(l.ORDER_QTY, 0);

      insert into RRL_PICK_PLAN_LINE (
        PICK_PLAN_LINE_ID, PICK_PLAN_ID, CUSTOMER_ORDER_ROW_ID, ARTICUL,
        PRODUCT_NAME, REQUESTED_QTY, STATUS, CREATED_AT, CREATED_BY
      ) values (
        v_line_id, v_pick_plan_id, l.CUSTOMER_ORDER_ROW_ID, upper(substr(l.ARTICUL, 1, 40)),
        l.PRODUCT_NAME, nvl(l.ORDER_QTY, 0), 'OPEN', sysdate, substr(p_created_by, 1, 50)
      );

      for c in (
        select r.rowid REMAIN_ROWID,
               r.CELL,
               r.UID_POLETA,
               r.REMAIN,
               p.EXPIRY_DATE,
               p.CREATION_DATE,
               p.PROD_BATCH_ID,
               p.SSCC,
               p.UNIT_COUNT,
               nvl(br.IS_SHIPMENT_ALLOWED, 1) IS_SHIPMENT_ALLOWED
          from RRL_REMAINS r
          join RRL_PALLETS p
            on p.UID_PALLET = r.UID_POLETA
          left join RRL_PROD_BATCH_READY_V br
            on br.PROD_BATCH_ID = p.PROD_BATCH_ID
         where r.REMAIN > 0
           and upper(p.ARTICUL) = upper(l.ARTICUL)
         order by case when v_strategy = 'FEFO' then p.EXPIRY_DATE end nulls last,
                  case when v_strategy = 'FIFO' then p.CREATION_DATE end nulls last,
                  r.TIME_OF_LAST_UPDATE nulls last,
                  r.UID_POLETA
      ) loop
        exit when v_remaining <= 0;

        declare
          v_locked_remain number;
        begin
          select REMAIN
            into v_locked_remain
            from RRL_REMAINS
           where rowid = c.REMAIN_ROWID
           for update;

          if c.IS_SHIPMENT_ALLOWED = 0 then
            log_decision(
              v_pick_plan_id,
              v_line_id,
              'SKIP_NOT_READY',
              'Pallet skipped because batch is not allowed for shipment',
              '{"pallet":"' || replace(c.UID_POLETA, '"', '\"') || '"}',
              p_created_by
            );
          else
            v_candidate_available := greatest(nvl(v_locked_remain, 0) - active_reserved_qty(c.UID_POLETA, l.ARTICUL), 0);
            v_reserved_by_other := v_reserved_by_other + (nvl(v_locked_remain, 0) - v_candidate_available);

            if v_candidate_available > 0 then
              v_reserve_qty := least(v_remaining, v_candidate_available);
              if v_reserve_qty >= v_candidate_available then
                v_task_type := 'FULL_PALLET';
              else
                v_task_type := 'CASE_PICK';
              end if;

              v_target_cell := null;
              v_pick_sequence := null;
              v_pick_face_id := null;
              v_pick_route_cell_id := null;

              if v_task_type = 'CASE_PICK' then
                RRL_PICK_TOPOLOGY_API.resolve_pick_face(
                  p_ware_id => v_order.WARE_ID,
                  p_articul => l.ARTICUL,
                  p_target_cell => v_target_cell,
                  p_pick_sequence => v_pick_sequence,
                  p_pick_face_id => v_pick_face_id,
                  p_pick_route_cell_id => v_pick_route_cell_id
                );

                if v_target_cell is not null then
                  log_decision(
                    v_pick_plan_id,
                    v_line_id,
                    'PICK_FACE_SELECTED',
                    'Case-pick task assigned to configured pick face',
                    '{"articul":"' || replace(l.ARTICUL, '"', '\"') || '","targetCell":"' || replace(v_target_cell, '"', '\"') || '"}',
                    p_created_by
                  );
                else
                  log_decision(
                    v_pick_plan_id,
                    v_line_id,
                    'NO_PICK_FACE',
                    'No active pick face found for case-pick task',
                    '{"articul":"' || replace(l.ARTICUL, '"', '\"') || '"}',
                    p_created_by
                  );
                end if;
              end if;

              select RRL_PICK_TASK_SQ.nextval into v_task_id from dual;
              insert into RRL_PICK_TASK (
                PICK_TASK_ID, PICK_PLAN_ID, PICK_PLAN_LINE_ID, CUSTOMER_ORDER_ID, CUSTOMER_ID,
                TASK_TYPE, STATUS, ARTICUL, PALLET_UID, SSCC, PROD_BATCH_ID,
                SOURCE_CELL_CODE, TARGET_CELL_CODE, QTY, PICK_SEQUENCE,
                PICK_FACE_ID, PICK_ROUTE_CELL_ID, CREATED_AT, CREATED_BY
              ) values (
                v_task_id, v_pick_plan_id, v_line_id, p_customer_order_id, v_order.CUSTOMER_ID,
                v_task_type, 'NEW', upper(substr(l.ARTICUL, 1, 40)), c.UID_POLETA,
                c.SSCC, c.PROD_BATCH_ID, c.CELL, v_target_cell, v_reserve_qty,
                v_pick_sequence, v_pick_face_id, v_pick_route_cell_id, sysdate, substr(p_created_by, 1, 50)
              );

              insert into RRL_PICK_RESERVATION (
                PICK_RESERVATION_ID, PICK_PLAN_ID, PICK_PLAN_LINE_ID, PICK_TASK_ID,
                CUSTOMER_ORDER_ID, CUSTOMER_ID, RESERVATION_LEVEL, RESERVATION_STATUS,
                RESERVATION_SCOPE, PALLET_UID, SSCC, ARTICUL, PROD_BATCH_ID,
                SOURCE_CELL_CODE, RESERVED_QTY, CREATED_AT, CREATED_BY
              ) values (
                RRL_PICK_RESERVATION_SQ.nextval, v_pick_plan_id, v_line_id, v_task_id,
                p_customer_order_id, v_order.CUSTOMER_ID, 'SOFT', 'ACTIVE',
                case when v_task_type = 'FULL_PALLET' then 'PALLET' else 'CASE' end,
                c.UID_POLETA, c.SSCC, upper(substr(l.ARTICUL, 1, 40)), c.PROD_BATCH_ID,
                c.CELL, v_reserve_qty, sysdate, substr(p_created_by, 1, 50)
              );

              v_line_planned := v_line_planned + v_reserve_qty;
              v_remaining := v_remaining - v_reserve_qty;
            end if;
          end if;
        exception
          when no_data_found then
            null;
        end;
      end loop;

      v_line_shortage := greatest(nvl(l.ORDER_QTY, 0) - v_line_planned, 0);
      v_planned_total := v_planned_total + v_line_planned;
      v_shortage_total := v_shortage_total + v_line_shortage;

      update RRL_PICK_PLAN_LINE
         set PLANNED_QTY = v_line_planned,
             FULL_PALLET_QTY = nvl((
               select sum(QTY)
                 from RRL_PICK_TASK
                where PICK_PLAN_LINE_ID = v_line_id
                  and TASK_TYPE = 'FULL_PALLET'
             ), 0),
             CASE_PICK_QTY = nvl((
               select sum(QTY)
                 from RRL_PICK_TASK
                where PICK_PLAN_LINE_ID = v_line_id
                  and TASK_TYPE = 'CASE_PICK'
             ), 0),
             SHORTAGE_QTY = v_line_shortage,
             STATUS = case
               when v_line_shortage = 0 then 'PLANNED_FULL'
               when v_line_planned > 0 then 'PLANNED_PARTIAL'
               else 'NO_STOCK'
             end,
             UPDATED_AT = sysdate,
             UPDATED_BY = substr(p_created_by, 1, 50)
       where PICK_PLAN_LINE_ID = v_line_id;

      if v_line_shortage > 0 then
        insert into RRL_PICK_SHORTAGE (
          PICK_SHORTAGE_ID, PICK_PLAN_ID, PICK_PLAN_LINE_ID,
          CUSTOMER_ORDER_ID, CUSTOMER_ORDER_ROW_ID, CUSTOMER_ID, ARTICUL,
          REQUESTED_QTY, AVAILABLE_QTY, RESERVED_BY_OTHER_QTY, PLANNED_QTY,
          SHORTAGE_QTY, REASON_CODE, REASON_TEXT, CREATED_AT, CREATED_BY
        ) values (
          RRL_PICK_SHORTAGE_SQ.nextval, v_pick_plan_id, v_line_id,
          p_customer_order_id, l.CUSTOMER_ORDER_ROW_ID, v_order.CUSTOMER_ID,
          upper(substr(l.ARTICUL, 1, 40)), nvl(l.ORDER_QTY, 0),
          v_line_planned, v_reserved_by_other, v_line_planned,
          v_line_shortage, 'NO_FREE_STOCK',
          'Free stock is not enough after active reservations',
          sysdate, substr(p_created_by, 1, 50)
        );
      end if;
    end loop;

    if v_requested_total = 0 then
      v_status := 'NO_STOCK';
    elsif v_planned_total = 0 then
      v_status := 'NO_STOCK';
    elsif v_shortage_total > 0 then
      v_status := 'PLANNED_PARTIAL';
    else
      v_status := 'PLANNED_FULL';
    end if;

    update RRL_PICK_PLAN
       set STATUS = v_status,
           TOTAL_ORDER_QTY = v_requested_total,
           TOTAL_PLANNED_QTY = v_planned_total,
           TOTAL_SHORTAGE_QTY = v_shortage_total,
           UPDATED_AT = sysdate,
           UPDATED_BY = substr(p_created_by, 1, 50)
     where PICK_PLAN_ID = v_pick_plan_id;

    log_decision(
      v_pick_plan_id,
      null,
      'PLAN_CREATED',
      'Picking plan created with soft reservations',
      '{"requested":' || to_char(v_requested_total) || ',"planned":' || to_char(v_planned_total) || ',"shortage":' || to_char(v_shortage_total) || '}',
      p_created_by
    );

    return v_pick_plan_id;
  end create_plan;

  procedure cancel_plan(
    p_pick_plan_id number,
    p_updated_by   varchar2 default null
  ) is
  begin
    update RRL_PICK_RESERVATION
       set RESERVATION_STATUS = 'RELEASED',
           RELEASED_AT = sysdate,
           UPDATED_AT = sysdate,
           UPDATED_BY = substr(p_updated_by, 1, 50)
     where PICK_PLAN_ID = p_pick_plan_id
       and RESERVATION_STATUS = 'ACTIVE';

    update RRL_PICK_TASK
       set STATUS = 'CANCELLED',
           ERROR_TEXT = 'Plan cancelled before execution',
           UPDATED_AT = sysdate
     where PICK_PLAN_ID = p_pick_plan_id
       and STATUS in ('NEW', 'ASSIGNED');

    update RRL_PICK_PLAN
       set STATUS = 'CANCELLED',
           UPDATED_AT = sysdate,
           UPDATED_BY = substr(p_updated_by, 1, 50)
     where PICK_PLAN_ID = p_pick_plan_id
       and STATUS not in ('DONE');

    log_decision(
      p_pick_plan_id,
      null,
      'PLAN_CANCELLED',
      'Picking plan cancelled and active reservations released',
      null,
      p_updated_by
    );
  end cancel_plan;
end RRL_PICKING_API;
/

insert into RIGHTS (RIGHT1, USER_GROUP, ID, DESCR)
select s.RIGHT1,
       'GLOBAL_ADMIN',
       (select nvl(max(ID), 0) from RIGHTS) + row_number() over (order by s.RIGHT1),
       s.DESCR
  from (
    select 'PICK_TOPOLOGY_VIEW' RIGHT1, 'View pick routes and pick faces' DESCR from dual
    union all select 'PICK_TOPOLOGY_EDIT', 'Edit pick routes and pick faces' from dual
  ) s
 where not exists (
   select 1
     from RIGHTS r
    where r.USER_GROUP = 'GLOBAL_ADMIN'
      and upper(r.RIGHT1) = s.RIGHT1
 );

insert into RRL_SCHEMA_MIGRATIONS (MIGRATION_ID, APPLIED_AT, DESCRIPTION)
select '2026-05-17-017-pick-face-route',
       sysdate,
       'Pick route, pick face and case-pick task sequencing'
  from dual
 where not exists (
   select 1
     from RRL_SCHEMA_MIGRATIONS
    where MIGRATION_ID = '2026-05-17-017-pick-face-route'
 );

commit;

prompt [migration 2026-05-17-017] done
