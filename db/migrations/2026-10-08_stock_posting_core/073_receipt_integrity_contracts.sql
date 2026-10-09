create or replace package RRL_STOCK_LOCATION_CORE authid definer
 accessible by(package RRL_STOCK_MES_MOVEMENT_CORE,package RRL_STOCK_RECEIPT_CORE,package RRL_STOCK_RESERVATION_CMD,package RRL_STOCK_POSTING_API,package RRL_STOCK_MOVE_CORE,
  package RRL_STOCK_RESERVE_CORE,package RRL_STOCK_RECEIPT_CORE,package RRL_STOCK_TRANSFER_CORE,package RRL_STOCK_EFFECT_CORE) as
 procedure assert_receiving(p_cell varchar2,p_expected_warehouse number);
 procedure assert_quarantine(p_cell varchar2,p_expected_warehouse number);
 procedure assert_ordinary(p_cell varchar2,p_expected_warehouse number,p_role varchar2);
end;
/

create or replace package RRL_STOCK_TRANSFER_CORE authid definer
 accessible by(package RRL_STOCK_INTERNAL_CMD,package RRL_STOCK_POSTING_API,package RRL_STOCK_TASK_CORE,
 package RRL_STOCK_MES_MOVEMENT_CORE,package RRL_STOCK_RECEIPT_CORE,package RRL_STOCK_MOVE_CORE,package RRL_STOCK_MES_CORE) as
 procedure move(p_uid varchar2,p_target_uid varchar2,p_from varchar2,p_to varchar2,p_qty number,
  p_uom varchar2,p_uom_version number,p_warehouse number,p_actor varchar2,p_line number,
  p_reservation number default null,p_units clob default null,p_new_reservation number default null,p_target_slot number default null,p_source_warehouse number default null,p_location_mode varchar2 default 'ORDINARY');
end;
/

create or replace package RRL_STOCK_TASK_PLAN authid definer
 accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_TASK_CORE) as
 procedure compile_task(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 function signature(p_task RRL_WAREHOUSE_TASK%rowtype) return varchar2;
end;
/

create or replace package RRL_STOCK_TASK_CORE authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure execute_task(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_MES_MOVEMENT_CORE authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure execute_movements(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_INTERNAL_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_move(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_move(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_UNIT_CORE authid definer
 accessible by(package RRL_STOCK_MES_MOVEMENT_CORE,package RRL_STOCK_INVARIANT_CORE,package RRL_STOCK_RESERVATION_CMD,package RRL_STOCK_TRANSFER_CORE,
 package RRL_STOCK_EFFECT_CORE,package RRL_STOCK_RECEIPT_CORE) as
 procedure admit_captured(p_uid varchar2,p_cell varchar2);
 procedure assert_composition(p_uid varchar2,p_cell varchar2);
 procedure issue_free_units(p_uid varchar2,p_cell varchar2,p_qty number,p_units clob);
 procedure reserve_units(p_uid varchar2,p_cell varchar2,p_id number,p_qty number,p_units clob);
 procedure release_units(p_id number,p_qty number,p_units clob,p_issue number default 0);
end;
/

create or replace package RRL_STOCK_RECEIPT_PLAN authid definer
 accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_RECEIPT_CORE) as
 procedure compile_receipt(p_request clob,p_operation varchar2,p_hints clob,p_policies out clob,p_resources out clob,p_domain out clob);
end;
/

create or replace package RRL_STOCK_RECEIPT_CORE authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure execute_receipt(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_CONFIG_API authid definer as
 procedure begin_change(p_actor varchar2,p_permission varchar2);
 procedure end_change;
end;
/

create or replace package RRL_STOCK_PALLET_UOM authid definer
 accessible by(package RRL_STOCK_INTERNAL_CMD,package RRL_STOCK_TASK_PLAN,package RRL_STOCK_TASK_CORE) as
 procedure resolve_quantity(p_uid varchar2,p_input varchar2,p_quantity varchar2,
  p_base out varchar2,p_quantity_base out number,p_version out number,p_signature out varchar2);
end;
/

create or replace package RRL_STOCK_UOM_CONFIG authid definer as
 procedure publish(p_article varchar2,p_input varchar2,p_base varchar2,p_numerator number,p_denominator number,p_scale number,p_provenance varchar2);
end;
/

-- No COMMIT/ROLLBACK or remote I/O: transaction belongs to the application command runner.
create or replace package RRL_STOCK_POSTING_API authid definer as
 procedure prepare_command(p_request clob,p_actor varchar2,p_replay out clob,p_hints clob default null);
 procedure execute_prepared(p_result out clob);
 procedure reset_connection;
end;
/
