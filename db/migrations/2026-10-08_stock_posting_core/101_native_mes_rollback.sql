declare n number;begin select count(*) into n from RRL_STOCK_OPERATION; if n>0 then raise_application_error(-20808,'POSTED_OPERATIONS_PREVENT_CODE_ROLLBACK');end if;end;
/
create or replace package RRL_MES_PRODUCTION_API as
  function create_order(
    p_order_no           varchar2,
    p_bom_id             number default null,
    p_target_articul     varchar2,
    p_planned_qty        number,
    p_unit_code          varchar2 default 'KG',
    p_ware_id            number default null,
    p_production_line    varchar2 default null,
    p_shift_id           varchar2 default null,
    p_planned_start_at   date default null,
    p_planned_finish_at  date default null,
    p_source_system      varchar2 default null,
    p_source_message_id  varchar2 default null,
    p_idempotency_key    varchar2 default null,
    p_comment_text       varchar2 default null,
    p_created_by         varchar2 default null
  ) return number;

  function issue_raw_to_production(
    p_production_order_id number,
    p_uid_pallet          varchar2 default null,
    p_raw_batch_id        number default null,
    p_raw_articul         varchar2 default null,
    p_quantity            number,
    p_unit_code           varchar2 default 'KG',
    p_source_location     varchar2 default null,
    p_production_location varchar2 default 'MES_PRODUCTION',
    p_created_by          varchar2 default null
  ) return number;

  function complete_order(
    p_production_order_id number,
    p_prod_batch_no       varchar2 default null,
    p_fact_qty            number,
    p_unit_code           varchar2 default 'KG',
    p_pallets_json        clob default null,
    p_idempotency_key     varchar2 default null,
    p_created_by          varchar2 default null
  ) return number;

  procedure apply_mes_movements_to_wms(
    p_production_order_id number,
    p_applied_by          varchar2 default null
  );

  procedure retry_mes_movement(
    p_movement_id number,
    p_updated_by  varchar2 default null
  );
end RRL_MES_PRODUCTION_API;
/

create or replace package RRL_STOCK_MES_MOVEMENT_PLAN authid definer
 accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_MES_MOVEMENT_CORE) as
 function signature(p_m RRL_MES_MOVEMENT%rowtype) return varchar2;
 procedure compile_movements(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
end;
/

create or replace package body RRL_MES_PRODUCTION_API as
  function next_line_no(p_production_order_id number) return number is
    v_line_no number;
  begin
    select nvl(max(LINE_NO), 0) + 10
      into v_line_no
      from RRL_PROD_ORDER_BOM_LINE
     where PRODUCTION_ORDER_ID = p_production_order_id;
    return v_line_no;
  end;

  function create_order(
    p_order_no           varchar2,
    p_bom_id             number default null,
    p_target_articul     varchar2,
    p_planned_qty        number,
    p_unit_code          varchar2 default 'KG',
    p_ware_id            number default null,
    p_production_line    varchar2 default null,
    p_shift_id           varchar2 default null,
    p_planned_start_at   date default null,
    p_planned_finish_at  date default null,
    p_source_system      varchar2 default null,
    p_source_message_id  varchar2 default null,
    p_idempotency_key    varchar2 default null,
    p_comment_text       varchar2 default null,
    p_created_by         varchar2 default null
  ) return number is
    v_id number;
    v_bom_id number;
    v_bom RRL_BOM%rowtype;
    v_factor number;
  begin
    if p_idempotency_key is not null then
      begin
        select PRODUCTION_ORDER_ID into v_id
          from RRL_PRODUCTION_ORDER
         where IDEMPOTENCY_KEY = p_idempotency_key;
        return v_id;
      exception
        when no_data_found then null;
      end;
    end if;

    begin
      select PRODUCTION_ORDER_ID into v_id
        from RRL_PRODUCTION_ORDER
       where ORDER_NO = p_order_no;
      return v_id;
    exception
      when no_data_found then null;
    end;

    if p_planned_qty is null or p_planned_qty <= 0 then
      raise_application_error(-20900, 'planned quantity must be greater than zero');
    end if;

    v_bom_id := p_bom_id;
    if v_bom_id is null then
      v_bom_id := RRL_BOM_API.find_primary_bom(
        p_target_articul => p_target_articul,
        p_planned_date => nvl(p_planned_start_at, trunc(sysdate)),
        p_ware_id => p_ware_id,
        p_production_line => p_production_line
      );
    end if;

    if v_bom_id is null then
      raise_application_error(-20901, 'approved primary BOM not found');
    end if;

    select * into v_bom
      from RRL_BOM
     where BOM_ID = v_bom_id
       and STATUS in ('APPROVED', 'ACTIVE');

    if upper(v_bom.TARGET_ARTICUL) <> upper(substr(p_target_articul, 1, 40)) then
      raise_application_error(-20902, 'BOM target articul does not match production order target');
    end if;

    select RRL_PRODUCTION_ORDER_SQ.nextval into v_id from dual;

    insert into RRL_PRODUCTION_ORDER (
      PRODUCTION_ORDER_ID, ORDER_NO, BOM_ID, TARGET_ARTICUL, TARGET_MOD_ID,
      TARGET_GTIN, PLANNED_QTY, UNIT_CODE, WARE_ID, PRODUCTION_LINE, SHIFT_ID,
      STATUS, PLANNED_START_AT, PLANNED_FINISH_AT, IDEMPOTENCY_KEY,
      SOURCE_SYSTEM, SOURCE_MESSAGE_ID, COMMENT_TEXT, CREATED_AT, CREATED_BY
    ) values (
      v_id, substr(p_order_no, 1, 100), v_bom_id, upper(substr(p_target_articul, 1, 40)),
      v_bom.TARGET_MOD_ID, v_bom.TARGET_GTIN, p_planned_qty, upper(substr(nvl(p_unit_code, v_bom.BASE_UNIT_CODE), 1, 20)),
      p_ware_id, substr(p_production_line, 1, 100), substr(p_shift_id, 1, 50),
      'RELEASED', p_planned_start_at, p_planned_finish_at, substr(p_idempotency_key, 1, 100),
      substr(p_source_system, 1, 50), substr(p_source_message_id, 1, 100),
      substr(p_comment_text, 1, 1000), sysdate, substr(p_created_by, 1, 50)
    );

    v_factor := p_planned_qty / v_bom.BASE_QTY;

    insert into RRL_PROD_ORDER_BOM_LINE (
      ORDER_LINE_ID, PRODUCTION_ORDER_ID, BOM_ID, BOM_LINE_ID, LINE_NO,
      COMPONENT_TYPE, COMPONENT_ARTICUL, COMPONENT_MOD_ID, COMPONENT_NAME,
      PLANNED_QTY, UNIT_CODE, LOSS_PERCENT, IS_REQUIRED, CREATED_AT, CREATED_BY
    )
    select RRL_PROD_ORDER_BOM_LINE_SQ.nextval,
           v_id,
           v_bom_id,
           l.BOM_LINE_ID,
           l.LINE_NO,
           l.COMPONENT_TYPE,
           upper(substr(l.COMPONENT_ARTICUL, 1, 40)),
           l.COMPONENT_MOD_ID,
           l.COMPONENT_NAME,
           round(nvl(l.QTY_PER_BASE, 0) * v_factor * (1 + nvl(l.LOSS_PERCENT, 0) / 100), 6),
           nvl(l.UNIT_CODE, v_bom.BASE_UNIT_CODE),
           nvl(l.LOSS_PERCENT, 0),
           nvl(l.IS_REQUIRED, 1),
           sysdate,
           substr(p_created_by, 1, 50)
      from RRL_BOM_LINE l
     where l.BOM_ID = v_bom_id;

    return v_id;
  end create_order;

  function issue_raw_to_production(
    p_production_order_id number,
    p_uid_pallet          varchar2 default null,
    p_raw_batch_id        number default null,
    p_raw_articul         varchar2 default null,
    p_quantity            number,
    p_unit_code           varchar2 default 'KG',
    p_source_location     varchar2 default null,
    p_production_location varchar2 default 'MES_PRODUCTION',
    p_created_by          varchar2 default null
  ) return number is
    v_id number;
    v_order RRL_PRODUCTION_ORDER%rowtype;
    v_raw_articul varchar2(40);
  begin
    if p_quantity is null or p_quantity <= 0 then
      raise_application_error(-20910, 'issue quantity must be greater than zero');
    end if;

    select * into v_order
      from RRL_PRODUCTION_ORDER
     where PRODUCTION_ORDER_ID = p_production_order_id
       for update;

    if v_order.STATUS in ('COMPLETED', 'CANCELLED') then
      raise_application_error(-20911, 'production order is already closed');
    end if;

    v_raw_articul := upper(substr(p_raw_articul, 1, 40));
    if v_raw_articul is null and p_raw_batch_id is not null then
      select upper(substr(ARTICUL, 1, 40))
        into v_raw_articul
        from RRL_RAW_BATCH
       where RAW_BATCH_ID = p_raw_batch_id;
    end if;

    select RRL_MES_MOVEMENT_SQ.nextval into v_id from dual;

    insert into RRL_MES_MOVEMENT (
      MOVEMENT_ID, MOVEMENT_TYPE, PRODUCTION_ORDER_ID, BOM_ID, RAW_BATCH_ID,
      RAW_ARTICUL, UID_PALLET, QUANTITY, UNIT_CODE, SOURCE_LOCATION, TARGET_LOCATION,
      STATUS, CREATED_AT, CREATED_BY
    ) values (
      v_id, 'RAW_ISSUE_TO_PRODUCTION', p_production_order_id, v_order.BOM_ID, p_raw_batch_id,
      v_raw_articul, substr(p_uid_pallet, 1, 200), p_quantity, upper(substr(p_unit_code, 1, 20)),
      substr(p_source_location, 1, 100), substr(p_production_location, 1, 100),
      'MES_POSTED', sysdate, substr(p_created_by, 1, 50)
    );

    update RRL_PRODUCTION_ORDER
       set STATUS = 'IN_PROGRESS',
           STARTED_AT = nvl(STARTED_AT, sysdate),
           UPDATED_AT = sysdate,
           UPDATED_BY = substr(p_created_by, 1, 50)
     where PRODUCTION_ORDER_ID = p_production_order_id
       and STATUS in ('DRAFT', 'RELEASED');

    return v_id;
  end issue_raw_to_production;

  function complete_order(
    p_production_order_id number,
    p_prod_batch_no       varchar2 default null,
    p_fact_qty            number,
    p_unit_code           varchar2 default 'KG',
    p_pallets_json        clob default null,
    p_idempotency_key     varchar2 default null,
    p_created_by          varchar2 default null
  ) return number is
    v_completion_id number;
    v_order RRL_PRODUCTION_ORDER%rowtype;
    v_prod_batch_id number;
    v_prod_batch_no varchar2(100);
    v_consumption_count number;
    v_trace_event_id number;
    v_dummy number;
  begin
    if p_idempotency_key is not null then
      begin
        select COMPLETION_ID into v_completion_id
          from RRL_MES_COMPLETION
         where IDEMPOTENCY_KEY = p_idempotency_key;
        return v_completion_id;
      exception
        when no_data_found then null;
      end;
    end if;

    if p_fact_qty is null or p_fact_qty <= 0 then
      raise_application_error(-20920, 'fact quantity must be greater than zero');
    end if;

    select * into v_order
      from RRL_PRODUCTION_ORDER
     where PRODUCTION_ORDER_ID = p_production_order_id
       for update;

    if v_order.STATUS in ('COMPLETED', 'CANCELLED') then
      raise_application_error(-20921, 'production order is already closed');
    end if;

    v_prod_batch_no := substr(nvl(p_prod_batch_no, v_order.ORDER_NO || '-LOT'), 1, 100);

    v_prod_batch_id := RRL_PRODUCTION_API.create_prod_batch(
      p_prod_batch_no => v_prod_batch_no,
      p_articul => v_order.TARGET_ARTICUL,
      p_mod_id => v_order.TARGET_MOD_ID,
      p_gtin => v_order.TARGET_GTIN,
      p_total_quantity => p_fact_qty,
      p_unit_code => nvl(p_unit_code, v_order.UNIT_CODE),
      p_ware_id => v_order.WARE_ID,
      p_source_system => 'MES',
      p_source_message_id => substr(nvl(p_idempotency_key, v_order.ORDER_NO || ':COMPLETE'), 1, 100),
      p_production_order_id => v_order.PRODUCTION_ORDER_ID,
      p_produced_date_from => trunc(sysdate),
      p_produced_date_to => trunc(sysdate),
      p_production_line => v_order.PRODUCTION_LINE,
      p_shift_id => v_order.SHIFT_ID,
      p_created_by => p_created_by
    );

    select count(*)
      into v_consumption_count
      from RRL_MES_MOVEMENT
     where PRODUCTION_ORDER_ID = p_production_order_id
       and MOVEMENT_TYPE = 'RAW_ISSUE_TO_PRODUCTION'
       and STATUS <> 'CANCELLED';

    if v_consumption_count > 0 then
      for r in (
        select RAW_BATCH_ID,
               RAW_ARTICUL,
               UID_PALLET,
               TARGET_LOCATION PRODUCTION_LOCATION,
               sum(QUANTITY) QUANTITY,
               max(UNIT_CODE) UNIT_CODE
          from RRL_MES_MOVEMENT
         where PRODUCTION_ORDER_ID = p_production_order_id
           and MOVEMENT_TYPE = 'RAW_ISSUE_TO_PRODUCTION'
           and STATUS <> 'CANCELLED'
         group by RAW_BATCH_ID, RAW_ARTICUL, UID_PALLET, TARGET_LOCATION
      ) loop
        v_dummy := RRL_PRODUCTION_API.add_raw_usage(
          p_prod_batch_id => v_prod_batch_id,
          p_raw_batch_id => r.RAW_BATCH_ID,
          p_raw_articul => r.RAW_ARTICUL,
          p_quantity_planned => r.QUANTITY,
          p_quantity_fact => r.QUANTITY,
          p_unit_code => r.UNIT_CODE,
          p_used_by => p_created_by
        );

        select RRL_MES_MOVEMENT_SQ.nextval into v_dummy from dual;
        insert into RRL_MES_MOVEMENT (
          MOVEMENT_ID, MOVEMENT_TYPE, PRODUCTION_ORDER_ID, PROD_BATCH_ID, BOM_ID,
          RAW_BATCH_ID, RAW_ARTICUL, UID_PALLET, QUANTITY, UNIT_CODE, SOURCE_LOCATION, TARGET_LOCATION,
          STATUS, CREATED_AT, CREATED_BY
        ) values (
          v_dummy, 'RAW_CONSUMPTION', p_production_order_id, v_prod_batch_id, v_order.BOM_ID,
          r.RAW_BATCH_ID, r.RAW_ARTICUL, r.UID_PALLET, r.QUANTITY, r.UNIT_CODE, nvl(r.PRODUCTION_LOCATION, 'MES_PROD'),
          'MES_FINISHED_GOODS', 'MES_POSTED', sysdate, substr(p_created_by, 1, 50)
        );
      end loop;
    else
      for r in (
        select BOM_LINE_ID, COMPONENT_ARTICUL, PLANNED_QTY, UNIT_CODE
          from RRL_PROD_ORDER_BOM_LINE
         where PRODUCTION_ORDER_ID = p_production_order_id
           and COMPONENT_TYPE in ('RAW', 'SEMIFINISHED', 'PACKAGING', 'ADDITIVE')
      ) loop
        v_dummy := RRL_PRODUCTION_API.add_raw_usage(
          p_prod_batch_id => v_prod_batch_id,
          p_raw_batch_id => null,
          p_raw_articul => r.COMPONENT_ARTICUL,
          p_quantity_planned => r.PLANNED_QTY,
          p_quantity_fact => round(r.PLANNED_QTY * p_fact_qty / v_order.PLANNED_QTY, 6),
          p_unit_code => r.UNIT_CODE,
          p_used_by => p_created_by
        );

        select RRL_MES_MOVEMENT_SQ.nextval into v_dummy from dual;
        insert into RRL_MES_MOVEMENT (
          MOVEMENT_ID, MOVEMENT_TYPE, PRODUCTION_ORDER_ID, PROD_BATCH_ID, BOM_ID,
          BOM_LINE_ID, RAW_ARTICUL, QUANTITY, UNIT_CODE, SOURCE_LOCATION, TARGET_LOCATION,
          STATUS, CREATED_AT, CREATED_BY
        ) values (
          v_dummy, 'RAW_CONSUMPTION', p_production_order_id, v_prod_batch_id, v_order.BOM_ID,
          r.BOM_LINE_ID, r.COMPONENT_ARTICUL, round(r.PLANNED_QTY * p_fact_qty / v_order.PLANNED_QTY, 6),
          r.UNIT_CODE, 'MES_PRODUCTION', 'MES_FINISHED_GOODS', 'MES_POSTED', sysdate,
          substr(p_created_by, 1, 50)
        );
      end loop;
    end if;

    select RRL_MES_MOVEMENT_SQ.nextval into v_dummy from dual;
    insert into RRL_MES_MOVEMENT (
      MOVEMENT_ID, MOVEMENT_TYPE, PRODUCTION_ORDER_ID, PROD_BATCH_ID, BOM_ID,
      QUANTITY, UNIT_CODE, SOURCE_LOCATION, TARGET_LOCATION, STATUS, CREATED_AT, CREATED_BY
    ) values (
      v_dummy, 'FG_LOT_RELEASE', p_production_order_id, v_prod_batch_id, v_order.BOM_ID,
      p_fact_qty, nvl(p_unit_code, v_order.UNIT_CODE), 'MES_PRODUCTION', 'MES_FINISHED_GOODS',
      'MES_POSTED', sysdate, substr(p_created_by, 1, 50)
    );

    if p_pallets_json is not null then
      for p in (
        select uid_pallet, pallet_no, quantity, pack_count, sscc
          from json_table(
            p_pallets_json,
            '$[*]' columns (
              uid_pallet varchar2(200) path '$.uid_pallet',
              pallet_no number path '$.pallet_no',
              quantity number path '$.quantity',
              pack_count number path '$.pack_count',
              sscc varchar2(50) path '$.sscc'
            )
          )
      ) loop
        if p.uid_pallet is null then
          raise_application_error(-20922, 'pallet uid is required');
        end if;

        merge into RRL_PROD_BATCH_PALLETS d
        using (
          select v_prod_batch_id PROD_BATCH_ID,
                 p.uid_pallet UID_PALLET
            from dual
        ) s
        on (d.PROD_BATCH_ID = s.PROD_BATCH_ID and d.UID_PALLET = s.UID_PALLET)
        when matched then update set
          d.PALLET_NO = nvl(p.pallet_no, d.PALLET_NO),
          d.QUANTITY = nvl(p.quantity, d.QUANTITY),
          d.PACK_COUNT = nvl(p.pack_count, d.PACK_COUNT),
          d.SSCC = nvl(p.sscc, d.SSCC)
        when not matched then insert (
          PROD_BATCH_ID, UID_PALLET, PALLET_NO, QUANTITY, PACK_COUNT,
          SSCC, AGGREGATION_STATUS, CREATED_AT, CREATED_BY
        ) values (
          v_prod_batch_id, p.uid_pallet, p.pallet_no, p.quantity, p.pack_count,
          p.sscc, 'DRAFT', sysdate, p_created_by
        );

        select RRL_MES_MOVEMENT_SQ.nextval into v_dummy from dual;
        insert into RRL_MES_MOVEMENT (
          MOVEMENT_ID, MOVEMENT_TYPE, PRODUCTION_ORDER_ID, PROD_BATCH_ID, BOM_ID,
          UID_PALLET, SSCC, QUANTITY, PACK_COUNT, UNIT_CODE, SOURCE_LOCATION,
          TARGET_LOCATION, STATUS, PAYLOAD_JSON, CREATED_AT, CREATED_BY
        ) values (
          v_dummy, 'FG_PALLET_RELEASE', p_production_order_id, v_prod_batch_id, v_order.BOM_ID,
          substr(p.uid_pallet, 1, 200), substr(p.sscc, 1, 50), p.quantity, p.pack_count,
          nvl(p_unit_code, v_order.UNIT_CODE), 'MES_PRODUCTION', 'MES_FG',
          'MES_POSTED',
          '{"uid_pallet":"' || replace(substr(p.uid_pallet, 1, 200), '"', '\"') || '"}',
          sysdate, substr(p_created_by, 1, 50)
        );
      end loop;
    end if;

    select RRL_MES_COMPLETION_SQ.nextval into v_completion_id from dual;
    insert into RRL_MES_COMPLETION (
      COMPLETION_ID, PRODUCTION_ORDER_ID, PROD_BATCH_ID, IDEMPOTENCY_KEY,
      STATUS, PAYLOAD_JSON, CREATED_AT, CREATED_BY
    ) values (
      v_completion_id, p_production_order_id, v_prod_batch_id,
      substr(p_idempotency_key, 1, 100), 'DONE', p_pallets_json, sysdate,
      substr(p_created_by, 1, 50)
    );

    update RRL_PRODUCTION_ORDER
       set STATUS = 'COMPLETED',
           FACT_QTY = p_fact_qty,
           COMPLETED_AT = sysdate,
           PROD_BATCH_ID = v_prod_batch_id,
           UPDATED_AT = sysdate,
           UPDATED_BY = substr(p_created_by, 1, 50)
     where PRODUCTION_ORDER_ID = p_production_order_id;

    update RRL_PROD_BATCH
       set QUALITY_STATUS = 'RELEASED',
           UPDATED_AT = sysdate,
           UPDATED_BY = substr(p_created_by, 1, 50)
     where PROD_BATCH_ID = v_prod_batch_id;

    v_trace_event_id := RRL_TRACEABILITY_API.add_trace_event(
      p_event_type => 'PRODUCTION_COMPLETED',
      p_entity_type => 'PRODUCTION_ORDER',
      p_entity_id => to_char(p_production_order_id),
      p_source_system => 'MES',
      p_correlation_id => v_order.ORDER_NO,
      p_idempotency_key => substr(nvl(p_idempotency_key, v_order.ORDER_NO || ':TRACE'), 1, 100),
      p_payload_json => p_pallets_json,
      p_created_by => p_created_by
    );

    v_dummy := RRL_TRACEABILITY_API.add_trace_edge(
      p_from_entity_type => 'PRODUCTION_ORDER',
      p_from_entity_id => to_char(p_production_order_id),
      p_to_entity_type => 'FINISHED_GOODS_LOT',
      p_to_entity_id => to_char(v_prod_batch_id),
      p_edge_type => 'PRODUCES',
      p_quantity => p_fact_qty,
      p_unit_code => nvl(p_unit_code, v_order.UNIT_CODE),
      p_trace_event_id => v_trace_event_id,
      p_created_by => p_created_by
    );

    v_dummy := RRL_TRACEABILITY_API.enqueue_event(
      p_event_type => 'PRODUCTION_COMPLETED',
      p_aggregate_type => 'PRODUCTION_ORDER',
      p_aggregate_id => to_char(p_production_order_id),
      p_idempotency_key => substr(nvl(p_idempotency_key, v_order.ORDER_NO || ':OUTBOX'), 1, 100),
      p_payload_json => p_pallets_json,
      p_target_system => 'TRACEABILITY',
      p_correlation_id => v_order.ORDER_NO
    );

    return v_completion_id;
  end complete_order;

  procedure apply_mes_movements_to_wms(
    p_production_order_id number,
    p_applied_by          varchar2 default null
  ) is
    v_event_id number;
    v_error varchar2(4000);
  begin
    for m in (
      select *
        from RRL_MES_MOVEMENT
       where PRODUCTION_ORDER_ID = p_production_order_id
         and STATUS in ('MES_POSTED', 'ERROR')
         and MOVEMENT_TYPE in ('RAW_ISSUE_TO_PRODUCTION', 'RAW_CONSUMPTION', 'FG_PALLET_RELEASE')
       order by MOVEMENT_ID
    ) loop
      begin
        if m.UID_PALLET is null then
          raise_application_error(-20940, 'legacy WMS event requires UID_PALLET');
        end if;

        if m.MOVEMENT_TYPE = 'FG_PALLET_RELEASE' then
          merge into RRL_PALLETS d
          using (
            select m.UID_PALLET UID_PALLET,
                   o.TARGET_ARTICUL ARTICUL,
                   m.QUANTITY UNIT_COUNT,
                   m.PROD_BATCH_ID PROD_BATCH_ID,
                   m.SSCC SSCC
              from RRL_PRODUCTION_ORDER o
             where o.PRODUCTION_ORDER_ID = p_production_order_id
          ) s
          on (d.UID_PALLET = s.UID_PALLET)
          when matched then update set
            d.ARTICUL = nvl(s.ARTICUL, d.ARTICUL),
            d.UNIT_COUNT = nvl(s.UNIT_COUNT, d.UNIT_COUNT),
            d.PROD_BATCH_ID = nvl(s.PROD_BATCH_ID, d.PROD_BATCH_ID),
            d.SSCC = nvl(s.SSCC, d.SSCC),
            d.QUALITY_STATUS = 'RELEASED'
          when not matched then insert (
            UID_PALLET, ARTICUL, UNIT_COUNT, PRIHOD_NAKLAD_ID,
            PROD_BATCH_ID, SSCC, QUALITY_STATUS
          ) values (
            s.UID_PALLET, s.ARTICUL, s.UNIT_COUNT, 0,
            s.PROD_BATCH_ID, s.SSCC, 'RELEASED'
          );
        end if;

        select RRL_EVENT_ID_SQ.nextval into v_event_id from dual;

        if m.MOVEMENT_TYPE = 'RAW_ISSUE_TO_PRODUCTION' then
          insert into RRL_EVENTS (
            ID_EVENT, CELL_FROM, CELL_TO, DATE_EVENT, COUNT_EVENT,
            TYPE_EVENT, UID_POLETA, USER_ID
          ) values (
            v_event_id, substr(nvl(m.SOURCE_LOCATION, 'UNKNOWN'), 1, 20),
            substr(nvl(m.TARGET_LOCATION, 'MES_PROD'), 1, 20), sysdate,
            nvl(m.QUANTITY, 0), 2, substr(m.UID_PALLET, 1, 200),
            substr(nvl(p_applied_by, user), 1, 50)
          );
        elsif m.MOVEMENT_TYPE = 'RAW_CONSUMPTION' then
          insert into RRL_EVENTS (
            ID_EVENT, CELL_FROM, CELL_TO, DATE_EVENT, COUNT_EVENT,
            TYPE_EVENT, UID_POLETA, USER_ID
          ) values (
            v_event_id, substr(nvl(m.SOURCE_LOCATION, 'MES_PROD'), 1, 20),
            'none', sysdate, nvl(m.QUANTITY, 0), 3, substr(m.UID_PALLET, 1, 200),
            substr(nvl(p_applied_by, user), 1, 50)
          );
        elsif m.MOVEMENT_TYPE = 'FG_PALLET_RELEASE' then
          insert into RRL_EVENTS (
            ID_EVENT, CELL_FROM, CELL_TO, DATE_EVENT, COUNT_EVENT,
            TYPE_EVENT, UID_POLETA, USER_ID
          ) values (
            v_event_id, substr(nvl(m.SOURCE_LOCATION, 'MES_PROD'), 1, 20),
            substr(nvl(m.TARGET_LOCATION, 'MES_FG'), 1, 20), sysdate,
            nvl(m.QUANTITY, 0), 1, substr(m.UID_PALLET, 1, 200),
            substr(nvl(p_applied_by, user), 1, 50)
          );
        else
          raise_application_error(-20941, 'movement type is not supported by legacy WMS bridge');
        end if;

        update RRL_MES_MOVEMENT
           set STATUS = 'APPLIED_TO_WMS',
               WMS_APPLIED_AT = sysdate,
               WMS_APPLIED_BY = substr(p_applied_by, 1, 50),
               LAST_ERROR = null,
               UPDATED_AT = sysdate,
               UPDATED_BY = substr(p_applied_by, 1, 50)
         where MOVEMENT_ID = m.MOVEMENT_ID;
      exception
        when others then
          v_error := sqlerrm;
          update RRL_MES_MOVEMENT
             set STATUS = 'ERROR',
                 RETRY_COUNT = RETRY_COUNT + 1,
                 LAST_ERROR = substr(v_error, 1, 4000),
                 UPDATED_AT = sysdate,
                 UPDATED_BY = substr(p_applied_by, 1, 50)
           where MOVEMENT_ID = m.MOVEMENT_ID;
      end;
    end loop;
  end apply_mes_movements_to_wms;

  procedure retry_mes_movement(
    p_movement_id number,
    p_updated_by  varchar2 default null
  ) is
  begin
    update RRL_MES_MOVEMENT
       set STATUS = 'MES_POSTED',
           LAST_ERROR = null,
           UPDATED_AT = sysdate,
           UPDATED_BY = substr(p_updated_by, 1, 50)
     where MOVEMENT_ID = p_movement_id
       and STATUS = 'ERROR';

    if sql%rowcount = 0 then
      raise_application_error(-20930, 'MES movement is not in ERROR status');
    end if;
  end retry_mes_movement;
end RRL_MES_PRODUCTION_API;
/

create or replace package body RRL_STOCK_MES_MOVEMENT_PLAN as
 function signature(p_m RRL_MES_MOVEMENT%rowtype) return varchar2 is v json_object_t:=json_object_t();
 begin
  v.put('id',p_m.MOVEMENT_ID);v.put('type',p_m.MOVEMENT_TYPE);v.put('order',p_m.PRODUCTION_ORDER_ID);
  v.put('uid',p_m.UID_PALLET);v.put('sscc',p_m.SSCC);v.put('batch',p_m.PROD_BATCH_ID);v.put('raw',p_m.RAW_ARTICUL);
  v.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(p_m.QUANTITY));v.put('unit',p_m.UNIT_CODE);
  v.put('from',p_m.SOURCE_LOCATION);v.put('to',p_m.TARGET_LOCATION);
  return rawtohex(sys.dbms_crypto.hash(v.to_clob,sys.dbms_crypto.hash_sh256));
 end;
 procedure compile_movements(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
  d json_object_t:=json_object_t.parse(p_request);s json_object_t;ids json_array_t;a json_array_t:=json_array_t();
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();v json_object_t:=json_object_t();h json_object_t:=json_object_t();
  m RRL_MES_MOVEMENT%rowtype;o RRL_PRODUCTION_ORDER%rowtype;v_id number;v_article varchar2(160);
  v_p number;v_target varchar2(200);v_reservation number;v_new_reservation number;v_qty number;
  v_num number;v_den number;v_scale number;v_base varchar2(20);v_version number;
  type quantity_map is table of number index by varchar2(2000);v_balances quantity_map;v_target_reservations quantity_map;
  type identity_map is table of varchar2(200) index by varchar2(2000);v_targets identity_map;
  v_source_key varchar2(2000);v_target_key varchar2(2000);v_physical_uid varchar2(200);
  function projected(p_uid varchar2,p_cell varchar2) return number is k varchar2(2000);n number;
  begin
   k:=rawtohex(RRL_STOCK_LOCK_API.resource_key('STOCK',p_uid,p_cell));
   if not v_balances.exists(k) then
    begin select REMAIN into n from RRL_REMAINS where UID_POLETA=p_uid and CELL=p_cell;exception when no_data_found then n:=0;end;
    v_balances(k):=n;
   end if;
   return v_balances(k);
  end;

 begin
  s:=d.get_object('source');ids:=s.get_array('movement_ids');
  if ids is null or ids.get_size<1 or ids.get_size>200 then raise_application_error(-20871,'MES_MOVEMENT_BATCH_SIZE');end if;
  select * into o from RRL_PRODUCTION_ORDER where PRODUCTION_ORDER_ID=s.get_number('production_order_id');
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PRODUCTION_ORDER',RRL_STOCK_PLAN_HELPER.decimal_text(o.PRODUCTION_ORDER_ID));
  for i in 0..ids.get_size-1 loop
   v_id:=ids.get_number(i);select * into m from RRL_MES_MOVEMENT where MOVEMENT_ID=v_id;
   if m.PRODUCTION_ORDER_ID!=o.PRODUCTION_ORDER_ID or m.UID_PALLET is null
    or m.MOVEMENT_TYPE not in('RAW_ISSUE_TO_PRODUCTION','RAW_CONSUMPTION','FG_PALLET_RELEASE') then
    raise_application_error(-20886,'MES_MOVEMENT_IDENTITY_CONFLICT');end if;
   v_physical_uid:=m.UID_PALLET;
   v_source_key:=rawtohex(RRL_STOCK_LOCK_API.resource_key('STOCK',m.UID_PALLET,m.SOURCE_LOCATION));
   if m.MOVEMENT_TYPE='RAW_CONSUMPTION' and v_targets.exists(v_source_key) then v_physical_uid:=v_targets(v_source_key);end if;
   if m.MOVEMENT_TYPE='FG_PALLET_RELEASE' then v_article:=o.TARGET_ARTICUL;
   else select ARTICUL into v_article from RRL_PALLETS where UID_PALLET=m.UID_PALLET;end if;
   select max(POLICY_VERSION) into v_version from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article and INPUT_UOM=m.UNIT_CODE;
   select BASE_UOM,NUMERATOR,DENOMINATOR,BASE_SCALE into v_base,v_num,v_den,v_scale
    from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article and INPUT_UOM=m.UNIT_CODE and POLICY_VERSION=v_version;
   v_qty:=RRL_STOCK_MATH.convert_exact(RRL_STOCK_PLAN_HELPER.decimal_text(m.QUANTITY),v_num,v_den,v_scale);
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_MES_MOVEMENT',RRL_STOCK_PLAN_HELPER.decimal_text(v_id));
   RRL_STOCK_PLAN_HELPER.stock_closure(f,r,v_physical_uid,v_article,
    case when m.MOVEMENT_TYPE!='FG_PALLET_RELEASE' then m.SOURCE_LOCATION end,
    case when m.MOVEMENT_TYPE!='RAW_CONSUMPTION' then m.TARGET_LOCATION end);
   v_target:=v_physical_uid;v_reservation:=null;v_new_reservation:=null;v_p:=null;
   if m.MOVEMENT_TYPE='RAW_ISSUE_TO_PRODUCTION' then
    v_p:=projected(v_physical_uid,m.SOURCE_LOCATION);
    if v_qty<v_p then
     v_target:='PART:'||substr(rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation||':'||RRL_STOCK_PLAN_HELPER.decimal_text(v_id),'AL32UTF8'),sys.dbms_crypto.hash_sh256)),1,64);
     select RRL_STOCK_RESERVATION_SQ.nextval into v_new_reservation from dual;
     RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(v_new_reservation));
     RRL_STOCK_PLAN_HELPER.anchor(r,30,'HU',v_target);RRL_STOCK_PLAN_HELPER.anchor(r,50,'STOCK',v_target);
     RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','PALLET:'||v_target);
    end if;
   end if;
   if m.MOVEMENT_TYPE!='FG_PALLET_RELEASE' then
    begin select RESERVATION_ID into v_reservation from RRL_STOCK_RESERVATION where UID_PALLET=m.UID_PALLET and CELL=m.SOURCE_LOCATION
     and SOURCE_DOC_TYPE='PRODUCTION_ORDER' and SOURCE_DOC_ID=o.PRODUCTION_ORDER_ID and RESERVATION_KIND='HARD'
     and STATUS in('ACTIVE','ALLOCATED','PICKING') and BASE_QTY>=v_qty;
    exception when no_data_found then null;when too_many_rows then raise_application_error(-20869,'MES_RESERVATION_AMBIGUOUS');end;
   else RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','PALLET:'||m.UID_PALLET);end if;
   if m.MOVEMENT_TYPE='RAW_CONSUMPTION' and v_target_reservations.exists(v_source_key) then v_reservation:=v_target_reservations(v_source_key);end if;
   if m.MOVEMENT_TYPE='RAW_ISSUE_TO_PRODUCTION' then
    v_source_key:=rawtohex(RRL_STOCK_LOCK_API.resource_key('STOCK',v_physical_uid,m.SOURCE_LOCATION));
    v_balances(v_source_key):=projected(v_physical_uid,m.SOURCE_LOCATION)-v_qty;
    v_target_key:=rawtohex(RRL_STOCK_LOCK_API.resource_key('STOCK',v_target,m.TARGET_LOCATION));
    v_balances(v_target_key):=projected(v_target,m.TARGET_LOCATION)+v_qty;
    v_target_key:=rawtohex(RRL_STOCK_LOCK_API.resource_key('STOCK',m.UID_PALLET,m.TARGET_LOCATION));
    if v_targets.exists(v_target_key) and v_targets(v_target_key)!=v_target then
     raise_application_error(-20886,'MES_CONSUMPTION_REQUIRES_PHYSICAL_PALLET_ALLOCATION');end if;
    v_targets(v_target_key):=v_target;
    if v_reservation is not null then v_target_reservations(v_target_key):=case when v_target=m.UID_PALLET then v_reservation else v_new_reservation end;end if;
   elsif m.MOVEMENT_TYPE='RAW_CONSUMPTION' then
    v_source_key:=rawtohex(RRL_STOCK_LOCK_API.resource_key('STOCK',v_physical_uid,m.SOURCE_LOCATION));
    if projected(v_physical_uid,m.SOURCE_LOCATION)<v_qty then raise_application_error(-20868,'MES_CONSUMPTION_STOCK_INSUFFICIENT');end if;
    v_balances(v_source_key):=v_balances(v_source_key)-v_qty;
   end if;
   v:=json_object_t();v.put('physical_uid',v_physical_uid);v.put('movement_id',v_id);v.put('signature',signature(m));v.put('article',v_article);
   v.put('base_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_qty));v.put('base_uom',v_base);v.put('uom_version',v_version);
   v.put('source_p',case when v_p is not null then RRL_STOCK_PLAN_HELPER.decimal_text(v_p) end);
   v.put('target_uid',v_target);v.put('reservation_id',v_reservation);v.put('new_reservation_id',v_new_reservation);a.append(v);
  end loop;
  h.put('production_order_id',o.PRODUCTION_ORDER_ID);h.put('movements',a);
  p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=h.to_clob;
 end;
end;
/
