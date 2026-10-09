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
       and (RESERVATION_LEVEL='SOFT' or exists(select 1 from RRL_STOCK_RELEASE where RELEASE_ID=1 and STATE!='ACTIVE'))
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
    v_release varchar2(20);v_requested_line_qty number;v_uom varchar2(20);v_version number;v_num number;v_den number;v_scale number;
  begin
    select STATE into v_release from RRL_STOCK_RELEASE where RELEASE_ID=1;
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
      v_requested_line_qty:=nvl(l.ORDER_QTY,0);
      if v_release='ACTIVE' then
       select max(POLICY_VERSION) into v_version from RRL_STOCK_UOM_CONVERSION where ARTICUL=l.ARTICUL and INPUT_UOM=l.UNIT_CODE;
       select BASE_UOM,NUMERATOR,DENOMINATOR,BASE_SCALE into v_uom,v_num,v_den,v_scale from RRL_STOCK_UOM_CONVERSION where ARTICUL=l.ARTICUL and INPUT_UOM=l.UNIT_CODE and POLICY_VERSION=v_version;
       v_requested_line_qty:=RRL_STOCK_MATH.convert_exact(RRL_STOCK_PLAN_HELPER.decimal_text(l.ORDER_QTY),v_num,v_den,v_scale);
      end if;
      v_remaining := v_requested_line_qty;
      v_line_planned := 0;
      v_reserved_by_other := 0;
      v_requested_total := v_requested_total + v_requested_line_qty;

      insert into RRL_PICK_PLAN_LINE (
        PICK_PLAN_LINE_ID, PICK_PLAN_ID, CUSTOMER_ORDER_ROW_ID, ARTICUL,
        PRODUCT_NAME, REQUESTED_QTY, STATUS, CREATED_AT, CREATED_BY
      ) values (
        v_line_id, v_pick_plan_id, l.CUSTOMER_ORDER_ROW_ID, upper(substr(l.ARTICUL, 1, 40)),
        l.PRODUCT_NAME, v_requested_line_qty, 'OPEN', sysdate, substr(p_created_by, 1, 50)
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
          join RRL_CELLS cc on cc.CELL=r.CELL
          left join RRL_PROD_BATCH_READY_V br
            on br.PROD_BATCH_ID = p.PROD_BATCH_ID
         where r.REMAIN > 0
           and (v_release!='ACTIVE' or (cc.WARE_ID=v_order.WARE_ID and nvl(cc.BLOCKED_FOR_REMAINS,0)=0 and nvl(cc.BLOCKED_FOR_POPOLNENIE,0)=0 and r.BASE_UOM=v_uom))
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
          if v_release='ACTIVE' then
           select REMAIN-HARD_RESERVED_BASE into v_locked_remain from RRL_REMAINS where rowid=c.REMAIN_ROWID;
          else
          select REMAIN
            into v_locked_remain
            from RRL_REMAINS
           where rowid = c.REMAIN_ROWID
           for update;
          end if;

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

      v_line_shortage := greatest(v_requested_line_qty - v_line_planned, 0);
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
          upper(substr(l.ARTICUL, 1, 40)), v_requested_line_qty,
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
    declare st varchar2(20);j json_object_t:=json_object_t();src json_object_t:=json_object_t();m json_object_t:=json_object_t();result clob;kind varchar2(80);request clob;doc number;
    begin
      select STATE into st from RRL_STOCK_RELEASE where RELEASE_ID=1;
      if st='ACTIVE' then
        if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID') is not null then
          select COMMAND_TYPE,CANONICAL_REQUEST into kind,request from RRL_STOCK_OPERATION where OPERATION_ID=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');
          doc:=json_object_t.parse(request).get_object('source').get_number('document_id');
          if kind!='PICK_PLAN_CANCEL' or doc!=p_pick_plan_id then raise_application_error(-20863,'PLAN_CANCEL_CONTEXT_CONFLICT');end if;
        else
          j.put('contract_version',2);j.put('operation_id','PLAN.CANCEL:'||to_char(p_pick_plan_id,'TM9'));j.put('command_type','PICK_PLAN_CANCEL');j.put('actor',p_updated_by);
          src.put('document_type','PICK_PLAN');src.put('document_id',p_pick_plan_id);j.put('source',src);j.put('lines',json_array_t());j.put('units',json_array_t());
          m.put('reason','Picking plan cancelled');m.put('only_cancelled_replenishment',0);m.put_null('reservation_kind');j.put('metadata',m);
          RRL_STOCK_NATIVE_API.post(j.to_clob,p_updated_by,result);return;
        end if;
      end if;
    end;

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
