create or replace package RRL_QUARANTINE_ACCESS authid definer accessible by(package RRL_STOCK_POSTING_API)as
 procedure assert_request(p_request clob,p_actor varchar2);
end;
/
create or replace package body RRL_QUARANTINE_ACCESS as
 procedure rights(p_actor varchar2,p_ware number)is begin
  if RRL_HAS_WRIGHT(p_actor,'QUARANTINE_MOVE')<>1 and RRL_ACCESS_API.allowed(p_actor,'quarantine_move','WAREHOUSE',to_char(p_ware))<>1
   then raise_application_error(-20882,'QUARANTINE_MOVE_FORBIDDEN');end if;
  if RRL_HAS_WRIGHT(p_actor,'INTERNAL_MOVE')<>1 and RRL_HAS_WRIGHT(p_actor,'stock_posting_manual_move')<>1
   and RRL_ACCESS_API.allowed(p_actor,'internal_move','WAREHOUSE',to_char(p_ware))<>1
   and RRL_ACCESS_API.allowed(p_actor,'stock_posting_manual_move','WAREHOUSE',to_char(p_ware))<>1
   then raise_application_error(-20882,'INTERNAL_MOVE_FORBIDDEN');end if;
 end;
 procedure assert_request(p_request clob,p_actor varchar2)is d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');
  s json_object_t:=d.get_object('source');uid_value varchar2(200):=m.get_string('uid');op varchar2(100):=d.get_string('operation_id');ware number;requested number:=s.get_number('warehouse_id');n number;
 begin
  if requested is not null then rights(p_actor,requested);end if;
  -- Archived replay uses its immutable original scope, without requiring the old stock to remain physically available.
  begin select json_value(RESOLVED_PLAN_JSON,'$.domain.warehouse' returning number),json_value(RESOLVED_PLAN_JSON,'$.domain.uid')into ware,uid_value
   from RRL_STOCK_OPERATION where OPERATION_ID=op and COMMAND_TYPE='MOVE_QUARANTINE';
  exception when no_data_found then
   begin select distinct c.WARE_ID into ware from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where r.UID_POLETA=uid_value and r.REMAIN>0;
   exception when no_data_found then raise_application_error(-20886,'QUARANTINE_SOURCE_REQUIRED');when too_many_rows then raise_application_error(-20886,'QUARANTINE_WAREHOUSE_AMBIGUOUS');end;
  end;
  if ware is null or uid_value is null then raise_application_error(-20886,'QUARANTINE_SOURCE_REQUIRED');end if;
  if requested is not null and requested<>ware then raise_application_error(-20886,'QUARANTINE_WAREHOUSE_CONFLICT');end if;
  if requested is null then rights(p_actor,ware);end if;
  select count(*)into n from RRL_TRADE_SITE where WARE_ID=ware;
  if n>0 then
   for o in(select distinct a.OWNER_ID from RRL_WMS_RECEIPT_UNIT u left join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY
     where u.CURRENT_UID=uid_value or u.UID_PALLET=uid_value)loop
    if o.OWNER_ID is null then raise_application_error(-20882,'TRADE_OWNER_ACCESS_DENIED');end if;
    RRL_TRADE_STOCK_GUARD.assert_owner(p_actor,ware,o.OWNER_ID,1);
   end loop;
  end if;
 end;
end;
/
