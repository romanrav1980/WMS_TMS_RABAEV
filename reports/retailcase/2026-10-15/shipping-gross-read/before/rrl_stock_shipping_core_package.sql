create or replace package RRL_STOCK_SHIPPING_CORE authid definer
 accessible by(package RRL_STOCK_PALLET_QC_CMD,package RRL_STOCK_POSTING_API,package RRL_STOCK_QC_GATE,package RRL_STOCK_HU_SHIP_CMD,package RRL_STOCK_LOADING_READ,package RRL_STOCK_SINGLE_LOAD_CMD) as
 procedure compile_shipment(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob,p_skip_qc boolean default false);
 procedure execute_shipment(p_request clob,p_actor varchar2,p_result out clob);
 procedure execute_resolved(p_request clob,p_domain clob,p_offset number,p_actor varchar2,p_result out clob);
end;
/
