package body RRL_PICK_TOPOLOGY_API as
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
