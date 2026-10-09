declare n number;begin select count(*) into n from RRL_STOCK_OPERATION; if n>0 then raise_application_error(-20808,'POSTED_OPERATIONS_PREVENT_CODE_ROLLBACK');end if;end;
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
  declare
 v_json_sql_1_1 varchar2(32767):=d.get_string('operation_id');
begin
select RESOLVED_PLAN_JSON into v_plan from RRL_STOCK_OPERATION where OPERATION_ID=v_json_sql_1_1;
end;
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
   declare
 v_json_sql_2_1 number:=x.get_number('id');
begin
select * into sr from RRL_STOCK_RESERVATION where RESERVATION_ID=v_json_sql_2_1 for update;
end;
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
    declare
 v_json_sql_3_1 varchar2(32767):=d.get_object('metadata').get_string('reason');
begin
update RRL_STOCK_RESERVATION set STATUS='RELEASED',RELEASED_AT=systimestamp,RELEASED_BY=p_actor,
     RELEASE_REASON=v_json_sql_3_1,RESERVATION_VERSION=RESERVATION_VERSION+1 where RESERVATION_ID=sr.RESERVATION_ID;
end;
    RRL_STOCK_CTX_API.end_effect;
   else raise_application_error(-20869,'RESERVATION_KIND_INVALID');end if;
  end loop;
  if d.get_string('command_type') in('WAVE_CANCEL','WAVE_RELEASE') then
   for task in(select TASK_ID,STATUS from RRL_WAREHOUSE_TASK where SOURCE_DOC_TYPE='PICK_WAVE' and SOURCE_DOC_ID=v_doc order by TASK_ID for update) loop
    if task.STATUS in('IN_PROGRESS','DONE') then raise_application_error(-20886,'WAVE_PHYSICAL_TASK_ALREADY_STARTED');end if;
    update RRL_WAREHOUSE_TASK set STATUS='CANCELLED' where TASK_ID=task.TASK_ID and STATUS in('PLANNED','ASSIGNED');
   end loop;
  end if;
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
   elsif g_kind in('DOCUMENT_RELEASE_RESERVATIONS','WAVE_CANCEL','WAVE_RELEASE') then RRL_STOCK_DOC_RESERVE_CMD.compile_release(p_request,g_operation,v_policies,v_resources,v_domain);
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
   elsif g_kind in('DOCUMENT_RELEASE_RESERVATIONS','WAVE_CANCEL','WAVE_RELEASE') then RRL_STOCK_DOC_RESERVE_CMD.execute_release(g_request,g_actor,p_result);
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
