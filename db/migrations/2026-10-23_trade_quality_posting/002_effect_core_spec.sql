create or replace package RRL_STOCK_EFFECT_CORE authid definer



 accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_MES_MOVEMENT_CORE,



 package RRL_STOCK_SHIPPING_CORE,package RRL_STOCK_CORRECTION_CORE,package RRL_STOCK_RETURN_DISPOSE,package RRL_STOCK_QUALITY_WRITEOFF) as



 procedure consume(p_uid varchar2,p_cell varchar2,p_qty number,p_uom varchar2,p_uom_version number,p_warehouse number,



  p_actor varchar2,p_line number,p_reservation number default null,p_doc_type varchar2 default null,



  p_doc_id number default null,p_units clob default null,p_outgoing_doc number default null,p_pallet_row number default null,p_supplier_return_receipt varchar2 default null,p_disposal_receipt varchar2 default null,p_quality_case number default null);



end;
/
