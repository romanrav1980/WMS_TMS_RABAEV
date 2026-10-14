create or replace package RRL_SCALE_PACKET_READ authid definer as
 function utc_stamp(p_text varchar2)return timestamp with time zone;
 function validate_json(p_source clob,p_capacity number,p_resolution number,
  p_expected_basis varchar2 default 'GROSS',p_sample_field varchar2 default 'gross_weight_kg')return clob;
end;
/

create or replace package RRL_WEIGHT_BOX_CAPACITY authid definer as
 function enabled(p_article varchar2)return number;
 function kg_volume_upper_bound(p_cell varchar2,p_article varchar2)return number;
 function physical_volume(p_uid varchar2,p_cell varchar2,p_quantity number,p_exact number default 1)return number;
 function reservation_volume(p_reservation number,p_quantity number)return number;
end;
/

create or replace package RRL_CASE_WEIGHT_SCAN authid definer as
 procedure assert_scan(p_request clob,p_article varchar2,p_line number,p_previous number);
end;
/

create or replace package RRL_STOCK_ELIGIBILITY authid definer as
 function reason(p_uid varchar2,p_cell varchar2,p_warehouse number,p_quantity number default 0,
  p_min_days number default null,p_min_percent number default null,p_purpose varchar2 default 'ALLOCATE',
  p_owner_reservation number default null,p_article varchar2 default null) return varchar2;
 procedure assert_source(p_uid varchar2,p_cell varchar2,p_warehouse number,p_quantity number,
  p_min_days number default null,p_min_percent number default null,p_purpose varchar2 default 'ALLOCATE',
  p_owner_reservation number default null,p_article varchar2 default null);
end;
/

create or replace package RRL_STOCK_MATH authid definer as
 function quantity(p_text varchar2,p_scale number default 9) return number;
 function convert_exact(p_text varchar2,p_numerator number,p_denominator number,p_scale number) return number;
 procedure assert_base(p_value number,p_scale number);
end;
/

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

create or replace package RRL_STOCK_EFFECT_CORE authid definer



 accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_MES_MOVEMENT_CORE,



 package RRL_STOCK_SHIPPING_CORE,package RRL_STOCK_CORRECTION_CORE,package RRL_STOCK_RETURN_DISPOSE) as



 procedure consume(p_uid varchar2,p_cell varchar2,p_qty number,p_uom varchar2,p_uom_version number,p_warehouse number,



  p_actor varchar2,p_line number,p_reservation number default null,p_doc_type varchar2 default null,



  p_doc_id number default null,p_units clob default null,p_outgoing_doc number default null,p_pallet_row number default null,p_supplier_return_receipt varchar2 default null,p_disposal_receipt varchar2 default null);



end;
/

create or replace package RRL_STOCK_OPERATION_CORE authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure begin_operation(p_request clob,p_actor varchar2,p_operation varchar2,p_kind varchar2,p_replay out clob,p_plan clob default null);
 procedure finish_operation(p_operation varchar2,p_result clob);
end;
/

create or replace package RRL_STOCK_RESERVE_CORE authid definer
 accessible by(package RRL_STOCK_UNLOAD_CMD,package RRL_STOCK_REPL_BIND,package RRL_STOCK_SHORT_RECOVERY,package RRL_STOCK_CASE_RETURN_CMD,package RRL_STOCK_CASE_SHORT_CMD,package RRL_STOCK_WAVE_LAUNCH_CMD,package RRL_STOCK_MES_CANCEL_CMD,package RRL_STOCK_MES_SUPPLY_CMD,package RRL_STOCK_DOC_RESERVE_CMD,package RRL_STOCK_WAVE_CMD,package RRL_STOCK_EFFECT_CORE,package RRL_STOCK_RESERVATION_CMD,package RRL_STOCK_POSTING_API,package RRL_STOCK_MOVE_CORE,package RRL_STOCK_TRANSFER_CORE,package RRL_STOCK_HU_UNPACK_CMD,package RRL_STOCK_HU_SLOT_MOVE_CMD,package RRL_STOCK_HU_REPACK_CMD) as
 procedure restore_consumed(p_id number,p_new_id number,p_qty number,p_uom_version number,p_actor varchar2);
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

create or replace package RRL_STOCK_LOCATION_CORE authid definer 
 accessible by(package RRL_STOCK_IW_RECOVERY_REC,package RRL_STOCK_INTERWARE_REC,package RRL_STOCK_STORE_RETURN_REC_CMD,package RRL_STOCK_RECEIPT_REVERSE,package RRL_STOCK_INVENTORY_BIRTH,package RRL_STOCK_WAVE_LAUNCH_CMD,package RRL_STOCK_INVENTORY_CMD,package RRL_STOCK_MES_SUPPLY_CMD,package RRL_STOCK_MES_MOVEMENT_CORE,package RRL_STOCK_RECEIPT_CORE,package RRL_STOCK_RESERVATION_CMD,package RRL_STOCK_POSTING_API,package RRL_STOCK_MOVE_CORE, 
  package RRL_STOCK_RESERVE_CORE,package RRL_STOCK_RECEIPT_CORE,package RRL_STOCK_TRANSFER_CORE,package RRL_STOCK_EFFECT_CORE) as 
 procedure assert_receiving(p_cell varchar2,p_expected_warehouse number); 
 procedure assert_quarantine(p_cell varchar2,p_expected_warehouse number); 
 procedure assert_ordinary(p_cell varchar2,p_expected_warehouse number,p_role varchar2); 
end;
/

-- Private compiler: derives all anchors from a typed command, never from caller-supplied lock lists.
create or replace package RRL_STOCK_COMMAND_PLAN authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_move(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob);
end;
/

-- First bounded handler. Reserved/marked/nested/partial moves require their dedicated handlers.
create or replace package RRL_STOCK_MOVE_CORE authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure manual_whole(p_request clob,p_actor varchar2,p_result out clob);
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

create or replace package RRL_STOCK_WAVE_READY authid definer as
 function snapshot_json(p_wave number) return clob;
 procedure assert_released(p_wave number);
end;
/

create or replace package RRL_STOCK_TRANSFER_CORE authid definer
 accessible by(package RRL_STOCK_HU_CMD,package RRL_STOCK_CASE_RETURN_CMD,package RRL_STOCK_CASE_MOVE_CMD,package RRL_STOCK_CASE_PICK_CMD,package RRL_STOCK_INTERNAL_CMD,package RRL_STOCK_POSTING_API,package RRL_STOCK_TASK_CORE,
 package RRL_STOCK_MES_MOVEMENT_CORE,package RRL_STOCK_RECEIPT_CORE,package RRL_STOCK_MOVE_CORE,package RRL_STOCK_MES_CORE) as
 procedure move(p_uid varchar2,p_target_uid varchar2,p_from varchar2,p_to varchar2,p_qty number,
  p_uom varchar2,p_uom_version number,p_warehouse number,p_actor varchar2,p_line number,
  p_reservation number default null,p_units clob default null,p_new_reservation number default null,p_target_slot number default null,p_source_warehouse number default null,p_location_mode varchar2 default 'ORDINARY');
end;
/

-- MIGRATION_ID: 2026-10-10-165-case-current-warehouse
create or replace package RRL_CASE_TASK_ACCESS authid definer as
 procedure assert_scope(p_task number,p_actor varchar2,p_permission varchar2,p_assignee varchar2 default null);
 procedure assert_command(p_request clob,p_actor varchar2);
end;
/

create or replace package RRL_CASE_RESOURCE_POLICY authid definer as
 function context_json(p_task number,p_action varchar2,p_actor varchar2,p_resource number default null,p_session number default null,p_equipment number default null) return clob;
end;
/

create or replace package RRL_WAREHOUSE_TASK_ACCESS authid definer as
 procedure assert_scope(p_task number,p_actor varchar2,p_assignee varchar2 default null);
 procedure assert_completion(p_request clob,p_actor varchar2);
end;
/

-- Read-only authoritative resource/assignment policy shared by task metadata and posting.
create or replace package RRL_TASK_RESOURCE_POLICY authid definer as
 function context_json(p_task number,p_action varchar2,p_actor varchar2,p_assignee varchar2,
  p_resource number default null,p_session number default null,p_equipment number default null) return clob;
end;
/

-- Recovery is metadata around existing stock commands, never a second quantity executor.
create or replace package RRL_STOCK_SHORT_RECOVERY authid definer
 accessible by(package RRL_STOCK_CASE_SHORT_CMD,package RRL_STOCK_INVENTORY_CMD,
 package RRL_STOCK_TASK_PLAN,package RRL_STOCK_TASK_DOMAIN,package RRL_STOCK_CASE_PICK_CMD) as
 procedure plan_inventory(p_request clob,p_resources in out nocopy json_array_t,p_policies in out nocopy json_array_t,p_domain in out nocopy json_object_t);
 procedure finish_inventory(p_request clob,p_actor varchar2,p_domain json_object_t,p_facts json_array_t,p_result in out nocopy json_object_t);
 procedure plan_replenishment(p_repl number,p_resources in out nocopy json_array_t);
 procedure finish_replenishment(p_task RRL_WAREHOUSE_TASK%rowtype,p_actor varchar2);
 procedure plan_ready(p_request clob,p_policies in out nocopy json_array_t,p_resources in out nocopy json_array_t,p_domain in out nocopy json_object_t);
 procedure execute_ready(p_request clob,p_actor varchar2,p_result out clob);
 procedure plan_pick(p_line number,p_resources in out nocopy json_array_t);
 procedure finish_pick(p_line number,p_actor varchar2);
 procedure plan_pick(p_line number,p_resources in out nocopy json_array_t,p_domain in out nocopy json_object_t);
 procedure finish_pick(p_line number,p_actor varchar2,p_domain json_object_t);
end;
/

create or replace package RRL_STOCK_TASK_SCAN authid definer as
 function profile_signature(p_article varchar2) return varchar2;
 procedure assert_draft(p_request clob,p_task number,p_uid varchar2,p_cell varchar2,p_actor varchar2);
end;
/

create or replace package RRL_PICK_RANGE_POLICY authid definer as
 function target_write_allowed(p_cell varchar2,p_article varchar2,p_repl number,p_quantity number)return number;
 function new_target_allowed(p_cell varchar2,p_article varchar2,p_exclude_repl number default null)return number;
end;
/

create or replace package RRL_STOCK_REPL_CAPACITY authid definer as
 function unit_volume(p_cell varchar2,p_article varchar2) return number;
 function remaining_base_quantity(p_cell varchar2,p_article varchar2,p_exclude_repl number default null) return number;
 procedure assert_arrival(p_repl number,p_base_quantity number);
end;
/

-- Count only usable coverage at the actual picking target, never storage or packed carrier stock.
create or replace package RRL_STOCK_REPL_NEED authid definer as
 function target_coverage(p_pick number,p_cell varchar2,p_exclude number default null) return number;
 function remaining_for_task(p_pick number,p_cell varchar2) return number;
end;
/

-- Bind delivered generic replenishment to existing CASE consumers; no second stock writer.
create or replace package RRL_STOCK_REPL_BIND authid definer
 accessible by(package RRL_STOCK_TASK_PLAN,package RRL_STOCK_TASK_CORE) as
 procedure plan_bind(p_task RRL_WAREHOUSE_TASK%rowtype,p_qty number,p_anchors in out nocopy json_array_t,p_plan out json_object_t);
 procedure execute_bind(p_task RRL_WAREHOUSE_TASK%rowtype,p_uid varchar2,p_reservation number,p_plan json_object_t,p_actor varchar2);
end;
/

create or replace package RRL_STOCK_REPL_ADMISSION authid definer as

 function lot_key(p_uid varchar2) return varchar2;
 function reason(p_uid varchar2,p_target varchar2,p_ware number,p_article varchar2) return varchar2;

 function mode_for(p_task number) return varchar2;

 function policy_signature(p_task number) return varchar2;

 procedure assert_target(p_uid varchar2,p_target varchar2,p_ware number,p_article varchar2);

end;
/

create or replace package RRL_STOCK_REPL_CONTINUATION authid definer
 accessible by(package RRL_STOCK_TASK_PLAN,package RRL_STOCK_TASK_CORE) as
 procedure plan_next(p_task RRL_WAREHOUSE_TASK%rowtype,p_qty number,p_residual number,p_rows in out nocopy json_array_t,p_domain in out nocopy json_object_t);
 procedure create_next(p_task RRL_WAREHOUSE_TASK%rowtype,p_domain json_object_t,p_actor varchar2);
end;
/

create or replace package RRL_STOCK_TASK_PLAN authid definer
 accessible by(package RRL_STOCK_HU_TASK,package RRL_STOCK_POSTING_API,package RRL_STOCK_TASK_CORE) as
 procedure compile_task(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 function signature(p_task RRL_WAREHOUSE_TASK%rowtype) return varchar2;
end;
/

create or replace package RRL_STOCK_TASK_CORE authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure execute_task(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_TASK_DOMAIN authid definer
 accessible by(package RRL_STOCK_TASK_CORE) as
 procedure sync_fact(p_task RRL_WAREHOUSE_TASK%rowtype,p_qty number,p_target_uid varchar2,p_residual number,p_actor varchar2);
end;
/

create or replace package RRL_STOCK_MES_CORE authid definer
 accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_TASK_CORE,package RRL_STOCK_TASK_DOMAIN) as
 procedure sync_warehouse_fact(p_task RRL_WAREHOUSE_TASK%rowtype,p_qty number,p_target_uid varchar2,p_residual number,p_actor varchar2);
end;
/

create or replace package RRL_STOCK_RESERVATION_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
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

create or replace package RRL_STOCK_INVARIANT_CORE authid definer
 accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_COMPOSITION_CORE) as
 function stock_uid(p_key raw) return varchar2;
 function snapshot_stock(p_resources clob) return clob;
 procedure verify_posting(p_resources clob,p_before clob,p_operation varchar2);
end;
/

create or replace package RRL_STOCK_SHIPPING_CORE authid definer
 accessible by(package RRL_STOCK_PALLET_QC_CMD,package RRL_STOCK_POSTING_API,package RRL_STOCK_QC_GATE,package RRL_STOCK_HU_SHIP_CMD,package RRL_STOCK_LOADING_READ,package RRL_STOCK_SINGLE_LOAD_CMD) as
 procedure compile_shipment(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob,p_skip_qc boolean default false);
 procedure execute_shipment(p_request clob,p_actor varchar2,p_result out clob);
 procedure execute_resolved(p_request clob,p_domain clob,p_offset number,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_MES_MOVEMENT_PLAN authid definer
 accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_MES_MOVEMENT_CORE) as
 function signature(p_m RRL_MES_MOVEMENT%rowtype) return varchar2;
 procedure compile_movements(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
end;
/

create or replace package RRL_STOCK_MES_MOVEMENT_CORE authid definer

 accessible by(package RRL_STOCK_POSTING_API) as

 procedure execute_movements(p_request clob,p_actor varchar2,p_result out clob);

end;
/

-- Dormant in PREPARED. Enforcement begins with the one global release switch.
create or replace package RRL_STOCK_WRITE_GUARD authid definer as
 function enforcement_required return boolean;
 procedure require_effect(p_kind varchar2,p_uid varchar2 default null,p_cell varchar2 default null,p_row_id number default null);
 procedure require_unit(p_key varchar2,p_uid varchar2);
end;
/

create or replace package RRL_STOCK_PALLET_UOM authid definer
 accessible by(package RRL_STOCK_INVENTORY_CMD,package RRL_STOCK_INTERNAL_CMD,package RRL_STOCK_TASK_PLAN,package RRL_STOCK_TASK_CORE) as
 procedure resolve_quantity(p_uid varchar2,p_input varchar2,p_quantity varchar2,
  p_base out varchar2,p_quantity_base out number,p_version out number,p_signature out varchar2);
end;
/

-- Own one whole-command transaction. Never retry an uncertain commit on this connection.
create or replace package RRL_STOCK_NATIVE_API authid definer as
 procedure post(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_INTERNAL_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_move(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_move(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_FULFILLMENT_FACT authid definer
 accessible by(package RRL_STOCK_UNLOAD_CMD,package RRL_STOCK_SHIPPING_CORE) as
 procedure project_ship(p_shipment number,p_identifier varchar2,p_order number,p_operation varchar2,p_facts clob,p_actor varchar2);
 procedure project_unload(p_shipment number,p_load varchar2,p_case number,p_actor varchar2);
 procedure project_unload_pallet(p_shipment number,p_load varchar2,p_uid varchar2,p_actor varchar2);
end;
/

create or replace package RRL_STOCK_QC_WEIGHT authid definer as
 procedure calculate(p_domain clob,p_expected out number,p_tolerance out number);
end;
/

-- Warehouse unit registry is reused; multiple profiles never multiply physical quantity.
create or replace package RRL_STOCK_QC_MARK authid definer as
 function required_for_article(p_article varchar2) return number;
 function required_for_plan(p_domain clob) return number;
 procedure validate_scan(p_domain clob,p_metadata clob,p_unit_count out number);
end;
/

create or replace package RRL_STOCK_QC_ITEM authid definer as
 procedure resolve_barcode(p_code varchar2,p_article out varchar2,p_input_uom out varchar2);
 procedure validate_scan(p_domain clob,p_metadata clob);
end;
/

create or replace package RRL_STOCK_QC_POLICY authid definer as
 procedure settings(p_warehouse number,p_mode out varchar2,p_independent out number);
 procedure settings_for_plan(p_domain clob,p_mode out varchar2,p_independent out number);
 function controller_allowed(p_domain clob,p_actor varchar2) return number;
 procedure assert_controller(p_domain clob,p_actor varchar2);
 procedure sampling(p_domain clob,p_bucket out number,p_percent out number,p_selected out number,p_rescan out number);
 function full_scan_required(p_domain clob) return number;
 procedure assign_sampling(p_domain clob);
end;
/

create or replace package RRL_STOCK_QC_GATE authid definer as
 function signature_version_for_plan(p_domain clob)return number;
 function signature_for_plan(p_domain clob) return varchar2;
 procedure assert_approved(p_domain clob);
 function status_json(p_identifier varchar2) return clob;
end;
/

create or replace package RRL_STOCK_UOM_CONFIG authid definer as
 procedure publish(p_article varchar2,p_input varchar2,p_base varchar2,p_numerator number,p_denominator number,p_scale number,p_provenance varchar2);
end;
/

-- Shared physical movement preserves every owner. It never consumes another customer's goods.
create or replace package RRL_STOCK_REPL_SHARED authid definer as
 function allowed(p_uid varchar2,p_cell varchar2,p_target varchar2,p_ware number,p_owner number) return number;
end;
/

create or replace package RRL_WEIGHT_CHOICE_UNIT_READ authid definer
 accessible by(package RRL_STOCK_WAVE_LAUNCH_CMD,package RRL_STOCK_WAVE_CMD) as
 function selected_units(p_task number,p_uid varchar2,p_cell varchar2,p_qty number)return clob;
end;
/

create or replace package RRL_STOCK_WAVE_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_reserve(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_reserve(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_DOC_RESERVE_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_release(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_release(p_request clob,p_actor varchar2,p_result out clob);
end;
/

-- Reuse existing MES demands, candidates, raw tasks and warehouse tasks.
create or replace package RRL_STOCK_MES_SUPPLY_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_MES_CANCEL_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
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

create or replace package RRL_MES_PRODUCTION_API as

  function create_order(

    p_order_no           varchar2,

    p_bom_id             number default null,

    p_target_articul     varchar2,

    p_planned_qty        number,

    p_unit_code          varchar2 default 'KG',

    p_ware_id            number default null,

    p_production_line    varchar2 default null,

    p_shift_id           varchar2 default null,

    p_planned_start_at   date default null,

    p_planned_finish_at  date default null,

    p_source_system      varchar2 default null,

    p_source_message_id  varchar2 default null,

    p_idempotency_key    varchar2 default null,

    p_comment_text       varchar2 default null,

    p_created_by         varchar2 default null

  ) return number;



  function issue_raw_to_production(

    p_production_order_id number,

    p_uid_pallet          varchar2 default null,

    p_raw_batch_id        number default null,

    p_raw_articul         varchar2 default null,

    p_quantity            number,

    p_unit_code           varchar2 default 'KG',

    p_source_location     varchar2 default null,

    p_production_location varchar2 default 'MES_PRODUCTION',

    p_created_by          varchar2 default null

  ) return number;



  function complete_order(

    p_production_order_id number,

    p_prod_batch_no       varchar2 default null,

    p_fact_qty            number,

    p_unit_code           varchar2 default 'KG',

    p_pallets_json        clob default null,

    p_idempotency_key     varchar2 default null,

    p_created_by          varchar2 default null

  ) return number;



  procedure apply_mes_movements_to_wms(

    p_production_order_id number,

    p_applied_by          varchar2 default null

  );



  procedure retry_mes_movement(

    p_movement_id number,

    p_updated_by  varchar2 default null

  );

end RRL_MES_PRODUCTION_API;
/

create or replace package RRL_STOCK_INVENTORY_CMD authid definer

 accessible by(package RRL_STOCK_POSTING_API) as

 procedure compile_count(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);

 procedure execute_count(p_request clob,p_actor varchar2,p_result out clob);

end;
/

create or replace package RRL_PICK_WAVE_META authid definer accessible by(package RRL_STOCK_DOC_RESERVE_CMD,package RRL_STOCK_WAVE_LAUNCH_CMD,package RRL_PICK_WAVE_API) as
  function create_wave(
    p_wave_code         varchar2 default null,
    p_wave_name         varchar2 default null,
    p_ware_id           number default null,
    p_route_id          number default null,
    p_dock_id           number default null,
    p_planned_start_at  date default null,
    p_planned_finish_at date default null,
    p_max_customers     number default 30,
    p_created_by        varchar2 default null
  ) return number;

  procedure add_plan(
    p_pick_wave_id number,
    p_pick_plan_id number,
    p_created_by   varchar2 default null
  );

  procedure preview_wave(
    p_pick_wave_id number,
    p_updated_by   varchar2 default null
  );

  procedure launch_wave(
    p_pick_wave_id number,
    p_launched_by  varchar2 default null
  );

  procedure release_reservations(
    p_pick_wave_id number,
    p_updated_by   varchar2 default null
  );

  procedure cancel_wave(
    p_pick_wave_id number,
    p_reason       varchar2 default null,
    p_updated_by   varchar2 default null
  );
end RRL_PICK_WAVE_META;
/

create or replace package RRL_DIRECT_RECEIVING_PICK authid definer
 accessible by(package RRL_PICKING_API,package RRL_STOCK_WAVE_LAUNCH_CMD) as
 function enabled(p_uid varchar2,p_cell varchar2,p_ware number,p_article varchar2)return number;
 procedure compile_holds(p_wave number,p_resources in out nocopy json_array_t,p_holds out clob);
 procedure apply_holds(p_holds clob,p_actor varchar2);
end;
/

create or replace package RRL_STOCK_WAVE_LAUNCH_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_PICK_WAVE_API as
  function create_wave(
    p_wave_code         varchar2 default null,
    p_wave_name         varchar2 default null,
    p_ware_id           number default null,
    p_route_id          number default null,
    p_dock_id           number default null,
    p_planned_start_at  date default null,
    p_planned_finish_at date default null,
    p_max_customers     number default 30,
    p_created_by        varchar2 default null
  ) return number;

  procedure add_plan(
    p_pick_wave_id number,
    p_pick_plan_id number,
    p_created_by   varchar2 default null
  );

  procedure preview_wave(
    p_pick_wave_id number,
    p_updated_by   varchar2 default null
  );

  procedure launch_wave(
    p_pick_wave_id number,
    p_launched_by  varchar2 default null
  ,
    p_operation_id varchar2 default null
  );

  procedure release_reservations(
    p_pick_wave_id number,
    p_updated_by   varchar2 default null
  ,
    p_operation_id varchar2 default null
  );

  procedure cancel_wave(
    p_pick_wave_id number,
    p_reason       varchar2 default null,
    p_updated_by   varchar2 default null
  ,
    p_operation_id varchar2 default null
  );
end RRL_PICK_WAVE_API;
/

create or replace package RRL_PICKING_API as
  function create_plan(
    p_customer_order_id number,
    p_plan_strategy     varchar2 default 'FEFO',
    p_created_by        varchar2 default null
  ) return number;

  procedure cancel_plan(
    p_pick_plan_id number,
    p_updated_by   varchar2 default null
  );
end RRL_PICKING_API;
/

-- Snapshot only planned keys in set SQL; outbox retains only changed unit/reservation rows.
create or replace package RRL_STOCK_CHANGE_AUDIT authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 function snapshot(p_resources clob) return clob;
 function differences(p_before clob,p_after clob) return clob;
end;
/

create or replace package RRL_STOCK_INVENTORY_BIRTH authid definer

 accessible by(package RRL_STOCK_POSTING_API) as

 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);

 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);

end;
/

-- Reverse physical receipt without deleting history or guessing consumed stock.
create or replace package RRL_STOCK_RECEIPT_REVERSE authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_INV_ENTRY authid definer
 accessible by(function RRL_REVIZION_CELL,function RRL_REVIZION_CELL_KOR,function RRL_INV_CREATE_LINE2,function RRL_INV_CREATE_LINE3,function RRL_INV_CREATE_LINE4) as
 function register_line(p_cell varchar2,p_barcode varchar2,p_article_part varchar2,p_qty number,p_document number,
  p_expiry date,p_actor varchar2,p_operation varchar2) return varchar2;
 function count_lot(p_cell varchar2,p_uid varchar2,p_quantity varchar2,p_unit varchar2,p_document number,
  p_actor varchar2,p_operation varchar2,p_reason varchar2) return varchar2;
end;
/

create or replace package RRL_STOCK_METADATA_TX authid definer as

 procedure begin_change(p_actor varchar2,p_permission varchar2);

 procedure end_change;

end;
/

create or replace package RRL_STOCK_REVISION_ENTRY authid definer
 accessible by(package REVIZION) as
 function count_row(p_article varchar2,p_cell varchar2,p_quantity number,p_unit varchar2,p_row number,p_actor varchar2,p_operation varchar2) return varchar2;
 function count_document(p_cell varchar2,p_document number,p_quantity number,p_unit varchar2,p_actor varchar2,p_operation varchar2) return varchar2;
 function birth_legacy(p_facts clob,p_actor varchar2,p_operation varchar2) return varchar2;
end;
/

create or replace package RRL_SSCC_ALLOCATOR authid definer as
 procedure assert_scope(p_ware number,p_actor varchar2,p_permission varchar2);
 function allocate(p_ware number,p_actor varchar2,p_permission varchar2) return varchar2;
end;
/

create or replace package RRL_CASE_SSCC_API authid definer as
 procedure issue(p_task number,p_request clob,p_actor varchar2,p_result out clob);
 procedure confirm_label(p_task number,p_sscc varchar2,p_actor varchar2,p_result out clob);
 procedure assert_ready(p_task number);
end;
/

create or replace package RRL_STOCK_CASE_PICK_CMD authid definer
 accessible by(package RRL_STOCK_CASE_RETURN_CMD,package RRL_STOCK_SHIPPING_CORE,package RRL_STOCK_CASE_SHORT_CMD,package RRL_STOCK_CASE_MOVE_CMD,package RRL_STOCK_POSTING_API) as
 function carrier_rows(p_task number) return clob;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_CASE_MOVE_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_ORDER_WEIGHT_READ authid definer as
 function snapshot_json(p_task number,p_line number,p_actor varchar2)return clob;
end;
/

create or replace package RRL_CASE_WEIGHT_DECISION authid definer as
 function current_json(p_request clob,p_task number,p_line number,p_actor varchar2)return clob;
 procedure plan_order(p_order number,p_article varchar2,p_resources in out json_array_t);
end;
/

create or replace package RRL_STOCK_CASE_SHORT_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

-- Projection onto the existing CASE lifecycle; no stock quantities or composition version are changed.
create or replace package RRL_STOCK_QC_CASE authid definer accessible by(package RRL_STOCK_PALLET_QC_CMD,package RRL_STOCK_SHIPPING_CORE) as
 procedure project(p_domain clob,p_ready number,p_failed number,p_is_plan number,p_actor varchar2,p_operation varchar2,p_reason varchar2);
 function nested(p_domain clob) return number;
end;
/

create or replace package RRL_WH_FINAL_SCALE_ADMISSION authid definer accessible by(package RRL_STOCK_PALLET_QC_CMD,package RRL_STOCK_QC_GATE,package RRL_STOCK_HU_CMD,package RRL_STOCK_HU_READ,package RRL_STOCK_LOAD_BOX_CORE) as
 procedure assert_capture(p_request clob,p_domain clob);
 procedure claim_capture(p_request clob,p_domain clob,p_operation varchar2);
 function approved(p_domain clob,p_operation varchar2)return number;
 function preserve_case(p_task number)return number;
 function mass_json(p_task number)return clob;
end;
/

create or replace package RRL_STOCK_PALLET_QC_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_QUALITY_ENTRY authid definer as
 function scan(p_pallet varchar2,p_errors number,p_note varchar2,p_picker varchar2,p_actor varchar2,p_operation varchar2) return number;
 function weight(p_kind varchar2,p_pallet varchar2,p_gross varchar2,p_wood varchar2,p_actor varchar2,p_operation varchar2) return number;
end;
/

create or replace package RRL_WEIGHT_DEVIATION_READ authid definer as
 function waived_line(p_line number)return number;
end;
/

create or replace package RRL_WEIGHT_CHOICE_DEMAND_READ authid definer
 accessible by(package RRL_STOCK_POOL_READ) as
 procedure adjustments(p_line number,p_unallocated number,p_pending out number,p_waived out number);
end;
/

create or replace package RRL_STOCK_POOL_READ authid definer as
 function snapshot_json(p_ware number,p_article varchar2) return clob;
 function line_snapshot_json(p_line number) return clob;
end;
/

create or replace package RRL_STOCK_POOL_CMD authid definer accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_WAVE_LAUNCH_CMD) as
 procedure compile_wave_pool(p_ware number,p_wave number,p_resources in out nocopy json_array_t,p_pools out json_array_t);
 procedure consume_wave_pool(p_pools json_array_t,p_actor varchar2);
 procedure compile_command(p_request clob,p_operation varchar2,p_hints clob,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_WAVE_PICK_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_FULLPAL_BIND_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_WAVE_EXEC_ACCESS authid definer as
 procedure assert_scope(p_wave number,p_actor varchar2,p_permission varchar2);
 procedure assert_command(p_request clob,p_actor varchar2);
 function deferred_snapshot_json(p_wave number) return clob;
 function mixed_snapshot_json(p_wave number) return clob;
end;
/

create or replace package RRL_STOCK_WAVE_FINISH_CMD authid definer as
 function snapshot_json(p_wave number) return clob;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_HU_READ authid definer as
 function snapshot_json(p_uid varchar2,p_ignore_task number default null) return clob;
 function case_snapshot_json(p_task number) return clob;
 procedure assert_quantity_write(p_uid varchar2);
end;
/

create or replace package RRL_STOCK_HU_SLOT authid definer
 accessible by(package RRL_STOCK_UNLOAD_CMD,package RRL_STOCK_HU_CMD,package RRL_STOCK_HU_UNPACK_CMD,package RRL_STOCK_HU_SLOT_MOVE_CMD,package RRL_STOCK_HU_REPACK_CMD) as
 function target_json(p_tree clob,p_metadata clob,p_ignored_task number,p_replace_root varchar2 default null,p_extra_weight number default 0,p_extra_volume number default 0) return clob;
end;
/

create or replace package RRL_STOCK_HU_CMD authid definer
 accessible by(package RRL_STOCK_HU_TASK,package RRL_STOCK_POSTING_API,package RRL_STOCK_HU_UNPACK_CMD,package RRL_STOCK_HU_SLOT_MOVE_CMD,package RRL_STOCK_HU_REPACK_CMD) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob,p_allow_slotted boolean default false);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
 procedure declare_tree(f in out nocopy json_array_t,r in out nocopy json_array_t,s clob);
end;
/

create or replace package RRL_STOCK_HU_TASK authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_HU_SHIP_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_HU_PLACEMENT_CORE authid definer
 accessible by(package RRL_STOCK_SINGLE_LOAD_CMD,package RRL_STOCK_UNLOAD_CMD,package RRL_STOCK_HU_UNPACK_CMD,package RRL_STOCK_HU_SLOT_MOVE_CMD,package RRL_STOCK_CASE_MOVE_CMD,package RRL_STOCK_CASE_RETURN_CMD,package RRL_STOCK_SHIPPING_CORE,package RRL_STOCK_HU_REPACK_CMD) as
 procedure declare_stock_source(r in out nocopy json_array_t,p_uid varchar2,p_cell varchar2,p_claims out clob);
 procedure release_stock_source(p_uid varchar2,p_cell varchar2,p_claims clob);
 procedure declare_existing_case(r in out nocopy json_array_t,p_case number);
 procedure release_case(p_case number,p_cell varchar2);
 procedure declare_place(r in out nocopy json_array_t,p_task number,p_sync number);
 procedure record_place(p_request clob,p_actor varchar2,p_uid varchar2,p_warehouse number,p_cell varchar2,p_task number,p_slot number,p_sync number,p_placement clob,p_case_task number default null);
end;
/

create or replace package RRL_STOCK_HU_SLOT_MOVE_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_HU_UNPACK_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_LOAD_RECONCILE_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_STORE_DISPOSITION authid definer accessible by(package RRL_STOCK_STORE_RECEIPT_CMD) as
 procedure resolve_counts(p_snapshot clob,p_metadata clob,p_lines out json_array_t,p_has_issue out boolean);
 procedure declare_rows(p_operation varchar2,p_lines json_array_t,p_has_issue boolean,r in out nocopy json_array_t);
 procedure persist(p_operation varchar2,p_domain json_object_t,p_actor varchar2,p_result out json_array_t);
end;
/

create or replace package RRL_STOCK_STORE_WEIGHT_CORE authid definer accessible by(package RRL_STOCK_STORE_RECEIPT_CMD) as
 procedure resolve_weight(p_source clob,p_metadata clob,p_actor varchar2,p_proof out json_object_t,p_has_issue out boolean);
 procedure declare_rows(p_operation varchar2,p_proof json_object_t,r in out nocopy json_array_t);
 procedure persist(p_operation varchar2,p_proof json_object_t,p_actor varchar2);
end;
/

create or replace package RRL_STOCK_STORE_CASE_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_STORE_RETURN_SAP_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_HU_REPACK_CMD authid definer accessible by(package RRL_STOCK_POSTING_API)as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_OUTGOING_QC_ACCESS authid definer as
 procedure assert_identifier(p_identifier varchar2,p_actor varchar2);
end;
/

create or replace package RRL_STOCK_UNLOAD_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure assert_scope(p_load varchar2,p_actor varchar2);
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_TARE_CANCEL_CMD authid definer accessible by(package RRL_STOCK_POSTING_API)as
 procedure assert_scope(p_request clob,p_actor varchar2);
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_CASE_RETURN_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_HU_UNIT_SIGNATURE authid definer as
 procedure describe_units(p_uid varchar2,p_cell varchar2,p_signature out varchar2,p_count out number);
 function signature_for(p_uid varchar2,p_cell varchar2) return varchar2;
end;
/

create or replace package RRL_STOCK_COMPOSITION_CORE authid definer accessible by(package RRL_STOCK_POSTING_API) as
 function snapshot_before(p_resources clob) return clob;
 procedure finish_changes(p_before clob);
end;
/

create or replace package RRL_STOCK_LOAD_BOX_CORE authid definer accessible by(package RRL_STOCK_HU_LOAD_CORE) as
 procedure compile_boxes(p_snapshot clob,p_context clob,p_operation varchar2,p_gross number,r in out nocopy json_array_t,p_boxes out json_array_t);
 procedure assert_policy(p_destinations clob,p_boxes json_array_t);
 procedure persist_boxes(p_operation varchar2,p_boxes json_array_t,p_actor varchar2);
end;
/

create or replace package RRL_STOCK_HU_LOAD_CORE authid definer accessible by(package RRL_STOCK_HU_SHIP_CMD,package RRL_STOCK_TRIP_DEPART_CMD,package RRL_STOCK_SINGLE_LOAD_CMD,package RRL_STOCK_LOAD_RECONCILE_CMD) as
 procedure compile_load(p_request clob,p_snapshot clob,p_shipments clob,f in out nocopy json_array_t,r in out nocopy json_array_t,p_domain out json_object_t);
 procedure begin_load(p_domain clob);
 procedure finish_load(p_domain clob,p_snapshot clob,p_operation varchar2,p_actor varchar2);
end;
/

create or replace package RRL_STOCK_LOADING_READ authid definer as
 procedure assert_scope(p_identifier varchar2,p_actor varchar2);
 procedure describe_source(p_identifier varchar2,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob,p_snapshot out clob);
 function preview_json(p_identifier varchar2,p_actor varchar2 default null) return clob;
end;
/

create or replace package RRL_STOCK_SINGLE_LOAD_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_LOAD_RECONCILE_READ authid definer as
 function preview_json(p_original varchar2) return clob;
end;
/

create or replace package RRL_STORE_EVIDENCE_API authid definer as
 procedure register_photo(p_load varchar2,p_store varchar2,p_view varchar2,p_actor varchar2,p_mime varchar2,p_width number,p_height number,p_bytes blob,p_result out clob);
 function photos_json(p_load varchar2,p_store varchar2,p_actor varchar2) return clob;
end;
/

create or replace package RRL_STORE_SCALE_API authid definer as
 procedure capture(p_source clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_TARE_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_TARE_POLICY authid definer accessible by(package RRL_STOCK_TARE_CMD) as
 procedure describe_store(p_store varchar2,p_domain out json_object_t);
 procedure record_delivery(p_operation varchar2,p_domain json_object_t);
end;
/

create or replace package RRL_TARE_PARTICIPANT authid definer as
 procedure warehouse_actor(p_actor varchar2,p_owner number);
 procedure holder_actor(p_actor varchar2,p_kind varchar2,p_id varchar2,p_owner number,p_trip RRL_TRANSPORT_TASK%rowtype,p_right varchar2);
end;
/

create or replace package RRL_STOCK_TARE_RESOLVE authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_TARE_PLANNING authid definer as
 function held_quantity(p_key raw) return number;
 procedure assert_available(p_key raw,p_physical number,p_required number);
 function case_booking(p_task number,p_ware number,p_type number) return varchar2;
 procedure require_case(p_task number,p_ware number,p_type number);
end;
/

create or replace package RRL_TARE_LOAD_RECOVERY_API authid definer accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_TARE_BOOK_CMD,package RRL_STOCK_UNLOAD_CMD)as
 procedure assert_scope(p_request clob,p_actor varchar2);
 function describe_recovery(p_request clob,p_actor varchar2)return clob;
 procedure declare_recovery(p_domain clob,p_operation varchar2,r in out nocopy json_array_t);
 procedure record_recovery(p_domain clob,p_operation varchar2,p_actor varchar2);
end;
/

create or replace package RRL_STOCK_TARE_BOOK_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_TARE_HANDOVER authid definer accessible by(package RRL_STOCK_TARE_CMD) as
 procedure describe_books(p_request clob,p_kind varchar2,p_offer varchar2,p_owner number,p_type number,p_condition varchar2,p_from_kind varchar2,p_trip number,p_vehicle number,p_qty number,p_books out json_array_t);
 procedure declare_books(p_books json_array_t,p_offer varchar2,p_resources in out nocopy json_array_t);
 procedure persist_offer(p_offer varchar2,p_books json_array_t);
 procedure transfer_books(p_books json_array_t,p_operation varchar2,p_actor varchar2);
end;
/

create or replace package RRL_STOCK_TARE_LOSS authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_RETURN_REUSE authid definer accessible by(package RRL_STOCK_STORE_RETURN_REC_CMD,package RRL_STOCK_STORE_RETURN_PUT) as
 procedure describe_boxes(p_approval RRL_STORE_RETURN_APPROVAL%rowtype,p_metadata json_object_t,p_scan_uom varchar2,p_batch_source varchar2,p_ware number,p_proof out json_object_t);
 procedure persist_boxes(p_operation varchar2,p_actor varchar2,p_proof json_object_t);
 procedure assert_pick_target(p_receipt RRL_STORE_RETURN_RECEIPT%rowtype,p_target varchar2);
end;
/

create or replace package RRL_STOCK_CASE_CLOSE authid definer accessible by(package RRL_STOCK_STORE_CASE_CMD) as
 procedure actor_scope(p_case varchar2,p_actor varchar2,p_action varchar2);
 procedure describe(p_case varchar2,p_metadata clob,p_actor varchar2,p_domain in out nocopy json_object_t);
 procedure declare_resources(p_domain json_object_t,p_operation varchar2,p_resources in out nocopy json_array_t);
 procedure persist(p_domain json_object_t,p_actor varchar2);
end;
/

create or replace package RRL_STOCK_BALANCE_CORE authid definer 
 accessible by(package RRL_STOCK_IW_RECOVERY_REC,package RRL_STOCK_UNLOAD_CMD,package RRL_STOCK_INTERWARE_REC,package RRL_STOCK_STORE_RETURN_REC_CMD,package RRL_STOCK_RECEIPT_REVERSE,package RRL_STOCK_INVENTORY_BIRTH,package RRL_STOCK_INVENTORY_CMD,package RRL_STOCK_EVENT_BRIDGE,package RRL_STOCK_MES_MOVEMENT_CORE,package RRL_STOCK_RESERVATION_CMD,package RRL_STOCK_POSTING_API,package RRL_STOCK_MOVE_CORE, 
  package RRL_STOCK_RESERVE_CORE,package RRL_STOCK_RECEIPT_CORE,package RRL_STOCK_TRANSFER_CORE,package RRL_STOCK_EFFECT_CORE) as 
 procedure apply_delta(p_uid varchar2,p_cell varchar2,p_delta_p number,p_delta_h number, 
   p_base_uom varchar2,p_uom_version number,p_expected_version number default null); 
 procedure write_move(p_uid varchar2,p_from varchar2,p_to varchar2,p_qty number,p_base_uom varchar2,p_uom_version number,p_line number,p_actor varchar2,p_event out number); 
 procedure write_leg(p_uid varchar2,p_from varchar2,p_to varchar2,p_signed_qty number,p_base_uom varchar2, 
   p_uom_version number,p_line number,p_leg number,p_type number,p_actor varchar2,p_event out number,p_outgoing_doc number default null,p_pallet_row number default null); 
end;
/

create or replace package RRL_FORECAST_SOURCE_RULES authid definer
 accessible by(package RRL_FORECAST_PROJECTOR)as
 procedure compile_leaves(p_tree clob,p_ware number,p_leaves out clob);
end;
/

create or replace package RRL_FORECAST_PROJECTOR authid definer as
 function load_write_allowed(p_load varchar2)return number;
 function day_write_allowed(p_ware number,p_day date)return number;
 procedure project_load(p_load varchar2,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_WORKLOAD_CONFIG_API authid definer as
 function write_allowed(p_operation varchar2)return number;
 procedure execute_command(p_operation varchar2,p_actor varchar2,p_action varchar2,p_body clob,p_result out clob);
end;

/

create or replace package RRL_TRANSPORT_EDIT_API authid definer as
 procedure create_trip(p_type varchar2,p_day date,p_actor varchar2,p_trip out number);
 procedure update_trip(p_trip number,p_actor varchar2,p_body clob,p_result out clob);
end;
/

create or replace package RRL_CLUSTER_CREATE_API authid definer as
 function write_allowed(p_operation varchar2)return number;
 procedure create_cluster(p_operation varchar2,p_actor varchar2,p_request clob,p_sts clob,p_result out clob);
end;
/

create or replace package RRL_WAVE_TIME_API authid definer as
 function write_allowed(p_operation varchar2)return number;
 procedure context(p_wave number,p_actor varchar2,p_result out clob);
 procedure approve(p_operation varchar2,p_actor varchar2,p_body clob,p_result out clob);
end;
/

create or replace package RRL_TT_ROUTE_SOURCE authid definer as
 procedure snapshot(p_trip number,p_actor varchar2,p_source out clob,p_hash out varchar2);
 procedure durations(p_trip number,p_actor varchar2,p_drive out number,p_back out number,p_basis out varchar2);
end;
/

create or replace package RRL_TT_OPERATION_PLAN_API authid definer as
 procedure generate(p_trip number,p_actor varchar2,p_result out clob);
 procedure write_fact(p_operation number,p_actor varchar2,p_body clob,p_result out clob);
 procedure assert_driver(p_driver number,p_actor varchar2);
 procedure mark_driver_fact(p_operation number,p_driver number,p_actor varchar2,p_action varchar2,p_result out clob);
end;

/

create or replace package RRL_TT_ROUTE_API authid definer as
 function write_allowed(p_operation varchar2)return number;
 procedure context(p_trip number,p_actor varchar2,p_result out clob);
 procedure apply_input(p_operation varchar2,p_actor varchar2,p_body clob,p_result out clob);
end;
/

create or replace package RRL_OUTBOX_DELIVERY_API authid definer as
 function write_allowed(p_event number)return number;
 procedure claim_next(p_worker varchar2,p_target varchar2,p_seconds number,p_result out clob);
 procedure begin_attempt(p_event number,p_version number,p_worker varchar2,p_system varchar2,p_kind varchar2,
  p_business varchar2,p_cert varchar2,p_thumb varchar2,p_signature varchar2,p_request clob,p_request_id out number);
 procedure finish_attempt(p_event number,p_version number,p_worker varchar2,p_request_id number,p_body clob,p_result out clob);
 procedure manual_retry(p_event number,p_actor varchar2,p_reason varchar2);
end;
/

create or replace package RRL_PICK_RANGE_APPLY_CORE authid definer
 accessible by(package RRL_PICK_RANGE_PROPOSAL_API)as
 procedure apply_change(p_operation varchar2,p_actor varchar2,p_action varchar2,p_ware number,p_article varchar2,
  p_request clob,p_source clob,p_result out clob);
end;
/

create or replace package RRL_PICK_RANGE_PROPOSAL_API authid definer as
 function write_allowed return number;
 procedure execute_command(p_operation varchar2,p_actor varchar2,p_action varchar2,p_ware number,p_article varchar2,
  p_request clob,p_source clob,p_result out clob);
end;
/

create or replace package RRL_PICK_TOPOLOGY_API as
  function upsert_route(
    p_pick_route_id number default null,
    p_route_code    varchar2,
    p_route_name    varchar2 default null,
    p_ware_id       number,
    p_route_kind    varchar2 default 'PICK',
    p_active        number default 1,
    p_updated_by    varchar2 default null
  ) return number;

  function upsert_route_cell(
    p_pick_route_cell_id number default null,
    p_pick_route_id      number,
    p_cell_code          varchar2,
    p_pick_sequence      number,
    p_zone_code          varchar2 default null,
    p_aisle_code         varchar2 default null,
    p_side_code          varchar2 default null,
    p_level_no           number default null,
    p_active             number default 1,
    p_updated_by         varchar2 default null
  ) return number;

  function upsert_pick_face(
    p_pick_face_id             number default null,
    p_ware_id                  number,
    p_cell_code                varchar2,
    p_pick_face_code           varchar2 default null,
    p_pick_face_type           varchar2 default 'REGULAR',
    p_pick_route_id            number default null,
    p_pick_route_cell_id       number default null,
    p_pick_sequence            number default null,
    p_min_case_qty             number default null,
    p_max_case_qty             number default null,
    p_replenishment_trigger_qty number default null,
    p_max_weight               number default null,
    p_max_volume               number default null,
    p_allow_dynamic_assignment number default 0,
    p_active                   number default 1,
    p_comment_text             varchar2 default null,
    p_updated_by               varchar2 default null
  ) return number;

  function assign_articul(
    p_pick_face_articul_id number default null,
    p_pick_face_id         number,
    p_articul              varchar2,
    p_priority             number default 100,
    p_min_qty              number default null,
    p_max_qty              number default null,
    p_case_pick_enabled    number default 1,
    p_active               number default 1,
    p_valid_from           date default null,
    p_valid_to             date default null,
    p_updated_by           varchar2 default null
  ) return number;

  procedure resolve_pick_face(
    p_ware_id            number,
    p_articul            varchar2,
    p_target_cell        out varchar2,
    p_pick_sequence      out number,
    p_pick_face_id       out number,
    p_pick_route_cell_id out number
  );
end RRL_PICK_TOPOLOGY_API;
/

create or replace package RRL_WEIGHT_BOX_READ authid definer as
 function decode_json(p_scan varchar2)return clob;
 procedure assert_sku(p_article varchar2,p_gtin varchar2 default null);
end;
/

create or replace package RRL_WH_SCALE_API authid definer as
 procedure capture(p_source clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_CASE_SCALE_ADMISSION authid definer as
 procedure assert_capture(p_request clob,p_previous number);
 procedure claim_capture(p_request clob,p_operation varchar2,p_previous number);
end;
/

create or replace package RRL_PICK_PLAN_ACCESS authid definer as
 procedure assert_scope(p_order number,p_actor varchar2,p_permission varchar2 default 'pick_plan_create');
end;
/

create or replace package RRL_PICK_PLAN_ADMISSION authid definer as
 procedure begin_plan(p_order number,p_actor varchar2);
 procedure end_plan;
end;
/

create or replace package RRL_WEIGHT_BOX_PLANNING_READ authid definer as
 function snapshot_json(p_row number,p_actor varchar2,p_permission varchar2 default 'pick_plan_create')return clob;
end;
/

create or replace package RRL_WEIGHT_BOX_CHOICE_API authid definer as
 procedure approve_request(p_request clob,p_actor varchar2,p_result out clob);
 procedure cancel_choice(p_choice varchar2,p_actor varchar2,p_reason varchar2,p_result out clob);
end;
/

create or replace package RRL_WEIGHT_PLAN_BIND authid definer accessible by(package RRL_PICKING_API)as
 function bound_plan(p_order number,p_strategy varchar2,p_actor varchar2)return number;
 function target_json(p_row number,p_actor varchar2)return clob;
 procedure finish_bind(p_choice varchar2,p_plan number,p_line number,p_actor varchar2);
end;
/

create or replace package RRL_PICKING_API as
  function create_plan(
    p_customer_order_id number,
    p_plan_strategy     varchar2 default 'FEFO',
    p_created_by        varchar2 default null
  ) return number;

  procedure cancel_plan(
    p_pick_plan_id number,
    p_updated_by   varchar2 default null
  );
end RRL_PICKING_API;
/

create or replace package RRL_PALLET_TYPE_API authid definer as
 procedure upsert_request(p_request clob,p_actor varchar2,p_id out number);
end;
/

create or replace package RRL_CASE_ROUTE_ADMISSION authid definer accessible by(package RRL_STOCK_CASE_PICK_CMD) as
 procedure assert_next(p_case number,p_line number);
end;
/

create or replace package RRL_INTERWARE_UNIT_SOURCE authid definer as
 procedure assert_scope(p_load varchar2,p_actor varchar2);
 procedure capture_plan(p_plan varchar2,p_actor varchar2);
 function plan_manifest(p_plan varchar2,p_actor varchar2)return clob;
 function issued_manifest(p_load varchar2,p_uid varchar2,p_snapshot clob)return clob;
end;
/

create or replace package RRL_INTERWARE_MARK_SCAN authid definer as
 function required_for_article(p_article varchar2) return number;
 function required_for_plan(p_domain clob) return number;
 procedure validate_scan(p_domain clob,p_metadata clob,p_unit_count out number);
end;
/

create or replace package RRL_STOCK_IW_RECOVERY_NEXT authid definer accessible by(package RRL_STOCK_INTERWARE_NEXT) as 
 function describe_source(p_st number,p_ware number) return json_object_t; 
 procedure declare_source(p_source json_object_t,p_operation varchar2,p_resources in out nocopy json_array_t); 
 procedure validate_load(p_source json_object_t,p_actor varchar2); 
 procedure dispatched(p_source json_object_t,p_actor varchar2); 
end;
/

create or replace package RRL_STOCK_INTERWARE_NEXT authid definer accessible by(package RRL_STOCK_SHIPPING_CORE) as 
 function describe_source(p_st number,p_ware number) return json_object_t; 
 procedure declare_source(p_source json_object_t,p_operation varchar2,p_resources in out nocopy json_array_t); 
 procedure validate_load(p_source json_object_t,p_actor varchar2); 
 procedure dispatched(p_source json_object_t,p_actor varchar2); 
end;
/

create or replace package RRL_STOCK_INTERWARE_CUSTODY authid definer accessible by(package RRL_STOCK_POSTING_API) as 
 procedure assert_scope(p_receipt varchar2,p_actor varchar2); 
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob); 
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob); 
end;
/

create or replace package RRL_STOCK_STORE_RECEIPT_READ authid definer as
 procedure require_receiver(p_actor varchar2,p_store varchar2);
 procedure describe_load(p_load varchar2,p_actor varchar2,p_store varchar2,p_domain out clob);
 function preview_json(p_load varchar2,p_actor varchar2,p_store varchar2) return clob;
end;
/

create or replace package RRL_STOCK_STORE_RETURN_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure assert_actor(p_actor varchar2);
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_STORE_CUSTODY_CMD authid definer accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_STORE_RECEIPT_CMD)as
 procedure assert_scope(p_receipt varchar2,p_actor varchar2);
 procedure declare_receipt(p_receipt varchar2,p_load varchar2,p_uid varchar2,p_resources in out nocopy json_array_t,p_operation varchar2 default null);
 procedure release_accepted(p_receipt varchar2,p_actor varchar2);
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_STORE_RECEIPT_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_STORE_RETURN_TR_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STORE_MARK_CORE authid definer accessible by(package RRL_STOCK_STORE_RECEIPT_READ,package RRL_STOCK_STORE_RECEIPT_CMD,package RRL_STORE_RETURN_UNIT_CORE)as
 function source_proof(p_domain json_object_t)return json_object_t;
 function preview(p_domain json_object_t)return clob;
 procedure verify_scans(p_domain json_object_t,p_metadata json_object_t,p_proof out json_object_t);
 procedure resolve_disposition(p_proof json_object_t,p_metadata json_object_t,p_lines json_array_t,p_units out json_array_t);
 procedure persist(p_operation varchar2,p_load varchar2,p_units json_array_t,p_actor varchar2);
 procedure declare_rows(p_domain json_object_t,p_policies in out nocopy json_array_t,p_resources in out nocopy json_array_t);
end;
/

create or replace package RRL_STORE_RETURN_UNIT_CORE authid definer as
 function approved_proof(p_approval varchar2)return clob;
 function custody_proof(p_approval varchar2,p_metadata json_object_t)return clob;
 function accepted_units(p_receipt varchar2,p_uid varchar2,p_uom varchar2)return clob;
 function select_units(p_receipt varchar2,p_uid varchar2,p_uom varchar2,p_qty number,p_keys clob)return clob;
 procedure persist(p_approval varchar2,p_receipt varchar2,p_uid varchar2,p_cell varchar2,p_units clob);
end;
/

create or replace package RRL_STOCK_STORE_RETURN_CUST_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure assert_scope(p_request clob,p_actor varchar2);
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_UNIT_CORE authid definer 
 accessible by(package RRL_STOCK_IW_RECOVERY_REC,package RRL_STOCK_STORE_RETURN_REC_CMD,package RRL_STOCK_INTERWARE_REC,package RRL_STOCK_UNLOAD_CMD,package RRL_STOCK_REPL_BIND,package RRL_STOCK_SHORT_RECOVERY,package RRL_STOCK_ELIGIBILITY,package RRL_STOCK_CASE_RETURN_CMD,package RRL_STOCK_INVENTORY_BIRTH,package RRL_STOCK_CASE_SHORT_CMD,package RRL_STOCK_RECEIPT_REVERSE,package RRL_STOCK_WAVE_LAUNCH_CMD,package RRL_STOCK_INVENTORY_CMD,package RRL_STOCK_MES_CANCEL_CMD,package RRL_STOCK_MES_SUPPLY_CMD,package RRL_STOCK_DOC_RESERVE_CMD,package RRL_STOCK_WAVE_CMD,package RRL_STOCK_MES_MOVEMENT_CORE,package RRL_STOCK_INVARIANT_CORE,package RRL_STOCK_RESERVATION_CMD,package RRL_STOCK_TRANSFER_CORE, 
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

create or replace package RRL_STOCK_STORE_RETURN_REC_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure assert_scope(p_pickup varchar2,p_actor varchar2);
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_STORE_RETURN_PUT authid definer accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_TASK_PLAN,package RRL_STOCK_TASK_CORE,package RRL_STOCK_TASK_DOMAIN) as
 procedure assert_scope(p_receipt varchar2,p_actor varchar2);
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
 procedure plan_task(p_task RRL_WAREHOUSE_TASK%rowtype,p_actor varchar2,p_resources in out nocopy json_array_t,p_domain in out nocopy json_object_t);
 procedure validate_task(p_task RRL_WAREHOUSE_TASK%rowtype,p_actor varchar2,p_frozen json_object_t);
 procedure complete_task(p_task RRL_WAREHOUSE_TASK%rowtype,p_quantity number,p_target_uid varchar2,p_actor varchar2);
end;
/

create or replace package RRL_REGULATORY_STOCK_OUTBOX authid definer accessible by(package RRL_REGULATORY_API)as
 procedure declare_events(p_operation varchar2,p_event varchar2,p_profiles clob,p_resources in out nocopy json_array_t);
 function enqueue_events(p_operation varchar2,p_event varchar2,p_domain clob,p_units clob,p_profiles clob)return clob;
end;
/

create or replace package RRL_REGULATORY_API as
  function upsert_mercury_site(
    p_site_code           varchar2,
    p_site_name           varchar2 default null,
    p_ware_id             number default null,
    p_enterprise_guid     varchar2 default null,
    p_enterprise_uuid     varchar2 default null,
    p_business_guid       varchar2 default null,
    p_business_uuid       varchar2 default null,
    p_address_text        varchar2 default null,
    p_active              number default 1,
    p_updated_by          varchar2 default user
  ) return number;

  function create_mercury_operation(
    p_prod_batch_id       number default null,
    p_raw_batch_id        number default null,
    p_mercury_site_id     number default null,
    p_operation_type      varchar2,
    p_mercury_operation_id varchar2 default null,
    p_external_operation_id varchar2 default null,
    p_status              varchar2 default 'DRAFT',
    p_request_json        clob default null,
    p_created_by          varchar2 default user
  ) return number;

  procedure update_mercury_operation(
    p_operation_row_id    number,
    p_status              varchar2 default null,
    p_mercury_operation_id varchar2 default null,
    p_external_operation_id varchar2 default null,
    p_response_json       clob default null,
    p_last_error          varchar2 default null,
    p_updated_by          varchar2 default user
  );

  function write_journal(
    p_system_code         varchar2,
    p_entity_type         varchar2,
    p_entity_id           varchar2 default null,
    p_prod_batch_id       number default null,
    p_raw_batch_id        number default null,
    p_uid_pallet          varchar2 default null,
    p_sscc                varchar2 default null,
    p_operation_type      varchar2,
    p_old_status          varchar2 default null,
    p_new_status          varchar2 default null,
    p_document_id         varchar2 default null,
    p_external_operation_id varchar2 default null,
    p_payload_json        clob default null,
    p_message             varchar2 default null,
    p_created_by          varchar2 default user
  ) return number;

  function set_crpt_code_status(
    p_cis                 varchar2,
    p_code_status         varchar2,
    p_event_type          varchar2 default null,
    p_document_id         varchar2 default null,
    p_document_no         varchar2 default null,
    p_payload_json        clob default null,
    p_error_text          varchar2 default null,
    p_updated_by          varchar2 default user
  ) return number;
  procedure declare_stock_events(p_operation varchar2,p_event varchar2,p_profiles clob,p_resources in out nocopy json_array_t);
  function enqueue_stock_events(p_operation varchar2,p_event varchar2,p_domain clob,p_units clob,p_profiles clob)return clob;
end RRL_REGULATORY_API;
/

create or replace package RRL_STOCK_RETURN_DISPOSE authid definer accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_EFFECT_CORE) as
 procedure assert_scope(p_request varchar2,p_actor varchar2);
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
 procedure validate_consume(p_receipt varchar2,p_uid varchar2,p_cell varchar2,p_quantity number,p_ware number,p_actor varchar2);
end;
/

create or replace package RRL_STOCK_SUP_RETURN authid definer accessible by(package RRL_STOCK_SHIPPING_CORE,package RRL_STOCK_EFFECT_CORE) as
 function describe_source(p_st number,p_supplier varchar2,p_ware number) return json_object_t;
 procedure declare_source(p_source json_object_t,p_operation varchar2,p_resources in out nocopy json_array_t);
 procedure validate_consume(p_receipt varchar2,p_uid varchar2,p_cell varchar2,p_quantity number,p_ware number,p_actor varchar2);
 procedure dispatched(p_source json_object_t,p_actor varchar2);
end;
/

create or replace package RRL_STOCK_TRIP_DEPART_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_INTERWARE_REC authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure assert_scope(p_plan varchar2,p_actor varchar2);
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_INTERWARE_THERMAL authid definer as
 function mode_json(p_plan varchar2)return clob;
 procedure assert_release(p_plan varchar2);
 procedure assert_cell(p_mode clob,p_ware number,p_cell varchar2);
 procedure record_decision(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_INTERWARE_DEPART_GATE authid definer as 
 function promises(p_trip number)return clob; 
 procedure assert_ready(p_promises clob); 
end;
/

create or replace package RRL_TRANSPORT_PLAN_RULES authid definer as
 procedure assert_actor(p_actor varchar2,p_ware number);
 procedure check_vehicle(p_vehicle_id number,p_sts clob,p_complete number,p_result out clob);
end;
/

create or replace package RRL_TRANSPORT_PLAN_API authid definer as
 function apply_write_allowed(p_plan number)return number;
 procedure apply_plan(p_plan number,p_day date,p_dock varchar2,p_actor varchar2,p_result out clob);
 procedure assign_sts(p_tt number,p_sts clob,p_actor varchar2,p_result out clob);
end;

/

create or replace package RRL_STOCK_IW_PUT_CELL authid definer
 accessible by(package RRL_STOCK_INTERWARE_PUT,package RRL_STOCK_IW_RECOVERY_PUT)as
 procedure assert_target(p_ware number,p_uid varchar2,p_from varchar2,p_target varchar2,p_gross number,p_task_id number);
end;
/

create or replace package RRL_STOCK_IW_RECOVERY_PUT authid definer accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_TASK_PLAN,package RRL_STOCK_TASK_CORE,package RRL_STOCK_TASK_DOMAIN) as
 procedure assert_scope(p_receipt varchar2,p_actor varchar2);
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
 procedure plan_task(p_task RRL_WAREHOUSE_TASK%rowtype,p_actor varchar2,p_resources in out nocopy json_array_t,p_domain in out nocopy json_object_t);
 procedure validate_task(p_task RRL_WAREHOUSE_TASK%rowtype,p_actor varchar2,p_frozen json_object_t);
 procedure complete_task(p_task RRL_WAREHOUSE_TASK%rowtype,p_quantity number,p_target_uid varchar2,p_actor varchar2);
end;

/

create or replace package RRL_STOCK_INTERWARE_PUT authid definer accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_TASK_PLAN,package RRL_STOCK_TASK_CORE,package RRL_STOCK_TASK_DOMAIN) as
 procedure assert_scope(p_receipt varchar2,p_actor varchar2,p_superseded number default null);
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
 procedure plan_task(p_task RRL_WAREHOUSE_TASK%rowtype,p_actor varchar2,p_resources in out nocopy json_array_t,p_domain in out nocopy json_object_t);
 procedure validate_task(p_task RRL_WAREHOUSE_TASK%rowtype,p_actor varchar2,p_frozen json_object_t);
 procedure complete_task(p_task RRL_WAREHOUSE_TASK%rowtype,p_quantity number,p_target_uid varchar2,p_actor varchar2);
end;
/

create or replace package RRL_STOCK_INTERWARE_SHORT_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as 
 procedure assert_scope(p_request clob,p_actor varchar2); 
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob); 
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob); 
end;
/

create or replace package RRL_IW_SHORTAGE_GUARD authid definer as
 procedure require_command(p_operation varchar2,p_kind varchar2);
end;
/

create or replace package RRL_STOCK_IW_RECOVERY_PLAN authid definer accessible by(package RRL_STOCK_POSTING_API) as 
 procedure assert_scope(p_request clob,p_actor varchar2); 
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob); 
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob); 
end;
/

create or replace package RRL_STOCK_IW_RECOVERY_REC authid definer accessible by(package RRL_STOCK_POSTING_API)as 
 procedure assert_scope(p_approval varchar2,p_actor varchar2); 
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob); 
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob); 
end;
/

create or replace package RRL_STOCK_IW_RECOVERY_CANCEL authid definer accessible by(package RRL_STOCK_POSTING_API)as
 procedure assert_scope(p_request varchar2,p_actor varchar2);
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_PALLET_FLOOR_READ authid definer as
 function scope_warehouse(p_uid varchar2,p_actor varchar2)return number;
 function describe_type(p_uid varchar2,p_actor varchar2)return clob;
end;
/

create or replace package RRL_STOCK_PALLET_TYPE_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API,trigger RRL_PALLET_FLOOR_GUARD)as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
 procedure assert_writing(p_uid varchar2,p_operation varchar2);
end;
/

create or replace package RRL_RECIPIENT_PALLET_POLICY authid definer as
 function rule_id(p_customer number,p_store number)return number;
 function type_id(p_customer number,p_store number)return number;
end;
/

create or replace package RRL_STOCK_CASE_TYPE_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API,trigger RRL_CASE_PALLET_TYPE_GUARD)as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
 procedure assert_writing(p_task number);
end;
/

create or replace package RRL_STOCK_POSTING_API authid definer as
 procedure prepare_command(p_request clob,p_actor varchar2,p_replay out clob,p_hints clob default null);
 procedure execute_prepared(p_result out clob);
 procedure stage_birth(p_uid varchar2);
 procedure finish_birth_capture;
 procedure reset_connection;
end;

/

create or replace package RRL_INTERWARE_ROUTING authid definer as
 function target_trip(p_plan varchar2)return number;
 function outbound_dock(p_plan varchar2)return varchar2;
 function ready_due(p_plan varchar2)return timestamp with time zone;
 function resolved(p_plan RRL_INTERWARE_PLAN%rowtype)return RRL_INTERWARE_PLAN%rowtype;
 procedure record_decision(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_TT_TIME_API authid definer as
 function write_allowed(p_operation varchar2)return number;
 procedure context(p_trip number,p_actor varchar2,p_result out clob);
 procedure approve(p_operation varchar2,p_actor varchar2,p_body clob,p_result out clob);
end;
/

create or replace package RRL_STORE_CALENDAR_API authid definer as
 function write_allowed(p_operation varchar2)return number;
 function config_write_allowed return number;
 procedure configure(p_ware number,p_store varchar2,p_body clob,p_actor varchar2,p_result out clob);
 procedure delivery_rule(p_ware number,p_store_id number,p_day date,p_offset out number,p_allowed out number,p_proof out clob);
 procedure context(p_ware number,p_store varchar2,p_day varchar2,p_actor varchar2,p_result out clob);
 procedure set_exception(p_operation varchar2,p_actor varchar2,p_body clob,p_result out clob);
end;
/

create or replace package RRL_STORE_ORDER_SCOPE authid definer as
 procedure actor_scope(p_actor varchar2,p_permission varchar2,p_ware out number,p_global out number);
 procedure assert_scope(p_actor varchar2,p_permission varchar2,p_ware number);
 procedure begin_source(p_actor varchar2,p_permission varchar2,p_ware number,p_order number default null);
 procedure begin_supply(p_actor varchar2,p_ware number,p_sender varchar2,p_order varchar2,p_message varchar2);
 procedure end_source;
end;
/

create or replace package RRL_SAP_STORE_ADMISSION_API authid definer as
 function write_allowed return number;
 procedure context(p_order number,p_actor varchar2,p_result out clob);
 procedure apply_decision(p_actor varchar2,p_body clob,p_result out clob);
end;
/

create or replace package RRL_DAY_REVIEW_API authid definer as
 function write_allowed return number;
 procedure context(p_ware number,p_day date,p_zone varchar2,p_actor varchar2,p_result out clob);
 procedure lookup(p_actor varchar2,p_operation varchar2,p_body clob,p_result out clob);
 procedure resolve(p_actor varchar2,p_operation varchar2,p_body clob,p_result out clob);
 procedure append_review(p_actor varchar2,p_operation varchar2,p_body clob,p_material clob,p_captured timestamp with time zone,p_result out clob);
end;
/

create or replace package RRL_ST_DEFER_API authid definer as
 function write_allowed return number;
 procedure history(p_st varchar2,p_actor varchar2,p_after number,p_result out clob);
 procedure context(p_st varchar2,p_actor varchar2,p_result out clob);
 procedure apply_decision(p_operation varchar2,p_actor varchar2,p_body clob,p_result out clob);
end;
/

create or replace package RRL_WARE_DEPOT_API authid definer as
 function write_allowed return number;
 procedure material(p_ware number,p_result out clob);
 procedure context(p_ware number,p_actor varchar2,p_result out clob);
 procedure apply_setting(p_operation varchar2,p_actor varchar2,p_body clob,p_result out clob);
end;
/

create or replace package RRL_RETURN_REUSE_API authid definer as
 procedure preview(p_receipt varchar2,p_line number,p_quantity varchar2,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_INTERWARE_PART authid definer accessible by(package RRL_STOCK_IW_RECOVERY_REC,package RRL_STOCK_INTERWARE_REC) as 
 procedure describe_partial(p_metadata json_object_t,p_original_uid varchar2,p_original_qty number,p_unit varchar2,p_article varchar2,p_domain in out json_object_t); 
 procedure describe_selected_units(p_metadata json_object_t,p_domain in out json_object_t); 
 procedure create_pallet(p_domain json_object_t,p_operation varchar2); 
end;
/

create or replace package RRL_INTERWARE_INCIDENT_API authid definer as
 function write_allowed return number;
 procedure close_case(p_operation varchar2,p_actor varchar2,p_request clob,p_result out clob);
end;
/

create or replace package RRL_IW_AGG_SCAN authid definer accessible by(package RRL_INTERWARE_MARK_SCAN)as
 procedure expand(p_metadata clob,p_scans out clob);
end;
/

create or replace package RRL_IW_HU_SOURCE authid definer as
 function stock_uid(p_load varchar2)return varchar2;
 function context_json(p_load varchar2)return clob;
 procedure capture_context(p_load varchar2,p_actor varchar2,p_context out clob);
 procedure assert_context(p_load varchar2,p_context clob);
end;
/

create or replace package RRL_IW_HU_REC_CORE authid definer accessible by(package RRL_STOCK_INTERWARE_REC)as
 procedure declare_rows(p_domain json_object_t,p_operation varchar2,p_resources in out nocopy json_array_t);
 procedure restore(p_domain json_object_t,p_operation varchar2,p_actor varchar2);
end;
/

create or replace package RRL_PICK_PLAN_CREATE_API authid definer as
 function create_command(p_operation varchar2,p_order number,p_strategy varchar2,p_actor varchar2)return number;
 procedure assert_write(p_operation varchar2);
 function current_operation return varchar2;
 function cached_plan return number;
end;
/

create or replace package RRL_PICK_PLAN_ADMISSION authid definer as
 procedure begin_plan(p_order number,p_actor varchar2);
 procedure end_plan;
end;

/

create or replace package RRL_PICKING_API as
  function create_plan(
    p_customer_order_id number,
    p_plan_strategy     varchar2 default 'FEFO',
    p_created_by        varchar2 default null
  ) return number;

  procedure cancel_plan(
    p_pick_plan_id number,
    p_updated_by   varchar2 default null
  );
end RRL_PICKING_API;

/

create or replace package body RRL_PICKING_API as
  function active_reserved_qty(
    p_pallet_uid varchar2,
    p_articul    varchar2,
    p_cell       varchar2 default null
  ) return number is
    v_qty number;
  begin
    select nvl(sum(RESERVED_QTY), 0)
      into v_qty
      from RRL_PICK_RESERVATION
     where RESERVATION_STATUS = 'ACTIVE'
       and (RESERVATION_LEVEL='SOFT' or exists(select 1 from RRL_STOCK_RELEASE where RELEASE_ID=1 and STATE!='ACTIVE'))
       and PALLET_UID = p_pallet_uid
       and (p_cell is null or SOURCE_CELL_CODE=p_cell)
       and upper(ARTICUL) = upper(p_articul);
    return v_qty;
  end active_reserved_qty;

  procedure log_decision(
    p_pick_plan_id      number,
    p_pick_plan_line_id number,
    p_decision_type     varchar2,
    p_message_text      varchar2,
    p_payload_json      clob default null,
    p_created_by        varchar2 default null
  ) is
  begin
    insert into RRL_PICK_DECISION_LOG (
      PICK_DECISION_ID, PICK_PLAN_ID, PICK_PLAN_LINE_ID,
      DECISION_TYPE, MESSAGE_TEXT, PAYLOAD_JSON, CREATED_AT, CREATED_BY
    ) values (
      RRL_PICK_DECISION_LOG_SQ.nextval, p_pick_plan_id, p_pick_plan_line_id,
      substr(p_decision_type, 1, 50), substr(p_message_text, 1, 1000),
      p_payload_json, sysdate, substr(p_created_by, 1, 50)
    );
  end log_decision;

  function create_plan(
    p_customer_order_id number,
    p_plan_strategy     varchar2 default 'FEFO',
    p_created_by        varchar2 default null
  ) return number is
    v_order RRL_CUSTOMER_ORDER%rowtype;
    v_pick_plan_id number;
    v_line_id number;
    v_task_id number;
    v_remaining number;
    v_candidate_available number;
    v_reserved_by_other number;
    v_reserve_qty number;
    v_requested_total number := 0;
    v_planned_total number := 0;
    v_shortage_total number := 0;
    v_line_planned number;
    v_line_shortage number;
    v_task_type varchar2(30);
    v_strategy varchar2(30);
    v_status varchar2(30);
    v_target_cell varchar2(60);
    v_pick_sequence number;
    v_pick_face_id number;
    v_pick_route_cell_id number;
    v_release varchar2(20);v_requested_line_qty number;v_uom varchar2(20);v_version number;v_num number;v_den number;v_scale number;v_demand json_object_t;v_soft number;v_fenced boolean:=false;v_mutating boolean:=false;v_bound_plan number;v_weight_wire clob;v_weight_choice json_object_t;v_weight_id varchar2(100);v_weight_uid varchar2(150);v_weight_cell varchar2(60);
  begin
    select STATE into v_release from RRL_STOCK_RELEASE where RELEASE_ID=1;
    if v_release='ACTIVE'then RRL_PICK_PLAN_ADMISSION.begin_plan(p_customer_order_id,p_created_by);v_fenced:=true;savepoint rrl_pick_plan_begin;v_mutating:=true;end if;
    if v_fenced then v_bound_plan:=RRL_PICK_PLAN_CREATE_API.cached_plan;
     if v_bound_plan is not null then RRL_PICK_PLAN_ADMISSION.end_plan;return v_bound_plan;end if;end if;
    v_strategy := upper(nvl(p_plan_strategy, 'FEFO'));
    if v_strategy not in ('FEFO', 'FIFO') then
      raise_application_error(-20980, 'unsupported picking strategy');
    end if;

    select *
      into v_order
      from RRL_CUSTOMER_ORDER
     where CUSTOMER_ORDER_ID = p_customer_order_id;

    if v_release='ACTIVE'then
     v_bound_plan:=RRL_WEIGHT_PLAN_BIND.bound_plan(p_customer_order_id,v_strategy,p_created_by);
     if v_bound_plan>0 then RRL_PICK_PLAN_ADMISSION.end_plan;return v_bound_plan;end if;
    end if;
    select RRL_PICK_PLAN_SQ.nextval into v_pick_plan_id from dual;

    insert into RRL_PICK_PLAN (
      PICK_PLAN_ID, CUSTOMER_ORDER_ID, CUSTOMER_ID, WARE_ID, ROUTE_ID, DOCK_ID,
      STATUS, PLAN_STRATEGY, CREATED_AT, CREATED_BY
    ) values (
      v_pick_plan_id, v_order.CUSTOMER_ORDER_ID, v_order.CUSTOMER_ID, v_order.WARE_ID,
      v_order.ROUTE_ID, v_order.DOCK_ID, 'DRAFT', v_strategy, sysdate, substr(p_created_by, 1, 50)
    );

    for l in (
      select *
        from RRL_CUSTOMER_ORDER_ROW
       where CUSTOMER_ORDER_ID = p_customer_order_id
         and STATUS <> 'CANCELLED'
       order by LINE_NO, CUSTOMER_ORDER_ROW_ID
    ) loop
      select RRL_PICK_PLAN_LINE_SQ.nextval into v_line_id from dual;
      v_requested_line_qty:=nvl(l.ORDER_QTY,0);v_weight_wire:=null;v_weight_choice:=null;v_weight_id:=null;v_weight_uid:=null;v_weight_cell:=null;
      if v_release='ACTIVE' then
       select max(POLICY_VERSION) into v_version from RRL_STOCK_UOM_CONVERSION where ARTICUL=l.ARTICUL and INPUT_UOM=l.UNIT_CODE;
       select BASE_UOM,NUMERATOR,DENOMINATOR,BASE_SCALE into v_uom,v_num,v_den,v_scale from RRL_STOCK_UOM_CONVERSION where ARTICUL=l.ARTICUL and INPUT_UOM=l.UNIT_CODE and POLICY_VERSION=v_version;
       v_demand:=json_object_t.parse(RRL_STOCK_POOL_READ.line_snapshot_json(l.CUSTOMER_ORDER_ROW_ID));
       if not v_demand.get_boolean('open')then continue;end if;
       if v_demand.get_string('quantity')='0'then v_requested_line_qty:=0;else v_requested_line_qty:=RRL_STOCK_MATH.quantity(v_demand.get_string('quantity'));end if;
       select nvl(sum(pr.RESERVED_QTY),0)into v_soft from RRL_PICK_RESERVATION pr
        join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_LINE_ID=pr.PICK_PLAN_LINE_ID join RRL_PICK_PLAN pp on pp.PICK_PLAN_ID=pl.PICK_PLAN_ID
        where pl.CUSTOMER_ORDER_ROW_ID=l.CUSTOMER_ORDER_ROW_ID and pr.RESERVATION_STATUS='ACTIVE'and pr.RESERVATION_LEVEL='SOFT'
         and pp.STATUS in('DRAFT','PLANNED_FULL','PLANNED_PARTIAL');
       v_requested_line_qty:=greatest(0,v_requested_line_qty-v_soft);
       if v_requested_line_qty=0 then continue;end if;
      end if;
      v_remaining := v_requested_line_qty;
      if v_release='ACTIVE'then
       v_weight_wire:=RRL_WEIGHT_PLAN_BIND.target_json(l.CUSTOMER_ORDER_ROW_ID,p_created_by);
       if v_weight_wire is not null then
        v_weight_choice:=json_object_t.parse(v_weight_wire);
        if v_weight_choice.has('already_planned')and v_weight_choice.get_boolean('already_planned')then continue;end if;
        v_remaining:=RRL_STOCK_MATH.quantity(v_weight_choice.get_string('quantity'));
        v_weight_id:=v_weight_choice.get_string('choice_id');v_weight_uid:=v_weight_choice.get_string('source_uid');v_weight_cell:=v_weight_choice.get_string('source_cell');
       end if;
      end if;

      v_line_planned := 0;
      v_reserved_by_other := 0;
      v_requested_total := v_requested_total + v_requested_line_qty;

      insert into RRL_PICK_PLAN_LINE (
        PICK_PLAN_LINE_ID, PICK_PLAN_ID, CUSTOMER_ORDER_ROW_ID, ARTICUL,
        PRODUCT_NAME, REQUESTED_QTY, STATUS, CREATED_AT, CREATED_BY
      ) values (
        v_line_id, v_pick_plan_id, l.CUSTOMER_ORDER_ROW_ID, case when v_release='ACTIVE' then l.ARTICUL else upper(substr(l.ARTICUL, 1, 40)) end,
        l.PRODUCT_NAME, v_requested_line_qty, 'OPEN', sysdate, substr(p_created_by, 1, 50)
      );

      for c in (
        select r.rowid REMAIN_ROWID,
               r.CELL,
               r.UID_POLETA,
               r.REMAIN,
               p.EXPIRY_DATE,
               p.CREATION_DATE,
               p.PROD_BATCH_ID,
               p.SSCC,
               p.UNIT_COUNT,
               nvl(br.IS_SHIPMENT_ALLOWED, 1) IS_SHIPMENT_ALLOWED
          from RRL_REMAINS r
          join RRL_PALLETS p
            on p.UID_PALLET = r.UID_POLETA
          join RRL_CELLS cc on cc.CELL=r.CELL
          left join RRL_PROD_BATCH_READY_V br
            on br.PROD_BATCH_ID = p.PROD_BATCH_ID
         where r.REMAIN > 0
           and(v_weight_id is null or(r.UID_POLETA=v_weight_uid and r.CELL=v_weight_cell))
           and (v_release!='ACTIVE' or (cc.WARE_ID=v_order.WARE_ID and nvl(cc.BLOCKED_FOR_REMAINS,0)=0 and nvl(cc.BLOCKED_FOR_POPOLNENIE,0)=0 and r.BASE_UOM=v_uom))
           and ((v_release='ACTIVE' and p.ARTICUL=l.ARTICUL) or (v_release!='ACTIVE' and upper(p.ARTICUL)=upper(l.ARTICUL)))
           and (v_release!='ACTIVE' or RRL_STOCK_ELIGIBILITY.reason(r.UID_POLETA,r.CELL,v_order.WARE_ID,0,null,null,'ALLOCATE',null,p.ARTICUL) is null)
         order by case when v_strategy = 'FEFO' then p.EXPIRY_DATE end nulls last,
                  case when v_strategy = 'FIFO' then p.CREATION_DATE end nulls last,
                  r.TIME_OF_LAST_UPDATE nulls last,
                  r.UID_POLETA
      ) loop
        exit when v_remaining <= 0;
        if v_release='ACTIVE'then
         begin RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',c.UID_POLETA));
         exception when others then if sqlcode=-20850 then raise_application_error(-20890,'PICK_PLAN_SOURCE_CHANGED_RETRY');else raise;end if;end;
        end if;

        declare
          v_locked_remain number;
        begin
          if v_release='ACTIVE' then
           select REMAIN-HARD_RESERVED_BASE into v_locked_remain from RRL_REMAINS where rowid=c.REMAIN_ROWID;
          else
          select REMAIN
            into v_locked_remain
            from RRL_REMAINS
           where rowid = c.REMAIN_ROWID
           for update;
          end if;

          if c.IS_SHIPMENT_ALLOWED = 0 then
            log_decision(
              v_pick_plan_id,
              v_line_id,
              'SKIP_NOT_READY',
              'Pallet skipped because batch is not allowed for shipment',
              '{"pallet":"' || replace(c.UID_POLETA, '"', '\"') || '"}',
              p_created_by
            );
          else
            v_candidate_available := greatest(nvl(v_locked_remain, 0) - active_reserved_qty(c.UID_POLETA, l.ARTICUL, c.CELL), 0);
            v_reserved_by_other := v_reserved_by_other + (nvl(v_locked_remain, 0) - v_candidate_available);

            if v_candidate_available > 0 then
              v_reserve_qty := least(v_remaining, v_candidate_available);
              if v_weight_id is not null and v_reserve_qty!=RRL_STOCK_MATH.quantity(v_weight_choice.get_string('quantity'))then
               raise_application_error(-20886,'WEIGHT_PLAN_SELECTED_WHOLE_BOX_SOURCE_NOT_FREE');end if;

              if (v_release='ACTIVE' and v_reserve_qty=c.REMAIN and v_locked_remain=c.REMAIN
                  and active_reserved_qty(c.UID_POLETA,l.ARTICUL,c.CELL)=0)
                 or (v_release!='ACTIVE' and v_reserve_qty>=v_candidate_available) then
                v_task_type := 'FULL_PALLET';
              else
                v_task_type := 'CASE_PICK';
              end if;

              v_target_cell := null;
              v_pick_sequence := null;
              v_pick_face_id := null;
              v_pick_route_cell_id := null;

              if v_task_type = 'CASE_PICK' then
                if RRL_DIRECT_RECEIVING_PICK.enabled(c.UID_POLETA,c.CELL,v_order.WARE_ID,l.ARTICUL)=0 then
                RRL_PICK_TOPOLOGY_API.resolve_pick_face(
                  p_ware_id => v_order.WARE_ID,
                  p_articul => l.ARTICUL,
                  p_target_cell => v_target_cell,
                  p_pick_sequence => v_pick_sequence,
                  p_pick_face_id => v_pick_face_id,
                  p_pick_route_cell_id => v_pick_route_cell_id
                );

                end if;
                if v_target_cell is not null then
                  log_decision(
                    v_pick_plan_id,
                    v_line_id,
                    'PICK_FACE_SELECTED',
                    'Case-pick task assigned to configured pick face',
                    '{"articul":"' || replace(l.ARTICUL, '"', '\"') || '","targetCell":"' || replace(v_target_cell, '"', '\"') || '"}',
                    p_created_by
                  );
                else
                  log_decision(
                    v_pick_plan_id,
                    v_line_id,
                    case when RRL_DIRECT_RECEIVING_PICK.enabled(c.UID_POLETA,c.CELL,v_order.WARE_ID,l.ARTICUL)=1 then 'DIRECT_RECEIVING_SOURCE'else 'NO_PICK_FACE'end,
                    case when RRL_DIRECT_RECEIVING_PICK.enabled(c.UID_POLETA,c.CELL,v_order.WARE_ID,l.ARTICUL)=1 then 'Pick-by-line from admitted SAP receiving pallet; no replenishment'else 'No active pick face found for case-pick task'end,
                    '{"articul":"' || replace(l.ARTICUL, '"', '\"') || '"}',
                    p_created_by
                  );
                end if;
              end if;

              select RRL_PICK_TASK_SQ.nextval into v_task_id from dual;
              insert into RRL_PICK_TASK (
                PICK_TASK_ID, PICK_PLAN_ID, PICK_PLAN_LINE_ID, CUSTOMER_ORDER_ID, CUSTOMER_ID,
                TASK_TYPE, STATUS, ARTICUL, PALLET_UID, SSCC, PROD_BATCH_ID,
                SOURCE_CELL_CODE, TARGET_CELL_CODE, QTY, PICK_SEQUENCE,
                PICK_FACE_ID, PICK_ROUTE_CELL_ID, CREATED_AT, CREATED_BY
              ) values (
                v_task_id, v_pick_plan_id, v_line_id, p_customer_order_id, v_order.CUSTOMER_ID,
                v_task_type, 'NEW', case when v_release='ACTIVE' then l.ARTICUL else upper(substr(l.ARTICUL, 1, 40)) end, c.UID_POLETA,
                c.SSCC, c.PROD_BATCH_ID, c.CELL, v_target_cell, v_reserve_qty,
                v_pick_sequence, v_pick_face_id, v_pick_route_cell_id, sysdate, substr(p_created_by, 1, 50)
              );

              insert into RRL_PICK_RESERVATION (
                PICK_RESERVATION_ID, PICK_PLAN_ID, PICK_PLAN_LINE_ID, PICK_TASK_ID,
                CUSTOMER_ORDER_ID, CUSTOMER_ID, RESERVATION_LEVEL, RESERVATION_STATUS,
                RESERVATION_SCOPE, PALLET_UID, SSCC, ARTICUL, PROD_BATCH_ID,
                SOURCE_CELL_CODE, RESERVED_QTY, CREATED_AT, CREATED_BY
              ) values (
                RRL_PICK_RESERVATION_SQ.nextval, v_pick_plan_id, v_line_id, v_task_id,
                p_customer_order_id, v_order.CUSTOMER_ID, 'SOFT', 'ACTIVE',
                case when v_task_type = 'FULL_PALLET' then 'PALLET' else 'CASE' end,
                c.UID_POLETA, c.SSCC, case when v_release='ACTIVE' then l.ARTICUL else upper(substr(l.ARTICUL, 1, 40)) end, c.PROD_BATCH_ID,
                c.CELL, v_reserve_qty, sysdate, substr(p_created_by, 1, 50)
              );

              v_line_planned := v_line_planned + v_reserve_qty;
              v_remaining := v_remaining - v_reserve_qty;
            end if;
          end if;
        exception
          when no_data_found then
            null;
        end;
      end loop;

      v_line_shortage := greatest(v_requested_line_qty - v_line_planned, 0);
      v_planned_total := v_planned_total + v_line_planned;
      v_shortage_total := v_shortage_total + v_line_shortage;

      update RRL_PICK_PLAN_LINE
         set PLANNED_QTY = v_line_planned,
             FULL_PALLET_QTY = nvl((
               select sum(QTY)
                 from RRL_PICK_TASK
                where PICK_PLAN_LINE_ID = v_line_id
                  and TASK_TYPE = 'FULL_PALLET'
             ), 0),
             CASE_PICK_QTY = nvl((
               select sum(QTY)
                 from RRL_PICK_TASK
                where PICK_PLAN_LINE_ID = v_line_id
                  and TASK_TYPE = 'CASE_PICK'
             ), 0),
             SHORTAGE_QTY = v_line_shortage,
             STATUS = case
               when v_line_shortage = 0 then 'PLANNED_FULL'
               when v_line_planned > 0 then 'PLANNED_PARTIAL'
               else 'NO_STOCK'
             end,
             UPDATED_AT = sysdate,
             UPDATED_BY = substr(p_created_by, 1, 50)
       where PICK_PLAN_LINE_ID = v_line_id;

      if v_weight_id is not null then
       RRL_WEIGHT_PLAN_BIND.finish_bind(v_weight_id,v_pick_plan_id,v_line_id,p_created_by);
       log_decision(v_pick_plan_id,v_line_id,'WEIGHT_BOX_CHOICE','Approved exact whole-box planning target',v_weight_wire,p_created_by);
      end if;
      if v_line_shortage > 0 then
        insert into RRL_PICK_SHORTAGE (
          PICK_SHORTAGE_ID, PICK_PLAN_ID, PICK_PLAN_LINE_ID,
          CUSTOMER_ORDER_ID, CUSTOMER_ORDER_ROW_ID, CUSTOMER_ID, ARTICUL,
          REQUESTED_QTY, AVAILABLE_QTY, RESERVED_BY_OTHER_QTY, PLANNED_QTY,
          SHORTAGE_QTY, REASON_CODE, REASON_TEXT, CREATED_AT, CREATED_BY
        ) values (
          RRL_PICK_SHORTAGE_SQ.nextval, v_pick_plan_id, v_line_id,
          p_customer_order_id, l.CUSTOMER_ORDER_ROW_ID, v_order.CUSTOMER_ID,
          case when v_release='ACTIVE' then l.ARTICUL else upper(substr(l.ARTICUL, 1, 40)) end, v_requested_line_qty,
          v_line_planned, v_reserved_by_other, v_line_planned,
          v_line_shortage, case when v_weight_id is not null then 'WEIGHT_BOX_CHOICE_PENDING'else 'NO_FREE_STOCK'end,
          case when v_weight_id is not null then 'Approved final whole-box deviation; physical execution pending'else 'Free stock is not enough after active reservations'end,
          sysdate, substr(p_created_by, 1, 50)
        );
      end if;
    end loop;

    if v_release='ACTIVE'and v_requested_total=0 then raise_application_error(-20886,'PICK_ORDER_DEMAND_ALREADY_PLANNED_OR_SECURED');end if;
    if v_requested_total = 0 then
      v_status := 'NO_STOCK';
    elsif v_planned_total = 0 then
      v_status := 'NO_STOCK';
    elsif v_shortage_total > 0 then
      v_status := 'PLANNED_PARTIAL';
    else
      v_status := 'PLANNED_FULL';
    end if;

    update RRL_PICK_PLAN
       set STATUS = v_status,
           TOTAL_ORDER_QTY = v_requested_total,
           TOTAL_PLANNED_QTY = v_planned_total,
           TOTAL_SHORTAGE_QTY = v_shortage_total,
           UPDATED_AT = sysdate,
           UPDATED_BY = substr(p_created_by, 1, 50)
     where PICK_PLAN_ID = v_pick_plan_id;

    log_decision(
      v_pick_plan_id,
      null,
      'PLAN_CREATED',
      'Picking plan created with soft reservations',
      '{"requested":' || to_char(v_requested_total) || ',"planned":' || to_char(v_planned_total) || ',"shortage":' || to_char(v_shortage_total) || '}',
      p_created_by
    );

    if v_fenced then RRL_PICK_PLAN_ADMISSION.end_plan;end if;
    return v_pick_plan_id;
  exception when others then
    if v_mutating then rollback to rrl_pick_plan_begin;end if;
    if v_fenced then RRL_PICK_PLAN_ADMISSION.end_plan;end if;
    raise;
  end create_plan;

  procedure cancel_plan(
    p_pick_plan_id number,
    p_updated_by   varchar2 default null
  ) is
  begin
    declare st varchar2(20);j json_object_t:=json_object_t();src json_object_t:=json_object_t();m json_object_t:=json_object_t();result clob;kind varchar2(80);request clob;doc number;
    begin
      select STATE into st from RRL_STOCK_RELEASE where RELEASE_ID=1;
      if st='ACTIVE' then
        if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID') is not null then
          select COMMAND_TYPE,CANONICAL_REQUEST into kind,request from RRL_STOCK_OPERATION where OPERATION_ID=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');
          doc:=json_object_t.parse(request).get_object('source').get_number('document_id');
          if kind!='PICK_PLAN_CANCEL' or doc!=p_pick_plan_id then raise_application_error(-20863,'PLAN_CANCEL_CONTEXT_CONFLICT');end if;
        else
          j.put('contract_version',2);j.put('operation_id','PLAN.CANCEL:'||to_char(p_pick_plan_id,'TM9'));j.put('command_type','PICK_PLAN_CANCEL');j.put('actor',p_updated_by);
          src.put('document_type','PICK_PLAN');src.put('document_id',p_pick_plan_id);j.put('source',src);j.put('lines',json_array_t());j.put('units',json_array_t());
          m.put('reason','Picking plan cancelled');m.put('only_cancelled_replenishment',0);m.put_null('reservation_kind');j.put('metadata',m);
          RRL_STOCK_NATIVE_API.post(j.to_clob,p_updated_by,result);return;
        end if;
      end if;
    end;

    update RRL_PICK_RESERVATION
       set RESERVATION_STATUS = 'RELEASED',
           RELEASED_AT = sysdate,
           UPDATED_AT = sysdate,
           UPDATED_BY = substr(p_updated_by, 1, 50)
     where PICK_PLAN_ID = p_pick_plan_id
       and RESERVATION_STATUS = 'ACTIVE';

    update RRL_PICK_TASK
       set STATUS = 'CANCELLED',
           ERROR_TEXT = 'Plan cancelled before execution',
           UPDATED_AT = sysdate
     where PICK_PLAN_ID = p_pick_plan_id
       and STATUS in ('NEW', 'ASSIGNED');

    update RRL_PICK_PLAN
       set STATUS = 'CANCELLED',
           UPDATED_AT = sysdate,
           UPDATED_BY = substr(p_updated_by, 1, 50)
     where PICK_PLAN_ID = p_pick_plan_id
       and STATUS not in ('DONE');

    log_decision(
      p_pick_plan_id,
      null,
      'PLAN_CANCELLED',
      'Picking plan cancelled and active reservations released',
      null,
      p_updated_by
    );
  end cancel_plan;
end RRL_PICKING_API;


/

create or replace package RRL_ST_LAYOUT_READ as
 function scope_order(p_order number,p_actor varchar2,p_permission varchar2 default 'customer_order_view')return number;
 function snapshot(p_order number,p_row number,p_target number,p_actor varchar2)return clob;
end;
/

﻿create or replace package RRL_STOCK_ST_ROW_CMD accessible by(package RRL_STOCK_POSTING_API)as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/
