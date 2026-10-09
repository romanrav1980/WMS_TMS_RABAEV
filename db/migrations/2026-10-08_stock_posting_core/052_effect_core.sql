create or replace package RRL_STOCK_EFFECT_CORE authid definer
 accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_MES_MOVEMENT_CORE,
 package RRL_STOCK_SHIPPING_CORE,package RRL_STOCK_CORRECTION_CORE) as
 procedure consume(p_uid varchar2,p_cell varchar2,p_qty number,p_uom varchar2,p_uom_version number,p_warehouse number,
  p_actor varchar2,p_line number,p_reservation number default null,p_doc_type varchar2 default null,
  p_doc_id number default null,p_units clob default null,p_outgoing_doc number default null,p_pallet_row number default null);
end;
/
create or replace package body RRL_STOCK_EFFECT_CORE as
 procedure consume(p_uid varchar2,p_cell varchar2,p_qty number,p_uom varchar2,p_uom_version number,p_warehouse number,
  p_actor varchar2,p_line number,p_reservation number default null,p_doc_type varchar2 default null,
  p_doc_id number default null,p_units clob default null,p_outgoing_doc number default null,p_pallet_row number default null) is
  v_p number;v_h number;v_ver number;v_uom varchar2(20);v_event number;
 begin
  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',p_uid));
  RRL_STOCK_LOCATION_CORE.assert_ordinary(p_cell,p_warehouse,'SOURCE');
  select REMAIN,HARD_RESERVED_BASE,STOCK_VERSION,BASE_UOM into v_p,v_h,v_ver,v_uom
   from RRL_REMAINS where UID_POLETA=p_uid and CELL=p_cell;
  if p_qty is null or p_qty<=0 or p_qty>v_p or p_uom is null or p_uom!=v_uom then raise_application_error(-20868,'CONSUMPTION_STOCK_CONFLICT');end if;
  if p_reservation is not null then
   RRL_STOCK_UNIT_CORE.release_units(p_reservation,p_qty,p_units,1);
   RRL_STOCK_RESERVE_CORE.consume_hard(p_reservation,p_qty,p_uom_version,p_doc_type,p_doc_id,p_actor);
  else
   if p_qty>v_p-v_h then raise_application_error(-20869,'CONSUMPTION_RESERVATION_CONFLICT');end if;
   RRL_STOCK_UNIT_CORE.issue_free_units(p_uid,p_cell,p_qty,p_units);
   RRL_STOCK_BALANCE_CORE.apply_delta(p_uid,p_cell,-p_qty,0,p_uom,p_uom_version,v_ver);
  end if;
  RRL_STOCK_BALANCE_CORE.write_leg(p_uid,p_cell,null,-p_qty,p_uom,p_uom_version,p_line,1,3,p_actor,v_event,p_outgoing_doc,p_pallet_row);
 end;
end;
/
