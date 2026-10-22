create or replace package body RRL_STOCK_EFFECT_CORE as



 procedure consume(p_uid varchar2,p_cell varchar2,p_qty number,p_uom varchar2,p_uom_version number,p_warehouse number,



  p_actor varchar2,p_line number,p_reservation number default null,p_doc_type varchar2 default null,



  p_doc_id number default null,p_units clob default null,p_outgoing_doc number default null,p_pallet_row number default null,p_supplier_return_receipt varchar2 default null,p_disposal_receipt varchar2 default null,p_quality_case number default null) is



  v_p number;v_h number;v_ver number;v_uom varchar2(20);v_event number;



 begin



  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',p_uid));



  if(case when p_supplier_return_receipt is null then 0 else 1 end)+(case when p_disposal_receipt is null then 0 else 1 end)+(case when p_quality_case is null then 0 else 1 end)>1 then raise_application_error(-20886,'CONSUMPTION_ONE_EXPLICIT_EXCEPTION_REQUIRED');end if;
  -- C-0153: an approved quality case may consume its own quarantined pallet; the owner re-validates the in-flight write-off.
  if p_quality_case is not null then RRL_STOCK_QUALITY_WRITEOFF.validate_consume(p_quality_case,p_uid,p_cell,p_qty,p_warehouse,p_actor);RRL_STOCK_LOCATION_CORE.assert_quarantine(p_cell,p_warehouse);
  elsif p_disposal_receipt is not null then RRL_STOCK_RETURN_DISPOSE.validate_consume(p_disposal_receipt,p_uid,p_cell,p_qty,p_warehouse,p_actor);RRL_STOCK_LOCATION_CORE.assert_quarantine(p_cell,p_warehouse);
  elsif p_supplier_return_receipt is null then RRL_STOCK_LOCATION_CORE.assert_ordinary(p_cell,p_warehouse,'SOURCE');

  else RRL_STOCK_SUP_RETURN.validate_consume(p_supplier_return_receipt,p_uid,p_cell,p_qty,p_warehouse,p_actor);RRL_STOCK_LOCATION_CORE.assert_quarantine(p_cell,p_warehouse);end if;



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
