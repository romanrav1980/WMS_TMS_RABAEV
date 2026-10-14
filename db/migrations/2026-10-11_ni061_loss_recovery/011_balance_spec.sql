create or replace package RRL_STOCK_BALANCE_CORE authid definer 
 accessible by(package RRL_STOCK_IW_RECOVERY_REC,package RRL_STOCK_UNLOAD_CMD,package RRL_STOCK_INTERWARE_REC,package RRL_STOCK_STORE_RETURN_REC_CMD,package RRL_STOCK_RECEIPT_REVERSE,package RRL_STOCK_INVENTORY_BIRTH,package RRL_STOCK_INVENTORY_CMD,package RRL_STOCK_EVENT_BRIDGE,package RRL_STOCK_MES_MOVEMENT_CORE,package RRL_STOCK_RESERVATION_CMD,package RRL_STOCK_POSTING_API,package RRL_STOCK_MOVE_CORE, 
  package RRL_STOCK_RESERVE_CORE,package RRL_STOCK_RECEIPT_CORE,package RRL_STOCK_TRANSFER_CORE,package RRL_STOCK_EFFECT_CORE) as 
 procedure apply_delta(p_uid varchar2,p_cell varchar2,p_delta_p number,p_delta_h number, 
   p_base_uom varchar2,p_uom_version number,p_expected_version number default null); 
 procedure write_move(p_uid varchar2,p_from varchar2,p_to varchar2,p_qty number,p_base_uom varchar2,p_uom_version number,p_line number,p_actor varchar2,p_event out number); 
 procedure write_leg(p_uid varchar2,p_from varchar2,p_to varchar2,p_signed_qty number,p_base_uom varchar2, 
   p_uom_version number,p_line number,p_leg number,p_type number,p_actor varchar2,p_event out number,p_outgoing_doc number default null,p_pallet_row number default null); 
end;
/
