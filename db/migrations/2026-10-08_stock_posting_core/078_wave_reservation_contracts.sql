create or replace package RRL_STOCK_RESERVE_CORE authid definer
 accessible by(package RRL_STOCK_WAVE_CMD,package RRL_STOCK_EFFECT_CORE,package RRL_STOCK_RESERVATION_CMD,package RRL_STOCK_POSTING_API,package RRL_STOCK_MOVE_CORE,package RRL_STOCK_TRANSFER_CORE) as
 procedure create_hard(p_id number,p_uid varchar2,p_cell varchar2,p_qty number,p_uom varchar2,p_uom_version number,
   p_doc_type varchar2,p_doc_id number,p_line_id number,p_domain varchar2,p_actor varchar2,p_details clob default null);
 procedure release_hard(p_id number,p_qty number,p_uom_version number,p_doc_type varchar2,p_doc_id number,p_actor varchar2);
 procedure consume_hard(p_id number,p_qty number,p_uom_version number,p_doc_type varchar2,p_doc_id number,p_actor varchar2);
 procedure relocate_hard(p_id number,p_new_id number,p_target_uid varchar2,p_target_cell varchar2,
   p_qty number,p_uom_version number,p_actor varchar2);
 procedure move_coverage(p_id number,p_new_id number,p_target_uid varchar2,p_target_cell varchar2,
  p_target_ware number,p_qty number,p_target_slot number,p_actor varchar2,p_result_id out number);
end;
/

create or replace package RRL_STOCK_UNIT_CORE authid definer
 accessible by(package RRL_STOCK_WAVE_CMD,package RRL_STOCK_MES_MOVEMENT_CORE,package RRL_STOCK_INVARIANT_CORE,package RRL_STOCK_RESERVATION_CMD,package RRL_STOCK_TRANSFER_CORE,
 package RRL_STOCK_EFFECT_CORE,package RRL_STOCK_RECEIPT_CORE) as
 function automatic_units(p_uid varchar2,p_cell varchar2,p_qty number) return clob;
 procedure admit_captured(p_uid varchar2,p_cell varchar2);
 procedure assert_composition(p_uid varchar2,p_cell varchar2);
 procedure issue_free_units(p_uid varchar2,p_cell varchar2,p_qty number,p_units clob);
 procedure reserve_units(p_uid varchar2,p_cell varchar2,p_id number,p_qty number,p_units clob);
 procedure release_units(p_id number,p_qty number,p_units clob,p_issue number default 0);
end;
/

create or replace package RRL_STOCK_RESERVATION_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

-- Extend existing replenishment rows. Do not recreate waves, plans, routes or warehouse tasks.
create or replace package RRL_STOCK_WAVE_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_reserve(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_reserve(p_request clob,p_actor varchar2,p_result out clob);
end;
/

-- No COMMIT/ROLLBACK or remote I/O: transaction belongs to the application command runner.
create or replace package RRL_STOCK_POSTING_API authid definer as
 procedure prepare_command(p_request clob,p_actor varchar2,p_replay out clob,p_hints clob default null);
 procedure execute_prepared(p_result out clob);
 procedure reset_connection;
end;
/
