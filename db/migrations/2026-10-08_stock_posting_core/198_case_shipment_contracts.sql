create or replace package RRL_STOCK_SHIPPING_CORE authid definer
 accessible by(package RRL_STOCK_PALLET_QC_CMD,package RRL_STOCK_POSTING_API) as
 procedure compile_shipment(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_shipment(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_CASE_PICK_CMD authid definer
 accessible by(package RRL_STOCK_SHIPPING_CORE,package RRL_STOCK_CASE_SHORT_CMD,package RRL_STOCK_CASE_MOVE_CMD,package RRL_STOCK_POSTING_API) as
 function carrier_rows(p_task number) return clob;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/
