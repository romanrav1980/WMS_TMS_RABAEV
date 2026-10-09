declare n number;begin select count(*) into n from RRL_STOCK_OPERATION; if n>0 then raise_application_error(-20808,'POSTED_OPERATIONS_PREVENT_CODE_ROLLBACK');end if;end;
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

create or replace package RRL_STOCK_RESERVE_CORE authid definer
 accessible by(package RRL_STOCK_MES_CANCEL_CMD,package RRL_STOCK_MES_SUPPLY_CMD,package RRL_STOCK_DOC_RESERVE_CMD,package RRL_STOCK_WAVE_CMD,package RRL_STOCK_EFFECT_CORE,package RRL_STOCK_RESERVATION_CMD,package RRL_STOCK_POSTING_API,package RRL_STOCK_MOVE_CORE,package RRL_STOCK_TRANSFER_CORE) as
 procedure create_hard(p_id number,p_uid varchar2,p_cell varchar2,p_qty number,p_uom varchar2,p_uom_version number,
   p_doc_type varchar2,p_doc_id number,p_line_id number,p_domain varchar2,p_actor varchar2,p_details clob default null);
 procedure release_hard(p_id number,p_qty number,p_uom_version number,p_doc_type varchar2,p_doc_id number,p_actor varchar2);
 procedure consume_hard(p_id number,p_qty number,p_uom_version number,p_doc_type varchar2,p_doc_id number,p_actor varchar2);
 procedure relocate_hard(p_id number,p_new_id number,p_target_uid varchar2,p_target_cell varchar2,
   p_qty number,p_uom_version number,p_actor varchar2);
 procedure move_coverage(p_id number,p_new_id number,p_target_uid varchar2,p_target_cell varchar2,
  p_target_ware number,p_qty number,p_target_slot number,p_actor varchar2,p_result_id out number);
end;
/

create or replace package RRL_STOCK_LOCATION_CORE authid definer
 accessible by(package RRL_STOCK_INVENTORY_CMD,package RRL_STOCK_MES_SUPPLY_CMD,package RRL_STOCK_MES_MOVEMENT_CORE,package RRL_STOCK_RECEIPT_CORE,package RRL_STOCK_RESERVATION_CMD,package RRL_STOCK_POSTING_API,package RRL_STOCK_MOVE_CORE,
  package RRL_STOCK_RESERVE_CORE,package RRL_STOCK_RECEIPT_CORE,package RRL_STOCK_TRANSFER_CORE,package RRL_STOCK_EFFECT_CORE) as
 procedure assert_receiving(p_cell varchar2,p_expected_warehouse number);
 procedure assert_quarantine(p_cell varchar2,p_expected_warehouse number);
 procedure assert_ordinary(p_cell varchar2,p_expected_warehouse number,p_role varchar2);
end;
/

create or replace package RRL_STOCK_UNIT_CORE authid definer
 accessible by(package RRL_STOCK_INVENTORY_CMD,package RRL_STOCK_MES_CANCEL_CMD,package RRL_STOCK_MES_SUPPLY_CMD,package RRL_STOCK_DOC_RESERVE_CMD,package RRL_STOCK_WAVE_CMD,package RRL_STOCK_MES_MOVEMENT_CORE,package RRL_STOCK_INVARIANT_CORE,package RRL_STOCK_RESERVATION_CMD,package RRL_STOCK_TRANSFER_CORE,
 package RRL_STOCK_EFFECT_CORE,package RRL_STOCK_RECEIPT_CORE) as
 function automatic_units(p_uid varchar2,p_cell varchar2,p_qty number) return clob;
 procedure admit_captured(p_uid varchar2,p_cell varchar2);
 procedure assert_composition(p_uid varchar2,p_cell varchar2);
 procedure issue_free_units(p_uid varchar2,p_cell varchar2,p_qty number,p_units clob);
 procedure reserve_units(p_uid varchar2,p_cell varchar2,p_id number,p_qty number,p_units clob);
 procedure release_units(p_id number,p_qty number,p_units clob,p_issue number default 0);
end;
/

create or replace package RRL_STOCK_POSTING_API authid definer as
 procedure prepare_command(p_request clob,p_actor varchar2,p_replay out clob,p_hints clob default null);
 procedure execute_prepared(p_result out clob);
 procedure reset_connection;
end;
/

create or replace package RRL_STOCK_INVENTORY_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_count(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_count(p_request clob,p_actor varchar2,p_result out clob);
end;
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

create or replace package body RRL_STOCK_RESERVE_CORE as
 procedure lock_identity(p_id number) is
 begin
  if p_id is null or p_id<1 or p_id!=trunc(p_id) then raise_application_error(-20876,'RESERVATION_ID_INVALID'); end if;
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_STOCK_RESERVATION',to_char(p_id,'TM9','NLS_NUMERIC_CHARACTERS=''.,''')));
 end;
 procedure check_owner(p_id number,p_qty number,p_doc_type varchar2,p_doc_id number,p_r out RRL_STOCK_RESERVATION%rowtype) is
 begin
  lock_identity(p_id);
  select * into p_r from RRL_STOCK_RESERVATION where RESERVATION_ID=p_id for update;
  if p_r.RESERVATION_KIND is null or p_r.RESERVATION_KIND!='HARD' or p_r.STATUS is null or p_r.STATUS not in('ACTIVE','ALLOCATED','PICKING')
   or p_r.BASE_QTY is null or p_r.BASE_UOM is null or p_qty is null or p_qty<=0 or p_qty>p_r.BASE_QTY
   or p_doc_type is null or p_doc_id is null or p_r.SOURCE_DOC_TYPE is null or p_r.SOURCE_DOC_ID is null or p_r.SOURCE_DOC_TYPE!=p_doc_type or p_r.SOURCE_DOC_ID!=p_doc_id then
   raise_application_error(-20869,'RESERVATION_CONFLICT');
  end if;
  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',p_r.UID_PALLET));
 end;
 procedure decrease(p_r RRL_STOCK_RESERVATION%rowtype,p_qty number,p_status varchar2,p_actor varchar2) is
 begin
  RRL_STOCK_CTX_API.begin_effect('RESERVATION',p_r.UID_PALLET,p_r.CELL,p_r.RESERVATION_ID);
  update RRL_STOCK_RESERVATION set BASE_QTY=BASE_QTY-p_qty,QTY=BASE_QTY-p_qty,UNIT_CODE=BASE_UOM,
   STATUS=case when BASE_QTY=p_qty then p_status else STATUS end,
   CONSUMED_AT=case when BASE_QTY=p_qty and p_status='CONSUMED' then systimestamp else CONSUMED_AT end,
   CONSUMED_BY=case when BASE_QTY=p_qty and p_status='CONSUMED' then p_actor else CONSUMED_BY end,
   RELEASED_AT=case when BASE_QTY=p_qty and p_status='RELEASED' then systimestamp else RELEASED_AT end,
   RELEASED_BY=case when BASE_QTY=p_qty and p_status='RELEASED' then p_actor else RELEASED_BY end,
   RESERVATION_VERSION=RESERVATION_VERSION+1
   where RESERVATION_ID=p_r.RESERVATION_ID and RESERVATION_VERSION=p_r.RESERVATION_VERSION;
  if sql%rowcount!=1 then raise_application_error(-20867,'VERSION_CONFLICT'); end if;
  RRL_STOCK_CTX_API.end_effect;
 end;
 procedure create_hard(p_id number,p_uid varchar2,p_cell varchar2,p_qty number,p_uom varchar2,p_uom_version number,
   p_doc_type varchar2,p_doc_id number,p_line_id number,p_domain varchar2,p_actor varchar2,p_details clob default null) is v_article varchar2(160);v_ware number;v_details json_object_t;
 begin
  lock_identity(p_id);
  select ARTICUL into v_article from RRL_PALLETS where UID_PALLET=p_uid;
  select WARE_ID into v_ware from RRL_CELLS where CELL=p_cell;
  if p_qty is null or p_qty<=0 or p_doc_id is null or p_doc_type is null or p_domain is null then raise_application_error(-20869,'RESERVATION_CONFLICT'); end if;
  RRL_STOCK_BALANCE_CORE.apply_delta(p_uid,p_cell,0,p_qty,p_uom,p_uom_version);
  RRL_STOCK_CTX_API.begin_effect('RESERVATION',p_uid,p_cell,p_id);
  insert into RRL_STOCK_RESERVATION(RESERVATION_ID,RESERVATION_KIND,RESERVATION_SCOPE,RESERVATION_DOMAIN,
   SOURCE_DOC_TYPE,SOURCE_DOC_ID,SOURCE_LINE_ID,ARTICUL,QTY,UNIT_CODE,WARE_ID,CELL,UID_PALLET,
   STATUS,PRIORITY,CREATED_BY,BASE_QTY,BASE_UOM,RESERVATION_VERSION)
   values(p_id,'HARD','QTY',p_domain,p_doc_type,p_doc_id,p_line_id,v_article,p_qty,p_uom,v_ware,p_cell,p_uid,
   'ACTIVE',0,p_actor,p_qty,p_uom,0);
  if p_details is not null then
   v_details:=json_object_t.parse(p_details);
   if v_details.get_string('reservation_scope') is null or v_details.get_string('reservation_scope') not in('PALLET','QTY') then raise_application_error(-20869,'RESERVATION_SCOPE_INVALID');end if;
   update RRL_STOCK_RESERVATION set RESERVATION_SCOPE=v_details.get_string('reservation_scope'),
    TASK_ID=v_details.get_number('task_id'),CUSTOMER_ID=v_details.get_number('customer_id'),CUSTOMER_ORDER_ID=v_details.get_number('customer_order_id'),
    PRODUCTION_ORDER_ID=case when p_doc_type='PRODUCTION_ORDER' then p_doc_id else v_details.get_number('production_order_id') end,
    PICK_PLAN_ID=case when p_doc_type='PICK_PLAN' then p_doc_id else v_details.get_number('pick_plan_id') end,
    PICK_PLAN_LINE_ID=v_details.get_number('pick_plan_line_id'),PICK_WAVE_ID=case when p_doc_type='PICK_WAVE' then p_doc_id else v_details.get_number('pick_wave_id') end,
    PICK_WAVE_LINE_ID=v_details.get_number('pick_wave_line_id'),BATCH_ID=v_details.get_string('batch_id'),PROD_BATCH_ID=v_details.get_number('prod_batch_id'),
    CELL_SLOT_ID=v_details.get_number('cell_slot_id'),PRIORITY=nvl(v_details.get_number('priority'),100),RESERVATION_VERSION=RESERVATION_VERSION+1
    where RESERVATION_ID=p_id;
  end if;
  RRL_STOCK_CTX_API.end_effect;
 end;
 procedure release_hard(p_id number,p_qty number,p_uom_version number,p_doc_type varchar2,p_doc_id number,p_actor varchar2) is r RRL_STOCK_RESERVATION%rowtype;
 begin
  check_owner(p_id,p_qty,p_doc_type,p_doc_id,r);
  RRL_STOCK_BALANCE_CORE.apply_delta(r.UID_PALLET,r.CELL,0,-p_qty,r.BASE_UOM,p_uom_version);
  decrease(r,p_qty,'RELEASED',p_actor);
 end;
 procedure consume_hard(p_id number,p_qty number,p_uom_version number,p_doc_type varchar2,p_doc_id number,p_actor varchar2) is r RRL_STOCK_RESERVATION%rowtype;
 begin
  check_owner(p_id,p_qty,p_doc_type,p_doc_id,r);
  RRL_STOCK_BALANCE_CORE.apply_delta(r.UID_PALLET,r.CELL,-p_qty,-p_qty,r.BASE_UOM,p_uom_version);
  decrease(r,p_qty,'CONSUMED',p_actor);
 end;
 procedure relocate_hard(p_id number,p_new_id number,p_target_uid varchar2,p_target_cell varchar2,
   p_qty number,p_uom_version number,p_actor varchar2) is
  r RRL_STOCK_RESERVATION%rowtype;v_art varchar2(160);v_ware number;
 begin
  lock_identity(p_id);lock_identity(p_new_id);
  select * into r from RRL_STOCK_RESERVATION where RESERVATION_ID=p_id for update;
  if r.RESERVATION_KIND!='HARD' or r.STATUS not in('ACTIVE','ALLOCATED','PICKING')
   or r.BASE_QTY is null or p_qty is null or p_qty<=0 or r.BASE_QTY<p_qty then raise_application_error(-20869,'RESERVATION_CONFLICT'); end if;
  select ARTICUL into v_art from RRL_PALLETS where UID_PALLET=p_target_uid;
  select WARE_ID into v_ware from RRL_CELLS where CELL=p_target_cell;
  if v_art!=r.ARTICUL then raise_application_error(-20869,'RESERVATION_ARTICLE_CONFLICT'); end if;
  -- Must accompany physical movement of the same q; source/destination P/H changed together.
  RRL_STOCK_BALANCE_CORE.apply_delta(r.UID_PALLET,r.CELL,-p_qty,-p_qty,r.BASE_UOM,p_uom_version);
  RRL_STOCK_BALANCE_CORE.apply_delta(p_target_uid,p_target_cell,p_qty,p_qty,r.BASE_UOM,p_uom_version);
  RRL_STOCK_CTX_API.begin_effect('RESERVATION',p_target_uid,p_target_cell,p_new_id);
  insert into RRL_STOCK_RESERVATION(RESERVATION_ID,RESERVATION_KIND,RESERVATION_SCOPE,RESERVATION_DOMAIN,
   SOURCE_DOC_TYPE,SOURCE_DOC_ID,SOURCE_LINE_ID,TASK_ID,CUSTOMER_ID,CUSTOMER_ORDER_ID,PRODUCTION_ORDER_ID,
   PICK_PLAN_ID,PICK_PLAN_LINE_ID,PICK_WAVE_ID,PICK_WAVE_LINE_ID,ARTICUL,QTY,UNIT_CODE,WARE_ID,CELL,
   BATCH_ID,PROD_BATCH_ID,UID_PALLET,SSCC,STATUS,PRIORITY,CREATED_BY,BASE_QTY,BASE_UOM,RESERVATION_VERSION)
   values(p_new_id,'HARD',r.RESERVATION_SCOPE,r.RESERVATION_DOMAIN,r.SOURCE_DOC_TYPE,r.SOURCE_DOC_ID,
   r.SOURCE_LINE_ID,r.TASK_ID,r.CUSTOMER_ID,r.CUSTOMER_ORDER_ID,r.PRODUCTION_ORDER_ID,r.PICK_PLAN_ID,
   r.PICK_PLAN_LINE_ID,r.PICK_WAVE_ID,r.PICK_WAVE_LINE_ID,r.ARTICUL,p_qty,r.BASE_UOM,v_ware,p_target_cell,
   r.BATCH_ID,r.PROD_BATCH_ID,p_target_uid,null,r.STATUS,r.PRIORITY,p_actor,p_qty,r.BASE_UOM,0);
  RRL_STOCK_CTX_API.end_effect;
  decrease(r,p_qty,'CONSUMED',p_actor);
 end;
 procedure move_coverage(p_id number,p_new_id number,p_target_uid varchar2,p_target_cell varchar2,
  p_target_ware number,p_qty number,p_target_slot number,p_actor varchar2,p_result_id out number) is
  v_r RRL_STOCK_RESERVATION%rowtype;v_new RRL_STOCK_RESERVATION%rowtype;
 begin
  lock_identity(p_id);
  select * into v_r from RRL_STOCK_RESERVATION where RESERVATION_ID=p_id for update;
  if v_r.BASE_QTY is null or p_qty is null or p_qty<=0 or p_qty>v_r.BASE_QTY
   or v_r.RESERVATION_KIND is null or v_r.RESERVATION_KIND!='HARD'
   or v_r.STATUS is null or v_r.STATUS not in('ACTIVE','ALLOCATED','PICKING')
   or v_r.BASE_UOM is null then raise_application_error(-20869,'RESERVATION_COVERAGE_CONFLICT');end if;
  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID') is null
   or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then
   raise_application_error(-20863,'STOCK_WRITE_FORBIDDEN');end if;
  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',v_r.UID_PALLET));
  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',p_target_uid));
  if p_target_slot is not null then
   RRL_STOCK_LOCK_API.assert_held(40,RRL_STOCK_LOCK_API.resource_key('SLOT',to_char(p_target_slot,'TM9')));
  end if;
  if p_qty=v_r.BASE_QTY then
   RRL_STOCK_CTX_API.begin_effect('RESERVATION',p_target_uid,p_target_cell,p_id);
   update RRL_STOCK_RESERVATION set UID_PALLET=p_target_uid,CELL=p_target_cell,WARE_ID=p_target_ware,
    CELL_SLOT_ID=p_target_slot,RESERVATION_VERSION=RESERVATION_VERSION+1 where RESERVATION_ID=p_id;
   RRL_STOCK_CTX_API.end_effect;
   p_result_id:=p_id;
  else
   lock_identity(p_new_id);v_new:=v_r;v_new.RESERVATION_ID:=p_new_id;
   v_new.UID_PALLET:=p_target_uid;v_new.CELL:=p_target_cell;v_new.WARE_ID:=p_target_ware;
   v_new.CELL_SLOT_ID:=p_target_slot;v_new.BASE_QTY:=p_qty;v_new.QTY:=p_qty;v_new.UNIT_CODE:=v_new.BASE_UOM;
   v_new.RESERVATION_VERSION:=0;v_new.CREATED_AT:=systimestamp;v_new.CREATED_BY:=p_actor;
   v_new.RELEASED_AT:=null;v_new.RELEASED_BY:=null;v_new.CONSUMED_AT:=null;v_new.CONSUMED_BY:=null;
   RRL_STOCK_CTX_API.begin_effect('RESERVATION',p_target_uid,p_target_cell,p_new_id);
   insert into RRL_STOCK_RESERVATION values v_new;
   RRL_STOCK_CTX_API.end_effect;
   RRL_STOCK_CTX_API.begin_effect('RESERVATION',v_r.UID_PALLET,v_r.CELL,p_id);
   update RRL_STOCK_RESERVATION set BASE_QTY=BASE_QTY-p_qty,QTY=BASE_QTY-p_qty,UNIT_CODE=BASE_UOM,
    RESERVATION_VERSION=RESERVATION_VERSION+1 where RESERVATION_ID=p_id;
   RRL_STOCK_CTX_API.end_effect;
   p_result_id:=p_new_id;
  end if;
 end;
end;
/

create or replace package body RRL_STOCK_LOCATION_CORE as
 procedure assert_receiving(p_cell varchar2,p_expected_warehouse number) is v_ware number;v_block number;
 begin
  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CELL',p_cell),4);
  select WARE_ID,nvl(BLOCKED_FOR_ACCEPT,0) into v_ware,v_block from RRL_CELLS where CELL=p_cell;
  if v_ware is null or p_expected_warehouse is null or v_ware!=p_expected_warehouse or v_block!=0 then raise_application_error(-20879,'RECEIVING_LOCATION_UNAVAILABLE');end if;
 end;
 procedure assert_quarantine(p_cell varchar2,p_expected_warehouse number) is v_ware number;
 begin
  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CELL',p_cell),4);
  select WARE_ID into v_ware from RRL_CELLS where CELL=p_cell;
  if v_ware is null or p_expected_warehouse is null or v_ware!=p_expected_warehouse then raise_application_error(-20877,'QUARANTINE_WAREHOUSE_CONFLICT');end if;
 end;
 procedure assert_ordinary(p_cell varchar2,p_expected_warehouse number,p_role varchar2) is
  v_ware number;v_remain number;v_replenish number;v_accept number;
 begin
  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CELL',p_cell),4);
  select WARE_ID,nvl(BLOCKED_FOR_REMAINS,0),nvl(BLOCKED_FOR_POPOLNENIE,0),nvl(BLOCKED_FOR_ACCEPT,0)
   into v_ware,v_remain,v_replenish,v_accept from RRL_CELLS where CELL=p_cell;
  if p_expected_warehouse is null or v_ware is null or v_ware!=p_expected_warehouse then
   raise_application_error(-20877,'WAREHOUSE_LOCATION_CONFLICT');
  end if;
  if p_role not in('SOURCE','TARGET','RECEIVE') or p_role is null then raise_application_error(-20878,'LOCATION_ROLE_INVALID'); end if;
  if v_remain!=0 or v_replenish!=0 or(p_role in('TARGET','RECEIVE') and v_accept!=0) then
   raise_application_error(-20879,'LOCATION_BLOCKED: quarantine/unavailable cell excluded');
  end if;
 end;
end;
/

create or replace package body RRL_STOCK_UNIT_CORE as
 procedure require_context is
 begin
  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID') is null or
   sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or
   sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then
   raise_application_error(-20863,'UNIT_WRITE_FORBIDDEN');end if;
 end;
 procedure own_unit(p_key varchar2) is
 begin
  if p_key is null then raise_application_error(-20884,'UNIT_BINDING_REQUIRED');end if;
  begin RRL_STOCK_LOCK_API.assert_held(60,RRL_STOCK_LOCK_API.resource_key('UNIT',p_key));
  exception when others then if sqlcode=-20850 then raise_application_error(-20890,'CLOSURE_CHANGED: units');else raise;end if;end;
 end;
 procedure assert_composition(p_uid varchar2,p_cell varchar2) is
  v_p number;v_base varchar2(20);v_total number;v_count number;v_bad number;v_article varchar2(160);v_marked number;v_scale number;
 begin
  select REMAIN,BASE_UOM into v_p,v_base from RRL_REMAINS where UID_POLETA=p_uid and CELL=p_cell;
  select ARTICUL into v_article from RRL_PALLETS where UID_PALLET=p_uid;
  select greatest(nvl((select MARKING_REQUIRED from RRL_SKU_RECEIPT_POLICY where ARTICUL=v_article),0),
   nvl((select CRPT_REQUIRED from RRL_FINISHED_GOODS_SKU where ARTICUL=v_article),0),
   case when exists(select 1 from RRL_SKU_RECEIPT_PROFILE where ARTICUL=v_article) then 1 else 0 end) into v_marked from dual;
  select count(*),nvl(sum(BASE_QTY),0),nvl(sum(case when PHYSICAL_UNIT_KEY is null or STOCK_STATUS is null or BASE_QTY<=0 or BASE_UOM is null or BASE_UOM!=v_base then 1 else 0 end),0)
   into v_count,v_total,v_bad from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and (STOCK_STATUS is null or STOCK_STATUS!='ISSUED');
  select max(BASE_SCALE) into v_scale from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article and BASE_UOM=v_base;
  if v_scale is null then raise_application_error(-20868,'COMPOSITION_BASE_POLICY_REQUIRED');end if;
  select count(*) into v_bad from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and (STOCK_STATUS is null or STOCK_STATUS!='ISSUED')
   and (STOCK_STATUS is null or BASE_QTY is null or BASE_QTY<=0 or abs(BASE_QTY)>=power(10,18) or trunc(BASE_QTY,v_scale)!=BASE_QTY or BASE_UOM is null or BASE_UOM!=v_base or PHYSICAL_UNIT_KEY is null);
  if v_bad>0 or (v_count>0 and v_total!=v_p) or (v_marked=1 and v_p>0 and v_count=0) then
   raise_application_error(-20884,'PHYSICAL_COMPOSITION_CONFLICT');end if;
 end;
 function automatic_units(p_uid varchar2,p_cell varchar2,p_qty number) return clob is
  a json_array_t:=json_array_t();v_n number;v_qty number:=0;
 begin
  require_context;assert_composition(p_uid,p_cell);
  select count(*) into v_n from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS!='ISSUED';
  if v_n=0 then return null;end if;
  for u in(select PHYSICAL_UNIT_KEY,BASE_QTY from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS='AVAILABLE' and HARD_RESERVATION_ID is null order by PHYSICAL_UNIT_KEY) loop
   exit when v_qty=p_qty;
   own_unit(u.PHYSICAL_UNIT_KEY);
   if v_qty+u.BASE_QTY>p_qty then raise_application_error(-20884,'PHYSICAL_UNIT_ALLOCATION_REQUIRES_SELECTION');end if;
   a.append(u.PHYSICAL_UNIT_KEY);v_qty:=v_qty+u.BASE_QTY;
   if a.get_size>10000 then raise_application_error(-20884,'UNIT_SELECTION_BOUND');end if;
  end loop;
  if v_qty!=p_qty then raise_application_error(-20884,'ADMITTED_FREE_UNITS_INSUFFICIENT');end if;
  return a.to_clob;
 end;
 procedure admit_captured(p_uid varchar2,p_cell varchar2) is
 begin
  require_context;assert_composition(p_uid,p_cell);
  for u in(select PHYSICAL_UNIT_KEY from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS='CAPTURED') loop own_unit(u.PHYSICAL_UNIT_KEY);end loop;
  RRL_STOCK_CTX_API.begin_effect('UNIT',p_uid,p_cell);
  update RRL_WMS_RECEIPT_UNIT set STOCK_STATUS='AVAILABLE',UNIT_VERSION=UNIT_VERSION+1
   where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS='CAPTURED';
  RRL_STOCK_CTX_API.end_effect;
 end;
 procedure issue_free_units(p_uid varchar2,p_cell varchar2,p_qty number,p_units clob) is v_total number;v_count number;v_qty number;v_expected number;v_distinct number;
 begin
  require_context;assert_composition(p_uid,p_cell);
  select count(*) into v_total from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS!='ISSUED';
  if v_total=0 then return;end if;
  select count(*),nvl(sum(BASE_QTY),0) into v_count,v_qty from RRL_WMS_RECEIPT_UNIT u
   where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS!='ISSUED'
    and (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY));
  if v_qty!=p_qty then raise_application_error(-20884,'ISSUE_UNIT_QUANTITY_CONFLICT');end if;
  if p_units is not null then
   select count(*),count(distinct K) into v_expected,v_distinct from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'));
   if v_count!=v_expected or v_expected!=v_distinct then raise_application_error(-20884,'UNIT_SELECTION_CONFLICT');end if;
  end if;
  for r in(select PHYSICAL_UNIT_KEY,STOCK_STATUS,HARD_RESERVATION_ID from RRL_WMS_RECEIPT_UNIT u
   where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS!='ISSUED'
    and (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY))) loop
   own_unit(r.PHYSICAL_UNIT_KEY);
   if r.HARD_RESERVATION_ID is not null then raise_application_error(-20869,'UNIT_RESERVED_BY_OTHER_OWNER');end if;
   if r.STOCK_STATUS!='AVAILABLE' then raise_application_error(-20884,'UNIT_NOT_ADMITTED');end if;
  end loop;
  RRL_STOCK_CTX_API.begin_effect('UNIT',p_uid,p_cell);
  update RRL_WMS_RECEIPT_UNIT u set STOCK_STATUS='ISSUED',UNIT_VERSION=UNIT_VERSION+1
   where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS!='ISSUED'
    and (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY));
  RRL_STOCK_CTX_API.end_effect;
 end;
 procedure reserve_units(p_uid varchar2,p_cell varchar2,p_id number,p_qty number,p_units clob) is
  v_count number;v_total number;v_chosen number;v_qty number;v_expected number;
 begin
  require_context;assert_composition(p_uid,p_cell);
  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',p_uid));
  select count(*),nvl(sum(BASE_QTY),0) into v_count,v_total from RRL_WMS_RECEIPT_UNIT
   where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS!='ISSUED';
  if v_count=0 then return;end if;
  select count(*),nvl(sum(BASE_QTY),0) into v_chosen,v_qty from RRL_WMS_RECEIPT_UNIT u
   where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS!='ISSUED'
    and (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY));
  if v_qty!=p_qty then raise_application_error(-20884,'RESERVATION_UNIT_QUANTITY_CONFLICT');end if;
  if p_units is not null then
   select count(*),count(distinct K) into v_expected,v_count from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'));
   if v_expected!=v_count or v_expected!=v_chosen then raise_application_error(-20884,'UNIT_SELECTION_CONFLICT');end if;
  end if;
  for r in(select PHYSICAL_UNIT_KEY,HARD_RESERVATION_ID,STOCK_STATUS from RRL_WMS_RECEIPT_UNIT u
   where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS!='ISSUED'
    and (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY))) loop
   own_unit(r.PHYSICAL_UNIT_KEY);
   if r.HARD_RESERVATION_ID is not null then raise_application_error(-20869,'UNIT_ALREADY_RESERVED');end if;
   if r.STOCK_STATUS!='AVAILABLE' then raise_application_error(-20884,'UNIT_NOT_ADMITTED');end if;
  end loop;
  RRL_STOCK_CTX_API.begin_effect('UNIT',p_uid,p_cell);
  update RRL_WMS_RECEIPT_UNIT u set HARD_RESERVATION_ID=p_id,UNIT_VERSION=UNIT_VERSION+1
   where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS!='ISSUED'
    and (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY));
  RRL_STOCK_CTX_API.end_effect;
 end;
 procedure release_units(p_id number,p_qty number,p_units clob,p_issue number default 0) is
  v_qty number;v_count number;v_expected number;v_distinct number;v_uid varchar2(200);v_cell varchar2(60);
 begin
  require_context;
  select UID_PALLET,CELL into v_uid,v_cell from RRL_STOCK_RESERVATION where RESERVATION_ID=p_id;
  assert_composition(v_uid,v_cell);
  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',v_uid));
  select count(*),nvl(sum(BASE_QTY),0) into v_count,v_qty from RRL_WMS_RECEIPT_UNIT u
   where HARD_RESERVATION_ID=p_id and STOCK_STATUS!='ISSUED'
    and (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY));
  if v_count=0 then
   select count(*) into v_expected from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=v_uid and CURRENT_CELL=v_cell and STOCK_STATUS!='ISSUED';
   if v_expected>0 then raise_application_error(-20869,'RESERVATION_UNIT_BINDING_REQUIRED');end if;
   return;end if;
  if v_qty!=p_qty then raise_application_error(-20884,'RESERVATION_UNIT_QUANTITY_CONFLICT');end if;
  if p_units is not null then
   select count(*),count(distinct K) into v_expected,v_distinct from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'));
   if v_count!=v_expected or v_expected!=v_distinct then raise_application_error(-20884,'UNIT_SELECTION_CONFLICT');end if;
  end if;
  for r in(select PHYSICAL_UNIT_KEY,STOCK_STATUS from RRL_WMS_RECEIPT_UNIT u
   where HARD_RESERVATION_ID=p_id and STOCK_STATUS!='ISSUED'
    and (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY))) loop
   own_unit(r.PHYSICAL_UNIT_KEY);
   if p_issue=1 and r.STOCK_STATUS!='AVAILABLE' then raise_application_error(-20884,'UNIT_NOT_ADMITTED');end if;
  end loop;
  RRL_STOCK_CTX_API.begin_effect('UNIT',v_uid,v_cell);
  update RRL_WMS_RECEIPT_UNIT u set HARD_RESERVATION_ID=null,UNIT_VERSION=UNIT_VERSION+1,
   STOCK_STATUS=case when p_issue=1 then 'ISSUED' else STOCK_STATUS end
   where HARD_RESERVATION_ID=p_id and STOCK_STATUS!='ISSUED'
    and (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY));
  RRL_STOCK_CTX_API.end_effect;
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

create or replace package body RRL_STOCK_INVENTORY_CMD as
 procedure compile_count(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
  d json_object_t:=json_object_t.parse(p_request);a json_array_t;b json_array_t:=json_array_t();x json_object_t;y json_object_t;v json_object_t:=json_object_t();
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();doc number;ware number;article varchar2(160);base varchar2(20);inputu varchar2(20);
  qty number;ver number;stockver number;signature varchar2(64);p number;h number;k varchar2(2000);
  type keys is table of boolean index by varchar2(2000);seen keys;
 begin
  doc:=d.get_object('source').get_number('revision_id');select WARE_ID into ware from RRL_REVIZION where ID=doc;
  a:=d.get_object('metadata').get_array('counts');
  if a is null or a.get_size<1 or a.get_size>200 then raise_application_error(-20881,'INVENTORY_COUNT_BATCH_BOUND');end if;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_REVIZION',RRL_STOCK_PLAN_HELPER.decimal_text(doc));
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i) as json_object_t);select ARTICUL into article from RRL_PALLETS where UID_PALLET=x.get_string('uid');
   if article is null or article!=x.get_string('article') then raise_application_error(-20887,'INVENTORY_LOT_ARTICLE_CONFLICT');end if;
   k:=rawtohex(RRL_STOCK_LOCK_API.resource_key('STOCK',x.get_string('uid'),x.get_string('cell')));if seen.exists(k) then raise_application_error(-20885,'INVENTORY_LOT_REPEATED');end if;seen(k):=true;
   inputu:=x.get_string('unit');
   RRL_STOCK_PALLET_UOM.resolve_quantity(x.get_string('uid'),inputu,
    case when regexp_like(x.get_string('quantity'),'^0([.]0{1,9})?$') then '1' else x.get_string('quantity') end,base,qty,ver,signature);
   if regexp_like(x.get_string('quantity'),'^0([.]0{1,9})?$') then qty:=0;end if;
   begin select REMAIN,HARD_RESERVED_BASE,STOCK_VERSION into p,h,stockver from RRL_REMAINS where UID_POLETA=x.get_string('uid') and CELL=x.get_string('cell');
   exception when no_data_found then p:=0;h:=0;stockver:=0;end;
   if x.get_number('expected_stock_version') is null or x.get_number('expected_stock_version')!=stockver then raise_application_error(-20867,'INVENTORY_SNAPSHOT_STALE');end if;
   RRL_STOCK_PLAN_HELPER.stock_closure(f,r,x.get_string('uid'),article,x.get_string('cell'),null);
   y:=json_object_t();y.put('uid',x.get_string('uid'));y.put('cell',x.get_string('cell'));y.put('article',article);
   y.put('base',base);y.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(qty));y.put('p',RRL_STOCK_PLAN_HELPER.decimal_text(p));
   y.put('h',RRL_STOCK_PLAN_HELPER.decimal_text(h));y.put('version',stockver);y.put('uom_version',ver);y.put('signature',signature);b.append(y);
  end loop;
  v.put('document',doc);v.put('warehouse',ware);v.put('counts',b);p_domain:=v.to_clob;p_policies:=f.to_clob;p_resources:=r.to_clob;
 end;
 procedure execute_count(p_request clob,p_actor varchar2,p_result out clob) is
  d json_object_t:=json_object_t.parse(p_request);v json_object_t;x json_object_t;sourcex json_object_t;fact json_object_t;result json_object_t:=json_object_t();
  a json_array_t;original json_array_t;facts json_array_t:=json_array_t();plan clob;doc number;ware number;cond number;
  p number;h number;stockver number;qty number;delta number;ver number;eventid number;marking number;signature varchar2(64);base varchar2(20);units clob;
 begin
  if RRL_HAS_WRIGHT(p_actor,'stock_inventory_count')!=1 then raise_application_error(-20882,'INVENTORY_COUNT_FORBIDDEN');end if;
  if trim(d.get_object('metadata').get_string('reason')) is null then raise_application_error(-20883,'INVENTORY_REASON_REQUIRED');end if;
  select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=d.get_string('operation_id');v:=json_object_t.parse(plan).get_object('domain');
  doc:=v.get_number('document');select WARE_ID,CONDITION into ware,cond from RRL_REVIZION where ID=doc for update;
  if ware!=v.get_number('warehouse') or cond is null or cond in(2,3) then raise_application_error(-20886,'INVENTORY_DOCUMENT_NOT_OPEN');end if;
  a:=v.get_array('counts');original:=d.get_object('metadata').get_array('counts');
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i) as json_object_t);sourcex:=treat(original.get(i) as json_object_t);
   RRL_STOCK_LOCATION_CORE.assert_quarantine(x.get_string('cell'),ware);
   begin select REMAIN,HARD_RESERVED_BASE,STOCK_VERSION into p,h,stockver from RRL_REMAINS where UID_POLETA=x.get_string('uid') and CELL=x.get_string('cell');
   exception when no_data_found then p:=0;h:=0;stockver:=0;end;
   if stockver!=x.get_number('version') or RRL_STOCK_PLAN_HELPER.decimal_text(p)!=x.get_string('p') or RRL_STOCK_PLAN_HELPER.decimal_text(h)!=x.get_string('h') then raise_application_error(-20890,'CLOSURE_CHANGED: inventory stock');end if;
   RRL_STOCK_PALLET_UOM.resolve_quantity(x.get_string('uid'),sourcex.get_string('unit'),
    case when regexp_like(sourcex.get_string('quantity'),'^0([.]0{1,9})?$') then '1' else sourcex.get_string('quantity') end,base,qty,ver,signature);
   if regexp_like(sourcex.get_string('quantity'),'^0([.]0{1,9})?$') then qty:=0;end if;
   if signature!=x.get_string('signature') or base!=x.get_string('base') then raise_application_error(-20890,'CLOSURE_CHANGED: inventory UOM');end if;
   if qty<h then raise_application_error(-20869,'INVENTORY_COUNT_BELOW_HARD: explicitly release conflicting reservations first');end if;
   delta:=qty-p;eventid:=null;units:=null;
   if sourcex.has('unit_keys') and sourcex.get_array('unit_keys').get_size>0 then units:=sourcex.get_array('unit_keys').to_clob;end if;
   if delta>0 then
    select greatest(nvl((select MARKING_REQUIRED from RRL_SKU_RECEIPT_POLICY where ARTICUL=x.get_string('article')),0),
      nvl((select CRPT_REQUIRED from RRL_FINISHED_GOODS_SKU where ARTICUL=x.get_string('article')),0),
      case when exists(select 1 from RRL_SKU_RECEIPT_PROFILE where ARTICUL=x.get_string('article')) then 1 else 0 end) into marking from dual;
    if marking!=0 then raise_application_error(-20884,'MARKED_INVENTORY_INCREASE_REQUIRES_CAPTURED_UNITS');end if;
    RRL_STOCK_BALANCE_CORE.apply_delta(x.get_string('uid'),x.get_string('cell'),delta,0,base,ver,stockver);
    RRL_STOCK_BALANCE_CORE.write_leg(x.get_string('uid'),null,x.get_string('cell'),delta,base,ver,i+1,1,1,p_actor,eventid);
   elsif delta<0 then
    RRL_STOCK_UNIT_CORE.issue_free_units(x.get_string('uid'),x.get_string('cell'),-delta,units);
    RRL_STOCK_BALANCE_CORE.apply_delta(x.get_string('uid'),x.get_string('cell'),delta,0,base,ver,stockver);
    RRL_STOCK_BALANCE_CORE.write_leg(x.get_string('uid'),x.get_string('cell'),null,delta,base,ver,i+1,1,3,p_actor,eventid);
   end if;
   fact:=json_object_t();fact.put('uid',x.get_string('uid'));fact.put('cell',x.get_string('cell'));fact.put('base_uom',base);
   fact.put('before',RRL_STOCK_PLAN_HELPER.decimal_text(p));fact.put('after',RRL_STOCK_PLAN_HELPER.decimal_text(qty));fact.put('delta',RRL_STOCK_PLAN_HELPER.decimal_text(delta));fact.put('event_id',eventid);facts.append(fact);
  end loop;
  result.put('operation_id',d.get_string('operation_id'));result.put('revision_id',doc);result.put('counts',facts);p_result:=result.to_clob;
 end;
end;
/
