create or replace package RRL_STOCK_CTX_API authid definer
 accessible by(package RRL_STOCK_SETTING_API,package RRL_STOCK_MES_CANCEL_CMD,package RRL_STOCK_MES_SUPPLY_CMD,package RRL_STOCK_DOC_RESERVE_CMD,package RRL_STOCK_BALANCE_CORE,package RRL_STOCK_RESERVE_CORE,package RRL_STOCK_RESERVATION_CMD,package RRL_STOCK_UNIT_CORE,package RRL_STOCK_TRANSFER_CORE,package RRL_STOCK_CONFIG_API,package RRL_STOCK_POSTING_API,package RRL_STOCK_OPERATION_CORE) as
 procedure open_operation(p_operation varchar2,p_mode varchar2 default 'EXPLICIT');
 procedure open_configuration(p_actor varchar2,p_permission varchar2);
 procedure begin_effect(p_kind varchar2,p_uid varchar2 default null,p_cell varchar2 default null,p_row_id number default null);
 procedure begin_staging(p_uid varchar2,p_cell varchar2);
 procedure end_effect;
 procedure clear_operation;
end;
/

create or replace package RRL_STOCK_BALANCE_CORE authid definer
 accessible by(package RRL_STOCK_EVENT_BRIDGE,package RRL_STOCK_MES_MOVEMENT_CORE,package RRL_STOCK_RESERVATION_CMD,package RRL_STOCK_POSTING_API,package RRL_STOCK_MOVE_CORE,
  package RRL_STOCK_RESERVE_CORE,package RRL_STOCK_RECEIPT_CORE,package RRL_STOCK_TRANSFER_CORE,package RRL_STOCK_EFFECT_CORE) as
 procedure apply_delta(p_uid varchar2,p_cell varchar2,p_delta_p number,p_delta_h number,
   p_base_uom varchar2,p_uom_version number,p_expected_version number default null);
 procedure write_move(p_uid varchar2,p_from varchar2,p_to varchar2,p_qty number,p_base_uom varchar2,p_uom_version number,p_line number,p_actor varchar2,p_event out number);
 procedure write_leg(p_uid varchar2,p_from varchar2,p_to varchar2,p_signed_qty number,p_base_uom varchar2,
   p_uom_version number,p_line number,p_leg number,p_type number,p_actor varchar2,p_event out number,p_outgoing_doc number default null,p_pallet_row number default null);
end;
/

create or replace package RRL_STOCK_OPERATION_CORE authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure begin_operation(p_request clob,p_actor varchar2,p_operation varchar2,p_kind varchar2,p_replay out clob,p_plan clob default null);
 procedure finish_operation(p_operation varchar2,p_result clob);
end;
/

-- First bounded handler. Reserved/marked/nested/partial moves require their dedicated handlers.
create or replace package RRL_STOCK_MOVE_CORE authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure manual_whole(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_EVENT_BRIDGE authid definer
 accessible by(trigger "BIN$UX1xZvUbS6/gYw8CAAo/Yg==$0") as
 procedure after_event(p_operation varchar2,p_line number,p_leg number,p_uid varchar2,p_from varchar2,p_to varchar2,
  p_qty number,p_uom varchar2,p_uom_version number,p_type number);
end;
/

create or replace package RRL_STOCK_SETTING_API authid definer as
 procedure set_compatibility(p_value varchar2,p_reason varchar2,p_actor varchar2);
end;
/

-- No COMMIT/ROLLBACK or remote I/O: transaction belongs to the application command runner.
create or replace package RRL_STOCK_POSTING_API authid definer as
 procedure prepare_command(p_request clob,p_actor varchar2,p_replay out clob,p_hints clob default null);
 procedure execute_prepared(p_result out clob);
 procedure reset_connection;
end;
/
