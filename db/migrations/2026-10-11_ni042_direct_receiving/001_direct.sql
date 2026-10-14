create or replace package RRL_DIRECT_RECEIVING_PICK authid definer
 accessible by(package RRL_PICKING_API,package RRL_STOCK_WAVE_LAUNCH_CMD) as
 function enabled(p_uid varchar2,p_cell varchar2,p_ware number,p_article varchar2)return number;
 procedure compile_holds(p_wave number,p_resources in out nocopy json_array_t,p_holds out clob);
 procedure apply_holds(p_holds clob,p_actor varchar2);
end;
/
create or replace package body RRL_DIRECT_RECEIVING_PICK as
 function enabled(p_uid varchar2,p_cell varchar2,p_ware number,p_article varchar2)return number is n number;
 begin
  select count(*)into n from RRL_SAP_PALLET_RECEIPT rec join RRL_SAP_SUPPLY_ORDER so on so.ORDER_ID=rec.ORDER_ID
   join RRL_RECEIPT_SKU_RULE rule on rule.WARE_ID=p_ware and rule.ARTICUL=p_article and rule.SOURCE_PICK_MODE='DIRECT'
   where rec.UID_PALLET=p_uid and so.WARE_ID=p_ware and so.RECEIVE_CELL=p_cell;
  if n=0 then return 0;end if;
  select count(*)into n from RRL_WAREHOUSE_TASK where UID_PALLET=p_uid and FROM_CELL=p_cell
   and TASK_TYPE='PUTAWAY'and STATUS='IN_PROGRESS';
  if n>0 then raise_application_error(-20886,'DIRECT_RECEIVING_PUTAWAY_IN_PROGRESS');end if;
  return 1;
 end;
 procedure compile_holds(p_wave number,p_resources in out nocopy json_array_t,p_holds out clob)is
  a json_array_t:=json_array_t();x json_object_t;
 begin
  for t in(select distinct wh.TASK_ID,wh.UID_PALLET,wh.FROM_CELL,wh.FROM_WARE_ID,wh.STATUS,wh.QTY,wh.FACT_QTY,
    wh.TO_CELL_SLOT_ID,pr.ARTICUL,claim.CELL_SLOT_ID CLAIM_SLOT,claim.STATUS CLAIM_STATUS
   from RRL_PICK_WAVE_ORDER wo join RRL_PICK_RESERVATION pr on pr.PICK_PLAN_ID=wo.PICK_PLAN_ID
   join RRL_PICK_TASK pt on pt.PICK_TASK_ID=pr.PICK_TASK_ID
   join RRL_WAREHOUSE_TASK wh on wh.UID_PALLET=pr.PALLET_UID and wh.FROM_CELL=pr.SOURCE_CELL_CODE
   left join RRL_RECEIPT_SLOT_CLAIM claim on claim.TASK_ID=wh.TASK_ID
   where wo.PICK_WAVE_ID=p_wave and wo.STATUS='ACTIVE'and pr.RESERVATION_STATUS='ACTIVE'and pr.RESERVATION_LEVEL='SOFT'
    and pt.TASK_TYPE='CASE_PICK'and pt.TARGET_CELL_CODE is null
    and wh.TASK_TYPE='PUTAWAY'and wh.TASK_SOURCE='SAP_RECEIPT'and wh.STATUS not in('DONE','CANCELLED')
   order by wh.TASK_ID fetch first 201 rows only)loop
   if enabled(t.UID_PALLET,t.FROM_CELL,t.FROM_WARE_ID,t.ARTICUL)=0 then continue;end if;
   if a.get_size>=200 then raise_application_error(-20881,'DIRECT_RECEIVING_PUTAWAY_BOUND');end if;
   if t.STATUS not in('PLANNED','ASSIGNED','ERROR')or nvl(t.FACT_QTY,0)!=0
    or(t.CLAIM_STATUS is not null and t.CLAIM_STATUS!='RESERVED')then raise_application_error(-20886,'DIRECT_RECEIVING_PUTAWAY_ALREADY_PHYSICAL');end if;
   RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(t.TASK_ID));
   if t.CLAIM_SLOT is not null then
    RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_RECEIPT_SLOT_CLAIM',RRL_STOCK_PLAN_HELPER.decimal_text(t.TASK_ID));
    RRL_STOCK_PLAN_HELPER.anchor(p_resources,40,'SLOT',RRL_STOCK_PLAN_HELPER.decimal_text(t.CLAIM_SLOT));
   end if;
   x:=json_object_t();x.put('task_id',t.TASK_ID);x.put('uid',t.UID_PALLET);x.put('cell',t.FROM_CELL);x.put('status',t.STATUS);
   x.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(t.QTY));x.put('slot',t.CLAIM_SLOT);a.append(x);
  end loop;
  p_holds:=a.to_clob;
 end;
 procedure apply_holds(p_holds clob,p_actor varchar2)is
  a json_array_t:=json_array_t.parse(p_holds);x json_object_t;t RRL_WAREHOUSE_TASK%rowtype;id number;slot_id number;n number;
 begin
  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')is null
   or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)
   then raise_application_error(-20863,'DIRECT_RECEIVING_NATIVE_OWNER_REQUIRED');end if;
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i)as json_object_t);id:=x.get_number('task_id');slot_id:=x.get_number('slot');
   RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(id)));
   select *into t from RRL_WAREHOUSE_TASK where TASK_ID=id for update;
   if t.STATUS!=x.get_string('status')or t.UID_PALLET!=x.get_string('uid')or t.FROM_CELL!=x.get_string('cell')
    or RRL_STOCK_PLAN_HELPER.decimal_text(t.QTY)!=x.get_string('quantity')or nvl(t.FACT_QTY,0)!=0
    then raise_application_error(-20890,'CLOSURE_CHANGED: direct receiving putaway');end if;
   select count(*)into n from RRL_RECEIPT_SLOT_CLAIM where TASK_ID=id;
   if slot_id is null and n>0 then raise_application_error(-20890,'CLOSURE_CHANGED: direct putaway claim');end if;
   if slot_id is not null then
    select count(*)into n from RRL_RECEIPT_SLOT_CLAIM where TASK_ID=id and CELL_SLOT_ID=slot_id and STATUS='RESERVED';
    if n!=1 then raise_application_error(-20890,'CLOSURE_CHANGED: direct putaway claim');end if;
    delete from RRL_RECEIPT_SLOT_CLAIM where TASK_ID=id;
   end if;
   update RRL_WAREHOUSE_TASK set STATUS='CANCELLED',CANCELLED_AT=sysdate,CANCELLED_BY=p_actor,
    LAST_ERROR='DIRECT_PICK_BY_LINE:'||sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID') where TASK_ID=id;
  end loop;
 end;
end;
/
