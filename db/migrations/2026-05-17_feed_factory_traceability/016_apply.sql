prompt [migration 2026-05-17-016] Picking plan and reservations - apply

declare
  procedure ensure_table(p_name varchar2, p_sql varchar2) is
    n number;
  begin
    select count(*) into n from user_tables where table_name = upper(p_name);
    if n = 0 then
      execute immediate p_sql;
    end if;
  end;

  procedure ensure_sequence(p_name varchar2, p_sql varchar2) is
    n number;
  begin
    select count(*) into n from user_sequences where sequence_name = upper(p_name);
    if n = 0 then
      execute immediate p_sql;
    end if;
  end;

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
  ensure_table('RRL_PICK_PLAN', q'[
    create table RRL_PICK_PLAN (
      PICK_PLAN_ID number not null,
      CUSTOMER_ORDER_ID number not null,
      CUSTOMER_ID number,
      WARE_ID number,
      ROUTE_ID number,
      DOCK_ID number,
      STATUS varchar2(30) default 'DRAFT' not null,
      PLAN_STRATEGY varchar2(30) default 'FEFO' not null,
      TOTAL_ORDER_QTY number default 0 not null,
      TOTAL_PLANNED_QTY number default 0 not null,
      TOTAL_SHORTAGE_QTY number default 0 not null,
      COMMENT_TEXT varchar2(1000),
      CREATED_AT date default sysdate not null,
      CREATED_BY varchar2(50),
      UPDATED_AT date,
      UPDATED_BY varchar2(50),
      constraint RRL_PICK_PLAN_PK primary key (PICK_PLAN_ID),
      constraint RRL_PICK_PLAN_FK1 foreign key (CUSTOMER_ORDER_ID) references RRL_CUSTOMER_ORDER (CUSTOMER_ORDER_ID),
      constraint RRL_PICK_PLAN_CHK1 check (STATUS in ('DRAFT', 'PLANNED_FULL', 'PLANNED_PARTIAL', 'NO_STOCK', 'RELEASED', 'CANCELLED', 'DONE')),
      constraint RRL_PICK_PLAN_CHK2 check (PLAN_STRATEGY in ('FEFO', 'FIFO'))
    )
  ]');

  ensure_table('RRL_PICK_PLAN_LINE', q'[
    create table RRL_PICK_PLAN_LINE (
      PICK_PLAN_LINE_ID number not null,
      PICK_PLAN_ID number not null,
      CUSTOMER_ORDER_ROW_ID number not null,
      ARTICUL varchar2(40) not null,
      PRODUCT_NAME varchar2(255),
      REQUESTED_QTY number not null,
      PLANNED_QTY number default 0 not null,
      FULL_PALLET_QTY number default 0 not null,
      CASE_PICK_QTY number default 0 not null,
      SHORTAGE_QTY number default 0 not null,
      STATUS varchar2(30) default 'OPEN' not null,
      CREATED_AT date default sysdate not null,
      CREATED_BY varchar2(50),
      UPDATED_AT date,
      UPDATED_BY varchar2(50),
      constraint RRL_PICK_PLAN_LINE_PK primary key (PICK_PLAN_LINE_ID),
      constraint RRL_PICK_PLAN_LINE_FK1 foreign key (PICK_PLAN_ID) references RRL_PICK_PLAN (PICK_PLAN_ID),
      constraint RRL_PICK_PLAN_LINE_FK2 foreign key (CUSTOMER_ORDER_ROW_ID) references RRL_CUSTOMER_ORDER_ROW (CUSTOMER_ORDER_ROW_ID),
      constraint RRL_PICK_PLAN_LINE_CHK1 check (REQUESTED_QTY >= 0),
      constraint RRL_PICK_PLAN_LINE_CHK2 check (STATUS in ('OPEN', 'PLANNED_FULL', 'PLANNED_PARTIAL', 'NO_STOCK', 'CANCELLED', 'DONE'))
    )
  ]');

  ensure_table('RRL_PICK_TASK', q'[
    create table RRL_PICK_TASK (
      PICK_TASK_ID number not null,
      PICK_PLAN_ID number not null,
      PICK_PLAN_LINE_ID number not null,
      CUSTOMER_ORDER_ID number not null,
      CUSTOMER_ID number,
      TASK_TYPE varchar2(30) not null,
      STATUS varchar2(30) default 'NEW' not null,
      ARTICUL varchar2(40) not null,
      PALLET_UID varchar2(200),
      SSCC varchar2(50),
      PROD_BATCH_ID number,
      SOURCE_CELL_CODE varchar2(60),
      TARGET_CELL_CODE varchar2(60),
      QTY number not null,
      PICK_SEQUENCE number,
      ASSIGNED_TO varchar2(50),
      CREATED_AT date default sysdate not null,
      CREATED_BY varchar2(50),
      STARTED_AT date,
      DONE_AT date,
      UPDATED_AT date,
      UPDATED_BY varchar2(50),
      ERROR_TEXT varchar2(4000),
      constraint RRL_PICK_TASK_PK primary key (PICK_TASK_ID),
      constraint RRL_PICK_TASK_FK1 foreign key (PICK_PLAN_ID) references RRL_PICK_PLAN (PICK_PLAN_ID),
      constraint RRL_PICK_TASK_FK2 foreign key (PICK_PLAN_LINE_ID) references RRL_PICK_PLAN_LINE (PICK_PLAN_LINE_ID),
      constraint RRL_PICK_TASK_FK3 foreign key (CUSTOMER_ORDER_ID) references RRL_CUSTOMER_ORDER (CUSTOMER_ORDER_ID),
      constraint RRL_PICK_TASK_CHK1 check (TASK_TYPE in ('FULL_PALLET', 'CASE_PICK')),
      constraint RRL_PICK_TASK_CHK2 check (STATUS in ('NEW', 'ASSIGNED', 'IN_PROGRESS', 'DONE', 'CANCELLED', 'FAILED')),
      constraint RRL_PICK_TASK_CHK3 check (QTY >= 0)
    )
  ]');

  ensure_table('RRL_PICK_RESERVATION', q'[
    create table RRL_PICK_RESERVATION (
      PICK_RESERVATION_ID number not null,
      PICK_PLAN_ID number not null,
      PICK_PLAN_LINE_ID number not null,
      PICK_TASK_ID number,
      CUSTOMER_ORDER_ID number not null,
      CUSTOMER_ID number,
      RESERVATION_LEVEL varchar2(20) default 'SOFT' not null,
      RESERVATION_STATUS varchar2(20) default 'ACTIVE' not null,
      RESERVATION_SCOPE varchar2(20) default 'PALLET' not null,
      PALLET_UID varchar2(200),
      SSCC varchar2(50),
      ARTICUL varchar2(40) not null,
      PROD_BATCH_ID number,
      SOURCE_CELL_CODE varchar2(60),
      RESERVED_QTY number not null,
      CREATED_AT date default sysdate not null,
      CREATED_BY varchar2(50),
      RELEASED_AT date,
      CONSUMED_AT date,
      UPDATED_AT date,
      UPDATED_BY varchar2(50),
      constraint RRL_PICK_RESERVATION_PK primary key (PICK_RESERVATION_ID),
      constraint RRL_PICK_RESERVATION_FK1 foreign key (PICK_PLAN_ID) references RRL_PICK_PLAN (PICK_PLAN_ID),
      constraint RRL_PICK_RESERVATION_FK2 foreign key (PICK_PLAN_LINE_ID) references RRL_PICK_PLAN_LINE (PICK_PLAN_LINE_ID),
      constraint RRL_PICK_RESERVATION_FK3 foreign key (PICK_TASK_ID) references RRL_PICK_TASK (PICK_TASK_ID),
      constraint RRL_PICK_RESERVATION_FK4 foreign key (CUSTOMER_ORDER_ID) references RRL_CUSTOMER_ORDER (CUSTOMER_ORDER_ID),
      constraint RRL_PICK_RESERVATION_CHK1 check (RESERVATION_LEVEL in ('SOFT', 'HARD')),
      constraint RRL_PICK_RESERVATION_CHK2 check (RESERVATION_STATUS in ('ACTIVE', 'CONSUMED', 'RELEASED', 'EXPIRED')),
      constraint RRL_PICK_RESERVATION_CHK3 check (RESERVATION_SCOPE in ('PALLET', 'CASE')),
      constraint RRL_PICK_RESERVATION_CHK4 check (RESERVED_QTY >= 0)
    )
  ]');

  ensure_table('RRL_PICK_SHORTAGE', q'[
    create table RRL_PICK_SHORTAGE (
      PICK_SHORTAGE_ID number not null,
      PICK_PLAN_ID number not null,
      PICK_PLAN_LINE_ID number,
      CUSTOMER_ORDER_ID number not null,
      CUSTOMER_ORDER_ROW_ID number,
      CUSTOMER_ID number,
      ARTICUL varchar2(40) not null,
      REQUESTED_QTY number default 0 not null,
      AVAILABLE_QTY number default 0 not null,
      RESERVED_BY_OTHER_QTY number default 0 not null,
      PLANNED_QTY number default 0 not null,
      SHORTAGE_QTY number default 0 not null,
      REASON_CODE varchar2(50),
      REASON_TEXT varchar2(1000),
      CREATED_AT date default sysdate not null,
      CREATED_BY varchar2(50),
      constraint RRL_PICK_SHORTAGE_PK primary key (PICK_SHORTAGE_ID),
      constraint RRL_PICK_SHORTAGE_FK1 foreign key (PICK_PLAN_ID) references RRL_PICK_PLAN (PICK_PLAN_ID),
      constraint RRL_PICK_SHORTAGE_FK2 foreign key (PICK_PLAN_LINE_ID) references RRL_PICK_PLAN_LINE (PICK_PLAN_LINE_ID),
      constraint RRL_PICK_SHORTAGE_FK3 foreign key (CUSTOMER_ORDER_ID) references RRL_CUSTOMER_ORDER (CUSTOMER_ORDER_ID)
    )
  ]');

  ensure_table('RRL_PICK_DECISION_LOG', q'[
    create table RRL_PICK_DECISION_LOG (
      PICK_DECISION_ID number not null,
      PICK_PLAN_ID number not null,
      PICK_PLAN_LINE_ID number,
      DECISION_TYPE varchar2(50) not null,
      MESSAGE_TEXT varchar2(1000),
      PAYLOAD_JSON clob,
      CREATED_AT date default sysdate not null,
      CREATED_BY varchar2(50),
      constraint RRL_PICK_DECISION_LOG_PK primary key (PICK_DECISION_ID),
      constraint RRL_PICK_DECISION_LOG_FK1 foreign key (PICK_PLAN_ID) references RRL_PICK_PLAN (PICK_PLAN_ID),
      constraint RRL_PICK_DECISION_LOG_FK2 foreign key (PICK_PLAN_LINE_ID) references RRL_PICK_PLAN_LINE (PICK_PLAN_LINE_ID)
    )
  ]');

  ensure_sequence('RRL_PICK_PLAN_SQ', 'create sequence RRL_PICK_PLAN_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_PICK_PLAN_LINE_SQ', 'create sequence RRL_PICK_PLAN_LINE_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_PICK_TASK_SQ', 'create sequence RRL_PICK_TASK_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_PICK_RESERVATION_SQ', 'create sequence RRL_PICK_RESERVATION_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_PICK_SHORTAGE_SQ', 'create sequence RRL_PICK_SHORTAGE_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_PICK_DECISION_LOG_SQ', 'create sequence RRL_PICK_DECISION_LOG_SQ start with 1 increment by 1 nocache');

  ensure_index('RRL_PICK_PLAN_I1', 'create index RRL_PICK_PLAN_I1 on RRL_PICK_PLAN (CUSTOMER_ORDER_ID, STATUS)');
  ensure_index('RRL_PICK_PLAN_LINE_I1', 'create index RRL_PICK_PLAN_LINE_I1 on RRL_PICK_PLAN_LINE (PICK_PLAN_ID, ARTICUL)');
  ensure_index('RRL_PICK_TASK_I1', 'create index RRL_PICK_TASK_I1 on RRL_PICK_TASK (PICK_PLAN_ID, STATUS)');
  ensure_index('RRL_PICK_TASK_I2', 'create index RRL_PICK_TASK_I2 on RRL_PICK_TASK (PALLET_UID, STATUS)');
  ensure_index('RRL_PICK_RESERVATION_I1', 'create index RRL_PICK_RESERVATION_I1 on RRL_PICK_RESERVATION (PALLET_UID, RESERVATION_STATUS)');
  ensure_index('RRL_PICK_RESERVATION_I2', 'create index RRL_PICK_RESERVATION_I2 on RRL_PICK_RESERVATION (PICK_PLAN_ID, RESERVATION_STATUS)');
  ensure_index('RRL_PICK_SHORTAGE_I1', 'create index RRL_PICK_SHORTAGE_I1 on RRL_PICK_SHORTAGE (PICK_PLAN_ID, ARTICUL)');
  ensure_index('RRL_PICK_DECISION_LOG_I1', 'create index RRL_PICK_DECISION_LOG_I1 on RRL_PICK_DECISION_LOG (PICK_PLAN_ID, CREATED_AT)');
end;
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

              select RRL_PICK_TASK_SQ.nextval into v_task_id from dual;
              insert into RRL_PICK_TASK (
                PICK_TASK_ID, PICK_PLAN_ID, PICK_PLAN_LINE_ID, CUSTOMER_ORDER_ID, CUSTOMER_ID,
                TASK_TYPE, STATUS, ARTICUL, PALLET_UID, SSCC, PROD_BATCH_ID,
                SOURCE_CELL_CODE, QTY, PICK_SEQUENCE, CREATED_AT, CREATED_BY
              ) values (
                v_task_id, v_pick_plan_id, v_line_id, p_customer_order_id, v_order.CUSTOMER_ID,
                v_task_type, 'NEW', upper(substr(l.ARTICUL, 1, 40)), c.UID_POLETA,
                c.SSCC, c.PROD_BATCH_ID, c.CELL, v_reserve_qty,
                null, sysdate, substr(p_created_by, 1, 50)
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

insert into RIGHTS (RIGHT1, USER_GROUP, ID, DESCR)
select s.RIGHT1,
       'GLOBAL_ADMIN',
       (select nvl(max(ID), 0) from RIGHTS) + row_number() over (order by s.RIGHT1),
       s.DESCR
  from (
    select 'PICK_PLAN_VIEW' RIGHT1, 'View picking plans' DESCR from dual
    union all
    select 'PICK_PLAN_CREATE', 'Create picking plans and soft reservations' from dual
    union all
    select 'PICK_PLAN_CANCEL', 'Cancel picking plans and release soft reservations' from dual
    union all
    select 'PICK_RESERVATION_VIEW', 'View picking reservations' from dual
    union all
    select 'PICK_SHORTAGE_VIEW', 'View picking shortages' from dual
  ) s
 where not exists (
   select 1
     from RIGHTS r
    where r.USER_GROUP = 'GLOBAL_ADMIN'
      and upper(r.RIGHT1) = s.RIGHT1
 );

merge into RRL_SCHEMA_MIGRATIONS d
using (
  select '2026-05-17-016-picking-plan-reservations' migration_id,
         'Picking plans, soft reservations, shortages, tasks, and decision log' description,
         '016_apply.sql' script_name,
         '016_rollback.sql' rollback_script
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

prompt [migration 2026-05-17-016] done
