create table RRL_TRADE_CASE_RETURN_UNIT(
 CASE_PICK_TASK_ID number not null references RRL_CASE_PICK_TASK(CASE_PICK_TASK_ID),
 PHYSICAL_UNIT_KEY varchar2(64) not null references RRL_WMS_RECEIPT_UNIT(PHYSICAL_UNIT_KEY),
 RETURN_OPERATION varchar2(100) not null references RRL_STOCK_OPERATION(OPERATION_ID),
 CREATED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_TC_RETURN_UNIT_PK primary key(CASE_PICK_TASK_ID,PHYSICAL_UNIT_KEY)
);
create or replace package RRL_TRADE_CASE_RETURN authid definer
 accessible by(package RRL_STOCK_CASE_RETURN_CMD) as
 procedure capture(p_task number,p_operation varchar2,p_actor varchar2);
end;
/
create or replace package body RRL_TRADE_CASE_RETURN as
 procedure capture(p_task number,p_operation varchar2,p_actor varchar2)is w number;n number;total number;tagged number;
 begin
  select WARE_ID into w from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=p_task;
  select count(*)into n from RRL_TRADE_SITE where WARE_ID=w;
  select count(*),count(a.PHYSICAL_UNIT_KEY)into total,tagged from RRL_CASE_CARRIER_LOT l
   join RRL_WMS_RECEIPT_UNIT u on u.CURRENT_UID=l.LOT_UID and u.STOCK_STATUS<>'ISSUED'
   left join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY where l.CASE_PICK_TASK_ID=p_task;
  if n=0 and tagged=0 then return;end if;
  if total=0 or tagged<>total then raise_application_error(-20886,'TRADE_RETURN_COMPLETE_ATTRIBUTES_REQUIRED');end if;
  if nvl(sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID'),'-')<>p_operation or
   nvl(sys_context('RRL_STOCK_WRITE_CTX','TX_ID'),'-')<>nvl(dbms_transaction.local_transaction_id(false),'?')then
   raise_application_error(-20863,'TRADE_RETURN_POSTING_CONTEXT_REQUIRED');end if;
  for unit_row in(select u.PHYSICAL_UNIT_KEY,u.CURRENT_UID,a.OWNER_ID from RRL_CASE_CARRIER_LOT l
   join RRL_WMS_RECEIPT_UNIT u on u.CURRENT_UID=l.LOT_UID and u.STOCK_STATUS<>'ISSUED'
   join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY where l.CASE_PICK_TASK_ID=p_task)loop
   RRL_STOCK_WRITE_GUARD.require_unit(unit_row.PHYSICAL_UNIT_KEY,unit_row.CURRENT_UID);
   RRL_TRADE_STOCK_GUARD.assert_owner(p_actor,w,unit_row.OWNER_ID,1);
   insert into RRL_TRADE_CASE_RETURN_UNIT(CASE_PICK_TASK_ID,PHYSICAL_UNIT_KEY,RETURN_OPERATION)
    values(p_task,unit_row.PHYSICAL_UNIT_KEY,p_operation);
  end loop;
 end;
end;
/
