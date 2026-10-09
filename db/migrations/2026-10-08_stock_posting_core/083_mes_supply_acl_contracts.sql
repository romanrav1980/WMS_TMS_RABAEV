create or replace package RRL_STOCK_CTX_API authid definer
 accessible by(package RRL_STOCK_MES_SUPPLY_CMD,package RRL_STOCK_DOC_RESERVE_CMD,package RRL_STOCK_BALANCE_CORE,package RRL_STOCK_RESERVE_CORE,package RRL_STOCK_RESERVATION_CMD,package RRL_STOCK_UNIT_CORE,package RRL_STOCK_TRANSFER_CORE,package RRL_STOCK_CONFIG_API,package RRL_STOCK_POSTING_API,package RRL_STOCK_OPERATION_CORE) as
 procedure open_operation(p_operation varchar2,p_mode varchar2 default 'EXPLICIT');
 procedure open_configuration(p_actor varchar2,p_permission varchar2);
 procedure begin_effect(p_kind varchar2,p_uid varchar2 default null,p_cell varchar2 default null,p_row_id number default null);
 procedure begin_staging(p_uid varchar2,p_cell varchar2);
 procedure end_effect;
 procedure clear_operation;
end;
/

create or replace package RRL_STOCK_LOCATION_CORE authid definer
 accessible by(package RRL_STOCK_MES_SUPPLY_CMD,package RRL_STOCK_MES_MOVEMENT_CORE,package RRL_STOCK_RECEIPT_CORE,package RRL_STOCK_RESERVATION_CMD,package RRL_STOCK_POSTING_API,package RRL_STOCK_MOVE_CORE,
  package RRL_STOCK_RESERVE_CORE,package RRL_STOCK_RECEIPT_CORE,package RRL_STOCK_TRANSFER_CORE,package RRL_STOCK_EFFECT_CORE) as
 procedure assert_receiving(p_cell varchar2,p_expected_warehouse number);
 procedure assert_quarantine(p_cell varchar2,p_expected_warehouse number);
 procedure assert_ordinary(p_cell varchar2,p_expected_warehouse number,p_role varchar2);
end;
/

-- Reuse existing MES demands, candidates, raw tasks and warehouse tasks.
create or replace package RRL_STOCK_MES_SUPPLY_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/
