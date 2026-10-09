create or replace package RRL_STOCK_BALANCE_CORE authid definer
 accessible by(package RRL_STOCK_MES_MOVEMENT_CORE,package RRL_STOCK_RESERVATION_CMD,package RRL_STOCK_POSTING_API,package RRL_STOCK_MOVE_CORE,
  package RRL_STOCK_RESERVE_CORE,package RRL_STOCK_RECEIPT_CORE,package RRL_STOCK_TRANSFER_CORE,package RRL_STOCK_EFFECT_CORE) as
 procedure apply_delta(p_uid varchar2,p_cell varchar2,p_delta_p number,p_delta_h number,
   p_base_uom varchar2,p_uom_version number,p_expected_version number default null);
 procedure write_move(p_uid varchar2,p_from varchar2,p_to varchar2,p_qty number,p_base_uom varchar2,p_uom_version number,p_line number,p_actor varchar2,p_event out number);
 procedure write_leg(p_uid varchar2,p_from varchar2,p_to varchar2,p_signed_qty number,p_base_uom varchar2,
   p_uom_version number,p_line number,p_leg number,p_type number,p_actor varchar2,p_event out number,p_outgoing_doc number default null,p_pallet_row number default null);
end;
/

create or replace package RRL_STOCK_EFFECT_CORE authid definer
 accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_MES_MOVEMENT_CORE,
 package RRL_STOCK_SHIPPING_CORE,package RRL_STOCK_CORRECTION_CORE) as
 procedure consume(p_uid varchar2,p_cell varchar2,p_qty number,p_uom varchar2,p_uom_version number,p_warehouse number,
  p_actor varchar2,p_line number,p_reservation number default null,p_doc_type varchar2 default null,
  p_doc_id number default null,p_units clob default null,p_outgoing_doc number default null,p_pallet_row number default null);
end;
/

create or replace package RRL_STOCK_SHIPPING_CORE authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_shipment(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_shipment(p_request clob,p_actor varchar2,p_result out clob);
end;
/

-- No COMMIT/ROLLBACK or remote I/O: transaction belongs to the application command runner.
create or replace package RRL_STOCK_POSTING_API authid definer as
 procedure prepare_command(p_request clob,p_actor varchar2,p_replay out clob,p_hints clob default null);
 procedure execute_prepared(p_result out clob);
 procedure reset_connection;
end;
/
