create or replace package RRL_STOCK_LOCK_API authid definer as
 function resource_lock_id(p_rank number,p_key raw) return number;
 function resource_key(p_kind varchar2,p_a varchar2,p_b varchar2 default null,p_c varchar2 default null) return raw;
 procedure begin_plan;
 procedure acquire_policies(p_plan clob);
 procedure acquire_resources(p_plan clob);
 procedure assert_held(p_rank number,p_key raw);
 procedure assert_policy(p_key raw,p_mode number);
 procedure clear_plan;
end;
/

create or replace package RRL_STOCK_BALANCE_CORE authid definer
 accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_MOVE_CORE,
  package RRL_STOCK_RESERVE_CORE,package RRL_STOCK_RECEIPT_CORE,package RRL_STOCK_TRANSFER_CORE,package RRL_STOCK_EFFECT_CORE) as
 procedure apply_delta(p_uid varchar2,p_cell varchar2,p_delta_p number,p_delta_h number,
   p_base_uom varchar2,p_uom_version number,p_expected_version number default null);
 procedure write_leg(p_uid varchar2,p_from varchar2,p_to varchar2,p_signed_qty number,p_base_uom varchar2,
   p_uom_version number,p_line number,p_leg number,p_type number,p_actor varchar2,p_event out number);
end;
/

create or replace package RRL_STOCK_RESERVE_CORE authid definer
 accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_MOVE_CORE,package RRL_STOCK_TRANSFER_CORE) as
 procedure create_hard(p_id number,p_uid varchar2,p_cell varchar2,p_qty number,p_uom varchar2,p_uom_version number,
   p_doc_type varchar2,p_doc_id number,p_line_id number,p_domain varchar2,p_actor varchar2);
 procedure release_hard(p_id number,p_qty number,p_uom_version number,p_doc_type varchar2,p_doc_id number,p_actor varchar2);
 procedure consume_hard(p_id number,p_qty number,p_uom_version number,p_doc_type varchar2,p_doc_id number,p_actor varchar2);
 procedure relocate_hard(p_id number,p_new_id number,p_target_uid varchar2,p_target_cell varchar2,
   p_qty number,p_uom_version number,p_actor varchar2);
 procedure move_coverage(p_id number,p_new_id number,p_target_uid varchar2,p_target_cell varchar2,
  p_target_ware number,p_qty number,p_target_slot number,p_actor varchar2,p_result_id out number);
end;
/

create or replace package RRL_STOCK_LOCATION_CORE authid definer
 accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_MOVE_CORE,
  package RRL_STOCK_RESERVE_CORE,package RRL_STOCK_RECEIPT_CORE,package RRL_STOCK_TRANSFER_CORE,package RRL_STOCK_EFFECT_CORE) as
 procedure assert_ordinary(p_cell varchar2,p_expected_warehouse number,p_role varchar2);
end;
/

create or replace package RRL_STOCK_PLAN_HELPER authid definer as
 procedure fence(p_plan in out nocopy json_array_t,p_kind varchar2,p_id varchar2,p_mode number default 4);
 procedure anchor(p_plan in out nocopy json_array_t,p_rank number,p_kind varchar2,p_a varchar2,p_b varchar2 default null);
 procedure row_key(p_plan in out nocopy json_array_t,p_table varchar2,p_id varchar2);
 procedure stock_closure(p_policies in out nocopy json_array_t,p_resources in out nocopy json_array_t,
  p_uid varchar2,p_article varchar2,p_from varchar2,p_to varchar2);
 function decimal_text(p_value number) return varchar2;
end;
/

create or replace package RRL_STOCK_TRANSFER_CORE authid definer
 accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_TASK_CORE,
 package RRL_STOCK_RECEIPT_CORE,package RRL_STOCK_MOVE_CORE,package RRL_STOCK_MES_CORE) as
 procedure move(p_uid varchar2,p_target_uid varchar2,p_from varchar2,p_to varchar2,p_qty number,
  p_uom varchar2,p_uom_version number,p_warehouse number,p_actor varchar2,p_line number,
  p_reservation number default null,p_units clob default null,p_new_reservation number default null,p_target_slot number default null);
end;
/

create or replace package RRL_STOCK_TASK_PLAN authid definer
 accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_TASK_CORE) as
 procedure compile_task(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 function signature(p_task RRL_WAREHOUSE_TASK%rowtype) return varchar2;
end;
/

create or replace package RRL_STOCK_MES_CORE authid definer
 accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_TASK_CORE,package RRL_STOCK_TASK_DOMAIN) as
 procedure sync_warehouse_fact(p_task RRL_WAREHOUSE_TASK%rowtype,p_qty number,p_target_uid varchar2,p_residual number,p_actor varchar2);
end;
/

create or replace package RRL_STOCK_TASK_DOMAIN authid definer
 accessible by(package RRL_STOCK_TASK_CORE) as
 procedure sync_fact(p_task RRL_WAREHOUSE_TASK%rowtype,p_qty number,p_target_uid varchar2,p_residual number,p_actor varchar2);
end;
/

create or replace package RRL_STOCK_TASK_CORE authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure execute_task(p_request clob,p_actor varchar2,p_result out clob);
end;
/

-- No COMMIT/ROLLBACK or remote I/O: transaction belongs to the application command runner.
create or replace package RRL_STOCK_POSTING_API authid definer as
 procedure prepare_command(p_request clob,p_actor varchar2,p_replay out clob);
 procedure execute_prepared(p_result out clob);
 procedure reset_connection;
end;
/
