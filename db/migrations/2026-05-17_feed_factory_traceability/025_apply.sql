prompt [migration 2026-05-17-025] MES raw supply Oracle API - apply

create or replace package RRL_MES_RAW_SUPPLY_API as
  function release_to_production(
    p_production_order_id number,
    p_to_ware_id          number default null,
    p_to_cell             varchar2 default 'MES_PROD',
    p_allow_partial       number default 0,
    p_created_by          varchar2 default null
  ) return number;
end RRL_MES_RAW_SUPPLY_API;
/

create or replace package body RRL_MES_RAW_SUPPLY_API as
  function issued_raw_qty(
    p_production_order_id number,
    p_bom_line_id         number,
    p_raw_articul         varchar2
  ) return number is
    v_qty number;
  begin
    select nvl(sum(nvl(QUANTITY, 0)), 0)
      into v_qty
      from RRL_MES_MOVEMENT
     where PRODUCTION_ORDER_ID = p_production_order_id
       and MOVEMENT_TYPE = 'RAW_ISSUE_TO_PRODUCTION'
       and STATUS <> 'CANCELLED'
       and (
            (BOM_LINE_ID is not null and BOM_LINE_ID = p_bom_line_id)
            or (BOM_LINE_ID is null and upper(RAW_ARTICUL) = upper(p_raw_articul))
       );
    return nvl(v_qty, 0);
  end issued_raw_qty;

  function release_to_production(
    p_production_order_id number,
    p_to_ware_id          number default null,
    p_to_cell             varchar2 default 'MES_PROD',
    p_allow_partial       number default 0,
    p_created_by          varchar2 default null
  ) return number is
    v_status varchar2(30);
    v_existing_tasks number;
    v_demand_id number;
    v_soft_reservation_id number;
    v_candidate_id number;
    v_shortage_id number;
    v_reservation_id number;
    v_task_id number;
    v_required_qty number;
    v_issued_qty number;
    v_open_qty number;
    v_available_qty number;
    v_available_total number;
    v_remaining_qty number;
    v_suggested_qty number;
    v_shortage_count number := 0;
    v_task_count number := 0;
    v_sort_order number;
    v_reservation_scope varchar2(20);
    v_actor varchar2(100) := substr(nvl(p_created_by, 'API'), 1, 100);
    v_to_cell varchar2(80) := substr(nvl(p_to_cell, 'MES_PROD'), 1, 80);
  begin
    if p_production_order_id is null then
      raise_application_error(-20950, 'production order id is required');
    end if;

    select STATUS
      into v_status
      from RRL_PRODUCTION_ORDER
     where PRODUCTION_ORDER_ID = p_production_order_id
     for update;

    if v_status in ('COMPLETED', 'CANCELLED') then
      raise_application_error(-20951, 'completed/cancelled production order cannot be released');
    end if;

    select count(*)
      into v_existing_tasks
      from RRL_MES_RAW_TRANSFER_TASK
     where PRODUCTION_ORDER_ID = p_production_order_id
       and TASK_STATUS in ('PLANNED', 'IN_PROGRESS');

    if v_existing_tasks > 0 then
      return v_existing_tasks;
    end if;

    update RRL_STOCK_RESERVATION
       set STATUS = 'CANCELLED',
           RELEASED_AT = systimestamp,
           RELEASED_BY = v_actor,
           RELEASE_REASON = 'MES raw supply recalculation'
     where RESERVATION_DOMAIN = 'MES_RAW'
       and PRODUCTION_ORDER_ID = p_production_order_id
       and RESERVATION_KIND = 'SOFT'
       and STATUS = 'ACTIVE';

    delete from RRL_MES_RAW_SUPPLY_CANDIDATE
     where PRODUCTION_ORDER_ID = p_production_order_id;
    delete from RRL_MES_RAW_SHORTAGE
     where PRODUCTION_ORDER_ID = p_production_order_id;
    delete from RRL_MES_RAW_DEMAND
     where PRODUCTION_ORDER_ID = p_production_order_id;

    for line in (
      select ORDER_LINE_ID, PRODUCTION_ORDER_ID, BOM_ID, BOM_LINE_ID, LINE_NO,
             COMPONENT_TYPE, upper(COMPONENT_ARTICUL) COMPONENT_ARTICUL,
             COMPONENT_NAME, PLANNED_QTY, UNIT_CODE
        from RRL_PROD_ORDER_BOM_LINE
       where PRODUCTION_ORDER_ID = p_production_order_id
         and COMPONENT_ARTICUL is not null
       order by LINE_NO, ORDER_LINE_ID
    ) loop
      v_required_qty := nvl(line.PLANNED_QTY, 0);
      v_issued_qty := issued_raw_qty(p_production_order_id, line.BOM_LINE_ID, line.COMPONENT_ARTICUL);
      v_open_qty := greatest(v_required_qty - v_issued_qty, 0);
      v_soft_reservation_id := null;

      if v_open_qty > 0 then
        select RRL_STOCK_RESERVATION_SQ.nextval into v_soft_reservation_id from dual;
        insert into RRL_STOCK_RESERVATION (
          RESERVATION_ID, RESERVATION_KIND, RESERVATION_SCOPE, RESERVATION_DOMAIN,
          SOURCE_DOC_TYPE, SOURCE_DOC_ID, SOURCE_LINE_ID, PRODUCTION_ORDER_ID,
          ARTICUL, QTY, UNIT_CODE, STATUS, PRIORITY, CREATED_BY
        ) values (
          v_soft_reservation_id, 'SOFT', 'QTY', 'MES_RAW',
          'PRODUCTION_ORDER', p_production_order_id, line.ORDER_LINE_ID, p_production_order_id,
          line.COMPONENT_ARTICUL, v_open_qty, line.UNIT_CODE, 'ACTIVE', 100, v_actor
        );
      end if;

      select RRL_MES_RAW_DEMAND_SQ.nextval into v_demand_id from dual;
      insert into RRL_MES_RAW_DEMAND (
        DEMAND_ID, PRODUCTION_ORDER_ID, ORDER_LINE_ID, BOM_ID, BOM_LINE_ID,
        RAW_ARTICUL, REQUIRED_QTY, ISSUED_QTY, OPEN_QTY, UNIT_CODE,
        SOFT_RESERVATION_ID, STATUS, CALCULATED_BY
      ) values (
        v_demand_id, p_production_order_id, line.ORDER_LINE_ID, line.BOM_ID, line.BOM_LINE_ID,
        line.COMPONENT_ARTICUL, v_required_qty, v_issued_qty, v_open_qty, line.UNIT_CODE,
        v_soft_reservation_id, case when v_open_qty > 0 then 'OPEN' else 'COVERED' end, v_actor
      );

      if v_open_qty > 0 then
        v_available_total := 0;
        v_remaining_qty := v_open_qty;
        v_sort_order := 0;

        for cand in (
          select w.ID WARE_ID,
                 r.CELL,
                 r.UID_POLETA UID_PALLET,
                 p.SSCC,
                 p.ARTICUL,
                 p.PRIHOD_NAKLAD_ID RAW_BATCH_ID,
                 to_char(p.PRIHOD_NAKLAD_ID) BATCH_ID,
                 p.EXPIRY_DATE,
                 nvl(p.QUALITY_STATUS, 'UNKNOWN') QUALITY_STATUS,
                 nvl(r.REMAIN, 0) PHYSICAL_QTY,
                 nvl((
                   select sum(nvl(sr.QTY, 0))
                     from RRL_STOCK_RESERVATION sr
                    where sr.RESERVATION_KIND = 'HARD'
                      and sr.STATUS in ('ACTIVE', 'ALLOCATED', 'PICKING')
                      and sr.UID_PALLET = r.UID_POLETA
                 ), 0) HARD_RESERVED_QTY
            from RRL_REMAINS r
            join RRL_CELLS c on c.CELL = r.CELL
            join RRL_WARES w on w.ID = c.WARE_ID
            join RRL_PALLETS p on p.UID_PALLET = r.UID_POLETA
           where nvl(w.FLAG_RAW_MATERIAL, 0) = 1
             and upper(p.ARTICUL) = line.COMPONENT_ARTICUL
             and nvl(r.REMAIN, 0) > 0
           order by p.EXPIRY_DATE nulls last, p.PRODUCED_DATE nulls last, r.CELL, r.UID_POLETA
           for update of r.REMAIN
        ) loop
          v_available_qty := greatest(nvl(cand.PHYSICAL_QTY, 0) - nvl(cand.HARD_RESERVED_QTY, 0), 0);
          if v_available_qty > 0 and v_remaining_qty > 0 then
            v_sort_order := v_sort_order + 1;
            v_suggested_qty := least(v_remaining_qty, v_available_qty);
            v_available_total := v_available_total + v_available_qty;
            v_remaining_qty := greatest(v_remaining_qty - v_suggested_qty, 0);

            select RRL_MES_RAW_SUPPLY_CANDIDATE_SQ.nextval into v_candidate_id from dual;
            insert into RRL_MES_RAW_SUPPLY_CANDIDATE (
              CANDIDATE_ID, DEMAND_ID, PRODUCTION_ORDER_ID, RAW_ARTICUL,
              UID_PALLET, BATCH_ID, RAW_BATCH_ID, SSCC, FROM_WARE_ID, FROM_CELL,
              PHYSICAL_QTY, HARD_RESERVED_QTY, AVAILABLE_QTY, SUGGESTED_QTY,
              EXPIRY_DATE, QUALITY_STATUS, SORT_ORDER
            ) values (
              v_candidate_id, v_demand_id, p_production_order_id, line.COMPONENT_ARTICUL,
              cand.UID_PALLET, cand.BATCH_ID, cand.RAW_BATCH_ID, cand.SSCC, cand.WARE_ID, cand.CELL,
              cand.PHYSICAL_QTY, cand.HARD_RESERVED_QTY, v_available_qty, v_suggested_qty,
              cand.EXPIRY_DATE, cand.QUALITY_STATUS, v_sort_order
            );
          end if;

          exit when v_remaining_qty = 0;
        end loop;

        if v_remaining_qty > 0 then
          v_shortage_count := v_shortage_count + 1;
          select RRL_MES_RAW_SHORTAGE_SQ.nextval into v_shortage_id from dual;
          insert into RRL_MES_RAW_SHORTAGE (
            SHORTAGE_ID, PRODUCTION_ORDER_ID, DEMAND_ID, RAW_ARTICUL,
            REQUIRED_QTY, ISSUED_QTY, AVAILABLE_QTY, SHORTAGE_QTY, UNIT_CODE, STATUS
          ) values (
            v_shortage_id, p_production_order_id, v_demand_id, line.COMPONENT_ARTICUL,
            v_required_qty, v_issued_qty, greatest(v_open_qty - v_remaining_qty, 0), v_remaining_qty,
            line.UNIT_CODE, 'OPEN'
          );
        end if;
      end if;
    end loop;

    if v_shortage_count > 0 and nvl(p_allow_partial, 0) <> 1 then
      return 0;
    end if;

    for c in (
      select d.ORDER_LINE_ID, d.BOM_ID, d.BOM_LINE_ID, d.REQUIRED_QTY, d.UNIT_CODE,
             sc.RAW_ARTICUL, sc.UID_PALLET, sc.BATCH_ID, sc.RAW_BATCH_ID, sc.SSCC,
             sc.FROM_WARE_ID, sc.FROM_CELL, sc.PHYSICAL_QTY, sc.SUGGESTED_QTY
        from RRL_MES_RAW_DEMAND d
        join RRL_MES_RAW_SUPPLY_CANDIDATE sc on sc.DEMAND_ID = d.DEMAND_ID
       where d.PRODUCTION_ORDER_ID = p_production_order_id
         and sc.SUGGESTED_QTY > 0
       order by d.DEMAND_ID, sc.SORT_ORDER, sc.CANDIDATE_ID
    ) loop
      v_reservation_scope := case
        when nvl(c.PHYSICAL_QTY, 0) > 0 and nvl(c.SUGGESTED_QTY, 0) >= nvl(c.PHYSICAL_QTY, 0)
        then 'PALLET'
        else 'QTY'
      end;

      select RRL_STOCK_RESERVATION_SQ.nextval into v_reservation_id from dual;
      insert into RRL_STOCK_RESERVATION (
        RESERVATION_ID, RESERVATION_KIND, RESERVATION_SCOPE, RESERVATION_DOMAIN,
        SOURCE_DOC_TYPE, SOURCE_DOC_ID, SOURCE_LINE_ID, PRODUCTION_ORDER_ID,
        ARTICUL, QTY, UNIT_CODE, WARE_ID, CELL, BATCH_ID, UID_PALLET, SSCC,
        STATUS, PRIORITY, CREATED_BY
      ) values (
        v_reservation_id, 'HARD', v_reservation_scope, 'MES_RAW',
        'PRODUCTION_ORDER', p_production_order_id, c.ORDER_LINE_ID, p_production_order_id,
        c.RAW_ARTICUL, c.SUGGESTED_QTY, c.UNIT_CODE, c.FROM_WARE_ID, c.FROM_CELL,
        c.BATCH_ID, c.UID_PALLET, c.SSCC, 'ACTIVE', 100, v_actor
      );

      select RRL_MES_RAW_TRANSFER_TASK_SQ.nextval into v_task_id from dual;
      insert into RRL_MES_RAW_TRANSFER_TASK (
        TASK_ID, PRODUCTION_ORDER_ID, ORDER_LINE_ID, BOM_ID, BOM_LINE_ID,
        RAW_ARTICUL, RAW_BATCH_ID, BATCH_ID, UID_PALLET, SSCC,
        FROM_WARE_ID, FROM_CELL, TO_WARE_ID, TO_CELL,
        REQUIRED_QTY, TASK_QTY, UNIT_CODE, RESERVATION_ID,
        TASK_STATUS, PRIORITY, CREATED_BY
      ) values (
        v_task_id, p_production_order_id, c.ORDER_LINE_ID, c.BOM_ID, c.BOM_LINE_ID,
        c.RAW_ARTICUL, c.RAW_BATCH_ID, c.BATCH_ID, c.UID_PALLET, c.SSCC,
        c.FROM_WARE_ID, c.FROM_CELL, p_to_ware_id, v_to_cell,
        c.REQUIRED_QTY, c.SUGGESTED_QTY, c.UNIT_CODE, v_reservation_id,
        'PLANNED', 100, v_actor
      );

      update RRL_STOCK_RESERVATION
         set TASK_ID = v_task_id
       where RESERVATION_ID = v_reservation_id;

      v_task_count := v_task_count + 1;
    end loop;

    if v_task_count > 0 then
      update RRL_PRODUCTION_ORDER
         set STATUS = case when STATUS = 'DRAFT' then 'RELEASED' else STATUS end,
             UPDATED_AT = systimestamp,
             UPDATED_BY = v_actor
       where PRODUCTION_ORDER_ID = p_production_order_id
         and STATUS not in ('COMPLETED', 'CANCELLED');
    end if;

    return v_task_count;
  exception
    when no_data_found then
      raise_application_error(-20952, 'MES production order not found');
  end release_to_production;
end RRL_MES_RAW_SUPPLY_API;
/

merge into RRL_SCHEMA_MIGRATIONS d
using (
  select '2026-05-17-025-mes-raw-supply-api' migration_id,
         'Oracle package for atomic MES release-to-production raw supply reservations' description,
         '025_apply.sql' script_name,
         '025_rollback.sql' rollback_script
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

prompt [migration 2026-05-17-025] done
