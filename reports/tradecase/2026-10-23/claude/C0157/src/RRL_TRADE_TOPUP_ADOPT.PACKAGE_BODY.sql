package body RRL_TRADE_TOPUP_ADOPT as
 procedure fail(p_code varchar2)is begin raise_application_error(-20911,p_code);end;

 function line_proposal(p_row number)return number is
  v_order number;v_ext varchar2(100);v_ware number;v_docver number;p RRL_TRADE_TOPUP_PROPOSAL%rowtype;ol RRL_TRADE_ORDER_LINE%rowtype;
  order_body clob;order_src varchar2(100);trip_body clob;trip_src varchar2(100);site_src varchar2(100);n number;qty number;uom varchar2(10);
 begin
  begin
   select CUSTOMER_ORDER_ID into v_order from RRL_CUSTOMER_ORDER_ROW where CUSTOMER_ORDER_ROW_ID=p_row;
   select EXTERNAL_ID,WARE_ID,DOCUMENT_VERSION into v_ext,v_ware,v_docver from RRL_TRADE_ORDER_LINK where CUSTOMER_ORDER_ID=v_order;
   select*into p from RRL_TRADE_TOPUP_PROPOSAL where WARE_ID=v_ware and SAP_ORDER_ID=v_ext;
  exception when no_data_found then return null;end;
  -- A cancelled/rejected proposal never turns its still-active external order into an ordinary free-stock order.
  if p.STATUS<>'SAP_ACCEPTED'then return -1;end if;
  select count(*)into n from RRL_TRADE_TOPUP_HOLD where PROPOSAL_ID=p.PROPOSAL_ID and STATUS='ACTIVE';
  if n=0 then return null;end if;  -- everything already taken over by a wave: nothing left to adopt
  select*into ol from RRL_TRADE_ORDER_LINE where CUSTOMER_ORDER_ROW_ID=p_row;
  if ol.SKU_ID<>p.SKU_ID or ol.SOURCE_OWNER_ID<>p.SOURCE_OWNER_ID or ol.TARGET_OWNER_ID<>p.TARGET_OWNER_ID or ol.MRC<>p.MRC then return -1;end if;
  select BODY_JSON,SOURCE_ID into order_body,order_src from RRL_TRADE_DOCUMENT
   where WARE_ID=v_ware and ENTITY_TYPE='ORDER'and EXTERNAL_ID=v_ext and VERSION_NO=v_docver and STATUS='ACCEPTED';
  if nvl(json_value(order_body,'$.order_kind'),'-')<>'TOPUP'or nvl(json_value(order_body,'$.parent_trip_id'),'-')<>p.TRIP_ID
   or nvl(json_value(order_body,'$.recipient_id'),'-')<>p.RECIPIENT_ID or nvl(json_value(order_body,'$.cancelled'),'false')='true'then return -1;end if;
  select x.QTY,x.UOM into qty,uom from json_table(order_body,'$.lines[*]'columns(LINE_ID varchar2(100)path'$.line_id',QTY number path'$.quantity',UOM varchar2(10)path'$.uom'))x
   where x.LINE_ID=ol.EXTERNAL_LINE_ID;
  if case when uom='BOX'then qty*p.UNITS_PER_BOX else qty end<>p.APPROVED_BOXES*p.UNITS_PER_BOX then return -1;end if;
  select SOURCE_ID into site_src from RRL_TRADE_SITE where WARE_ID=v_ware;
  -- SAP sends both documents: the separate order AND the updated trip that contains it. Without the second, no tasks.
  select BODY_JSON,SOURCE_ID into trip_body,trip_src from RRL_TRADE_DOCUMENT where WARE_ID=v_ware and ENTITY_TYPE='TRIP'and EXTERNAL_ID=p.TRIP_ID and STATUS='ACCEPTED';
  if order_src<>site_src or trip_src<>site_src or nvl(json_value(trip_body,'$.cancelled'),'false')='true'then return -1;end if;
  select count(*)into n from json_table(trip_body,'$.orders[*]'columns(O varchar2(100)path'$.order_id',L varchar2(100)path'$.line_id',Q number path'$.quantity'))t
   where t.O=v_ext and t.L=ol.EXTERNAL_LINE_ID and t.Q=qty;
  if n<>1 then return -1;end if;
  return p.PROPOSAL_ID;
 exception when no_data_found or too_many_rows then return -1;
 end;

 function hold_rid(p_proposal number,p_uid varchar2,p_cell varchar2)return number is v number;
 begin
  select max(RESERVATION_ID)into v from RRL_TRADE_TOPUP_HOLD where PROPOSAL_ID=p_proposal and UID_PALLET=p_uid and CELL=p_cell and STATUS='ACTIVE';
  return v;
 end;

 function gate(p_row number,p_uid varchar2,p_cell varchar2)return varchar2 is v number;n number;
 begin
  v:=line_proposal(p_row);
  if v is null then return null;end if;
  if v=-1 then return 'TRADE_TOPUP_ADOPTION_CONDITIONS_NOT_MET';end if;
  -- Own order row: only the sources of its own hold (still held, or already taken over by its wave during execution).
  select count(*)into n from RRL_TRADE_TOPUP_HOLD where PROPOSAL_ID=v and UID_PALLET=p_uid and CELL=p_cell and STATUS in('ACTIVE','ADOPTED');
  if n=0 then return 'TRADE_TOPUP_HELD_SOURCE_REQUIRED';end if;
  return null;
 end;

 function hold_free(p_proposal number,p_row number,p_uid varchar2,p_cell varchar2)return number is h number;s number;
 begin
  select nvl(sum(BASE_QTY),0)into h from RRL_TRADE_TOPUP_HOLD where PROPOSAL_ID=p_proposal and UID_PALLET=p_uid and CELL=p_cell and STATUS='ACTIVE';
  select nvl(sum(pr.RESERVED_QTY),0)into s from RRL_PICK_RESERVATION pr join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_LINE_ID=pr.PICK_PLAN_LINE_ID
   join RRL_PICK_PLAN pp on pp.PICK_PLAN_ID=pl.PICK_PLAN_ID
   where pl.CUSTOMER_ORDER_ROW_ID=p_row and pr.PALLET_UID=p_uid and pr.SOURCE_CELL_CODE=p_cell
    and pr.RESERVATION_STATUS='ACTIVE'and pr.RESERVATION_LEVEL='SOFT'and pp.STATUS in('DRAFT','PLANNED_FULL','PLANNED_PARTIAL');
  return greatest(0,h-s);
 end;

 function task_proposal(p_task number,p_uid varchar2,p_cell varchar2)return number is v_row number;v number;
 begin
  select pl.CUSTOMER_ORDER_ROW_ID into v_row from RRL_PICK_TASK t join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_LINE_ID=t.PICK_PLAN_LINE_ID where t.PICK_TASK_ID=p_task;
  v:=line_proposal(v_row);
  if v is null then return null;end if;
  if v=-1 then fail('TRADE_TOPUP_ADOPTION_CONDITIONS_NOT_MET');end if;
  if hold_rid(v,p_uid,p_cell)is null then fail('TRADE_TOPUP_HOLD_CHANGED');end if;
  return v;
 exception when no_data_found then return null;
 end;

 procedure compile_wave(p_wave number,p_resources in out nocopy json_array_t)is v number;flag number;
 begin
  for r in(select distinct pl.CUSTOMER_ORDER_ROW_ID ROW_ID,pr.ARTICUL,w.WARE_ID from RRL_PICK_RESERVATION pr
    join RRL_PICK_WAVE_ORDER wo on wo.PICK_PLAN_ID=pr.PICK_PLAN_ID join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_LINE_ID=pr.PICK_PLAN_LINE_ID
    join RRL_PICK_WAVE w on w.PICK_WAVE_ID=wo.PICK_WAVE_ID
    where wo.PICK_WAVE_ID=p_wave and wo.STATUS='ACTIVE'and pr.RESERVATION_STATUS='ACTIVE'and pr.RESERVATION_LEVEL='SOFT'order by 1)loop
   v:=line_proposal(r.ROW_ID);
   if v>0 then
    flag:=0;
    begin select nvl(SHIP_FROM_STOCK,case STOCK_ALLOC_CLASS when 'DRY_RACK'then 1 else 0 end)into flag from RRL_RECEIPT_SKU_RULE where WARE_ID=r.WARE_ID and ARTICUL=r.ARTICUL;
    exception when no_data_found then null;end;
    -- The common pool would promise this quantity a second time; held top-ups of pool articles are refused explicitly.
    if flag=1 then fail('TRADE_TOPUP_COMMON_POOL_UNSUPPORTED');end if;
    -- Same row key as top-up confirm/release: launch and cancellation of one proposal are serialized.
    RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_TRADE_TOPUP_PROPOSAL',RRL_STOCK_PLAN_HELPER.decimal_text(v));
   end if;
  end loop;
 end;

 function split_units(p_hold number,p_qty number)return clob is a json_array_t:=json_array_t();
 begin
  for u in(select PHYSICAL_UNIT_KEY from RRL_WMS_RECEIPT_UNIT where HARD_RESERVATION_ID=p_hold and STOCK_STATUS<>'ISSUED'
    order by PHYSICAL_UNIT_KEY fetch first p_qty rows only)loop a.append(u.PHYSICAL_UNIT_KEY);end loop;
  if a.get_size<>p_qty then fail('TRADE_TOPUP_HOLD_UNITS_CHANGED');end if;
  return a.to_clob;
 end;

 procedure mark_adopted(p_hold number,p_rid number,p_qty number,p_proposal number,p_wave number,p_task number,p_line number,p_op varchar2,p_actor varchar2)is
 begin
  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')is null or sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')<>p_op
   or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')<>dbms_transaction.local_transaction_id(false)then raise_application_error(-20863,'TOPUP_ADOPTION_ONLY_IN_WAVE_LAUNCH');end if;
  if p_rid=p_hold then
   update RRL_TRADE_TOPUP_HOLD set STATUS='ADOPTED',RELEASED_OPERATION_ID=p_op where RESERVATION_ID=p_hold and PROPOSAL_ID=p_proposal and STATUS='ACTIVE'and BASE_QTY=p_qty;
   if sql%rowcount<>1 then fail('TRADE_TOPUP_HOLD_CHANGED');end if;
  else
   update RRL_TRADE_TOPUP_HOLD set BASE_QTY=BASE_QTY-p_qty where RESERVATION_ID=p_hold and PROPOSAL_ID=p_proposal and STATUS='ACTIVE'and BASE_QTY>p_qty;
   if sql%rowcount<>1 then fail('TRADE_TOPUP_HOLD_CHANGED');end if;
   insert into RRL_TRADE_TOPUP_HOLD(RESERVATION_ID,PROPOSAL_ID,UID_PALLET,CELL,BASE_QTY,STATUS,CREATED_OPERATION_ID,RELEASED_OPERATION_ID)
    select p_rid,PROPOSAL_ID,UID_PALLET,CELL,p_qty,'ADOPTED',p_op,p_op from RRL_TRADE_TOPUP_HOLD where RESERVATION_ID=p_hold;
  end if;
  insert into RRL_TRADE_TOPUP_ADOPTION(RESERVATION_ID,PROPOSAL_ID,HOLD_RESERVATION_ID,PICK_WAVE_ID,PICK_TASK_ID,PICK_PLAN_LINE_ID,BASE_QTY,OPERATION_ID,ACTOR)
   values(p_rid,p_proposal,p_hold,p_wave,p_task,p_line,p_qty,p_op,p_actor);
 end;
end;