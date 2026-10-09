package RRL_PICK_TOPOLOGY_API as
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
