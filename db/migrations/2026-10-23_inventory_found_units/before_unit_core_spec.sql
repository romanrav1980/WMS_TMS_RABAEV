create or replace package RRL_STOCK_UNIT_CORE authid definer 
 accessible by(package RRL_TRADE_TOPUP_CMD,package RRL_STOCK_IW_RECOVERY_REC,package RRL_STOCK_STORE_RETURN_REC_CMD,package RRL_STOCK_INTERWARE_REC,package RRL_STOCK_UNLOAD_CMD,package RRL_STOCK_REPL_BIND,package RRL_STOCK_SHORT_RECOVERY,package RRL_STOCK_ELIGIBILITY,package RRL_STOCK_CASE_RETURN_CMD,package RRL_STOCK_INVENTORY_BIRTH,package RRL_STOCK_CASE_SHORT_CMD,package RRL_STOCK_RECEIPT_REVERSE,package RRL_STOCK_WAVE_LAUNCH_CMD,package RRL_STOCK_INVENTORY_CMD,package RRL_STOCK_MES_CANCEL_CMD,package RRL_STOCK_MES_SUPPLY_CMD,package RRL_STOCK_DOC_RESERVE_CMD,package RRL_STOCK_WAVE_CMD,package RRL_STOCK_MES_MOVEMENT_CORE,package RRL_STOCK_INVARIANT_CORE,package RRL_STOCK_RESERVATION_CMD,package RRL_STOCK_TRANSFER_CORE, 
 package RRL_STOCK_EFFECT_CORE,package RRL_STOCK_RECEIPT_CORE) as 
 procedure receive_partial_issued(p_old_uid varchar2,p_source_cell varchar2,p_uid varchar2,p_target_cell varchar2,p_qty number,p_units clob); 
 procedure receive_return(p_old_uid varchar2,p_source_cell varchar2,p_uid varchar2,p_target_cell varchar2,p_qty number,p_units clob); 
 procedure receive_issued(p_uid varchar2,p_source_cell varchar2,p_target_cell varchar2,p_qty number,p_units clob); 
 procedure restore_issued(p_uid varchar2,p_cell varchar2,p_new_reservation number,p_qty number,p_units clob); 
 function automatic_units(p_uid varchar2,p_cell varchar2,p_qty number) return clob; 
 procedure admit_captured(p_uid varchar2,p_cell varchar2); 
 procedure assert_composition(p_uid varchar2,p_cell varchar2); 
 procedure issue_free_units(p_uid varchar2,p_cell varchar2,p_qty number,p_units clob); 
 procedure reserve_units(p_uid varchar2,p_cell varchar2,p_id number,p_qty number,p_units clob); 
 procedure release_units(p_id number,p_qty number,p_units clob,p_issue number default 0); 
end;
/
