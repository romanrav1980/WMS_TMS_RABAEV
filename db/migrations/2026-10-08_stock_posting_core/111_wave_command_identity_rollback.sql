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

create or replace package RRL_STOCK_DOC_RESERVE_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_release(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_release(p_request clob,p_actor varchar2,p_result out clob);
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
    declare
      st varchar2(20);j json_object_t:=json_object_t();src json_object_t:=json_object_t();m json_object_t:=json_object_t();result clob;
    begin
      select STATE into st from RRL_STOCK_RELEASE where RELEASE_ID=1;
      if st='ACTIVE' then
        j.put('contract_version',2);j.put('operation_id','WAVE_RELEASE:'||to_char(p_pick_wave_id,'TM9'));

        j.put('command_type','WAVE_RELEASE');
        j.put('actor',p_updated_by);src.put('document_type','PICK_WAVE');src.put('document_id',p_pick_wave_id);
        j.put('source',src);j.put('lines',json_array_t());j.put('units',json_array_t());
        m.put('reason','Release wave reservations');m.put('only_cancelled_replenishment',0);m.put_null('reservation_kind');j.put('metadata',m);
        RRL_STOCK_NATIVE_API.post(j.to_clob,p_updated_by,result);return;
      end if;
    end;

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
    declare
      st varchar2(20);j json_object_t:=json_object_t();src json_object_t:=json_object_t();m json_object_t:=json_object_t();result clob;
    begin
      select STATE into st from RRL_STOCK_RELEASE where RELEASE_ID=1;
      if st='ACTIVE' then
        j.put('contract_version',2);j.put('operation_id','WAVE_CANCEL:'||to_char(p_pick_wave_id,'TM9'));

        j.put('command_type','WAVE_CANCEL');
        j.put('actor',p_updated_by);src.put('document_type','PICK_WAVE');src.put('document_id',p_pick_wave_id);
        j.put('source',src);j.put('lines',json_array_t());j.put('units',json_array_t());
        m.put('reason',p_reason);m.put('only_cancelled_replenishment',0);m.put_null('reservation_kind');j.put('metadata',m);
        RRL_STOCK_NATIVE_API.post(j.to_clob,p_updated_by,result);return;
      end if;
    end;

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
  if d.get_string('command_type') in('WAVE_CANCEL','WAVE_RELEASE') then
   for z in(select PICK_WAVE_TASK_ID,PICK_TASK_ID from RRL_PICK_WAVE_TASK where PICK_WAVE_ID=v_doc order by PICK_WAVE_TASK_ID) loop
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(z.PICK_WAVE_TASK_ID));
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(z.PICK_TASK_ID));
   end loop;
   for z in(select PICK_RESERVATION_ID from RRL_PICK_RESERVATION where PICK_PLAN_ID in(select PICK_PLAN_ID from RRL_PICK_WAVE_ORDER where PICK_WAVE_ID=v_doc) order by PICK_RESERVATION_ID) loop
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(z.PICK_RESERVATION_ID));
   end loop;
   for z in(select PICK_WAVE_REPLENISH_TASK_ID from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_ID=v_doc order by PICK_WAVE_REPLENISH_TASK_ID) loop
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE_REPLENISH_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(z.PICK_WAVE_REPLENISH_TASK_ID));
   end loop;
   for z in(select TASK_ID from RRL_WAREHOUSE_TASK where SOURCE_DOC_TYPE='PICK_WAVE' and SOURCE_DOC_ID=v_doc order by TASK_ID) loop
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(z.TASK_ID));
   end loop;
  end if;
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
  if d.get_string('command_type')='WAVE_CANCEL' then
   if RRL_HAS_WRIGHT(p_actor,'pick_wave_cancel')!=1 then raise_application_error(-20882,'WAVE_CANCEL_FORBIDDEN');end if;
   RRL_PICK_WAVE_META.cancel_wave(v_doc,d.get_object('metadata').get_string('reason'),p_actor);
  elsif d.get_string('command_type')='WAVE_RELEASE' then
   if RRL_HAS_WRIGHT(p_actor,'pick_wave_release_reserves')!=1 then raise_application_error(-20882,'WAVE_RELEASE_FORBIDDEN');end if;
   RRL_PICK_WAVE_META.release_reservations(v_doc,p_actor);
  end if;
  j.put('operation_id',d.get_string('operation_id'));j.put('document_type',v_type);j.put('document_id',v_doc);j.put('released_count',a.get_size);p_result:=j.to_clob;
 end;
end;
/
