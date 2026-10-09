declare n number;begin select count(*) into n from RRL_STOCK_OPERATION; if n>0 then raise_application_error(-20808,'POSTED_OPERATIONS_PREVENT_CODE_ROLLBACK');end if;end;
/
create or replace package RRL_PICK_WAVE_META authid definer accessible by(package RRL_STOCK_WAVE_LAUNCH_CMD,package RRL_PICK_WAVE_API) as
  function create_wave(
    p_wave_code         varchar2 default null,
    p_wave_name         varchar2 default null,
    p_ware_id           number default null,
    p_route_id          number default null,
    p_dock_id           number default null,
    p_planned_start_at  date default null,
    p_planned_finish_at date default null,
    p_max_customers     number default 30,
    p_created_by        varchar2 default null
  ) return number;

  procedure add_plan(
    p_pick_wave_id number,
    p_pick_plan_id number,
    p_created_by   varchar2 default null
  );

  procedure preview_wave(
    p_pick_wave_id number,
    p_updated_by   varchar2 default null
  );

  procedure launch_wave(
    p_pick_wave_id number,
    p_launched_by  varchar2 default null
  );

  procedure release_reservations(
    p_pick_wave_id number,
    p_updated_by   varchar2 default null
  );

  procedure cancel_wave(
    p_pick_wave_id number,
    p_reason       varchar2 default null,
    p_updated_by   varchar2 default null
  );
end RRL_PICK_WAVE_META;
/

create or replace package RRL_PICK_WAVE_API as
  function create_wave(
    p_wave_code         varchar2 default null,
    p_wave_name         varchar2 default null,
    p_ware_id           number default null,
    p_route_id          number default null,
    p_dock_id           number default null,
    p_planned_start_at  date default null,
    p_planned_finish_at date default null,
    p_max_customers     number default 30,
    p_created_by        varchar2 default null
  ) return number;

  procedure add_plan(
    p_pick_wave_id number,
    p_pick_plan_id number,
    p_created_by   varchar2 default null
  );

  procedure preview_wave(
    p_pick_wave_id number,
    p_updated_by   varchar2 default null
  );

  procedure launch_wave(
    p_pick_wave_id number,
    p_launched_by  varchar2 default null
  );

  procedure release_reservations(
    p_pick_wave_id number,
    p_updated_by   varchar2 default null
  );

  procedure cancel_wave(
    p_pick_wave_id number,
    p_reason       varchar2 default null,
    p_updated_by   varchar2 default null
  );
end RRL_PICK_WAVE_API;
/

create or replace package RRL_STOCK_DOC_RESERVE_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_release(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_release(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_POSTING_API authid definer as
 procedure prepare_command(p_request clob,p_actor varchar2,p_replay out clob,p_hints clob default null);
 procedure execute_prepared(p_result out clob);
 procedure reset_connection;
end;
/

create or replace package RRL_STOCK_TRANSFER_CORE authid definer
 accessible by(package RRL_STOCK_INTERNAL_CMD,package RRL_STOCK_POSTING_API,package RRL_STOCK_TASK_CORE,
 package RRL_STOCK_MES_MOVEMENT_CORE,package RRL_STOCK_RECEIPT_CORE,package RRL_STOCK_MOVE_CORE,package RRL_STOCK_MES_CORE) as
 procedure move(p_uid varchar2,p_target_uid varchar2,p_from varchar2,p_to varchar2,p_qty number,
  p_uom varchar2,p_uom_version number,p_warehouse number,p_actor varchar2,p_line number,
  p_reservation number default null,p_units clob default null,p_new_reservation number default null,p_target_slot number default null,p_source_warehouse number default null,p_location_mode varchar2 default 'ORDINARY');
end;
/

create or replace package body RRL_PICK_WAVE_META as
  procedure write_audit(
    p_pick_wave_id number,
    p_event_type   varchar2,
    p_message_text varchar2,
    p_payload_json clob default null,
    p_created_by   varchar2 default null
  ) is
  begin
    insert into RRL_PICK_WAVE_AUDIT (
      PICK_WAVE_AUDIT_ID, PICK_WAVE_ID, EVENT_TYPE, MESSAGE_TEXT,
      PAYLOAD_JSON, CREATED_AT, CREATED_BY
    ) values (
      RRL_PICK_WAVE_AUDIT_SQ.nextval, p_pick_wave_id, substr(p_event_type, 1, 50),
      substr(p_message_text, 1, 1000), p_payload_json, sysdate, substr(p_created_by, 1, 50)
    );
  end write_audit;

  procedure refresh_counters(p_pick_wave_id number, p_updated_by varchar2 default null) is
  begin
    update RRL_PICK_WAVE w
       set CUSTOMER_COUNT = (
             select count(distinct CUSTOMER_ID)
               from RRL_PICK_WAVE_ORDER
              where PICK_WAVE_ID = p_pick_wave_id
                and STATUS = 'ACTIVE'
           ),
           ORDER_COUNT = (
             select count(distinct CUSTOMER_ORDER_ID)
               from RRL_PICK_WAVE_ORDER
              where PICK_WAVE_ID = p_pick_wave_id
                and STATUS = 'ACTIVE'
           ),
           PLAN_COUNT = (
             select count(*)
               from RRL_PICK_WAVE_ORDER
              where PICK_WAVE_ID = p_pick_wave_id
                and STATUS = 'ACTIVE'
           ),
           TASK_COUNT = (
             select count(*)
               from RRL_PICK_WAVE_TASK
              where PICK_WAVE_ID = p_pick_wave_id
                and STATUS <> 'CANCELLED'
           ),
           HARD_RESERVE_QTY = (
             select nvl(sum(RESERVED_QTY), 0)
               from RRL_PICK_WAVE_RESERVATION
              where PICK_WAVE_ID = p_pick_wave_id
                and RESERVATION_STATUS = 'HARD'
           ),
           UPDATED_AT = sysdate,
           UPDATED_BY = substr(p_updated_by, 1, 50)
     where PICK_WAVE_ID = p_pick_wave_id;
  end refresh_counters;

  procedure clear_preview(p_pick_wave_id number) is
  begin
    delete from RRL_PICK_WAVE_SHORTAGE where PICK_WAVE_ID = p_pick_wave_id;
    delete from RRL_PICK_WAVE_DEMAND where PICK_WAVE_ID = p_pick_wave_id;
    delete from RRL_PICK_WAVE_LINE where PICK_WAVE_ID = p_pick_wave_id;
  end clear_preview;

  function create_wave(
    p_wave_code         varchar2 default null,
    p_wave_name         varchar2 default null,
    p_ware_id           number default null,
    p_route_id          number default null,
    p_dock_id           number default null,
    p_planned_start_at  date default null,
    p_planned_finish_at date default null,
    p_max_customers     number default 30,
    p_created_by        varchar2 default null
  ) return number is
    v_id number;
    v_code varchar2(50);
  begin
    select RRL_PICK_WAVE_SQ.nextval into v_id from dual;
    v_code := nvl(substr(p_wave_code, 1, 50), 'WAVE-' || to_char(sysdate, 'YYYYMMDD') || '-' || to_char(v_id));

    insert into RRL_PICK_WAVE (
      PICK_WAVE_ID, WAVE_CODE, WAVE_NAME, WARE_ID, ROUTE_ID, DOCK_ID,
      STATUS, WAVE_KIND, PLANNED_START_AT, PLANNED_FINISH_AT, MAX_CUSTOMERS,
      CREATED_AT, CREATED_BY
    ) values (
      v_id, v_code, substr(p_wave_name, 1, 255), p_ware_id, p_route_id, p_dock_id,
      'DRAFT', 'CUSTOMER_ORDER', p_planned_start_at, p_planned_finish_at,
      nvl(p_max_customers, 30), sysdate, substr(p_created_by, 1, 50)
    );

    write_audit(v_id, 'WAVE_CREATED', 'Wave created', '{"waveCode":"' || replace(v_code, '"', '\"') || '"}', p_created_by);
    return v_id;
  end create_wave;

  procedure add_plan(
    p_pick_wave_id number,
    p_pick_plan_id number,
    p_created_by   varchar2 default null
  ) is
    v_wave RRL_PICK_WAVE%rowtype;
    v_plan RRL_PICK_PLAN%rowtype;
    v_order_no varchar2(100);
    v_existing number;
    v_customer_count number;
    v_customer_already number;
  begin
    select *
      into v_wave
      from RRL_PICK_WAVE
     where PICK_WAVE_ID = p_pick_wave_id
     for update;

    if v_wave.STATUS not in ('DRAFT', 'PREVIEW') then
      raise_application_error(-20990, 'wave does not accept new plans');
    end if;

    select *
      into v_plan
      from RRL_PICK_PLAN
     where PICK_PLAN_ID = p_pick_plan_id;

    if v_plan.STATUS not in ('PLANNED_FULL', 'PLANNED_PARTIAL') then
      raise_application_error(-20991, 'pick plan must be planned before adding to wave');
    end if;

    if v_wave.WARE_ID is not null and v_plan.WARE_ID is not null and v_wave.WARE_ID <> v_plan.WARE_ID then
      raise_application_error(-20992, 'pick plan warehouse does not match wave warehouse');
    end if;

    select count(*)
      into v_existing
      from RRL_PICK_WAVE_ORDER wo
      join RRL_PICK_WAVE w
        on w.PICK_WAVE_ID = wo.PICK_WAVE_ID
     where wo.PICK_PLAN_ID = p_pick_plan_id
       and wo.STATUS = 'ACTIVE'
       and w.STATUS in ('DRAFT', 'PREVIEW', 'LAUNCHED')
       and wo.PICK_WAVE_ID <> p_pick_wave_id;

    if v_existing > 0 then
      raise_application_error(-20993, 'pick plan is already assigned to another open wave');
    end if;

    select count(*)
      into v_existing
      from RRL_PICK_WAVE_ORDER
     where PICK_WAVE_ID = p_pick_wave_id
       and PICK_PLAN_ID = p_pick_plan_id
       and STATUS = 'ACTIVE';

    if v_existing > 0 then
      return;
    end if;

    select count(distinct CUSTOMER_ID)
      into v_customer_count
      from RRL_PICK_WAVE_ORDER
     where PICK_WAVE_ID = p_pick_wave_id
       and STATUS = 'ACTIVE';

    select count(*)
      into v_customer_already
      from RRL_PICK_WAVE_ORDER
     where PICK_WAVE_ID = p_pick_wave_id
       and STATUS = 'ACTIVE'
       and nvl(CUSTOMER_ID, -1) = nvl(v_plan.CUSTOMER_ID, -1);

    if v_customer_already = 0 and v_customer_count >= nvl(v_wave.MAX_CUSTOMERS, 30) then
      raise_application_error(-20994, 'wave customer limit exceeded');
    end if;

    select ORDER_NO
      into v_order_no
      from RRL_CUSTOMER_ORDER
     where CUSTOMER_ORDER_ID = v_plan.CUSTOMER_ORDER_ID;

    insert into RRL_PICK_WAVE_ORDER (
      PICK_WAVE_ORDER_ID, PICK_WAVE_ID, PICK_PLAN_ID, CUSTOMER_ORDER_ID,
      CUSTOMER_ID, ORDER_NO, STATUS, CREATED_AT, CREATED_BY
    ) values (
      RRL_PICK_WAVE_ORDER_SQ.nextval, p_pick_wave_id, p_pick_plan_id, v_plan.CUSTOMER_ORDER_ID,
      v_plan.CUSTOMER_ID, substr(v_order_no, 1, 100), 'ACTIVE', sysdate, substr(p_created_by, 1, 50)
    );

    if v_wave.STATUS = 'PREVIEW' then
      clear_preview(p_pick_wave_id);
      update RRL_PICK_WAVE
         set STATUS = 'DRAFT',
             UPDATED_AT = sysdate,
             UPDATED_BY = substr(p_created_by, 1, 50)
       where PICK_WAVE_ID = p_pick_wave_id;
    end if;

    refresh_counters(p_pick_wave_id, p_created_by);
    write_audit(p_pick_wave_id, 'PLAN_ADDED', 'Pick plan added to wave', '{"pickPlanId":' || to_char(p_pick_plan_id) || '}', p_created_by);
  end add_plan;

  procedure preview_wave(
    p_pick_wave_id number,
    p_updated_by   varchar2 default null
  ) is
    v_status varchar2(30);
    v_plan_count number;
  begin
    select STATUS
      into v_status
      from RRL_PICK_WAVE
     where PICK_WAVE_ID = p_pick_wave_id
     for update;

    if v_status not in ('DRAFT', 'PREVIEW') then
      raise_application_error(-20995, 'wave cannot be previewed in current status');
    end if;

    select count(*)
      into v_plan_count
      from RRL_PICK_WAVE_ORDER
     where PICK_WAVE_ID = p_pick_wave_id
       and STATUS = 'ACTIVE';

    if v_plan_count = 0 then
      raise_application_error(-20996, 'wave has no active plans');
    end if;

    clear_preview(p_pick_wave_id);

    insert into RRL_PICK_WAVE_LINE (
      PICK_WAVE_LINE_ID, PICK_WAVE_ID, PICK_WAVE_ORDER_ID, PICK_PLAN_ID,
      PICK_PLAN_LINE_ID, CUSTOMER_ORDER_ROW_ID, ARTICUL, REQUESTED_QTY,
      PLANNED_QTY, SHORTAGE_QTY, STATUS, CREATED_AT, CREATED_BY
    )
    select RRL_PICK_WAVE_LINE_SQ.nextval,
           wo.PICK_WAVE_ID,
           wo.PICK_WAVE_ORDER_ID,
           wo.PICK_PLAN_ID,
           pl.PICK_PLAN_LINE_ID,
           pl.CUSTOMER_ORDER_ROW_ID,
           pl.ARTICUL,
           pl.REQUESTED_QTY,
           pl.PLANNED_QTY,
           pl.SHORTAGE_QTY,
           'PREVIEW',
           sysdate,
           substr(p_updated_by, 1, 50)
      from RRL_PICK_WAVE_ORDER wo
      join RRL_PICK_PLAN_LINE pl
        on pl.PICK_PLAN_ID = wo.PICK_PLAN_ID
     where wo.PICK_WAVE_ID = p_pick_wave_id
       and wo.STATUS = 'ACTIVE';

    insert into RRL_PICK_WAVE_DEMAND (
      PICK_WAVE_DEMAND_ID, PICK_WAVE_ID, ARTICUL, TASK_TYPE,
      TARGET_CELL_CODE, PICK_FACE_ID, PICK_ROUTE_CELL_ID, DEMAND_QTY,
      TASK_COUNT, CREATED_AT, CREATED_BY
    )
    select RRL_PICK_WAVE_DEMAND_SQ.nextval,
           q.PICK_WAVE_ID,
           q.ARTICUL,
           q.TASK_TYPE,
           q.TARGET_CELL_CODE,
           q.PICK_FACE_ID,
           q.PICK_ROUTE_CELL_ID,
           q.DEMAND_QTY,
           q.TASK_COUNT,
           sysdate,
           substr(p_updated_by, 1, 50)
      from (
        select wo.PICK_WAVE_ID,
               t.ARTICUL,
               t.TASK_TYPE,
               t.TARGET_CELL_CODE,
               t.PICK_FACE_ID,
               t.PICK_ROUTE_CELL_ID,
               sum(t.QTY) DEMAND_QTY,
               count(*) TASK_COUNT
          from RRL_PICK_WAVE_ORDER wo
          join RRL_PICK_TASK t
            on t.PICK_PLAN_ID = wo.PICK_PLAN_ID
         where wo.PICK_WAVE_ID = p_pick_wave_id
           and wo.STATUS = 'ACTIVE'
           and t.STATUS in ('NEW', 'ASSIGNED')
         group by wo.PICK_WAVE_ID, t.ARTICUL, t.TASK_TYPE, t.TARGET_CELL_CODE, t.PICK_FACE_ID, t.PICK_ROUTE_CELL_ID
      ) q;

    insert into RRL_PICK_WAVE_SHORTAGE (
      PICK_WAVE_SHORTAGE_ID, PICK_WAVE_ID, PICK_SHORTAGE_ID, PICK_PLAN_ID,
      CUSTOMER_ORDER_ID, CUSTOMER_ID, ARTICUL, REQUESTED_QTY, PLANNED_QTY,
      SHORTAGE_QTY, REASON_CODE, REASON_TEXT, CREATED_AT, CREATED_BY
    )
    select RRL_PICK_WAVE_SHORTAGE_SQ.nextval,
           wo.PICK_WAVE_ID,
           s.PICK_SHORTAGE_ID,
           s.PICK_PLAN_ID,
           s.CUSTOMER_ORDER_ID,
           s.CUSTOMER_ID,
           s.ARTICUL,
           s.REQUESTED_QTY,
           s.PLANNED_QTY,
           s.SHORTAGE_QTY,
           s.REASON_CODE,
           s.REASON_TEXT,
           sysdate,
           substr(p_updated_by, 1, 50)
      from RRL_PICK_WAVE_ORDER wo
      join RRL_PICK_SHORTAGE s
        on s.PICK_PLAN_ID = wo.PICK_PLAN_ID
     where wo.PICK_WAVE_ID = p_pick_wave_id
       and wo.STATUS = 'ACTIVE';

    update RRL_PICK_WAVE
       set STATUS = 'PREVIEW',
           UPDATED_AT = sysdate,
           UPDATED_BY = substr(p_updated_by, 1, 50)
     where PICK_WAVE_ID = p_pick_wave_id;

    refresh_counters(p_pick_wave_id, p_updated_by);
    write_audit(p_pick_wave_id, 'WAVE_PREVIEWED', 'Wave preview calculated', '{"plans":' || to_char(v_plan_count) || '}', p_updated_by);
  end preview_wave;

  procedure launch_wave(
    p_pick_wave_id number,
    p_launched_by  varchar2 default null
  ) is
    v_status varchar2(30);
    v_res_count number := 0;
    v_task_count number := 0;
    v_replenish_count number := 0;
  begin
    if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID') is null then raise_application_error(-20863,'WAVE_LAUNCH_REQUIRES_POSTING_CONTEXT');end if;
    select STATUS
      into v_status
      from RRL_PICK_WAVE
     where PICK_WAVE_ID = p_pick_wave_id
     for update;

    if v_status = 'DRAFT' then
      preview_wave(p_pick_wave_id, p_launched_by);
    end if;

    select STATUS
      into v_status
      from RRL_PICK_WAVE
     where PICK_WAVE_ID = p_pick_wave_id
     for update;

    if v_status <> 'PREVIEW' then
      raise_application_error(-20997, 'wave must be in PREVIEW status before launch');
    end if;

    for r in (
      select pr.PICK_RESERVATION_ID,
             pr.PICK_PLAN_ID,
             pr.PICK_PLAN_LINE_ID,
             pr.PICK_TASK_ID,
             pr.CUSTOMER_ORDER_ID,
             pr.CUSTOMER_ID,
             pr.PALLET_UID,
             pr.SSCC,
             pr.ARTICUL,
             pr.SOURCE_CELL_CODE,
             pr.RESERVED_QTY
        from RRL_PICK_WAVE_ORDER wo
        join RRL_PICK_RESERVATION pr
          on pr.PICK_PLAN_ID = wo.PICK_PLAN_ID
       where wo.PICK_WAVE_ID = p_pick_wave_id
         and wo.STATUS = 'ACTIVE'
         and pr.RESERVATION_STATUS = 'ACTIVE'
         and pr.RESERVATION_LEVEL = 'SOFT'
       order by pr.PICK_RESERVATION_ID
       for update
    ) loop
      update RRL_PICK_RESERVATION
         set RESERVATION_LEVEL = 'HARD',
             UPDATED_AT = sysdate,
             UPDATED_BY = substr(p_launched_by, 1, 50)
       where PICK_RESERVATION_ID = r.PICK_RESERVATION_ID;

      insert into RRL_PICK_WAVE_RESERVATION (
        PICK_WAVE_RESERVATION_ID, PICK_WAVE_ID, PICK_RESERVATION_ID, PICK_TASK_ID,
        PICK_PLAN_ID, PICK_PLAN_LINE_ID, CUSTOMER_ORDER_ID, CUSTOMER_ID,
        RESERVATION_STATUS, PALLET_UID, SSCC, ARTICUL, SOURCE_CELL_CODE,
        RESERVED_QTY, CREATED_AT, CREATED_BY
      ) values (
        RRL_PICK_WAVE_RES_SQ.nextval, p_pick_wave_id, r.PICK_RESERVATION_ID, r.PICK_TASK_ID,
        r.PICK_PLAN_ID, r.PICK_PLAN_LINE_ID, r.CUSTOMER_ORDER_ID, r.CUSTOMER_ID,
        'HARD', r.PALLET_UID, r.SSCC, r.ARTICUL, r.SOURCE_CELL_CODE,
        r.RESERVED_QTY, sysdate, substr(p_launched_by, 1, 50)
      );
      v_res_count := v_res_count + 1;
    end loop;

    if v_res_count = 0 then
      raise_application_error(-20998, 'wave has no active soft reservations to launch');
    end if;

    insert into RRL_PICK_WAVE_TASK (
      PICK_WAVE_TASK_ID, PICK_WAVE_ID, PICK_TASK_ID, TASK_TYPE, STATUS,
      ARTICUL, PALLET_UID, SOURCE_CELL_CODE, TARGET_CELL_CODE, QTY,
      PICK_SEQUENCE, PICK_FACE_ID, PICK_ROUTE_CELL_ID, CREATED_AT, CREATED_BY
    )
    select RRL_PICK_WAVE_TASK_SQ.nextval,
           p_pick_wave_id,
           t.PICK_TASK_ID,
           t.TASK_TYPE,
           'NEW',
           t.ARTICUL,
           t.PALLET_UID,
           t.SOURCE_CELL_CODE,
           t.TARGET_CELL_CODE,
           t.QTY,
           t.PICK_SEQUENCE,
           t.PICK_FACE_ID,
           t.PICK_ROUTE_CELL_ID,
           sysdate,
           substr(p_launched_by, 1, 50)
      from RRL_PICK_WAVE_ORDER wo
      join RRL_PICK_TASK t
        on t.PICK_PLAN_ID = wo.PICK_PLAN_ID
     where wo.PICK_WAVE_ID = p_pick_wave_id
       and wo.STATUS = 'ACTIVE'
       and t.STATUS in ('NEW', 'ASSIGNED')
       and not exists (
         select 1
           from RRL_PICK_WAVE_TASK wt
          where wt.PICK_WAVE_ID = p_pick_wave_id
            and wt.PICK_TASK_ID = t.PICK_TASK_ID
       );

    v_task_count := sql%rowcount;

    insert into RRL_PICK_WAVE_REPLENISH_TASK (
      PICK_WAVE_REPLENISH_TASK_ID, PICK_WAVE_ID, PICK_TASK_ID, STATUS,
      ARTICUL, PALLET_UID, SOURCE_CELL_CODE, TARGET_CELL_CODE, QTY,
      PICK_SEQUENCE, CREATED_AT, CREATED_BY
    )
    select RRL_PICK_WAVE_REPL_SQ.nextval,
           p_pick_wave_id,
           t.PICK_TASK_ID,
           'NEW',
           t.ARTICUL,
           t.PALLET_UID,
           t.SOURCE_CELL_CODE,
           t.TARGET_CELL_CODE,
           t.QTY,
           t.PICK_SEQUENCE,
           sysdate,
           substr(p_launched_by, 1, 50)
      from RRL_PICK_WAVE_ORDER wo
      join RRL_PICK_TASK t
        on t.PICK_PLAN_ID = wo.PICK_PLAN_ID
     where wo.PICK_WAVE_ID = p_pick_wave_id
       and wo.STATUS = 'ACTIVE'
       and t.TASK_TYPE = 'CASE_PICK'
       and t.TARGET_CELL_CODE is not null;

    v_replenish_count := sql%rowcount;

    update RRL_PICK_TASK
       set STATUS = 'ASSIGNED',
           UPDATED_AT = sysdate,
           UPDATED_BY = substr(p_launched_by, 1, 50)
     where PICK_TASK_ID in (
       select PICK_TASK_ID
         from RRL_PICK_WAVE_TASK
        where PICK_WAVE_ID = p_pick_wave_id
     )
       and STATUS = 'NEW';

    update RRL_PICK_PLAN
       set STATUS = 'RELEASED',
           UPDATED_AT = sysdate,
           UPDATED_BY = substr(p_launched_by, 1, 50)
     where PICK_PLAN_ID in (
       select PICK_PLAN_ID
         from RRL_PICK_WAVE_ORDER
        where PICK_WAVE_ID = p_pick_wave_id
          and STATUS = 'ACTIVE'
     )
       and STATUS in ('PLANNED_FULL', 'PLANNED_PARTIAL');

    update RRL_PICK_WAVE
       set STATUS = 'LAUNCHED',
           LAUNCHED_AT = sysdate,
           LAUNCHED_BY = substr(p_launched_by, 1, 50),
           UPDATED_AT = sysdate,
           UPDATED_BY = substr(p_launched_by, 1, 50)
     where PICK_WAVE_ID = p_pick_wave_id;

    refresh_counters(p_pick_wave_id, p_launched_by);
    write_audit(
      p_pick_wave_id,
      'WAVE_LAUNCHED',
      'Wave launched and soft reservations converted to hard reservations',
      '{"reservations":' || to_char(v_res_count) || ',"tasks":' || to_char(v_task_count) || ',"replenishmentTasks":' || to_char(v_replenish_count) || '}',
      p_launched_by
    );
  end launch_wave;

  procedure release_reservations(
    p_pick_wave_id number,
    p_updated_by   varchar2 default null
  ) is
    v_blocking_tasks number;
  begin
    select count(*)
      into v_blocking_tasks
      from RRL_PICK_WAVE_TASK
     where PICK_WAVE_ID = p_pick_wave_id
       and STATUS not in ('NEW', 'ASSIGNED', 'CANCELLED');

    if v_blocking_tasks > 0 then
      raise_application_error(-20999, 'wave has already started tasks; reservations cannot be released automatically');
    end if;

    update RRL_PICK_RESERVATION
       set RESERVATION_LEVEL = 'SOFT',
           RESERVATION_STATUS = 'ACTIVE',
           UPDATED_AT = sysdate,
           UPDATED_BY = substr(p_updated_by, 1, 50)
     where PICK_RESERVATION_ID in (
       select PICK_RESERVATION_ID
         from RRL_PICK_WAVE_RESERVATION
        where PICK_WAVE_ID = p_pick_wave_id
          and RESERVATION_STATUS = 'HARD'
     );

    update RRL_PICK_WAVE_RESERVATION
       set RESERVATION_STATUS = 'RELEASED',
           RELEASED_AT = sysdate,
           UPDATED_AT = sysdate,
           UPDATED_BY = substr(p_updated_by, 1, 50)
     where PICK_WAVE_ID = p_pick_wave_id
       and RESERVATION_STATUS = 'HARD';

    update RRL_PICK_TASK
       set STATUS = 'NEW',
           UPDATED_AT = sysdate,
           UPDATED_BY = substr(p_updated_by, 1, 50)
     where PICK_TASK_ID in (
       select PICK_TASK_ID
         from RRL_PICK_WAVE_TASK
        where PICK_WAVE_ID = p_pick_wave_id
          and STATUS in ('NEW', 'ASSIGNED')
     )
       and STATUS = 'ASSIGNED';

    update RRL_PICK_WAVE_TASK
       set STATUS = 'CANCELLED',
           UPDATED_AT = sysdate,
           UPDATED_BY = substr(p_updated_by, 1, 50)
     where PICK_WAVE_ID = p_pick_wave_id
       and STATUS in ('NEW', 'ASSIGNED');

    update RRL_PICK_WAVE_REPLENISH_TASK
       set STATUS = 'CANCELLED',
           UPDATED_AT = sysdate,
           UPDATED_BY = substr(p_updated_by, 1, 50)
     where PICK_WAVE_ID = p_pick_wave_id
       and STATUS in ('NEW', 'ASSIGNED');

    update RRL_PICK_PLAN p
       set STATUS = case when nvl(p.TOTAL_SHORTAGE_QTY, 0) > 0 then 'PLANNED_PARTIAL' else 'PLANNED_FULL' end,
           UPDATED_AT = sysdate,
           UPDATED_BY = substr(p_updated_by, 1, 50)
     where p.PICK_PLAN_ID in (
       select PICK_PLAN_ID
         from RRL_PICK_WAVE_ORDER
        where PICK_WAVE_ID = p_pick_wave_id
          and STATUS = 'ACTIVE'
     )
       and p.STATUS = 'RELEASED';

    update RRL_PICK_WAVE
       set STATUS = 'PREVIEW',
           UPDATED_AT = sysdate,
           UPDATED_BY = substr(p_updated_by, 1, 50)
     where PICK_WAVE_ID = p_pick_wave_id
       and STATUS = 'LAUNCHED';

    refresh_counters(p_pick_wave_id, p_updated_by);
    write_audit(p_pick_wave_id, 'RESERVATIONS_RELEASED', 'Hard reservations returned to soft reservation state', null, p_updated_by);
  end release_reservations;

  procedure cancel_wave(
    p_pick_wave_id number,
    p_reason       varchar2 default null,
    p_updated_by   varchar2 default null
  ) is
    v_status varchar2(30);
  begin
    select STATUS
      into v_status
      from RRL_PICK_WAVE
     where PICK_WAVE_ID = p_pick_wave_id
     for update;

    if v_status = 'LAUNCHED' then
      release_reservations(p_pick_wave_id, p_updated_by);
    elsif v_status not in ('DRAFT', 'PREVIEW', 'CANCELLED') then
      raise_application_error(-21000, 'wave cannot be cancelled in current status');
    end if;

    update RRL_PICK_WAVE
       set STATUS = 'CANCELLED',
           CANCELLED_AT = sysdate,
           CANCELLED_BY = substr(p_updated_by, 1, 50),
           COMMENT_TEXT = substr(nvl(p_reason, COMMENT_TEXT), 1, 1000),
           UPDATED_AT = sysdate,
           UPDATED_BY = substr(p_updated_by, 1, 50)
     where PICK_WAVE_ID = p_pick_wave_id;

    refresh_counters(p_pick_wave_id, p_updated_by);
    write_audit(p_pick_wave_id, 'WAVE_CANCELLED', 'Wave cancelled', substr(p_reason, 1, 1000), p_updated_by);
  end cancel_wave;
end RRL_PICK_WAVE_META;
/

create or replace package body RRL_PICK_WAVE_API as
  procedure write_audit(
    p_pick_wave_id number,
    p_event_type   varchar2,
    p_message_text varchar2,
    p_payload_json clob default null,
    p_created_by   varchar2 default null
  ) is
  begin
    insert into RRL_PICK_WAVE_AUDIT (
      PICK_WAVE_AUDIT_ID, PICK_WAVE_ID, EVENT_TYPE, MESSAGE_TEXT,
      PAYLOAD_JSON, CREATED_AT, CREATED_BY
    ) values (
      RRL_PICK_WAVE_AUDIT_SQ.nextval, p_pick_wave_id, substr(p_event_type, 1, 50),
      substr(p_message_text, 1, 1000), p_payload_json, sysdate, substr(p_created_by, 1, 50)
    );
  end write_audit;

  procedure refresh_counters(p_pick_wave_id number, p_updated_by varchar2 default null) is
  begin
    update RRL_PICK_WAVE w
       set CUSTOMER_COUNT = (
             select count(distinct CUSTOMER_ID)
               from RRL_PICK_WAVE_ORDER
              where PICK_WAVE_ID = p_pick_wave_id
                and STATUS = 'ACTIVE'
           ),
           ORDER_COUNT = (
             select count(distinct CUSTOMER_ORDER_ID)
               from RRL_PICK_WAVE_ORDER
              where PICK_WAVE_ID = p_pick_wave_id
                and STATUS = 'ACTIVE'
           ),
           PLAN_COUNT = (
             select count(*)
               from RRL_PICK_WAVE_ORDER
              where PICK_WAVE_ID = p_pick_wave_id
                and STATUS = 'ACTIVE'
           ),
           TASK_COUNT = (
             select count(*)
               from RRL_PICK_WAVE_TASK
              where PICK_WAVE_ID = p_pick_wave_id
                and STATUS <> 'CANCELLED'
           ),
           HARD_RESERVE_QTY = (
             select nvl(sum(RESERVED_QTY), 0)
               from RRL_PICK_WAVE_RESERVATION
              where PICK_WAVE_ID = p_pick_wave_id
                and RESERVATION_STATUS = 'HARD'
           ),
           UPDATED_AT = sysdate,
           UPDATED_BY = substr(p_updated_by, 1, 50)
     where PICK_WAVE_ID = p_pick_wave_id;
  end refresh_counters;

  procedure clear_preview(p_pick_wave_id number) is
  begin
    delete from RRL_PICK_WAVE_SHORTAGE where PICK_WAVE_ID = p_pick_wave_id;
    delete from RRL_PICK_WAVE_DEMAND where PICK_WAVE_ID = p_pick_wave_id;
    delete from RRL_PICK_WAVE_LINE where PICK_WAVE_ID = p_pick_wave_id;
  end clear_preview;

  function create_wave(
    p_wave_code         varchar2 default null,
    p_wave_name         varchar2 default null,
    p_ware_id           number default null,
    p_route_id          number default null,
    p_dock_id           number default null,
    p_planned_start_at  date default null,
    p_planned_finish_at date default null,
    p_max_customers     number default 30,
    p_created_by        varchar2 default null
  ) return number is
    v_id number;
    v_code varchar2(50);
  begin
    select RRL_PICK_WAVE_SQ.nextval into v_id from dual;
    v_code := nvl(substr(p_wave_code, 1, 50), 'WAVE-' || to_char(sysdate, 'YYYYMMDD') || '-' || to_char(v_id));

    insert into RRL_PICK_WAVE (
      PICK_WAVE_ID, WAVE_CODE, WAVE_NAME, WARE_ID, ROUTE_ID, DOCK_ID,
      STATUS, WAVE_KIND, PLANNED_START_AT, PLANNED_FINISH_AT, MAX_CUSTOMERS,
      CREATED_AT, CREATED_BY
    ) values (
      v_id, v_code, substr(p_wave_name, 1, 255), p_ware_id, p_route_id, p_dock_id,
      'DRAFT', 'CUSTOMER_ORDER', p_planned_start_at, p_planned_finish_at,
      nvl(p_max_customers, 30), sysdate, substr(p_created_by, 1, 50)
    );

    write_audit(v_id, 'WAVE_CREATED', 'Wave created', '{"waveCode":"' || replace(v_code, '"', '\"') || '"}', p_created_by);
    return v_id;
  end create_wave;

  procedure add_plan(
    p_pick_wave_id number,
    p_pick_plan_id number,
    p_created_by   varchar2 default null
  ) is
    v_wave RRL_PICK_WAVE%rowtype;
    v_plan RRL_PICK_PLAN%rowtype;
    v_order_no varchar2(100);
    v_existing number;
    v_customer_count number;
    v_customer_already number;
  begin
    select *
      into v_wave
      from RRL_PICK_WAVE
     where PICK_WAVE_ID = p_pick_wave_id
     for update;

    if v_wave.STATUS not in ('DRAFT', 'PREVIEW') then
      raise_application_error(-20990, 'wave does not accept new plans');
    end if;

    select *
      into v_plan
      from RRL_PICK_PLAN
     where PICK_PLAN_ID = p_pick_plan_id;

    if v_plan.STATUS not in ('PLANNED_FULL', 'PLANNED_PARTIAL') then
      raise_application_error(-20991, 'pick plan must be planned before adding to wave');
    end if;

    if v_wave.WARE_ID is not null and v_plan.WARE_ID is not null and v_wave.WARE_ID <> v_plan.WARE_ID then
      raise_application_error(-20992, 'pick plan warehouse does not match wave warehouse');
    end if;

    select count(*)
      into v_existing
      from RRL_PICK_WAVE_ORDER wo
      join RRL_PICK_WAVE w
        on w.PICK_WAVE_ID = wo.PICK_WAVE_ID
     where wo.PICK_PLAN_ID = p_pick_plan_id
       and wo.STATUS = 'ACTIVE'
       and w.STATUS in ('DRAFT', 'PREVIEW', 'LAUNCHED')
       and wo.PICK_WAVE_ID <> p_pick_wave_id;

    if v_existing > 0 then
      raise_application_error(-20993, 'pick plan is already assigned to another open wave');
    end if;

    select count(*)
      into v_existing
      from RRL_PICK_WAVE_ORDER
     where PICK_WAVE_ID = p_pick_wave_id
       and PICK_PLAN_ID = p_pick_plan_id
       and STATUS = 'ACTIVE';

    if v_existing > 0 then
      return;
    end if;

    select count(distinct CUSTOMER_ID)
      into v_customer_count
      from RRL_PICK_WAVE_ORDER
     where PICK_WAVE_ID = p_pick_wave_id
       and STATUS = 'ACTIVE';

    select count(*)
      into v_customer_already
      from RRL_PICK_WAVE_ORDER
     where PICK_WAVE_ID = p_pick_wave_id
       and STATUS = 'ACTIVE'
       and nvl(CUSTOMER_ID, -1) = nvl(v_plan.CUSTOMER_ID, -1);

    if v_customer_already = 0 and v_customer_count >= nvl(v_wave.MAX_CUSTOMERS, 30) then
      raise_application_error(-20994, 'wave customer limit exceeded');
    end if;

    select ORDER_NO
      into v_order_no
      from RRL_CUSTOMER_ORDER
     where CUSTOMER_ORDER_ID = v_plan.CUSTOMER_ORDER_ID;

    insert into RRL_PICK_WAVE_ORDER (
      PICK_WAVE_ORDER_ID, PICK_WAVE_ID, PICK_PLAN_ID, CUSTOMER_ORDER_ID,
      CUSTOMER_ID, ORDER_NO, STATUS, CREATED_AT, CREATED_BY
    ) values (
      RRL_PICK_WAVE_ORDER_SQ.nextval, p_pick_wave_id, p_pick_plan_id, v_plan.CUSTOMER_ORDER_ID,
      v_plan.CUSTOMER_ID, substr(v_order_no, 1, 100), 'ACTIVE', sysdate, substr(p_created_by, 1, 50)
    );

    if v_wave.STATUS = 'PREVIEW' then
      clear_preview(p_pick_wave_id);
      update RRL_PICK_WAVE
         set STATUS = 'DRAFT',
             UPDATED_AT = sysdate,
             UPDATED_BY = substr(p_created_by, 1, 50)
       where PICK_WAVE_ID = p_pick_wave_id;
    end if;

    refresh_counters(p_pick_wave_id, p_created_by);
    write_audit(p_pick_wave_id, 'PLAN_ADDED', 'Pick plan added to wave', '{"pickPlanId":' || to_char(p_pick_plan_id) || '}', p_created_by);
  end add_plan;

  procedure preview_wave(
    p_pick_wave_id number,
    p_updated_by   varchar2 default null
  ) is
    v_status varchar2(30);
    v_plan_count number;
  begin
    select STATUS
      into v_status
      from RRL_PICK_WAVE
     where PICK_WAVE_ID = p_pick_wave_id
     for update;

    if v_status not in ('DRAFT', 'PREVIEW') then
      raise_application_error(-20995, 'wave cannot be previewed in current status');
    end if;

    select count(*)
      into v_plan_count
      from RRL_PICK_WAVE_ORDER
     where PICK_WAVE_ID = p_pick_wave_id
       and STATUS = 'ACTIVE';

    if v_plan_count = 0 then
      raise_application_error(-20996, 'wave has no active plans');
    end if;

    clear_preview(p_pick_wave_id);

    insert into RRL_PICK_WAVE_LINE (
      PICK_WAVE_LINE_ID, PICK_WAVE_ID, PICK_WAVE_ORDER_ID, PICK_PLAN_ID,
      PICK_PLAN_LINE_ID, CUSTOMER_ORDER_ROW_ID, ARTICUL, REQUESTED_QTY,
      PLANNED_QTY, SHORTAGE_QTY, STATUS, CREATED_AT, CREATED_BY
    )
    select RRL_PICK_WAVE_LINE_SQ.nextval,
           wo.PICK_WAVE_ID,
           wo.PICK_WAVE_ORDER_ID,
           wo.PICK_PLAN_ID,
           pl.PICK_PLAN_LINE_ID,
           pl.CUSTOMER_ORDER_ROW_ID,
           pl.ARTICUL,
           pl.REQUESTED_QTY,
           pl.PLANNED_QTY,
           pl.SHORTAGE_QTY,
           'PREVIEW',
           sysdate,
           substr(p_updated_by, 1, 50)
      from RRL_PICK_WAVE_ORDER wo
      join RRL_PICK_PLAN_LINE pl
        on pl.PICK_PLAN_ID = wo.PICK_PLAN_ID
     where wo.PICK_WAVE_ID = p_pick_wave_id
       and wo.STATUS = 'ACTIVE';

    insert into RRL_PICK_WAVE_DEMAND (
      PICK_WAVE_DEMAND_ID, PICK_WAVE_ID, ARTICUL, TASK_TYPE,
      TARGET_CELL_CODE, PICK_FACE_ID, PICK_ROUTE_CELL_ID, DEMAND_QTY,
      TASK_COUNT, CREATED_AT, CREATED_BY
    )
    select RRL_PICK_WAVE_DEMAND_SQ.nextval,
           q.PICK_WAVE_ID,
           q.ARTICUL,
           q.TASK_TYPE,
           q.TARGET_CELL_CODE,
           q.PICK_FACE_ID,
           q.PICK_ROUTE_CELL_ID,
           q.DEMAND_QTY,
           q.TASK_COUNT,
           sysdate,
           substr(p_updated_by, 1, 50)
      from (
        select wo.PICK_WAVE_ID,
               t.ARTICUL,
               t.TASK_TYPE,
               t.TARGET_CELL_CODE,
               t.PICK_FACE_ID,
               t.PICK_ROUTE_CELL_ID,
               sum(t.QTY) DEMAND_QTY,
               count(*) TASK_COUNT
          from RRL_PICK_WAVE_ORDER wo
          join RRL_PICK_TASK t
            on t.PICK_PLAN_ID = wo.PICK_PLAN_ID
         where wo.PICK_WAVE_ID = p_pick_wave_id
           and wo.STATUS = 'ACTIVE'
           and t.STATUS in ('NEW', 'ASSIGNED')
         group by wo.PICK_WAVE_ID, t.ARTICUL, t.TASK_TYPE, t.TARGET_CELL_CODE, t.PICK_FACE_ID, t.PICK_ROUTE_CELL_ID
      ) q;

    insert into RRL_PICK_WAVE_SHORTAGE (
      PICK_WAVE_SHORTAGE_ID, PICK_WAVE_ID, PICK_SHORTAGE_ID, PICK_PLAN_ID,
      CUSTOMER_ORDER_ID, CUSTOMER_ID, ARTICUL, REQUESTED_QTY, PLANNED_QTY,
      SHORTAGE_QTY, REASON_CODE, REASON_TEXT, CREATED_AT, CREATED_BY
    )
    select RRL_PICK_WAVE_SHORTAGE_SQ.nextval,
           wo.PICK_WAVE_ID,
           s.PICK_SHORTAGE_ID,
           s.PICK_PLAN_ID,
           s.CUSTOMER_ORDER_ID,
           s.CUSTOMER_ID,
           s.ARTICUL,
           s.REQUESTED_QTY,
           s.PLANNED_QTY,
           s.SHORTAGE_QTY,
           s.REASON_CODE,
           s.REASON_TEXT,
           sysdate,
           substr(p_updated_by, 1, 50)
      from RRL_PICK_WAVE_ORDER wo
      join RRL_PICK_SHORTAGE s
        on s.PICK_PLAN_ID = wo.PICK_PLAN_ID
     where wo.PICK_WAVE_ID = p_pick_wave_id
       and wo.STATUS = 'ACTIVE';

    update RRL_PICK_WAVE
       set STATUS = 'PREVIEW',
           UPDATED_AT = sysdate,
           UPDATED_BY = substr(p_updated_by, 1, 50)
     where PICK_WAVE_ID = p_pick_wave_id;

    refresh_counters(p_pick_wave_id, p_updated_by);
    write_audit(p_pick_wave_id, 'WAVE_PREVIEWED', 'Wave preview calculated', '{"plans":' || to_char(v_plan_count) || '}', p_updated_by);
  end preview_wave;

  procedure launch_wave(
    p_pick_wave_id number,
    p_launched_by  varchar2 default null
  ) is
    v_status varchar2(30);
    v_res_count number := 0;
    v_task_count number := 0;
    v_replenish_count number := 0;
  begin
    declare
      st varchar2(20);j json_object_t:=json_object_t();src json_object_t:=json_object_t();result clob;
    begin
      select STATE into st from RRL_STOCK_RELEASE where RELEASE_ID=1;
      if st='ACTIVE' then
        j.put('contract_version',2);j.put('operation_id','WAVE.LAUNCH:'||to_char(p_pick_wave_id,'TM9'));
        j.put('command_type','WAVE_LAUNCH');j.put('actor',p_launched_by);
        src.put('wave_id',p_pick_wave_id);j.put('source',src);j.put('lines',json_array_t());
        j.put('units',json_array_t());j.put('metadata',json_object_t());
        RRL_STOCK_NATIVE_API.post(j.to_clob,p_launched_by,result);return;
      end if;
    end;

    select STATUS
      into v_status
      from RRL_PICK_WAVE
     where PICK_WAVE_ID = p_pick_wave_id
     for update;

    if v_status = 'DRAFT' then
      preview_wave(p_pick_wave_id, p_launched_by);
    end if;

    select STATUS
      into v_status
      from RRL_PICK_WAVE
     where PICK_WAVE_ID = p_pick_wave_id
     for update;

    if v_status <> 'PREVIEW' then
      raise_application_error(-20997, 'wave must be in PREVIEW status before launch');
    end if;

    for r in (
      select pr.PICK_RESERVATION_ID,
             pr.PICK_PLAN_ID,
             pr.PICK_PLAN_LINE_ID,
             pr.PICK_TASK_ID,
             pr.CUSTOMER_ORDER_ID,
             pr.CUSTOMER_ID,
             pr.PALLET_UID,
             pr.SSCC,
             pr.ARTICUL,
             pr.SOURCE_CELL_CODE,
             pr.RESERVED_QTY
        from RRL_PICK_WAVE_ORDER wo
        join RRL_PICK_RESERVATION pr
          on pr.PICK_PLAN_ID = wo.PICK_PLAN_ID
       where wo.PICK_WAVE_ID = p_pick_wave_id
         and wo.STATUS = 'ACTIVE'
         and pr.RESERVATION_STATUS = 'ACTIVE'
         and pr.RESERVATION_LEVEL = 'SOFT'
       order by pr.PICK_RESERVATION_ID
       for update
    ) loop
      update RRL_PICK_RESERVATION
         set RESERVATION_LEVEL = 'HARD',
             UPDATED_AT = sysdate,
             UPDATED_BY = substr(p_launched_by, 1, 50)
       where PICK_RESERVATION_ID = r.PICK_RESERVATION_ID;

      insert into RRL_PICK_WAVE_RESERVATION (
        PICK_WAVE_RESERVATION_ID, PICK_WAVE_ID, PICK_RESERVATION_ID, PICK_TASK_ID,
        PICK_PLAN_ID, PICK_PLAN_LINE_ID, CUSTOMER_ORDER_ID, CUSTOMER_ID,
        RESERVATION_STATUS, PALLET_UID, SSCC, ARTICUL, SOURCE_CELL_CODE,
        RESERVED_QTY, CREATED_AT, CREATED_BY
      ) values (
        RRL_PICK_WAVE_RES_SQ.nextval, p_pick_wave_id, r.PICK_RESERVATION_ID, r.PICK_TASK_ID,
        r.PICK_PLAN_ID, r.PICK_PLAN_LINE_ID, r.CUSTOMER_ORDER_ID, r.CUSTOMER_ID,
        'HARD', r.PALLET_UID, r.SSCC, r.ARTICUL, r.SOURCE_CELL_CODE,
        r.RESERVED_QTY, sysdate, substr(p_launched_by, 1, 50)
      );
      v_res_count := v_res_count + 1;
    end loop;

    if v_res_count = 0 then
      raise_application_error(-20998, 'wave has no active soft reservations to launch');
    end if;

    insert into RRL_PICK_WAVE_TASK (
      PICK_WAVE_TASK_ID, PICK_WAVE_ID, PICK_TASK_ID, TASK_TYPE, STATUS,
      ARTICUL, PALLET_UID, SOURCE_CELL_CODE, TARGET_CELL_CODE, QTY,
      PICK_SEQUENCE, PICK_FACE_ID, PICK_ROUTE_CELL_ID, CREATED_AT, CREATED_BY
    )
    select RRL_PICK_WAVE_TASK_SQ.nextval,
           p_pick_wave_id,
           t.PICK_TASK_ID,
           t.TASK_TYPE,
           'NEW',
           t.ARTICUL,
           t.PALLET_UID,
           t.SOURCE_CELL_CODE,
           t.TARGET_CELL_CODE,
           t.QTY,
           t.PICK_SEQUENCE,
           t.PICK_FACE_ID,
           t.PICK_ROUTE_CELL_ID,
           sysdate,
           substr(p_launched_by, 1, 50)
      from RRL_PICK_WAVE_ORDER wo
      join RRL_PICK_TASK t
        on t.PICK_PLAN_ID = wo.PICK_PLAN_ID
     where wo.PICK_WAVE_ID = p_pick_wave_id
       and wo.STATUS = 'ACTIVE'
       and t.STATUS in ('NEW', 'ASSIGNED')
       and not exists (
         select 1
           from RRL_PICK_WAVE_TASK wt
          where wt.PICK_WAVE_ID = p_pick_wave_id
            and wt.PICK_TASK_ID = t.PICK_TASK_ID
       );

    v_task_count := sql%rowcount;

    insert into RRL_PICK_WAVE_REPLENISH_TASK (
      PICK_WAVE_REPLENISH_TASK_ID, PICK_WAVE_ID, PICK_TASK_ID, STATUS,
      ARTICUL, PALLET_UID, SOURCE_CELL_CODE, TARGET_CELL_CODE, QTY,
      PICK_SEQUENCE, CREATED_AT, CREATED_BY
    )
    select RRL_PICK_WAVE_REPL_SQ.nextval,
           p_pick_wave_id,
           t.PICK_TASK_ID,
           'NEW',
           t.ARTICUL,
           t.PALLET_UID,
           t.SOURCE_CELL_CODE,
           t.TARGET_CELL_CODE,
           t.QTY,
           t.PICK_SEQUENCE,
           sysdate,
           substr(p_launched_by, 1, 50)
      from RRL_PICK_WAVE_ORDER wo
      join RRL_PICK_TASK t
        on t.PICK_PLAN_ID = wo.PICK_PLAN_ID
     where wo.PICK_WAVE_ID = p_pick_wave_id
       and wo.STATUS = 'ACTIVE'
       and t.TASK_TYPE = 'CASE_PICK'
       and t.TARGET_CELL_CODE is not null;

    v_replenish_count := sql%rowcount;

    update RRL_PICK_TASK
       set STATUS = 'ASSIGNED',
           UPDATED_AT = sysdate,
           UPDATED_BY = substr(p_launched_by, 1, 50)
     where PICK_TASK_ID in (
       select PICK_TASK_ID
         from RRL_PICK_WAVE_TASK
        where PICK_WAVE_ID = p_pick_wave_id
     )
       and STATUS = 'NEW';

    update RRL_PICK_PLAN
       set STATUS = 'RELEASED',
           UPDATED_AT = sysdate,
           UPDATED_BY = substr(p_launched_by, 1, 50)
     where PICK_PLAN_ID in (
       select PICK_PLAN_ID
         from RRL_PICK_WAVE_ORDER
        where PICK_WAVE_ID = p_pick_wave_id
          and STATUS = 'ACTIVE'
     )
       and STATUS in ('PLANNED_FULL', 'PLANNED_PARTIAL');

    update RRL_PICK_WAVE
       set STATUS = 'LAUNCHED',
           LAUNCHED_AT = sysdate,
           LAUNCHED_BY = substr(p_launched_by, 1, 50),
           UPDATED_AT = sysdate,
           UPDATED_BY = substr(p_launched_by, 1, 50)
     where PICK_WAVE_ID = p_pick_wave_id;

    refresh_counters(p_pick_wave_id, p_launched_by);
    write_audit(
      p_pick_wave_id,
      'WAVE_LAUNCHED',
      'Wave launched and soft reservations converted to hard reservations',
      '{"reservations":' || to_char(v_res_count) || ',"tasks":' || to_char(v_task_count) || ',"replenishmentTasks":' || to_char(v_replenish_count) || '}',
      p_launched_by
    );
  end launch_wave;

  procedure release_reservations(
    p_pick_wave_id number,
    p_updated_by   varchar2 default null
  ) is
    v_blocking_tasks number;
  begin
    select count(*)
      into v_blocking_tasks
      from RRL_PICK_WAVE_TASK
     where PICK_WAVE_ID = p_pick_wave_id
       and STATUS not in ('NEW', 'ASSIGNED', 'CANCELLED');

    if v_blocking_tasks > 0 then
      raise_application_error(-20999, 'wave has already started tasks; reservations cannot be released automatically');
    end if;

    update RRL_PICK_RESERVATION
       set RESERVATION_LEVEL = 'SOFT',
           RESERVATION_STATUS = 'ACTIVE',
           UPDATED_AT = sysdate,
           UPDATED_BY = substr(p_updated_by, 1, 50)
     where PICK_RESERVATION_ID in (
       select PICK_RESERVATION_ID
         from RRL_PICK_WAVE_RESERVATION
        where PICK_WAVE_ID = p_pick_wave_id
          and RESERVATION_STATUS = 'HARD'
     );

    update RRL_PICK_WAVE_RESERVATION
       set RESERVATION_STATUS = 'RELEASED',
           RELEASED_AT = sysdate,
           UPDATED_AT = sysdate,
           UPDATED_BY = substr(p_updated_by, 1, 50)
     where PICK_WAVE_ID = p_pick_wave_id
       and RESERVATION_STATUS = 'HARD';

    update RRL_PICK_TASK
       set STATUS = 'NEW',
           UPDATED_AT = sysdate,
           UPDATED_BY = substr(p_updated_by, 1, 50)
     where PICK_TASK_ID in (
       select PICK_TASK_ID
         from RRL_PICK_WAVE_TASK
        where PICK_WAVE_ID = p_pick_wave_id
          and STATUS in ('NEW', 'ASSIGNED')
     )
       and STATUS = 'ASSIGNED';

    update RRL_PICK_WAVE_TASK
       set STATUS = 'CANCELLED',
           UPDATED_AT = sysdate,
           UPDATED_BY = substr(p_updated_by, 1, 50)
     where PICK_WAVE_ID = p_pick_wave_id
       and STATUS in ('NEW', 'ASSIGNED');

    update RRL_PICK_WAVE_REPLENISH_TASK
       set STATUS = 'CANCELLED',
           UPDATED_AT = sysdate,
           UPDATED_BY = substr(p_updated_by, 1, 50)
     where PICK_WAVE_ID = p_pick_wave_id
       and STATUS in ('NEW', 'ASSIGNED');

    update RRL_PICK_PLAN p
       set STATUS = case when nvl(p.TOTAL_SHORTAGE_QTY, 0) > 0 then 'PLANNED_PARTIAL' else 'PLANNED_FULL' end,
           UPDATED_AT = sysdate,
           UPDATED_BY = substr(p_updated_by, 1, 50)
     where p.PICK_PLAN_ID in (
       select PICK_PLAN_ID
         from RRL_PICK_WAVE_ORDER
        where PICK_WAVE_ID = p_pick_wave_id
          and STATUS = 'ACTIVE'
     )
       and p.STATUS = 'RELEASED';

    update RRL_PICK_WAVE
       set STATUS = 'PREVIEW',
           UPDATED_AT = sysdate,
           UPDATED_BY = substr(p_updated_by, 1, 50)
     where PICK_WAVE_ID = p_pick_wave_id
       and STATUS = 'LAUNCHED';

    refresh_counters(p_pick_wave_id, p_updated_by);
    write_audit(p_pick_wave_id, 'RESERVATIONS_RELEASED', 'Hard reservations returned to soft reservation state', null, p_updated_by);
  end release_reservations;

  procedure cancel_wave(
    p_pick_wave_id number,
    p_reason       varchar2 default null,
    p_updated_by   varchar2 default null
  ) is
    v_status varchar2(30);
  begin
    select STATUS
      into v_status
      from RRL_PICK_WAVE
     where PICK_WAVE_ID = p_pick_wave_id
     for update;

    if v_status = 'LAUNCHED' then
      release_reservations(p_pick_wave_id, p_updated_by);
    elsif v_status not in ('DRAFT', 'PREVIEW', 'CANCELLED') then
      raise_application_error(-21000, 'wave cannot be cancelled in current status');
    end if;

    update RRL_PICK_WAVE
       set STATUS = 'CANCELLED',
           CANCELLED_AT = sysdate,
           CANCELLED_BY = substr(p_updated_by, 1, 50),
           COMMENT_TEXT = substr(nvl(p_reason, COMMENT_TEXT), 1, 1000),
           UPDATED_AT = sysdate,
           UPDATED_BY = substr(p_updated_by, 1, 50)
     where PICK_WAVE_ID = p_pick_wave_id;

    refresh_counters(p_pick_wave_id, p_updated_by);
    write_audit(p_pick_wave_id, 'WAVE_CANCELLED', 'Wave cancelled', substr(p_reason, 1, 1000), p_updated_by);
  end cancel_wave;
end RRL_PICK_WAVE_API;
/

create or replace package body RRL_STOCK_DOC_RESERVE_CMD as
 function document_table(p_type varchar2) return varchar2 is
 begin
  case p_type when 'PICK_WAVE' then return 'RRL_PICK_WAVE';when 'PICK_PLAN' then return 'RRL_PICK_PLAN';
   when 'PRODUCTION_ORDER' then return 'RRL_PRODUCTION_ORDER';else raise_application_error(-20869,'RESERVATION_DOCUMENT_TYPE_UNSUPPORTED');end case;
 end;
 procedure compile_release(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
  d json_object_t:=json_object_t.parse(p_request);s json_object_t;v_type varchar2(40);v_doc number;v_only number;v_kind varchar2(10);
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();a json_array_t:=json_array_t();v json_object_t:=json_object_t();x json_object_t;
 begin
  s:=d.get_object('source');v_type:=s.get_string('document_type');v_doc:=s.get_number('document_id');
  v_only:=nvl(d.get_object('metadata').get_number('only_cancelled_replenishment'),0);v_kind:=d.get_object('metadata').get_string('reservation_kind');
  if v_kind is not null and v_kind not in('SOFT','HARD') then raise_application_error(-20869,'RESERVATION_KIND_INVALID');end if;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  RRL_STOCK_PLAN_HELPER.row_key(r,document_table(v_type),RRL_STOCK_PLAN_HELPER.decimal_text(v_doc));
  for sr in(select * from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE=v_type and SOURCE_DOC_ID=v_doc
   and STATUS in('ACTIVE','ALLOCATED','PICKING') and (v_kind is null or RESERVATION_KIND=v_kind) and
    (v_only=0 or (v_type='PICK_WAVE' and RESERVATION_DOMAIN='WAVE' and exists(
     select 1 from RRL_PICK_WAVE_REPLENISH_TASK rt where rt.PICK_WAVE_ID=v_doc and rt.PICK_WAVE_REPLENISH_TASK_ID=SOURCE_LINE_ID and rt.STATUS in('CANCELLED','FAILED'))))
   order by RESERVATION_ID) loop
   if a.get_size>=10000 then raise_application_error(-20881,'DOCUMENT_RESERVATION_BOUND');end if;
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(sr.RESERVATION_ID));
   if sr.UID_PALLET is not null then RRL_STOCK_PLAN_HELPER.stock_closure(f,r,sr.UID_PALLET,sr.ARTICUL,sr.CELL,null);
   else RRL_STOCK_PLAN_HELPER.fence(f,'SKU',sr.ARTICUL);end if;
   if v_only=1 then RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE_REPLENISH_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(sr.SOURCE_LINE_ID));end if;
   x:=json_object_t();x.put('id',sr.RESERVATION_ID);x.put('version',sr.RESERVATION_VERSION);x.put('uid',sr.UID_PALLET);x.put('cell',sr.CELL);a.append(x);
  end loop;
  v.put('document_type',v_type);v.put('document_id',v_doc);v.put('only_cancelled',v_only);v.put('reservations',a);
  p_domain:=v.to_clob;p_policies:=f.to_clob;p_resources:=r.to_clob;
 end;
 procedure execute_release(p_request clob,p_actor varchar2,p_result out clob) is
  d json_object_t:=json_object_t.parse(p_request);v json_object_t;x json_object_t;j json_object_t:=json_object_t();
  a json_array_t;sr RRL_STOCK_RESERVATION%rowtype;v_plan clob;v_type varchar2(40);v_doc number;v_status varchar2(40);v_version number;
 begin
  select RESOLVED_PLAN_JSON into v_plan from RRL_STOCK_OPERATION where OPERATION_ID=d.get_string('operation_id');
  v:=json_object_t.parse(v_plan).get_object('domain');v_type:=v.get_string('document_type');v_doc:=v.get_number('document_id');a:=v.get_array('reservations');
  if RRL_HAS_WRIGHT(p_actor,'stock_reservation_edit')!=1
   and not(v_type='PICK_WAVE' and (RRL_HAS_WRIGHT(p_actor,'pick_wave_launch')=1 or RRL_HAS_WRIGHT(p_actor,'pick_wave_cancel')=1 or RRL_HAS_WRIGHT(p_actor,'pick_wave_release_reserves')=1))
   and not(v_type='PICK_PLAN' and RRL_HAS_WRIGHT(p_actor,'pick_plan_cancel')=1)
   and not(v_type='PRODUCTION_ORDER' and (RRL_HAS_WRIGHT(p_actor,'mes_raw_transfer_create')=1 or RRL_HAS_WRIGHT(p_actor,'mes_raw_transfer_cancel')=1 or RRL_HAS_WRIGHT(p_actor,'mes_raw_supply_calculate')=1))
   then raise_application_error(-20882,'DOCUMENT_RESERVATION_RELEASE_FORBIDDEN');end if;
  case v_type when 'PICK_WAVE' then select STATUS into v_status from RRL_PICK_WAVE where PICK_WAVE_ID=v_doc for update;
   when 'PICK_PLAN' then select STATUS into v_status from RRL_PICK_PLAN where PICK_PLAN_ID=v_doc for update;
   when 'PRODUCTION_ORDER' then select STATUS into v_status from RRL_PRODUCTION_ORDER where PRODUCTION_ORDER_ID=v_doc for update;
   else raise_application_error(-20869,'DOCUMENT_TYPE_INVALID');end case;
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i) as json_object_t);
   select * into sr from RRL_STOCK_RESERVATION where RESERVATION_ID=x.get_number('id') for update;
   if sr.RESERVATION_VERSION!=x.get_number('version') or sr.SOURCE_DOC_TYPE!=v_type or sr.SOURCE_DOC_ID!=v_doc or sr.STATUS not in('ACTIVE','ALLOCATED','PICKING') then raise_application_error(-20890,'CLOSURE_CHANGED: document reservation');end if;
   if v.get_number('only_cancelled')=1 then
    select STATUS into v_status from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_ID=v_doc and PICK_WAVE_REPLENISH_TASK_ID=sr.SOURCE_LINE_ID for update;
    if v_status not in('CANCELLED','FAILED') then raise_application_error(-20890,'CLOSURE_CHANGED: replenishment cancellation');end if;
   end if;
   if sr.RESERVATION_KIND='HARD' then
    select max(POLICY_VERSION) into v_version from RRL_STOCK_UOM_CONVERSION where ARTICUL=sr.ARTICUL and INPUT_UOM=sr.BASE_UOM and BASE_UOM=sr.BASE_UOM and NUMERATOR=1 and DENOMINATOR=1;
    if v_version is null then raise_application_error(-20868,'RESERVATION_RELEASE_BASE_POLICY_REQUIRED');end if;
    RRL_STOCK_UNIT_CORE.release_units(sr.RESERVATION_ID,sr.BASE_QTY,null,0);
    RRL_STOCK_RESERVE_CORE.release_hard(sr.RESERVATION_ID,sr.BASE_QTY,v_version,v_type,v_doc,p_actor);
   elsif sr.RESERVATION_KIND='SOFT' then
    RRL_STOCK_CTX_API.begin_effect('RESERVATION',sr.UID_PALLET,sr.CELL,sr.RESERVATION_ID);
    update RRL_STOCK_RESERVATION set STATUS='RELEASED',RELEASED_AT=systimestamp,RELEASED_BY=p_actor,
     RELEASE_REASON=d.get_object('metadata').get_string('reason'),RESERVATION_VERSION=RESERVATION_VERSION+1 where RESERVATION_ID=sr.RESERVATION_ID;
    RRL_STOCK_CTX_API.end_effect;
   else raise_application_error(-20869,'RESERVATION_KIND_INVALID');end if;
  end loop;
  j.put('operation_id',d.get_string('operation_id'));j.put('document_type',v_type);j.put('document_id',v_doc);j.put('released_count',a.get_size);p_result:=j.to_clob;
 end;
end;
/

create or replace package body RRL_STOCK_POSTING_API as
 g_request clob;g_resolution clob;g_actor varchar2(50);g_operation varchar2(100);g_kind varchar2(80);g_tx varchar2(100);g_prepared boolean:=false;
 procedure reset_connection is
 begin
  RRL_STOCK_CTX_API.clear_operation;RRL_STOCK_LOCK_API.clear_plan;
  g_request:=null;g_resolution:=null;g_actor:=null;g_operation:=null;g_kind:=null;g_tx:=null;g_prepared:=false;
 end;
 procedure prepare_command(p_request clob,p_actor varchar2,p_replay out clob,p_hints clob default null) is
  v_doc json_object_t;v_policies clob;v_resources clob;v_exists number;v_release varchar2(20);v_domain clob;v_resolution json_object_t:=json_object_t();
  v_plan json_array_t:=json_array_t();v_entry json_object_t:=json_object_t();v_resources_json json_array_t:=json_array_t();
 begin
  p_replay:=null;
  if g_prepared or sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID') is not null then
   raise_application_error(-20862,'POSTING_ALREADY_ENTERED');
  end if;
  if p_request is null or dbms_lob.getlength(p_request)>4194304 then raise_application_error(-20871,'OPERATION_CONTRACT_INVALID'); end if;
  v_doc:=json_object_t.parse(p_request);v_doc.on_error(1);
  g_operation:=v_doc.get_string('operation_id');g_kind:=v_doc.get_string('command_type');
  if v_doc.get_number('contract_version') is null or v_doc.get_number('contract_version')!=2 or v_doc.get_string('actor') is null
   or v_doc.get_string('actor')!=p_actor or p_actor is null or length(p_actor)>50
   or g_operation is null or length(g_operation)>100 or g_kind is null then
   raise_application_error(-20871,'OPERATION_CONTRACT_INVALID');
  end if;
  -- Immutable committed replay is considered before any mutable article/cell/UOM validation.
  select count(*) into v_exists from RRL_STOCK_OPERATION where OPERATION_ID=g_operation;
  if v_exists!=0 then
   v_entry.put('key_hex',rawtohex(RRL_STOCK_LOCK_API.resource_key('RELEASE','STOCK')));v_entry.put('mode',4);v_plan.append(v_entry);
   v_entry:=json_object_t();v_entry.put('rank',10);
   v_entry.put('key_hex',rawtohex(RRL_STOCK_LOCK_API.resource_key('OP',g_operation)));v_resources_json.append(v_entry);
   v_policies:=v_plan.to_clob;v_resources:=v_resources_json.to_clob;
  else
   if g_kind in('MANUAL_MOVE','COMPAT_MANUAL_MOVE') then RRL_STOCK_COMMAND_PLAN.compile_move(p_request,g_operation,v_policies,v_resources);
   elsif g_kind='WAVE_LAUNCH' then RRL_STOCK_WAVE_LAUNCH_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind='INVENTORY_COUNT' then RRL_STOCK_INVENTORY_CMD.compile_count(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind='MES_RAW_TASK_CANCEL' then RRL_STOCK_MES_CANCEL_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind in('MES_RELEASE_TO_PRODUCTION','MES_CALCULATE_SUPPLY') then RRL_STOCK_MES_SUPPLY_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind='DOCUMENT_RELEASE_RESERVATIONS' then RRL_STOCK_DOC_RESERVE_CMD.compile_release(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind='WAVE_RESERVE_SOURCES' then RRL_STOCK_WAVE_CMD.compile_reserve(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind in('SHIP_DOCUMENT','SHIP_PALLET') then RRL_STOCK_SHIPPING_CORE.compile_shipment(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind in('INTERNAL_MOVE','MOVE_QUARANTINE') then RRL_STOCK_INTERNAL_CMD.compile_move(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind='MES_MOVEMENTS' then RRL_STOCK_MES_MOVEMENT_PLAN.compile_movements(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind='SAP_RECEIPT' then RRL_STOCK_RECEIPT_PLAN.compile_receipt(p_request,g_operation,p_hints,v_policies,v_resources,v_domain);
   elsif g_kind='TASK_COMPLETE' then RRL_STOCK_TASK_PLAN.compile_task(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind in('RESERVATION_CREATE','RESERVATION_PROMOTE','RESERVATION_RELEASE','RESERVATION_CANCEL','RESERVATION_CONSUME') then RRL_STOCK_RESERVATION_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
   else raise_application_error(-20888,'COMMAND_HANDLER_NOT_INSTALLED');end if;
  end if;
  RRL_STOCK_LOCK_API.begin_plan;
  RRL_STOCK_LOCK_API.acquire_policies(v_policies);
  RRL_STOCK_LOCK_API.acquire_resources(v_resources);
  select STATE into v_release from RRL_STOCK_RELEASE where RELEASE_ID=1;
  if v_release!='ACTIVE' then raise_application_error(-20860,'STOCK_RELEASE_NOT_ACTIVE'); end if;
  if v_domain is not null then v_resolution.put('domain',json_object_t.parse(v_domain));end if;
  v_resolution.put('stock_before',json_array_t.parse(RRL_STOCK_INVARIANT_CORE.snapshot_stock(v_resources)));
  v_resolution.put('resources',json_array_t.parse(v_resources));
  v_resolution.put('policies',json_array_t.parse(v_policies));
  RRL_STOCK_OPERATION_CORE.begin_operation(p_request,p_actor,g_operation,g_kind,p_replay,v_resolution.to_clob);
  if p_replay is not null then return; end if;
  g_request:=p_request;g_resolution:=v_resolution.to_clob;g_actor:=p_actor;g_tx:=dbms_transaction.local_transaction_id(false);g_prepared:=true;
  if g_kind='SAP_RECEIPT' then RRL_STOCK_CTX_API.begin_staging(v_resolution.get_object('domain').get_string('uid'),v_resolution.get_object('domain').get_string('receive_cell'));end if;
 end;
 procedure execute_prepared(p_result out clob) is
  v_outbox number;v_existing number;v_key varchar2(100);v_json json_object_t;v_resolved json_object_t;
 begin
  if not g_prepared or g_tx is null or dbms_transaction.local_transaction_id(false) is null
   or g_tx!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20850,'WRITE_PLAN_VIOLATION'); end if;
  if g_kind='SAP_RECEIPT' then RRL_STOCK_CTX_API.end_effect;end if;
  if g_kind in('MANUAL_MOVE','COMPAT_MANUAL_MOVE') then RRL_STOCK_MOVE_CORE.manual_whole(g_request,g_actor,p_result);
  elsif g_kind='WAVE_LAUNCH' then RRL_STOCK_WAVE_LAUNCH_CMD.execute_command(g_request,g_actor,p_result);
   elsif g_kind='INVENTORY_COUNT' then RRL_STOCK_INVENTORY_CMD.execute_count(g_request,g_actor,p_result);
   elsif g_kind='MES_RAW_TASK_CANCEL' then RRL_STOCK_MES_CANCEL_CMD.execute_command(g_request,g_actor,p_result);
   elsif g_kind in('MES_RELEASE_TO_PRODUCTION','MES_CALCULATE_SUPPLY') then RRL_STOCK_MES_SUPPLY_CMD.execute_command(g_request,g_actor,p_result);
   elsif g_kind='DOCUMENT_RELEASE_RESERVATIONS' then RRL_STOCK_DOC_RESERVE_CMD.execute_release(g_request,g_actor,p_result);
  elsif g_kind='WAVE_RESERVE_SOURCES' then RRL_STOCK_WAVE_CMD.execute_reserve(g_request,g_actor,p_result);
  elsif g_kind in('SHIP_DOCUMENT','SHIP_PALLET') then RRL_STOCK_SHIPPING_CORE.execute_shipment(g_request,g_actor,p_result);
  elsif g_kind in('INTERNAL_MOVE','MOVE_QUARANTINE') then RRL_STOCK_INTERNAL_CMD.execute_move(g_request,g_actor,p_result);
  elsif g_kind='MES_MOVEMENTS' then RRL_STOCK_MES_MOVEMENT_CORE.execute_movements(g_request,g_actor,p_result);
  elsif g_kind='SAP_RECEIPT' then RRL_STOCK_RECEIPT_CORE.execute_receipt(g_request,g_actor,p_result);
  elsif g_kind='TASK_COMPLETE' then RRL_STOCK_TASK_CORE.execute_task(g_request,g_actor,p_result);
  elsif g_kind in('RESERVATION_CREATE','RESERVATION_PROMOTE','RESERVATION_RELEASE','RESERVATION_CANCEL','RESERVATION_CONSUME') then RRL_STOCK_RESERVATION_CMD.execute_command(g_request,g_actor,p_result);
  else raise_application_error(-20888,'COMMAND_HANDLER_NOT_INSTALLED'); end if;
  v_resolved:=json_object_t.parse(g_resolution);
  RRL_STOCK_INVARIANT_CORE.verify_posting(v_resolved.get_array('resources').to_clob,v_resolved.get_array('stock_before').to_clob,g_operation);
  v_key:='STOCK:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(g_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256));
  RRL_STOCK_LOCK_API.assert_held(70,RRL_STOCK_LOCK_API.resource_key('UNIQUE','STOCK.OUTBOX:'||substr(v_key,7)));
  select count(*) into v_existing from RRL_EVENT_OUTBOX where IDEMPOTENCY_KEY=v_key;
  if v_existing!=0 then raise_application_error(-20889,'OUTBOX_IDENTITY_CONFLICT'); end if;
  v_outbox:=RRL_TRACEABILITY_API.enqueue_event('STOCK_POSTED','STOCK_OPERATION',g_operation,v_key,p_result,'WMS',g_operation);
  v_json:=json_object_t.parse(p_result);v_json.put('outbox_id',v_outbox);p_result:=v_json.to_clob;
  RRL_STOCK_OPERATION_CORE.finish_operation(g_operation,p_result);
  g_prepared:=false;
 end;
end;
/

create or replace package body RRL_STOCK_TRANSFER_CORE as
 procedure require_row(p_id number) is
 begin
  begin RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_STOCK_RESERVATION',
   RRL_STOCK_PLAN_HELPER.decimal_text(p_id)));
  exception when others then
   if sqlcode=-20850 then raise_application_error(-20890,'CLOSURE_CHANGED: reservation set');else raise;end if;
  end;
 end;
 procedure move(p_uid varchar2,p_target_uid varchar2,p_from varchar2,p_to varchar2,p_qty number,
  p_uom varchar2,p_uom_version number,p_warehouse number,p_actor varchar2,p_line number,
  p_reservation number default null,p_units clob default null,p_new_reservation number default null,p_target_slot number default null,p_source_warehouse number default null,p_location_mode varchar2 default 'ORDINARY') is
  v_p number;v_h number;v_ver number;v_uom varchar2(20);v_article varchar2(160);v_sum number;
  v_hmove number:=0;v_event number;v_units number;v_unit_qty number;v_selected number;v_expected number;
  v_r RRL_STOCK_RESERVATION%rowtype;v_result_reservation number;
 begin
  if p_uid is null or p_target_uid is null or p_from is null or p_to is null or p_from=p_to
   or p_qty is null or p_qty<=0 then raise_application_error(-20886,'TRANSFER_CONTRACT_INVALID');end if;
  RRL_STOCK_LOCK_API.assert_held(30,RRL_STOCK_LOCK_API.resource_key('HU',p_uid));
  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',p_uid));
  RRL_STOCK_LOCK_API.assert_held(30,RRL_STOCK_LOCK_API.resource_key('HU',p_target_uid));
  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',p_target_uid));
  if p_location_mode='PUTAWAY' then
   RRL_STOCK_LOCATION_CORE.assert_receiving(p_from,nvl(p_source_warehouse,p_warehouse));
   RRL_STOCK_LOCATION_CORE.assert_ordinary(p_to,p_warehouse,'TARGET');
  elsif p_location_mode='QUARANTINE' then
   if RRL_HAS_WRIGHT(p_actor,'QUARANTINE_MOVE')!=1 then raise_application_error(-20882,'QUARANTINE_MOVE_FORBIDDEN');end if;
   RRL_STOCK_LOCATION_CORE.assert_quarantine(p_from,nvl(p_source_warehouse,p_warehouse));
   RRL_STOCK_LOCATION_CORE.assert_quarantine(p_to,p_warehouse);
  elsif p_location_mode='ORDINARY' then
   RRL_STOCK_LOCATION_CORE.assert_ordinary(p_from,nvl(p_source_warehouse,p_warehouse),'SOURCE');
   RRL_STOCK_LOCATION_CORE.assert_ordinary(p_to,p_warehouse,'TARGET');
  else raise_application_error(-20878,'TRANSFER_LOCATION_MODE_INVALID');end if;
  select REMAIN,HARD_RESERVED_BASE,STOCK_VERSION,BASE_UOM into v_p,v_h,v_ver,v_uom
   from RRL_REMAINS where UID_POLETA=p_uid and CELL=p_from;
  if v_uom is null or v_uom!=p_uom or p_qty>v_p then raise_application_error(-20868,'TRANSFER_STOCK_CONFLICT');end if;
  select ARTICUL into v_article from RRL_PALLETS where UID_PALLET=p_uid;
  select count(*) into v_sum from RRL_STOCK_RESERVATION where UID_PALLET=p_uid and CELL=p_from and RESERVATION_KIND='HARD' and STATUS in('ACTIVE','ALLOCATED','PICKING') and (BASE_QTY is null or BASE_QTY<=0 or BASE_UOM is null or BASE_UOM!=p_uom);
  if v_sum>0 then raise_application_error(-20869,'HARD_BASE_IDENTITY_CONFLICT');end if;
  select nvl(sum(BASE_QTY),0) into v_sum from RRL_STOCK_RESERVATION where UID_PALLET=p_uid
   and CELL=p_from and RESERVATION_KIND='HARD' and STATUS in('ACTIVE','ALLOCATED','PICKING');
  if v_sum!=v_h then raise_application_error(-20869,'HARD_MATERIALIZATION_CONFLICT');end if;
  for r in(select RESERVATION_ID from RRL_STOCK_RESERVATION where UID_PALLET=p_uid and CELL=p_from
   and RESERVATION_KIND='HARD' and STATUS in('ACTIVE','ALLOCATED','PICKING')) loop require_row(r.RESERVATION_ID);end loop;
  if p_qty=v_p then
   v_hmove:=v_h;
  elsif p_reservation is not null then
   require_row(p_reservation);
   select * into v_r from RRL_STOCK_RESERVATION where RESERVATION_ID=p_reservation;
   if v_r.UID_PALLET is null or v_r.UID_PALLET!=p_uid or v_r.CELL is null or v_r.CELL!=p_from
    or v_r.RESERVATION_KIND!='HARD' or v_r.STATUS not in('ACTIVE','ALLOCATED','PICKING')
    or v_r.BASE_QTY is null or v_r.BASE_QTY<=0 then raise_application_error(-20869,'TRANSFER_RESERVATION_CONFLICT');end if;
   v_hmove:=p_qty;
  elsif p_qty>v_p-v_h then raise_application_error(-20869,'TRANSFER_UNRESERVED_INSUFFICIENT');end if;
  if p_target_uid!=p_uid then
   declare t RRL_PALLETS%rowtype;s RRL_PALLETS%rowtype;
   begin
    select * into s from RRL_PALLETS where UID_PALLET=p_uid;
    select * into t from RRL_PALLETS where UID_PALLET=p_target_uid;
    if t.ARTICUL!=s.ARTICUL or t.PRIHOD_NAKLAD_ID!=s.PRIHOD_NAKLAD_ID
     or (t.EXPIRY_DATE!=s.EXPIRY_DATE or (t.EXPIRY_DATE is null and s.EXPIRY_DATE is not null) or (t.EXPIRY_DATE is not null and s.EXPIRY_DATE is null)) or (t.PRODUCED_DATE!=s.PRODUCED_DATE or (t.PRODUCED_DATE is null and s.PRODUCED_DATE is not null) or (t.PRODUCED_DATE is not null and s.PRODUCED_DATE is null))
     or (t.PROD_BATCH_ID!=s.PROD_BATCH_ID or (t.PROD_BATCH_ID is null and s.PROD_BATCH_ID is not null) or (t.PROD_BATCH_ID is not null and s.PROD_BATCH_ID is null)) then raise_application_error(-20887,'TRANSFER_LOT_IDENTITY_CONFLICT');end if;
   end;
  end if;
  select count(*),nvl(sum(BASE_QTY),0) into v_units,v_unit_qty from RRL_WMS_RECEIPT_UNIT
   where CURRENT_UID=p_uid and CURRENT_CELL=p_from and STOCK_STATUS!='ISSUED';
  if v_units>0 then
   if p_target_uid!=p_uid then raise_application_error(-20888,'HU_REBIND_HANDLER_REQUIRED');end if;
   if v_unit_qty!=v_p then raise_application_error(-20884,'COMPOSITION_STOCK_CONFLICT');end if;
   if p_qty!=v_p and p_units is null then raise_application_error(-20884,'PARTIAL_UNIT_SELECTION_REQUIRED');end if;
   select count(*),nvl(sum(u.BASE_QTY),0) into v_selected,v_unit_qty from RRL_WMS_RECEIPT_UNIT u
    where u.CURRENT_UID=p_uid and u.CURRENT_CELL=p_from and u.STOCK_STATUS!='ISSUED' and
     (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY));
   if v_unit_qty!=p_qty then raise_application_error(-20884,'SELECTED_UNIT_QUANTITY_CONFLICT');end if;
   if p_units is not null then
    select count(distinct K) into v_expected from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'));
    if v_expected!=v_selected then raise_application_error(-20884,'SELECTED_UNIT_IDENTITY_CONFLICT');end if;
   end if;
   if p_qty!=v_p and p_reservation is not null then
    select nvl(sum(u.BASE_QTY),0) into v_unit_qty from RRL_WMS_RECEIPT_UNIT u
     where u.CURRENT_UID=p_uid and u.CURRENT_CELL=p_from and u.HARD_RESERVATION_ID=p_reservation and
      (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY));
    if v_unit_qty!=v_hmove then raise_application_error(-20869,'RESERVED_UNIT_SELECTION_CONFLICT');end if;
   end if;
   for u in(select PHYSICAL_UNIT_KEY,HARD_RESERVATION_ID from RRL_WMS_RECEIPT_UNIT
    where CURRENT_UID=p_uid and CURRENT_CELL=p_from and STOCK_STATUS!='ISSUED' and
     (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=PHYSICAL_UNIT_KEY))) loop
    begin RRL_STOCK_LOCK_API.assert_held(60,RRL_STOCK_LOCK_API.resource_key('UNIT',u.PHYSICAL_UNIT_KEY));
    exception when others then if sqlcode=-20850 then raise_application_error(-20890,'CLOSURE_CHANGED: unit set');else raise;end if;end;
    if u.HARD_RESERVATION_ID is not null and p_qty!=v_p and
      (p_reservation is null or u.HARD_RESERVATION_ID!=p_reservation) then raise_application_error(-20869,'UNIT_RESERVED_BY_OTHER_OWNER');end if;
   end loop;
  else
   select nvl(max(MARKING_REQUIRED),0) into v_expected from RRL_SKU_RECEIPT_POLICY where ARTICUL=v_article;
   if v_expected=1 then raise_application_error(-20884,'MARKED_BINDING_REQUIRED');end if;
  end if;
  RRL_STOCK_BALANCE_CORE.apply_delta(p_uid,p_from,-p_qty,-v_hmove,p_uom,p_uom_version,v_ver);
  RRL_STOCK_BALANCE_CORE.apply_delta(p_target_uid,p_to,p_qty,v_hmove,p_uom,p_uom_version);
  if p_qty=v_p then
   for c in(select TASK_ID from RRL_RECEIPT_SLOT_CLAIM where UID_PALLET=p_uid and CELL=p_from and STATUS='OCCUPIED') loop
    RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_RECEIPT_SLOT_CLAIM',RRL_STOCK_PLAN_HELPER.decimal_text(c.TASK_ID)));
    delete from RRL_RECEIPT_SLOT_CLAIM where TASK_ID=c.TASK_ID and STATUS='OCCUPIED';
   end loop;
  end if;
  if v_hmove>0 then
   for r in(select RESERVATION_ID,BASE_QTY from RRL_STOCK_RESERVATION
    where UID_PALLET=p_uid and CELL=p_from and RESERVATION_KIND='HARD' and STATUS in('ACTIVE','ALLOCATED','PICKING')
     and (p_qty=v_p or RESERVATION_ID=p_reservation)) loop
    RRL_STOCK_RESERVE_CORE.move_coverage(r.RESERVATION_ID,p_new_reservation,p_target_uid,p_to,p_warehouse,
     case when p_qty=v_p then r.BASE_QTY else v_hmove end,p_target_slot,p_actor,v_result_reservation);
    RRL_STOCK_CTX_API.begin_effect('UNIT',p_uid,p_from);
    update RRL_WMS_RECEIPT_UNIT set HARD_RESERVATION_ID=v_result_reservation,UNIT_VERSION=UNIT_VERSION+1
     where CURRENT_UID=p_uid and CURRENT_CELL=p_from and HARD_RESERVATION_ID=r.RESERVATION_ID and
      (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=PHYSICAL_UNIT_KEY));
    RRL_STOCK_CTX_API.end_effect;
   end loop;
  end if;
  RRL_STOCK_CTX_API.begin_effect('UNIT',p_uid,p_from);
  update RRL_WMS_RECEIPT_UNIT set CURRENT_UID=p_target_uid,CURRENT_CELL=p_to,UNIT_VERSION=UNIT_VERSION+1
   where CURRENT_UID=p_uid and CURRENT_CELL=p_from and STOCK_STATUS!='ISSUED' and
    (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=PHYSICAL_UNIT_KEY));
  RRL_STOCK_CTX_API.end_effect;
  if p_target_uid=p_uid then
   RRL_STOCK_BALANCE_CORE.write_move(p_uid,p_from,p_to,p_qty,p_uom,p_uom_version,p_line,p_actor,v_event);
  else
  RRL_STOCK_BALANCE_CORE.write_leg(p_uid,p_from,null,-p_qty,p_uom,p_uom_version,p_line,1,2,p_actor,v_event);
  RRL_STOCK_BALANCE_CORE.write_leg(p_target_uid,null,p_to,p_qty,p_uom,p_uom_version,p_line,2,2,p_actor,v_event);
  end if;
 end;
end;
/
