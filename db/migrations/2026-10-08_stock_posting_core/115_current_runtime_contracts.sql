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
 accessible by(package RRL_STOCK_RECEIPT_REVERSE,package RRL_STOCK_INVENTORY_BIRTH,package RRL_STOCK_INVENTORY_CMD,package RRL_STOCK_EVENT_BRIDGE,package RRL_STOCK_MES_MOVEMENT_CORE,package RRL_STOCK_RESERVATION_CMD,package RRL_STOCK_POSTING_API,package RRL_STOCK_MOVE_CORE,
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

create or replace package RRL_STOCK_RESERVE_CORE authid definer
 accessible by(package RRL_STOCK_CASE_RETURN_CMD,package RRL_STOCK_CASE_SHORT_CMD,package RRL_STOCK_WAVE_LAUNCH_CMD,package RRL_STOCK_MES_CANCEL_CMD,package RRL_STOCK_MES_SUPPLY_CMD,package RRL_STOCK_DOC_RESERVE_CMD,package RRL_STOCK_WAVE_CMD,package RRL_STOCK_EFFECT_CORE,package RRL_STOCK_RESERVATION_CMD,package RRL_STOCK_POSTING_API,package RRL_STOCK_MOVE_CORE,package RRL_STOCK_TRANSFER_CORE) as
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
 accessible by(package RRL_STOCK_RECEIPT_REVERSE,package RRL_STOCK_INVENTORY_BIRTH,package RRL_STOCK_WAVE_LAUNCH_CMD,package RRL_STOCK_INVENTORY_CMD,package RRL_STOCK_MES_SUPPLY_CMD,package RRL_STOCK_MES_MOVEMENT_CORE,package RRL_STOCK_RECEIPT_CORE,package RRL_STOCK_RESERVATION_CMD,package RRL_STOCK_POSTING_API,package RRL_STOCK_MOVE_CORE,
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

create or replace package RRL_STOCK_TRANSFER_CORE authid definer
 accessible by(package RRL_STOCK_CASE_RETURN_CMD,package RRL_STOCK_CASE_MOVE_CMD,package RRL_STOCK_CASE_PICK_CMD,package RRL_STOCK_INTERNAL_CMD,package RRL_STOCK_POSTING_API,package RRL_STOCK_TASK_CORE,
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

create or replace package RRL_STOCK_UNIT_CORE authid definer
 accessible by(package RRL_STOCK_CASE_RETURN_CMD,package RRL_STOCK_INVENTORY_BIRTH,package RRL_STOCK_CASE_SHORT_CMD,package RRL_STOCK_RECEIPT_REVERSE,package RRL_STOCK_WAVE_LAUNCH_CMD,package RRL_STOCK_INVENTORY_CMD,package RRL_STOCK_MES_CANCEL_CMD,package RRL_STOCK_MES_SUPPLY_CMD,package RRL_STOCK_DOC_RESERVE_CMD,package RRL_STOCK_WAVE_CMD,package RRL_STOCK_MES_MOVEMENT_CORE,package RRL_STOCK_INVARIANT_CORE,package RRL_STOCK_RESERVATION_CMD,package RRL_STOCK_TRANSFER_CORE,
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
 accessible by(package RRL_STOCK_POSTING_API) as
 function snapshot_stock(p_resources clob) return clob;
 procedure verify_posting(p_resources clob,p_before clob,p_operation varchar2);
end;
/

create or replace package RRL_STOCK_EFFECT_CORE authid definer
 accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_MES_MOVEMENT_CORE,
 package RRL_STOCK_SHIPPING_CORE,package RRL_STOCK_CORRECTION_CORE) as
 procedure consume(p_uid varchar2,p_cell varchar2,p_qty number,p_uom varchar2,p_uom_version number,p_warehouse number,
  p_actor varchar2,p_line number,p_reservation number default null,p_doc_type varchar2 default null,
  p_doc_id number default null,p_units clob default null,p_outgoing_doc number default null,p_pallet_row number default null);
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

create or replace package RRL_STOCK_SHIPPING_CORE authid definer
 accessible by(package RRL_STOCK_PALLET_QC_CMD,package RRL_STOCK_POSTING_API) as
 procedure compile_shipment(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_shipment(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_UOM_CONFIG authid definer as
 procedure publish(p_article varchar2,p_input varchar2,p_base varchar2,p_numerator number,p_denominator number,p_scale number,p_provenance varchar2);
end;
/

-- Extend existing replenishment rows. Do not recreate waves, plans, routes or warehouse tasks.
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

-- Inventory changes are measured per physical lot UID; no guessed distribution across lots.
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

-- Existing initial inventory import creates a declared lot; ordinary receipt remains SAP-only.
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

-- Rare metadata/placement changes take CONFIG X before any document or slot lock.
-- This grants no stock/configuration write context and cannot conduct quantities.
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

-- Approval of measured shortage; physical quantity remains unchanged.
create or replace package RRL_STOCK_CASE_SHORT_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

-- Existing quality facts and configured shipment share one root transaction.
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

-- No COMMIT/ROLLBACK or remote I/O: transaction belongs to the application command runner.
create or replace package RRL_STOCK_POSTING_API authid definer as
 procedure prepare_command(p_request clob,p_actor varchar2,p_replay out clob,p_hints clob default null);
 procedure execute_prepared(p_result out clob);
 procedure stage_birth(p_uid varchar2);
 procedure finish_birth_capture;
 procedure reset_connection;
end;
/

create or replace package RRL_STOCK_CASE_RETURN_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/
