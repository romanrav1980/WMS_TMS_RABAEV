prompt [migration 2026-05-22-042] warehouse map draft publish API - apply

update RRL_PICK_ROUTE_CELL
   set ACTIVE = 0,
       UPDATED_AT = sysdate,
       UPDATED_BY = '042_MAP_API'
 where PICK_ROUTE_CELL_ID in (
   select PICK_ROUTE_CELL_ID
     from (
       select PICK_ROUTE_CELL_ID,
              row_number() over (
                partition by PICK_ROUTE_ID, CELL_SLOT_ID
                order by PICK_SEQUENCE, PICK_ROUTE_CELL_ID
              ) as RN
         from RRL_PICK_ROUTE_CELL
        where ACTIVE = 1
          and CELL_SLOT_ID is not null
     )
    where RN > 1
 );

declare
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
  ensure_index('RRL_PICK_ROUTE_CELL_UX_SLOT',
    q'[create unique index RRL_PICK_ROUTE_CELL_UX_SLOT on RRL_PICK_ROUTE_CELL (
       case when ACTIVE = 1 and CELL_SLOT_ID is not null then PICK_ROUTE_ID end,
       case when ACTIVE = 1 and CELL_SLOT_ID is not null then CELL_SLOT_ID end
    )]');
end;
/

create or replace package RRL_WAREHOUSE_MAP_API as
  function VALIDATE_DRAFT(
    p_canvas_id     number,
    p_pick_route_id number default null
  ) return clob;

  procedure PUBLISH_DRAFT(
    p_canvas_id     number,
    p_pick_route_id number default null,
    p_published_by  varchar2 default null
  );
end RRL_WAREHOUSE_MAP_API;
/

create or replace package body RRL_WAREHOUSE_MAP_API as
  function count_validation_errors(
    p_canvas_id     number,
    p_pick_route_id number
  ) return number is
    v_errors number := 0;
    v_route_topology_id number;
  begin
    select v_errors + count(*) into v_errors
      from RRL_WAREHOUSE_MAP_CAMERA
     where CANVAS_ID = p_canvas_id
       and ACTIVE = 1
       and (WIDTH_M <= 0 or DEPTH_M <= 0 or HEIGHT_M <= 0 or DEFAULT_PASSAGE_WIDTH_M <= 0);

    select v_errors + count(*) into v_errors
      from RRL_WAREHOUSE_MAP_PASSAGE
     where CANVAS_ID = p_canvas_id
       and ACTIVE = 1
       and WIDTH_M <= 0;

    select v_errors + count(*) into v_errors
      from (
        select CANVAS_ID, upper(CAMERA_CODE)
          from RRL_WAREHOUSE_MAP_CAMERA
         where CANVAS_ID = p_canvas_id
           and ACTIVE = 1
         group by CANVAS_ID, upper(CAMERA_CODE)
        having count(*) > 1
      );

    if p_pick_route_id is not null then
      begin
        select TOPOLOGY_ID into v_route_topology_id
          from RRL_PICK_ROUTE
         where PICK_ROUTE_ID = p_pick_route_id;
      exception
        when no_data_found then
          v_errors := v_errors + 1;
          v_route_topology_id := null;
      end;

      select v_errors + count(*) into v_errors
        from (
          select PICK_ROUTE_ID, PICK_SEQUENCE
            from RRL_PICK_ROUTE_CELL
           where PICK_ROUTE_ID = p_pick_route_id
             and ACTIVE = 1
           group by PICK_ROUTE_ID, PICK_SEQUENCE
          having count(*) > 1
        );

      select v_errors + count(*) into v_errors
        from (
          select PICK_ROUTE_ID, TOPOLOGY_CELL_ID
            from RRL_PICK_ROUTE_CELL
           where PICK_ROUTE_ID = p_pick_route_id
             and TOPOLOGY_CELL_ID is not null
             and ACTIVE = 1
           group by PICK_ROUTE_ID, TOPOLOGY_CELL_ID
          having count(*) > 1
        );

      select v_errors + count(*) into v_errors
        from (
          select PICK_ROUTE_ID, CELL_SLOT_ID
            from RRL_PICK_ROUTE_CELL
           where PICK_ROUTE_ID = p_pick_route_id
             and CELL_SLOT_ID is not null
             and ACTIVE = 1
           group by PICK_ROUTE_ID, CELL_SLOT_ID
          having count(*) > 1
        );

      select v_errors + count(*) into v_errors
        from RRL_PICK_ROUTE_CELL rc
        join RRL_TOPOLOGY_CELL_SLOT s
          on s.CELL_SLOT_ID = rc.CELL_SLOT_ID
       where rc.PICK_ROUTE_ID = p_pick_route_id
         and rc.ACTIVE = 1
         and s.SLOT_KIND <> 'PICK_FACE_SLOT';

      select v_errors + count(*) into v_errors
        from RRL_PICK_ROUTE_CELL rc
        join RRL_TOPOLOGY_CELL c
          on c.TOPOLOGY_CELL_ID = rc.TOPOLOGY_CELL_ID
       where rc.PICK_ROUTE_ID = p_pick_route_id
         and rc.ACTIVE = 1
         and c.CELL_KIND not in ('PICK_FACE', 'FRACTIONAL_PICK_FACE');

      select v_errors + count(*) into v_errors
        from RRL_PICK_ROUTE_CELL rc
       where rc.PICK_ROUTE_ID = p_pick_route_id
         and rc.ACTIVE = 1
         and rc.TOPOLOGY_CELL_ID is null
         and rc.CELL_SLOT_ID is null;
    end if;

    return v_errors;
  end count_validation_errors;

  function VALIDATE_DRAFT(
    p_canvas_id     number,
    p_pick_route_id number default null
  ) return clob is
    v_canvas_count number;
    v_errors number;
    v_route_rows number := 0;
    v_storage_slot_rows number := 0;
    v_non_pick_cell_rows number := 0;
  begin
    select count(*) into v_canvas_count
      from RRL_WAREHOUSE_MAP_CANVAS
     where CANVAS_ID = p_canvas_id
       and ACTIVE = 1;
    if v_canvas_count = 0 then
      return '{"valid":false,"error_count":1,"errors":["canvas_not_found"]}';
    end if;

    if p_pick_route_id is not null then
      select count(*) into v_route_rows
        from RRL_PICK_ROUTE_CELL
       where PICK_ROUTE_ID = p_pick_route_id
         and ACTIVE = 1;

      select count(*) into v_storage_slot_rows
        from RRL_PICK_ROUTE_CELL rc
        join RRL_TOPOLOGY_CELL_SLOT s
          on s.CELL_SLOT_ID = rc.CELL_SLOT_ID
       where rc.PICK_ROUTE_ID = p_pick_route_id
         and rc.ACTIVE = 1
         and s.SLOT_KIND <> 'PICK_FACE_SLOT';

      select count(*) into v_non_pick_cell_rows
        from RRL_PICK_ROUTE_CELL rc
        join RRL_TOPOLOGY_CELL c
          on c.TOPOLOGY_CELL_ID = rc.TOPOLOGY_CELL_ID
       where rc.PICK_ROUTE_ID = p_pick_route_id
         and rc.ACTIVE = 1
         and c.CELL_KIND not in ('PICK_FACE', 'FRACTIONAL_PICK_FACE');
    end if;

    v_errors := count_validation_errors(p_canvas_id, p_pick_route_id);
    return '{"valid":' || case when v_errors = 0 then 'true' else 'false' end ||
           ',"error_count":' || to_char(v_errors) ||
           ',"route_row_count":' || to_char(v_route_rows) ||
           ',"storage_slot_route_rows":' || to_char(v_storage_slot_rows) ||
           ',"non_pick_cell_route_rows":' || to_char(v_non_pick_cell_rows) ||
           '}';
  end VALIDATE_DRAFT;

  procedure PUBLISH_DRAFT(
    p_canvas_id     number,
    p_pick_route_id number default null,
    p_published_by  varchar2 default null
  ) is
    v_errors number;
    v_topology_id number;
  begin
    v_errors := count_validation_errors(p_canvas_id, p_pick_route_id);
    if v_errors > 0 then
      raise_application_error(-20420, 'Warehouse map draft validation failed: ' || to_char(v_errors));
    end if;

    update RRL_WAREHOUSE_MAP_CANVAS
       set STATUS = 'PUBLISHED',
           PUBLISHED_AT = sysdate,
           PUBLISHED_BY = substr(nvl(p_published_by, user), 1, 50),
           UPDATED_AT = sysdate,
           UPDATED_BY = substr(nvl(p_published_by, user), 1, 50)
     where CANVAS_ID = p_canvas_id
       and ACTIVE = 1;

    if sql%rowcount = 0 then
      raise_application_error(-20421, 'Canvas not found or inactive');
    end if;

    if p_pick_route_id is not null then
      select TOPOLOGY_ID into v_topology_id
        from RRL_PICK_ROUTE
       where PICK_ROUTE_ID = p_pick_route_id;

      update RRL_PICK_ROUTE
         set STATUS = 'ARCHIVED',
             ACTIVE = 0,
             UPDATED_AT = sysdate,
             UPDATED_BY = substr(nvl(p_published_by, user), 1, 50)
       where TOPOLOGY_ID = v_topology_id
         and ROUTE_KIND = 'PICK'
         and PICK_ROUTE_ID <> p_pick_route_id
         and ACTIVE = 1
         and STATUS <> 'ARCHIVED';

      update RRL_PICK_ROUTE
         set STATUS = 'PUBLISHED',
             ACTIVE = 1,
             UPDATED_AT = sysdate,
             UPDATED_BY = substr(nvl(p_published_by, user), 1, 50)
       where PICK_ROUTE_ID = p_pick_route_id;
    end if;
  end PUBLISH_DRAFT;
end RRL_WAREHOUSE_MAP_API;
/

merge into RRL_SCHEMA_MIGRATIONS d
using (
  select '2026-05-22-042-warehouse-map-draft-publish-api' migration_id,
         'Oracle validation and publish boundary for saved warehouse map canvas and pick-route draft rows' description,
         '042_apply.sql' script_name,
         '042_rollback.sql' rollback_script
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

prompt [migration 2026-05-22-042] apply done
