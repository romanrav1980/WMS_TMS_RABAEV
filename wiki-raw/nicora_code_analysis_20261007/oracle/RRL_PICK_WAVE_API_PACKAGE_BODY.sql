package body RRL_PICK_WAVE_API as
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
