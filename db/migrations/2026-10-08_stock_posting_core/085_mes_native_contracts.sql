create or replace package RRL_MES_RAW_SUPPLY_OLD authid definer
 accessible by(package RRL_MES_RAW_SUPPLY_API) as
 function release_to_production(p_production_order_id number,p_to_ware_id number default null,p_to_cell varchar2 default 'MES_PROD',p_allow_partial number default 0,p_created_by varchar2 default null) return number;
end;
/

create or replace package RRL_MES_RAW_SUPPLY_API authid definer as
 function release_to_production(p_production_order_id number,p_to_ware_id number default null,
  p_to_cell varchar2 default 'MES_PROD',p_allow_partial number default 0,p_created_by varchar2 default null,p_operation_id varchar2 default null) return number;
end;
/
