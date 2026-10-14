set define off

CREATE OR REPLACE package ARTICULS is
  function ei(articul1 varchar2) return varchar2;
  function UPDATE_MOD(
    ID1             INTEGER,
    ARTICUL1        VARCHAR2,
    NAME1           VARCHAR2,
    SHT_IN_KOR1     NUMBER,
    SHT_WEIGHT1     NUMBER,
    KARTON_WEIGHT1  NUMBER,
    DELETED1        INTEGER,
    SHK_SHT1        VARCHAR2,
    SHK_KOR1        VARCHAR2,
    X               NUMBER,
    Y               NUMBER,
    Z               NUMBER,
    BRT_KOR         NUMBER
  ,p_actor varchar2 default null) return int;
  function event_on_change_picking_cell(articul1 varchar2, new_cell varchar2, current_cell varchar2, iser_id1 varchar2) return int;
  function eans(art1 varchar2) return varchar2;
end ARTICULS;
/


CREATE OR REPLACE package ARTICULS_SP_OLD accessible by(package ARTICULS) is
  function ei(articul1 varchar2) return varchar2;
  function UPDATE_MOD(
    ID1             INTEGER,
    ARTICUL1        VARCHAR2,
    NAME1           VARCHAR2,
    SHT_IN_KOR1     NUMBER,
    SHT_WEIGHT1     NUMBER,
    KARTON_WEIGHT1  NUMBER,
    DELETED1        INTEGER,
    SHK_SHT1        VARCHAR2,
    SHK_KOR1        VARCHAR2,
    X               NUMBER,
    Y               NUMBER,
    Z               NUMBER,
    BRT_KOR         NUMBER
  ) return int;
  function event_on_change_picking_cell(articul1 varchar2, new_cell varchar2, current_cell varchar2, iser_id1 varchar2) return int;
  function eans(art1 varchar2) return varchar2;
end ARTICULS_SP_OLD;
/


CREATE OR REPLACE package COMPL is
  function update_seq(articul1 varchar2, ware_id1 int, SQ1 int, SQGROUP int) return int;
  function show_sq(articul1 varchar2, ware_id1 int) return int;
  function show_sq_gr(articul1 varchar2, ware_id1 int) return int;
  function divide_st_bypal(stn varchar2, ware_id1 int) return int;
  function create_order_from_spallets(st_numb varchar2, user_id1 varchar2) return int;
  function path(articul1 varchar2, sborka_pallet_uid varchar2) return varchar2;
  function truncate_order_by_remains(ware_id6 int) return int;
  function orders_start_plan(ord_id1 int) return int;
  function orders_create_vycherk(ord_id1 int) return int;
  function orders_check(ware_id6 int) return int;
  function divide_order_bypal2(ord_id1 int, user_id11 varchar2) return int;
  function update_seq2(articul1 varchar2, cell1 varchar2, SQ1 int, SQGROUP int) return int;
  function add_art_2pall(articul1 varchar2) return int;
  function add_art_2pall(articul1 varchar2, count1 number, pall_uid1 varchar2, ware_id1 int, ord_number1 varchar2) return int;
  function order_rows_count(order_id1 int) return int;
  function order_vycherk_count(order_id1 int) return int;
  function reset_2_first_status(order_id1 int) return int;
  function debug_truncate_rem(articul1 varchar2, ware_id6 int) return number;
  function debug_truncate_reserv(articul1 varchar2, ware_id6 int) return number;
  function debug_truncate_orders(articul1 varchar2, ware_id6 int) return number;
  function RRL_GIVE_PALLET_UID(ST_NUMBER1 varchar2, USER_ID1 varchar2, PALLET_NUMBER1 int) return varchar2;
  function RRL_SBORKA_PAL_REMOVE_EMPTY(ST_NUMBER1 varchar2, USER_ID1 varchar2) return int;
  function RRL_COPY_PALLET_ROW3(row_id2 int, count1 number, PALLET_UID_NEW VARCHAR2) return int;
  function SET_SBORSHIK(PALLET_UID1 varchar2, SBORSHIK1 varchar2, user_id1 varchar2) return int;
  function pallet_compl_date(pall_uid varchar2) return date;
  function time_shift_start(time1 date) return date;
  function time_shift_end(time1 date) return date;
end COMPL;
/


CREATE OR REPLACE package CROSS_DOCKING is
  function SYNC_SBORKA_PALL(sb_pall_uid varchar2) return int;
  function SYNC_ARTICUL(articul1 varchar2) return int;
  function SYNC_MOD(mod_id1 int) return int;
  function SYNC_SBOR_PALL_ROW(row_id1 int) return int;
end CROSS_DOCKING;
/


CREATE OR REPLACE package        DOCK_PLANNING is

   function IS_AUTO_PLAN_DOCK(  TT_ID int) return int ;


end DOCK_PLANNING;
/


CREATE OR REPLACE PACKAGE        GOODS_TO_PICK is

id1 int;
tmp int;

function delete_wtasks( summary_task_id1 int ) return int ;
 function add_summary_task( ware_id1 int)  return int ;
 function add_pallet_2_summary_task(  PUID varchar2 , summary_task_id1 int ) return int;
 function add_pallet_2_summary_task2(  PUID varchar2   ) return int;
 function distance_2_pick( CELL1 varchar2 , ware_id1 int ) return number;
 function get_opened_summary_task(ware_id1 int) return int;
function create_wtasks( summary_task_id1 int ) return int;
function update_wt_row( summary_task_id1 int , 
       articul1 varchar2 , QUANTITY1 number , QUANTITY_PLANNED1 number ,
       QUANTITY_COMPLETE1 number  ) return int ;






END GOODS_TO_PICK;
/


CREATE OR REPLACE package HELP is
  function update_object(
    OBJECT_NAME1 varchar2,
    BUSINESS_FIELD1 varchar2,
    PARENT_OBJECT1 varchar2,
    COMMENT11 varchar2,
    TYPE2 varchar2,
    ARTICLE2 varchar2
  ) return int;
end HELP;
/


CREATE OR REPLACE package ORDERS is
  function cleanup_order(ord_id int) return int;
  function DELETE_PALLETS(ST_NUMBER1 varchar2, user_id1 varchar2) return varchar2;
  function create_order(
    st_numb1 varchar2,
    CREATE_DATE1 date,
    WARE_ID1 integer,
    ADDR1 varchar2,
    STATE1 varchar2,
    ORDDATE1 date,
    user_id1 varchar2
  ) return int;
  function add_order_row(ord_id int, ARTICUL1 varchar2, QUANTITY1 number, WARE_ID1 int) return int;
  function cleanup_order2(ord_number1 varchar2) return int;
  function contains_invalid_logo(ord_number1 varchar2) return int;
  function wares_of_order(ord_number1 varchar2) return varchar2;
  function count_of_sq_gr(ord_number1 varchar2) return int;
  function get_unfinished_quantity(articul1 varchar2, from_date1 date) return number;
  function get_unfinished_quantityo(articul1 varchar2, from_date1 date) return number;
end ORDERS;
/


CREATE OR REPLACE package PALL_SPLITTER is
  function show_sq_gr(articul1 varchar2, ware_id1 int) return int;
  function is_pallet_has_full_pallet_row(pallet_uid1 varchar2) return int;
  function add_row_2sborka_pallets(articul1 varchar2, count1 number, pall_uid1 varchar2, ware_id1 int, ord_number1 varchar2) return int;
  function create_return_task(supp_inn varchar2, user_id1 varchar2, ware_id1 int) return varchar2;
  function split_ufa(ord_number1 varchar2, ware_id2 int) return int;
  function split_vegetables(ord_number1 varchar2, ware_id2 int) return int;
end PALL_SPLITTER;
/


CREATE OR REPLACE package pk_pivot
--AUTHID CURRENT_USER
as
  --code based on famous Tom Kyte's books examples
  --but not copy-pasted from there

  type refcursor is ref cursor;

  type array is table of varchar2(30);

  type array_varchar2 is table of varchar2(255);

  function pivotsql( p_query in varchar2, --query string which returns data you want to make crosstab on
                     p_rowfields in varchar2, --row fields separated by comma
                     p_columnfield in varchar2, --one column field
                     p_function in varchar2, --aggregate function ('SUM','AVG','COUNT','MIN','MAX')
                     p_functionfield in varchar2, --field for aggregate function
                     p_page in number default 1 --page from right to left (not all columns can be shown on one page)
                   ) return varchar2;                                                                                                 --returns query text for crosstab
/*
example:
SELECT PK_CROSSTAB.PivotSQL('SELECT * FROM scott.emp','empno','job','sum','sal') FROM SYS.DUAL

--------
SELECT deptno
,sum(DECODE(job,'BOSS',sal,null)) as BOSS
,sum(DECODE(job,'FIN',sal,null)) as FIN
,sum(DECODE(job,'HR',sal,null)) as HR
,sum(DECODE(job,'Sales',sal,null)) as Sales
FROM (SELECT * FROM scott.emp)
GROUP BY deptno
ORDER BY deptno
*/

end;
/


CREATE OR REPLACE package PRIHOD is
  function prihod_is_closed(ord_id int) return int;
  function close_price_control(prih_id int) return int;
  function set_brak_perc_new(puid1 varchar2, new_perc number, reason_id int) return int;
  function set_dock(prih_id int, h_dock varchar2) return int;
  function set_ware_id(prih_id int, new_ware_id int) return int;
  function set_priority(prih_id int, new_priority_id int, new_user_id varchar2) return int;
  function set_prihod_kpp(prihod_id int, kpp_n varchar2) return int;
  function is_prihod_fresh(prihod_id int) return varchar2;
  function prihod_pall_count(prihod_naklad_id int) return int;
  function get_brak_reason(reason_id int) return varchar2;
  function order_zakaz_number(prihod_naklad_id int) return varchar2;
end PRIHOD;
/


CREATE OR REPLACE package REMAINS is
  function create_snapshot(type2 int) return int;
  function close_snapshot(snap_shot_id1 int) return int;
  function add_row_2_snapshot(snap_shot_id1 int, cell1 varchar, articul1 varchar2) return int;
  function remains_free(articul1 varchar2) return number;
  function remains_in_otbor(articul1 varchar2) return number;
  function remains_in_otbor_all(articul1 varchar2) return number;
  function remains_free_all(articul1 varchar2) return number;
  function remains_partion_in_cell(pallet_uid1 varchar2, cell3 varchar2) return number;
  function remains_partion_in_otbor(pallet_uid1 varchar2) return number;
  function remains_except_part_in_otb(pallet_uid1 varchar2) return number;
  function close_othod_pallet(PALLET_ID1 varchar2, iser_id21 varchar2,p_operation_id varchar2 default null) return varchar2;
  function trial_by_weight(PALLET_UID1 varchar2, TRIAL_WEIGHT1 varchar2, WOOD_WEIGHT1 varchar2, user_id1 varchar2,p_operation_id varchar2 default null) return int;
  function set_scan_proove(PALLET_UID1 varchar2, count_of_errors1 int, prim1 varchar2, SBORSHIK1 varchar2, KLADOVSHIK1 varchar2,p_operation_id varchar2 default null) return int;
  function othod_pallet_podbor_partii(PALLET_ID1 varchar2) return int;
  function move_pall_2_picking_cell(pall_uid1 varchar2, user_id2 varchar2,p_operation_id varchar2 default null) return varchar2;
  function close_othod_pall_row(PALLET_ROW_ID1 int, prih_pall_uid5 varchar2, kolvo_provod number, iser_id21 varchar2) return int;
  function OTHOD_PALLET_PODBOR_PARTI4CELL(PALLET_ID1 varchar2, cell1 varchar2) return int;
  function get_remains_text(articul1 varchar2) return varchar2;
  function turnover_now(articul1 varchar2) return number;
  function remains_of_prihods(articul1 varchar2, d_from date, d_to date) return number;
  function storno_op(pall_uid1 varchar2, user_id1 varchar2) return int;
end REMAINS;
/


CREATE OR REPLACE package REVIZION is

  
  
  
  
function revision_cond( rev_id int ) return int ;
function clear_cell2( cell1 varchar2     ) return int;
function clear_cell( cell1 varchar2 , puid varchar2   ) return int ;
function add_row_2_revizion( cell1 varchar2 , revision_id1 int   ) return int;
function create_revizion( ware_id1 int , user_id1 varchar2 ) return int ;
function revision_cell_kor( cell1 varchar2 , revision_id1 int ,  count2 number , user_id3 varchar2 ,p_operation_id varchar2 default null) return varchar2 ;
function add_row_2_reviz_type_art( cell1 varchar2 , revision_id1 int   ) return int;
function  RRL_REVIZION_CELL_PALL( articul1 varchar2, CELL1 varchar2 , count_pal int , 
   revision_row_id1 int , user_id1 varchar2 ) return varchar2 ;
   
function add_row_2_reviz_type_art2( cell1 varchar2 , articul2 varchar2 , revision_id1 int   ) return int ;
function articul_name( art varchar2 ) return varchar2;
function update_revision_row( cell1 varchar2 , articul2 varchar2 ,  revision_rowid int ,  rev_id2 int   ) return int;
function CreateNaklad_2_revizion( rev_id1 int ) return int ;
function revision_cell_sht_deleted( cell1 varchar2 , revision_id1 int , count2 number , user_id3 varchar2 ,p_operation_id varchar2 default null) return varchar2 ;
function  RRL_REVIZION_CELL_SHT( articul1 varchar2, CELL1 varchar2 , count_sht number , revision_row_id1 int , user_id1 varchar2 ,p_operation_id varchar2 default null) return varchar2;
function  RRL_REVIZION_CLEAR_MINUS( revision_id1 int , user_id1 varchar2 ) return int ;

FUNCTION  RRL_INV_CREATE_LINE5 
( 
    cell1 varchar2 ,
    articul2 varchar2,
    count1 NUMBER ,
    expiury_date date ,
    fasovka_id1 int ,
    brak_perc1 number ,
    pall_weight1 number , 
    pall_n int ,
    tn_weight1 number ,
    count_kor1 number ,
    user_id2 varchar2 , 
    NAKLAD_ID int
,p_operation_id varchar2 default null) return varchar2;

function rev_create_snap_shot_after( rev_id int ) return int ;
function rev_create_snap_shot_before( rev_id int ) return int ;
FUNCTION  close_revision( rev_id int ) return int;

function remain_after( rev_id int ,articul1 varchar2 , cell1 varchar2  ) return number  ;
function remain_before( rev_id int ,articul1 varchar2 , cell1 varchar2  ) return number  ;


end REVIZION;
/


CREATE OR REPLACE package REVIZION_SP_OLD accessible by(package REVIZION) is

  
  
  
  
function revision_cond( rev_id int ) return int ;
function clear_cell2( cell1 varchar2     ) return int;
function clear_cell( cell1 varchar2 , puid varchar2   ) return int ;
function add_row_2_revizion( cell1 varchar2 , revision_id1 int   ) return int;
function create_revizion( ware_id1 int , user_id1 varchar2 ) return int ;
function revision_cell_kor( cell1 varchar2 , revision_id1 int ,  count2 number , user_id3 varchar2 ) return varchar2 ;
function add_row_2_reviz_type_art( cell1 varchar2 , revision_id1 int   ) return int;
function  RRL_REVIZION_CELL_PALL( articul1 varchar2, CELL1 varchar2 , count_pal int , 
   revision_row_id1 int , user_id1 varchar2 ) return varchar2 ;
   
function add_row_2_reviz_type_art2( cell1 varchar2 , articul2 varchar2 , revision_id1 int   ) return int ;
function articul_name( art varchar2 ) return varchar2;
function update_revision_row( cell1 varchar2 , articul2 varchar2 ,  revision_rowid int ,  rev_id2 int   ) return int;
function CreateNaklad_2_revizion( rev_id1 int ) return int ;
function revision_cell_sht_deleted( cell1 varchar2 , revision_id1 int , count2 number , user_id3 varchar2 ) return varchar2 ;
function  RRL_REVIZION_CELL_SHT( articul1 varchar2, CELL1 varchar2 , count_sht number , revision_row_id1 int , user_id1 varchar2 ) return varchar2;
function  RRL_REVIZION_CLEAR_MINUS( revision_id1 int , user_id1 varchar2 ) return int ;

FUNCTION  RRL_INV_CREATE_LINE5 
( 
    cell1 varchar2 ,
    articul2 varchar2,
    count1 NUMBER ,
    expiury_date date ,
    fasovka_id1 int ,
    brak_perc1 number ,
    pall_weight1 number , 
    pall_n int ,
    tn_weight1 number ,
    count_kor1 number ,
    user_id2 varchar2 , 
    NAKLAD_ID int
) return varchar2;

function rev_create_snap_shot_after( rev_id int ) return int ;
function rev_create_snap_shot_before( rev_id int ) return int ;
FUNCTION  close_revision( rev_id int ) return int;

function remain_after( rev_id int ,articul1 varchar2 , cell1 varchar2  ) return number  ;
function remain_before( rev_id int ,articul1 varchar2 , cell1 varchar2  ) return number  ;


end REVIZION_SP_OLD;
/


CREATE OR REPLACE package RRL_API_AUDIT_API as
  function start_call(
    p_request_id             varchar2,
    p_replay_of_call_id      number default null,
    p_replay_run_id          varchar2 default null,
    p_method                 varchar2,
    p_path                   varchar2,
    p_query_string           varchar2 default null,
    p_url                    varchar2 default null,
    p_client_ip              varchar2 default null,
    p_user_agent             varchar2 default null,
    p_request_headers_json   clob default null,
    p_request_body           clob default null,
    p_request_body_sha256    varchar2 default null,
    p_request_body_truncated number default 0,
    p_replayable             number default 1,
    p_local_log_path         varchar2 default null
  ) return number;

  procedure finish_call(
    p_api_call_id            number,
    p_response_status        number default null,
    p_response_headers_json  clob default null,
    p_response_body          clob default null,
    p_response_body_truncated number default 0,
    p_error_text             varchar2 default null,
    p_status                 varchar2 default 'DONE',
    p_duration_ms            number default null,
    p_local_log_path         varchar2 default null
  );

  procedure mark_replay_result(
    p_source_call_id         number,
    p_replay_call_id         number default null,
    p_error_text             varchar2 default null
  );
end RRL_API_AUDIT_API;
/


CREATE OR REPLACE package RRL_BOM_API as
  function create_bom(
    p_bom_code         varchar2,
    p_bom_name         varchar2 default null,
    p_target_articul   varchar2,
    p_target_mod_id    number default null,
    p_target_gtin      varchar2 default null,
    p_bom_kind         varchar2 default 'FINISHED_GOODS',
    p_base_qty         number,
    p_base_unit_code   varchar2 default 'KG',
    p_is_primary       number default 0,
    p_valid_from       date,
    p_valid_to         date default null,
    p_ware_id          number default null,
    p_production_line  varchar2 default null,
    p_comment_text     varchar2 default null,
    p_created_by       varchar2 default null
  ) return number;

  procedure update_bom(
    p_bom_id           number,
    p_bom_code         varchar2 default null,
    p_bom_name         varchar2 default null,
    p_target_articul   varchar2 default null,
    p_target_mod_id    number default null,
    p_target_gtin      varchar2 default null,
    p_bom_kind         varchar2 default null,
    p_base_qty         number default null,
    p_base_unit_code   varchar2 default null,
    p_is_primary       number default null,
    p_valid_from       date default null,
    p_valid_to         date default null,
    p_ware_id          number default null,
    p_production_line  varchar2 default null,
    p_comment_text     varchar2 default null,
    p_updated_by       varchar2 default null
  );

  function add_line(
    p_bom_id             number,
    p_line_no            number default null,
    p_component_type     varchar2 default 'RAW',
    p_component_articul  varchar2 default null,
    p_component_mod_id   number default null,
    p_component_name     varchar2 default null,
    p_qty_per_base       number default null,
    p_unit_code          varchar2 default null,
    p_loss_percent       number default 0,
    p_min_tolerance_pct  number default null,
    p_max_tolerance_pct  number default null,
    p_is_required        number default 1,
    p_substitution_group varchar2 default null,
    p_replacement_ratio  number default null,
    p_comment_text       varchar2 default null,
    p_created_by         varchar2 default null
  ) return number;

  procedure update_line(
    p_bom_line_id        number,
    p_line_no            number default null,
    p_component_type     varchar2 default null,
    p_component_articul  varchar2 default null,
    p_component_mod_id   number default null,
    p_component_name     varchar2 default null,
    p_qty_per_base       number default null,
    p_unit_code          varchar2 default null,
    p_loss_percent       number default null,
    p_min_tolerance_pct  number default null,
    p_max_tolerance_pct  number default null,
    p_is_required        number default null,
    p_substitution_group varchar2 default null,
    p_replacement_ratio  number default null,
    p_comment_text       varchar2 default null,
    p_updated_by         varchar2 default null
  );

  procedure delete_line(
    p_bom_line_id number,
    p_deleted_by  varchar2 default null
  );

  procedure approve_bom(
    p_bom_id      number,
    p_approved_by varchar2 default null
  );

  procedure block_bom(
    p_bom_id     number,
    p_reason     varchar2 default null,
    p_updated_by varchar2 default null
  );

  procedure archive_bom(
    p_bom_id     number,
    p_reason     varchar2 default null,
    p_updated_by varchar2 default null
  );

  procedure make_primary(
    p_bom_id     number,
    p_updated_by varchar2 default null
  );

  function clone_bom(
    p_source_bom_id number,
    p_bom_code      varchar2,
    p_valid_from    date,
    p_valid_to      date default null,
    p_created_by    varchar2 default null
  ) return number;

  function find_primary_bom(
    p_target_articul  varchar2,
    p_planned_date    date default null,
    p_target_mod_id   number default null,
    p_ware_id         number default null,
    p_production_line varchar2 default null
  ) return number;
end RRL_BOM_API;
/


CREATE OR REPLACE package RRL_BOX_ASSEMBLY_READ authid definer as
 function clocks_json(p_tree clob,p_ware number,p_region varchar2)return clob;
end;
/


CREATE OR REPLACE package RRL_CASE_PALLET_TYPE_READ authid definer as
 function describe_type(p_task number,p_actor varchar2)return clob;
end;
/


CREATE OR REPLACE package RRL_CASE_RESOURCE_POLICY authid definer as
 function context_json(p_task number,p_action varchar2,p_actor varchar2,p_resource number default null,p_session number default null,p_equipment number default null) return clob;
end;
/


CREATE OR REPLACE package RRL_CASE_ROUTE_ADMISSION authid definer accessible by(package RRL_STOCK_CASE_PICK_CMD) as
 procedure assert_next(p_case number,p_line number);
end;
/


CREATE OR REPLACE package RRL_CASE_SCALE_ADMISSION authid definer as
 procedure assert_capture(p_request clob,p_previous number);
 procedure claim_capture(p_request clob,p_operation varchar2,p_previous number);
end;
/


CREATE OR REPLACE package RRL_CASE_SSCC_API authid definer as
 procedure issue(p_task number,p_request clob,p_actor varchar2,p_result out clob);
 procedure confirm_label(p_task number,p_sscc varchar2,p_actor varchar2,p_result out clob);
 procedure assert_ready(p_task number);
end;
/


CREATE OR REPLACE package RRL_CASE_TASK_ACCESS authid definer as
 procedure assert_scope(p_task number,p_actor varchar2,p_permission varchar2,p_assignee varchar2 default null);
 procedure assert_command(p_request clob,p_actor varchar2);
end;
/


CREATE OR REPLACE package RRL_CASE_WEIGHT_DECISION authid definer as
 function current_json(p_request clob,p_task number,p_line number,p_actor varchar2)return clob;
 procedure plan_order(p_order number,p_article varchar2,p_resources in out json_array_t);
end;
/


CREATE OR REPLACE package RRL_CASE_WEIGHT_SCAN authid definer as
 procedure assert_scan(p_request clob,p_article varchar2,p_line number,p_previous number);
end;
/


CREATE OR REPLACE package RRL_CLUSTER_CREATE_API authid definer as
 function write_allowed(p_operation varchar2)return number;
 procedure create_cluster(p_operation varchar2,p_actor varchar2,p_request clob,p_sts clob,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_CUSTOMER_ORDER_API as
  function normalize_key(p_value varchar2) return varchar2 deterministic;

  function ensure_customer_from_legacy_addr(
    p_legacy_addr varchar2,
    p_created_by  varchar2 default null
  ) return number;

  function import_legacy_order(
    p_legacy_order_id number,
    p_created_by      varchar2 default null
  ) return number;

  procedure sync_fulfillment_from_legacy(
    p_customer_order_id number,
    p_created_by        varchar2 default null
  );
end RRL_CUSTOMER_ORDER_API;
/


CREATE OR REPLACE package RRL_CUSTOMER_RULE_API as
  function resolve_vehicle_type(
    p_customer_id           number,
    p_customer_store_map_id number default null
  ) return number;

  function split_order_by_pallet_capacity(
    p_customer_order_id  number,
    p_total_pallet_count number,
    p_vehicle_type_id    number default null,
    p_created_by         varchar2 default null
  ) return number;
end RRL_CUSTOMER_RULE_API;
/


CREATE OR REPLACE package RRL_DAY_INSPECT_API authid definer as
 function write_allowed(p_operation varchar2,p_actor varchar2) return number;
 procedure lookup(p_actor varchar2,p_operation varchar2,p_body clob,p_result out clob);
 procedure resolve(p_actor varchar2,p_operation varchar2,p_body clob,p_result out clob);
 procedure append_inspection(p_actor varchar2,p_operation varchar2,p_body clob,p_current_hash varchar2,p_checked_at varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_DAY_REVIEW_API authid definer as
 function write_allowed return number;
 procedure context(p_ware number,p_day date,p_zone varchar2,p_actor varchar2,p_result out clob);
 procedure lookup(p_actor varchar2,p_operation varchar2,p_body clob,p_result out clob);
 procedure resolve(p_actor varchar2,p_operation varchar2,p_body clob,p_result out clob);
 procedure append_review(p_actor varchar2,p_operation varchar2,p_body clob,p_material clob,p_captured timestamp with time zone,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_DIRECT_RECEIVING_PICK authid definer
 accessible by(package RRL_PICKING_API,package RRL_STOCK_WAVE_LAUNCH_CMD) as
 function enabled(p_uid varchar2,p_cell varchar2,p_ware number,p_article varchar2)return number;
 procedure compile_holds(p_wave number,p_resources in out nocopy json_array_t,p_holds out clob);
 procedure apply_holds(p_holds clob,p_actor varchar2);
end;
/


CREATE OR REPLACE package RRL_FORECAST_PROJECTOR authid definer as
 function load_write_allowed(p_load varchar2)return number;
 function day_write_allowed(p_ware number,p_day date)return number;
 procedure project_load(p_load varchar2,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_FORECAST_SOURCE_RULES authid definer
 accessible by(package RRL_FORECAST_PROJECTOR)as
 procedure compile_leaves(p_tree clob,p_ware number,p_leaves out clob);
end;
/


CREATE OR REPLACE package RRL_HU_PACK_CLOCK authid definer as
 procedure begin_empty_box(p_uid varchar2,p_operation varchar2,p_actor varchar2);
 function clock_json(p_uid varchar2,p_version number)return json_object_t;
 function writing return boolean;
end;
/


CREATE OR REPLACE package RRL_INTERWARE_DEPART_GATE authid definer as
 function promises(p_trip number)return clob;
 procedure assert_ready(p_promises clob);
end;
/


CREATE OR REPLACE package RRL_INTERWARE_INCIDENT_API authid definer as
 function write_allowed return number;
 procedure close_case(p_operation varchar2,p_actor varchar2,p_request clob,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_INTERWARE_MARK_SCAN authid definer as
 function required_for_article(p_article varchar2) return number;
 function required_for_plan(p_domain clob) return number;
 procedure validate_scan(p_domain clob,p_metadata clob,p_unit_count out number);
end;
/


CREATE OR REPLACE package RRL_INTERWARE_ROUTING authid definer as
 function target_trip(p_plan varchar2)return number;
 function outbound_dock(p_plan varchar2)return varchar2;
 function ready_due(p_plan varchar2)return timestamp with time zone;
 function resolved(p_plan RRL_INTERWARE_PLAN%rowtype)return RRL_INTERWARE_PLAN%rowtype;
 procedure record_decision(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_INTERWARE_THERMAL authid definer as
 function mode_json(p_plan varchar2)return clob;
 procedure assert_release(p_plan varchar2);
 procedure assert_cell(p_mode clob,p_ware number,p_cell varchar2);
 procedure record_decision(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_INTERWARE_UNIT_SOURCE authid definer as
 procedure assert_scope(p_load varchar2,p_actor varchar2);
 procedure capture_plan(p_plan varchar2,p_actor varchar2);
 function plan_manifest(p_plan varchar2,p_actor varchar2)return clob;
 function issued_manifest(p_load varchar2,p_uid varchar2,p_snapshot clob)return clob;
end;
/


CREATE OR REPLACE package RRL_IW_AGG_SCAN authid definer accessible by(package RRL_INTERWARE_MARK_SCAN,package RRL_STORE_RETURN_UNIT_CORE,package RRL_STORE_AGG_SCAN)as

 procedure expand(p_metadata clob,p_scans out clob);

end;
/


CREATE OR REPLACE package RRL_IW_GROUP_ARCHIVE authid definer accessible by(package RRL_IW_GROUP_SOURCE,package RRL_IW_GROUP_REC)as
 function snapshot_json(p_load varchar2)return clob;
end;
/


CREATE OR REPLACE package RRL_IW_GROUP_CUSTODY_CORE authid definer accessible by(package RRL_STOCK_INTERWARE_CUSTODY)as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_IW_GROUP_FACT_GUARD authid definer as
 procedure assert_head(p_operation varchar2,p_plan varchar2,p_uid varchar2,p_ware number,p_actor varchar2,p_kind varchar2,p_cell varchar2 default null,p_unload varchar2 default null);
end;
/


CREATE OR REPLACE package RRL_IW_GROUP_NEXT authid definer accessible by(package RRL_STOCK_INTERWARE_NEXT)as
 function describe_source(p_st number,p_ware number)return json_object_t;
 procedure declare_source(p_source json_object_t,p_operation varchar2,p_resources in out nocopy json_array_t);
 procedure validate_load(p_source json_object_t,p_actor varchar2);
 procedure dispatched(p_source json_object_t,p_actor varchar2);
end;
/


CREATE OR REPLACE package RRL_IW_GROUP_PUT authid definer accessible by(package RRL_STOCK_HU_TASK)as
 procedure describe_receipt(p_receipt varchar2,p_target varchar2,p_actor varchar2,p_task number,p_domain out json_object_t);
 procedure declare_rows(p_domain json_object_t,p_operation varchar2,p_resources in out nocopy json_array_t);
 procedure validate_receipt(p_domain json_object_t,p_actor varchar2,p_task number);
 procedure record_plan(p_operation varchar2,p_task number,p_domain json_object_t,p_actor varchar2);
 procedure record_complete(p_operation varchar2,p_task number,p_domain json_object_t,p_actor varchar2);
end;
/


CREATE OR REPLACE package RRL_IW_GROUP_PUT_GUARD authid definer as
 procedure assert_fact(p_operation varchar2,p_receipt varchar2,p_task number,p_uid varchar2,p_ware number,p_target varchar2,p_actor varchar2,p_planning number);
end;
/


CREATE OR REPLACE package RRL_IW_GROUP_REC authid definer accessible by(package RRL_STOCK_INTERWARE_REC)as
 procedure describe_source(p_request clob,p_actor varchar2,p_domain out json_object_t);
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure assert_fresh(p_request clob,p_actor varchar2,p_domain json_object_t);
end;
/


CREATE OR REPLACE package RRL_IW_GROUP_SOURCE authid definer as
 function source_json(p_load varchar2,p_actor varchar2)return clob;
end;
/


CREATE OR REPLACE package RRL_IW_GROUP_THERMAL authid definer as
 procedure assert_cell(p_ware number,p_article varchar2,p_cell varchar2);
end;
/


CREATE OR REPLACE package RRL_IW_HU_REC_CORE authid definer accessible by(package RRL_STOCK_INTERWARE_REC)as
 procedure declare_rows(p_domain json_object_t,p_operation varchar2,p_resources in out nocopy json_array_t);
 procedure restore(p_domain json_object_t,p_operation varchar2,p_actor varchar2);
end;
/


CREATE OR REPLACE package RRL_IW_HU_SOURCE authid definer as
 function stock_uid(p_load varchar2)return varchar2;
 function context_json(p_load varchar2)return clob;
 procedure capture_context(p_load varchar2,p_actor varchar2,p_context out clob);
 procedure assert_context(p_load varchar2,p_context clob);
end;
/


CREATE OR REPLACE package RRL_IW_SHORTAGE_GUARD authid definer as
 procedure require_command(p_operation varchar2,p_kind varchar2);
end;
/


CREATE OR REPLACE package RRL_MES_PRODUCTION_API as

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


CREATE OR REPLACE package RRL_MES_RAW_SUPPLY_API authid definer as
 function release_to_production(p_production_order_id number,p_to_ware_id number default null,
  p_to_cell varchar2 default 'MES_PROD',p_allow_partial number default 0,p_created_by varchar2 default null,p_operation_id varchar2 default null) return number;
end;
/


CREATE OR REPLACE package RRL_MES_RAW_SUPPLY_OLD authid definer
 accessible by(package RRL_MES_RAW_SUPPLY_API) as
 function release_to_production(p_production_order_id number,p_to_ware_id number default null,p_to_cell varchar2 default 'MES_PROD',p_allow_partial number default 0,p_created_by varchar2 default null) return number;
end;
/


CREATE OR REPLACE package RRL_NORM_COST_CORRECTION authid definer as
 function confirmed_total(p_cost varchar2)return number;
 procedure validate_report(p_cost varchar2,p_ware number,p_kind varchar2,p_object number,p_currency varchar2,p_delta number,p_expected number);
 procedure validate_decision(p_expense varchar2,p_phase varchar2,p_outcome varchar2);
end;
/


CREATE OR REPLACE package RRL_ORDER_WEIGHT_READ authid definer as
 function snapshot_json(p_task number,p_line number,p_actor varchar2)return clob;
end;
/


CREATE OR REPLACE package RRL_OUTBOX_DELIVERY_API authid definer as
 function write_allowed(p_event number)return number;
 procedure claim_next(p_worker varchar2,p_target varchar2,p_seconds number,p_result out clob);
 procedure begin_attempt(p_event number,p_version number,p_worker varchar2,p_system varchar2,p_kind varchar2,
  p_business varchar2,p_cert varchar2,p_thumb varchar2,p_signature varchar2,p_request clob,p_request_id out number);
 procedure finish_attempt(p_event number,p_version number,p_worker varchar2,p_request_id number,p_body clob,p_result out clob);
 procedure manual_retry(p_event number,p_actor varchar2,p_reason varchar2);
end;
/


CREATE OR REPLACE package RRL_OUTGOING_QC_ACCESS authid definer as
 procedure assert_identifier(p_identifier varchar2,p_actor varchar2);
end;
/


CREATE OR REPLACE package RRL_PALLET_FLOOR_READ authid definer as
 function scope_warehouse(p_uid varchar2,p_actor varchar2)return number;
 function describe_type(p_uid varchar2,p_actor varchar2)return clob;
end;
/


CREATE OR REPLACE package RRL_PALLET_TYPE_API authid definer as
 procedure upsert_request(p_request clob,p_actor varchar2,p_id out number);
end;
/


CREATE OR REPLACE package RRL_PICKING_API as
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


CREATE OR REPLACE package RRL_PICK_PLAN_ACCESS authid definer as
 procedure assert_scope(p_order number,p_actor varchar2,p_permission varchar2 default 'pick_plan_create');
end;
/


CREATE OR REPLACE package RRL_PICK_PLAN_ADMISSION authid definer as
 procedure begin_plan(p_order number,p_actor varchar2);
 procedure end_plan;
end;
/


CREATE OR REPLACE package RRL_PICK_PLAN_CREATE_API authid definer as
 function create_command(p_operation varchar2,p_order number,p_strategy varchar2,p_actor varchar2)return number;
 procedure assert_write(p_operation varchar2);
 function current_operation return varchar2;
 function cached_plan return number;
end;
/


CREATE OR REPLACE package RRL_PICK_RANGE_APPLY_CORE authid definer
 accessible by(package RRL_PICK_RANGE_PROPOSAL_API)as
 procedure apply_change(p_operation varchar2,p_actor varchar2,p_action varchar2,p_ware number,p_article varchar2,
  p_request clob,p_source clob,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_PICK_RANGE_POLICY authid definer as
 function target_write_allowed(p_cell varchar2,p_article varchar2,p_repl number,p_quantity number)return number;
 function new_target_allowed(p_cell varchar2,p_article varchar2,p_exclude_repl number default null)return number;
end;
/


CREATE OR REPLACE package RRL_PICK_RANGE_PROPOSAL_API authid definer as
 function write_allowed return number;
 procedure execute_command(p_operation varchar2,p_actor varchar2,p_action varchar2,p_ware number,p_article varchar2,
  p_request clob,p_source clob,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_PICK_TOPOLOGY_API as
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


CREATE OR REPLACE package RRL_PICK_WAVE_API as
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


CREATE OR REPLACE package RRL_PICK_WAVE_META authid definer accessible by(package RRL_STOCK_DOC_RESERVE_CMD,package RRL_STOCK_WAVE_LAUNCH_CMD,package RRL_PICK_WAVE_API) as
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


CREATE OR REPLACE package RRL_PRODUCTION_API as
  function create_prod_batch(
    p_prod_batch_no        varchar2,
    p_articul              varchar2 default null,
    p_mod_id               number default null,
    p_gtin                 varchar2 default null,
    p_product_name         varchar2 default null,
    p_total_quantity       number default null,
    p_total_pack_count     number default null,
    p_unit_code            varchar2 default 'PCS',
    p_ware_id              number default null,
    p_source_system        varchar2 default null,
    p_source_message_id    varchar2 default null,
    p_external_operation_id varchar2 default null,
    p_external_batch_id    varchar2 default null,
    p_production_order_id  number default null,
    p_produced_date_from   date default null,
    p_produced_date_to     date default null,
    p_expiry_date_from     date default null,
    p_expiry_date_to       date default null,
    p_production_line      varchar2 default null,
    p_shift_id             varchar2 default null,
    p_mercury_required     number default 0,
    p_crpt_required        number default 0,
    p_created_by           varchar2 default user
  ) return number;

  procedure attach_pallet(
    p_prod_batch_id        number,
    p_uid_pallet           varchar2,
    p_pallet_no            number default null,
    p_quantity             number default null,
    p_pack_count           number default null,
    p_net_weight           number default null,
    p_gross_weight         number default null,
    p_sscc                 varchar2 default null,
    p_quality_status       varchar2 default null,
    p_created_by           varchar2 default user
  );

  function register_raw_batch(
    p_raw_batch_no         varchar2,
    p_articul              varchar2 default null,
    p_supplier_id          varchar2 default null,
    p_producer_name        varchar2 default null,
    p_quantity_initial     number default null,
    p_quantity_available   number default null,
    p_unit_code            varchar2 default 'PCS',
    p_ware_id              number default null,
    p_mercury_stock_entry_uuid varchar2 default null,
    p_mercury_vsd_uuid     varchar2 default null,
    p_created_by           varchar2 default user
  ) return number;

  function add_raw_usage(
    p_prod_batch_id        number,
    p_raw_batch_id         number default null,
    p_raw_articul          varchar2 default null,
    p_quantity_planned     number default null,
    p_quantity_fact        number default null,
    p_unit_code            varchar2 default 'PCS',
    p_used_by              varchar2 default user
  ) return number;

  procedure set_mercury_batch(
    p_prod_batch_id        number,
    p_mercury_operation_id varchar2 default null,
    p_stock_entry_uuid     varchar2 default null,
    p_stock_entry_guid     varchar2 default null,
    p_vet_document_uuid    varchar2 default null,
    p_vet_document_status  varchar2 default null,
    p_vet_document_type    varchar2 default null,
    p_vet_document_form    varchar2 default null,
    p_product_item_guid    varchar2 default null,
    p_product_item_name    varchar2 default null,
    p_last_error           varchar2 default null
  );

  function add_crpt_code(
    p_prod_batch_id        number,
    p_uid_pallet           varchar2 default null,
    p_gtin                 varchar2,
    p_cis                  varchar2,
    p_serial_no            varchar2 default null,
    p_datamatrix_full      varchar2 default null,
    p_parent_sscc          varchar2 default null
  ) return number;

  function create_aggregation(
    p_sscc                 varchar2,
    p_prod_batch_id        number default null,
    p_uid_pallet           varchar2 default null,
    p_parent_sscc          varchar2 default null,
    p_aggregation_level    varchar2 default 'PALLET'
  ) return number;

  procedure add_aggregation_item(
    p_aggregation_id       number,
    p_child_type           varchar2,
    p_child_cis            varchar2 default null,
    p_child_sscc           varchar2 default null,
    p_gtin                 varchar2 default null,
    p_prod_batch_id        number default null
  );

  function enqueue_event(
    p_system_code          varchar2,
    p_event_type           varchar2,
    p_prod_batch_id        number default null,
    p_uid_pallet           varchar2 default null,
    p_document_no          varchar2 default null,
    p_payload_json         clob default null,
    p_idempotency_key      varchar2 default null
  ) return number;

  procedure set_batch_status(
    p_prod_batch_id        number,
    p_quality_status       varchar2 default null,
    p_mercury_status       varchar2 default null,
    p_crpt_status          varchar2 default null,
    p_updated_by           varchar2 default user
  );

  function register_file_message(
    p_exchange_type        varchar2,
    p_source_system        varchar2,
    p_message_id           varchar2,
    p_external_operation_id varchar2 default null,
    p_file_name            varchar2 default null,
    p_file_path            varchar2 default null,
    p_file_hash            varchar2 default null
  ) return number;

  procedure mark_file_processed(
    p_message_id           varchar2,
    p_prod_batch_id        number default null,
    p_processed_by         varchar2 default user
  );

  procedure mark_file_error(
    p_message_id           varchar2,
    p_error_code           varchar2,
    p_error_text           varchar2,
    p_processed_by         varchar2 default user
  );

  function get_setting(p_setting_key varchar2) return varchar2;

  procedure set_setting(
    p_setting_key          varchar2,
    p_setting_value        varchar2,
    p_description          varchar2 default null
  );
end RRL_PRODUCTION_API;
/


CREATE OR REPLACE package RRL_QC_SCOPE_READ authid definer as
 function policy_json(p_domain clob) return clob;
 function exemption_json(p_domain clob) return clob;
 procedure record_exemption(p_domain clob,p_signature varchar2);
end;
/


CREATE OR REPLACE package RRL_RECIPIENT_PALLET_POLICY authid definer as
 function rule_id(p_customer number,p_store number)return number;
 function type_id(p_customer number,p_store number)return number;
end;
/


CREATE OR REPLACE package RRL_REGULATORY_API as
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


CREATE OR REPLACE package RRL_REGULATORY_STOCK_OUTBOX authid definer accessible by(package RRL_REGULATORY_API)as
 procedure declare_events(p_operation varchar2,p_event varchar2,p_profiles clob,p_resources in out nocopy json_array_t);
 function enqueue_events(p_operation varchar2,p_event varchar2,p_domain clob,p_units clob,p_profiles clob)return clob;
end;
/


CREATE OR REPLACE package RRL_RETURN_PALLET_IDENTITY authid definer
 accessible by(package RRL_STORE_RETURN_UNIT_CORE,package RRL_STOCK_STORE_RETURN_REC_CMD)as
 procedure assert_preserved(p_approval varchar2,p_uid varchar2);
end;
/


CREATE OR REPLACE package RRL_RETURN_REUSE_API authid definer as
 procedure preview(p_receipt varchar2,p_line number,p_quantity varchar2,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_SAP_RECEIPT_API as
 function pallet_write_allowed return boolean;
 procedure register_pallet(p_sscc varchar2,p_articul varchar2,p_expiry date,p_produced date,
 p_qty number,p_naklad number,p_actor varchar2);
end;
/


CREATE OR REPLACE package RRL_SAP_STORE_ADMISSION_API authid definer as
 function write_allowed return number;
 procedure context(p_order number,p_actor varchar2,p_result out clob);
 procedure apply_decision(p_actor varchar2,p_body clob,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_SCALE_PACKET_READ authid definer as
 function utc_stamp(p_text varchar2)return timestamp with time zone;
 function validate_json(p_source clob,p_capacity number,p_resolution number,
  p_expected_basis varchar2 default 'GROSS',p_sample_field varchar2 default 'gross_weight_kg')return clob;
end;
/


CREATE OR REPLACE package RRL_SSCC_ALLOCATOR authid definer as
 procedure assert_scope(p_ware number,p_actor varchar2,p_permission varchar2);
 function allocate(p_ware number,p_actor varchar2,p_permission varchar2) return varchar2;
end;
/


CREATE OR REPLACE package RRL_STOCK_BALANCE_CORE authid definer 
 accessible by(package RRL_STOCK_IW_RECOVERY_REC,package RRL_STOCK_UNLOAD_CMD,package RRL_STOCK_INTERWARE_REC,package RRL_STOCK_STORE_RETURN_REC_CMD,package RRL_STOCK_RECEIPT_REVERSE,package RRL_STOCK_INVENTORY_BIRTH,package RRL_STOCK_INVENTORY_CMD,package RRL_STOCK_EVENT_BRIDGE,package RRL_STOCK_MES_MOVEMENT_CORE,package RRL_STOCK_RESERVATION_CMD,package RRL_STOCK_POSTING_API,package RRL_STOCK_MOVE_CORE, 
  package RRL_STOCK_RESERVE_CORE,package RRL_STOCK_RECEIPT_CORE,package RRL_STOCK_TRANSFER_CORE,package RRL_STOCK_EFFECT_CORE) as 
 procedure apply_delta(p_uid varchar2,p_cell varchar2,p_delta_p number,p_delta_h number, 
   p_base_uom varchar2,p_uom_version number,p_expected_version number default null); 
 procedure write_move(p_uid varchar2,p_from varchar2,p_to varchar2,p_qty number,p_base_uom varchar2,p_uom_version number,p_line number,p_actor varchar2,p_event out number); 
 procedure write_leg(p_uid varchar2,p_from varchar2,p_to varchar2,p_signed_qty number,p_base_uom varchar2, 
   p_uom_version number,p_line number,p_leg number,p_type number,p_actor varchar2,p_event out number,p_outgoing_doc number default null,p_pallet_row number default null); 
end;
/


CREATE OR REPLACE package RRL_STOCK_CASE_BIND_MOVE authid definer accessible by(package RRL_STOCK_CASE_MOVE_CMD,package RRL_STOCK_HU_CMD,package RRL_STOCK_HU_SLOT_MOVE_CMD)as
 procedure plan_move(p_case RRL_CASE_PICK_TASK%rowtype,p_resources in out nocopy json_array_t,p_domain in out nocopy json_object_t);
 procedure validate_move(p_case RRL_CASE_PICK_TASK%rowtype,p_frozen json_object_t);
 procedure finish_move(p_case RRL_CASE_PICK_TASK%rowtype,p_frozen json_object_t,p_version number,p_actor varchar2);
 procedure plan_tree(p_nodes json_array_t,p_resources in out nocopy json_array_t,p_domain in out nocopy json_object_t);
 procedure validate_tree(p_nodes json_array_t,p_domain json_object_t);
 function binding_for(p_domain json_object_t,p_case_id number)return json_object_t;
end;
/


CREATE OR REPLACE package RRL_STOCK_CASE_CLOSE authid definer accessible by(package RRL_STOCK_STORE_CASE_CMD) as
 procedure actor_scope(p_case varchar2,p_actor varchar2,p_action varchar2);
 procedure describe(p_case varchar2,p_metadata clob,p_actor varchar2,p_domain in out nocopy json_object_t);
 procedure declare_resources(p_domain json_object_t,p_operation varchar2,p_resources in out nocopy json_array_t);
 procedure persist(p_domain json_object_t,p_actor varchar2);
end;
/


CREATE OR REPLACE package RRL_STOCK_CASE_MOVE_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_CASE_PICK_CMD authid definer
 accessible by(package RRL_STOCK_CASE_RETURN_CMD,package RRL_STOCK_SHIPPING_CORE,package RRL_STOCK_CASE_SHORT_CMD,package RRL_STOCK_CASE_MOVE_CMD,package RRL_STOCK_POSTING_API) as
 function carrier_rows(p_task number) return clob;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_CASE_RETURN_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_CASE_SHORT_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_CASE_TYPE_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API,trigger RRL_CASE_PALLET_TYPE_GUARD)as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
 procedure assert_writing(p_task number);
end;
/


CREATE OR REPLACE package RRL_STOCK_CHANGE_AUDIT authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 function snapshot(p_resources clob) return clob;
 function differences(p_before clob,p_after clob) return clob;
end;
/


CREATE OR REPLACE package RRL_STOCK_COMMAND_PLAN authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_move(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_COMPOSITION_CORE authid definer accessible by(package RRL_STOCK_POSTING_API) as
 function snapshot_before(p_resources clob) return clob;
 procedure finish_changes(p_before clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_CONFIG_API authid definer as
 procedure begin_change(p_actor varchar2,p_permission varchar2);
 procedure end_change;
end;
/


CREATE OR REPLACE package RRL_STOCK_CTX_API authid definer
 accessible by(package RRL_STOCK_POOL_CMD,package RRL_STOCK_SETTING_API,package RRL_STOCK_MES_CANCEL_CMD,package RRL_STOCK_MES_SUPPLY_CMD,package RRL_STOCK_DOC_RESERVE_CMD,package RRL_STOCK_BALANCE_CORE,package RRL_STOCK_RESERVE_CORE,package RRL_STOCK_RESERVATION_CMD,package RRL_STOCK_UNIT_CORE,package RRL_STOCK_TRANSFER_CORE,package RRL_STOCK_CONFIG_API,package RRL_STOCK_POSTING_API,package RRL_STOCK_OPERATION_CORE,package RRL_STOCK_COMPOSITION_CORE) as
 procedure open_operation(p_operation varchar2,p_mode varchar2 default 'EXPLICIT');
 procedure open_configuration(p_actor varchar2,p_permission varchar2);
 procedure begin_effect(p_kind varchar2,p_uid varchar2 default null,p_cell varchar2 default null,p_row_id number default null);
 procedure begin_staging(p_uid varchar2,p_cell varchar2);
 procedure end_effect;
 procedure clear_operation;
end;
/


CREATE OR REPLACE package RRL_STOCK_DOC_RESERVE_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_release(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_release(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_EFFECT_CORE authid definer



 accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_MES_MOVEMENT_CORE,



 package RRL_STOCK_SHIPPING_CORE,package RRL_STOCK_CORRECTION_CORE,package RRL_STOCK_RETURN_DISPOSE) as



 procedure consume(p_uid varchar2,p_cell varchar2,p_qty number,p_uom varchar2,p_uom_version number,p_warehouse number,



  p_actor varchar2,p_line number,p_reservation number default null,p_doc_type varchar2 default null,



  p_doc_id number default null,p_units clob default null,p_outgoing_doc number default null,p_pallet_row number default null,p_supplier_return_receipt varchar2 default null,p_disposal_receipt varchar2 default null);



end;
/


CREATE OR REPLACE package RRL_STOCK_ELIGIBILITY authid definer as
 function reason(p_uid varchar2,p_cell varchar2,p_warehouse number,p_quantity number default 0,
  p_min_days number default null,p_min_percent number default null,p_purpose varchar2 default 'ALLOCATE',
  p_owner_reservation number default null,p_article varchar2 default null) return varchar2;
 procedure assert_source(p_uid varchar2,p_cell varchar2,p_warehouse number,p_quantity number,
  p_min_days number default null,p_min_percent number default null,p_purpose varchar2 default 'ALLOCATE',
  p_owner_reservation number default null,p_article varchar2 default null);
end;
/


CREATE OR REPLACE package RRL_STOCK_EVENT_BRIDGE authid definer
 accessible by(trigger "BIN$UX1xZvUbS6/gYw8CAAo/Yg==$0") as
 procedure after_event(p_operation varchar2,p_line number,p_leg number,p_uid varchar2,p_from varchar2,p_to varchar2,
  p_qty number,p_uom varchar2,p_uom_version number,p_type number);
end;
/


CREATE OR REPLACE package RRL_STOCK_FULFILLMENT_FACT authid definer
 accessible by(package RRL_STOCK_UNLOAD_CMD,package RRL_STOCK_SHIPPING_CORE) as
 procedure project_ship(p_shipment number,p_identifier varchar2,p_order number,p_operation varchar2,p_facts clob,p_actor varchar2);
 procedure project_unload(p_shipment number,p_load varchar2,p_case number,p_actor varchar2);
 procedure project_unload_pallet(p_shipment number,p_load varchar2,p_uid varchar2,p_actor varchar2);
end;
/


CREATE OR REPLACE package RRL_STOCK_FULLPAL_BIND_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_HU_CMD authid definer
 accessible by(package RRL_STOCK_HU_TASK,package RRL_STOCK_POSTING_API,package RRL_STOCK_HU_UNPACK_CMD,package RRL_STOCK_HU_SLOT_MOVE_CMD,package RRL_STOCK_HU_REPACK_CMD) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob,p_allow_slotted boolean default false,p_defer_wait_planning boolean default false);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
 procedure declare_tree(f in out nocopy json_array_t,r in out nocopy json_array_t,s clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_HU_LOAD_CORE authid definer accessible by(package RRL_STOCK_HU_SHIP_CMD,package RRL_STOCK_TRIP_DEPART_CMD,package RRL_STOCK_SINGLE_LOAD_CMD,package RRL_STOCK_LOAD_RECONCILE_CMD) as
 procedure compile_load(p_request clob,p_snapshot clob,p_shipments clob,f in out nocopy json_array_t,r in out nocopy json_array_t,p_domain out json_object_t);
 procedure begin_load(p_domain clob);
 procedure finish_load(p_domain clob,p_snapshot clob,p_operation varchar2,p_actor varchar2);
end;
/


CREATE OR REPLACE package RRL_STOCK_HU_PLACEMENT_CORE authid definer
 accessible by(package RRL_STOCK_SINGLE_LOAD_CMD,package RRL_STOCK_UNLOAD_CMD,package RRL_STOCK_HU_UNPACK_CMD,package RRL_STOCK_HU_SLOT_MOVE_CMD,package RRL_STOCK_CASE_MOVE_CMD,package RRL_STOCK_CASE_RETURN_CMD,package RRL_STOCK_SHIPPING_CORE,package RRL_STOCK_HU_REPACK_CMD) as
 procedure declare_stock_source(r in out nocopy json_array_t,p_uid varchar2,p_cell varchar2,p_claims out clob);
 procedure release_stock_source(p_uid varchar2,p_cell varchar2,p_claims clob);
 procedure declare_existing_case(r in out nocopy json_array_t,p_case number);
 procedure release_case(p_case number,p_cell varchar2);
 procedure declare_place(r in out nocopy json_array_t,p_task number,p_sync number);
 procedure record_place(p_request clob,p_actor varchar2,p_uid varchar2,p_warehouse number,p_cell varchar2,p_task number,p_slot number,p_sync number,p_placement clob,p_case_task number default null);
end;
/


CREATE OR REPLACE package RRL_STOCK_HU_READ authid definer as
 function snapshot_json(p_uid varchar2,p_ignore_task number default null) return clob;
 function case_snapshot_json(p_task number) return clob;
 procedure assert_quantity_write(p_uid varchar2);
end;
/


CREATE OR REPLACE package RRL_STOCK_HU_REPACK_CMD authid definer accessible by(package RRL_STOCK_POSTING_API)as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_HU_SHIP_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_HU_SLOT authid definer
 accessible by(package RRL_STOCK_UNLOAD_CMD,package RRL_STOCK_HU_CMD,package RRL_STOCK_HU_UNPACK_CMD,package RRL_STOCK_HU_SLOT_MOVE_CMD,package RRL_STOCK_HU_REPACK_CMD) as
 function target_json(p_tree clob,p_metadata clob,p_ignored_task number,p_replace_root varchar2 default null,p_extra_weight number default 0,p_extra_volume number default 0) return clob;
end;
/


CREATE OR REPLACE package RRL_STOCK_HU_SLOT_MOVE_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_HU_TASK authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_HU_UNIT_SIGNATURE authid definer as
 procedure describe_units(p_uid varchar2,p_cell varchar2,p_signature out varchar2,p_count out number);
 function signature_for(p_uid varchar2,p_cell varchar2) return varchar2;
end;
/


CREATE OR REPLACE package RRL_STOCK_HU_UNPACK_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_INTERNAL_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_move(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_move(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_INTERWARE_CUSTODY authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure assert_scope(p_receipt varchar2,p_actor varchar2);
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_INTERWARE_NEXT authid definer accessible by(package RRL_STOCK_SHIPPING_CORE) as
 function describe_source(p_st number,p_ware number) return json_object_t;
 procedure declare_source(p_source json_object_t,p_operation varchar2,p_resources in out nocopy json_array_t);
 procedure validate_load(p_source json_object_t,p_actor varchar2);
 procedure dispatched(p_source json_object_t,p_actor varchar2);
end;
/


CREATE OR REPLACE package RRL_STOCK_INTERWARE_PART authid definer accessible by(package RRL_STOCK_IW_RECOVERY_REC,package RRL_STOCK_INTERWARE_REC) as 
 procedure describe_partial(p_metadata json_object_t,p_original_uid varchar2,p_original_qty number,p_unit varchar2,p_article varchar2,p_domain in out json_object_t); 
 procedure describe_selected_units(p_metadata json_object_t,p_domain in out json_object_t); 
 procedure create_pallet(p_domain json_object_t,p_operation varchar2); 
end;
/


CREATE OR REPLACE package RRL_STOCK_INTERWARE_PUT authid definer accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_TASK_PLAN,package RRL_STOCK_TASK_CORE,package RRL_STOCK_TASK_DOMAIN,package RRL_STOCK_HU_TASK) as
 procedure assert_scope(p_receipt varchar2,p_actor varchar2,p_superseded number default null);
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
 procedure plan_task(p_task RRL_WAREHOUSE_TASK%rowtype,p_actor varchar2,p_resources in out nocopy json_array_t,p_domain in out nocopy json_object_t);
 procedure validate_task(p_task RRL_WAREHOUSE_TASK%rowtype,p_actor varchar2,p_frozen json_object_t);
 procedure complete_task(p_task RRL_WAREHOUSE_TASK%rowtype,p_quantity number,p_target_uid varchar2,p_actor varchar2);
end;
/


CREATE OR REPLACE package RRL_STOCK_INTERWARE_REC authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure assert_scope(p_plan varchar2,p_actor varchar2);
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_INTERWARE_SHORT_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as 
 procedure assert_scope(p_request clob,p_actor varchar2); 
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob); 
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob); 
end;
/


CREATE OR REPLACE package RRL_STOCK_INVARIANT_CORE authid definer
 accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_COMPOSITION_CORE) as
 function stock_uid(p_key raw) return varchar2;
 function snapshot_stock(p_resources clob) return clob;
 procedure verify_posting(p_resources clob,p_before clob,p_operation varchar2);
end;
/


CREATE OR REPLACE package RRL_STOCK_INVENTORY_BIRTH authid definer

 accessible by(package RRL_STOCK_POSTING_API) as

 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);

 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);

end;
/


CREATE OR REPLACE package RRL_STOCK_INVENTORY_CMD authid definer

 accessible by(package RRL_STOCK_POSTING_API) as

 procedure compile_count(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);

 procedure execute_count(p_request clob,p_actor varchar2,p_result out clob);

end;
/


CREATE OR REPLACE package RRL_STOCK_INV_ENTRY authid definer
 accessible by(function RRL_REVIZION_CELL,function RRL_REVIZION_CELL_KOR,function RRL_INV_CREATE_LINE2,function RRL_INV_CREATE_LINE3,function RRL_INV_CREATE_LINE4) as
 function register_line(p_cell varchar2,p_barcode varchar2,p_article_part varchar2,p_qty number,p_document number,
  p_expiry date,p_actor varchar2,p_operation varchar2) return varchar2;
 function count_lot(p_cell varchar2,p_uid varchar2,p_quantity varchar2,p_unit varchar2,p_document number,
  p_actor varchar2,p_operation varchar2,p_reason varchar2) return varchar2;
end;
/


CREATE OR REPLACE package RRL_STOCK_IW_PUT_CELL authid definer
 accessible by(package RRL_STOCK_INTERWARE_PUT,package RRL_STOCK_IW_RECOVERY_PUT)as
 procedure assert_target(p_ware number,p_uid varchar2,p_from varchar2,p_target varchar2,p_gross number,p_task_id number);
end;
/


CREATE OR REPLACE package RRL_STOCK_IW_RECOVERY_CANCEL authid definer accessible by(package RRL_STOCK_POSTING_API)as
 procedure assert_scope(p_request varchar2,p_actor varchar2);
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_IW_RECOVERY_NEXT authid definer accessible by(package RRL_STOCK_INTERWARE_NEXT) as 
 function describe_source(p_st number,p_ware number) return json_object_t; 
 procedure declare_source(p_source json_object_t,p_operation varchar2,p_resources in out nocopy json_array_t); 
 procedure validate_load(p_source json_object_t,p_actor varchar2); 
 procedure dispatched(p_source json_object_t,p_actor varchar2); 
end;
/


CREATE OR REPLACE package RRL_STOCK_IW_RECOVERY_PLAN authid definer accessible by(package RRL_STOCK_POSTING_API) as 
 procedure assert_scope(p_request clob,p_actor varchar2); 
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob); 
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob); 
end;
/


CREATE OR REPLACE package RRL_STOCK_IW_RECOVERY_PUT authid definer accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_TASK_PLAN,package RRL_STOCK_TASK_CORE,package RRL_STOCK_TASK_DOMAIN) as
 procedure assert_scope(p_receipt varchar2,p_actor varchar2);
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
 procedure plan_task(p_task RRL_WAREHOUSE_TASK%rowtype,p_actor varchar2,p_resources in out nocopy json_array_t,p_domain in out nocopy json_object_t);
 procedure validate_task(p_task RRL_WAREHOUSE_TASK%rowtype,p_actor varchar2,p_frozen json_object_t);
 procedure complete_task(p_task RRL_WAREHOUSE_TASK%rowtype,p_quantity number,p_target_uid varchar2,p_actor varchar2);
end;
/


CREATE OR REPLACE package RRL_STOCK_IW_RECOVERY_REC authid definer accessible by(package RRL_STOCK_POSTING_API)as 
 procedure assert_scope(p_approval varchar2,p_actor varchar2); 
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob); 
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob); 
end;
/


CREATE OR REPLACE package RRL_STOCK_LOADING_READ authid definer as
 procedure assert_scope(p_identifier varchar2,p_actor varchar2);
 procedure describe_source(p_identifier varchar2,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob,p_snapshot out clob);
 function preview_json(p_identifier varchar2,p_actor varchar2 default null) return clob;
end;
/


CREATE OR REPLACE package RRL_STOCK_LOAD_BOX_CORE authid definer accessible by(package RRL_STOCK_HU_LOAD_CORE) as
 procedure compile_boxes(p_snapshot clob,p_context clob,p_operation varchar2,p_gross number,r in out nocopy json_array_t,p_boxes out json_array_t);
 procedure assert_policy(p_destinations clob,p_boxes json_array_t);
 procedure persist_boxes(p_operation varchar2,p_boxes json_array_t,p_actor varchar2);
end;
/


CREATE OR REPLACE package RRL_STOCK_LOAD_FLOOR authid definer
 accessible by(package RRL_STOCK_HU_LOAD_CORE,package RRL_STOCK_TRIP_DEPART_CMD,package RRL_TRANSPORT_PLAN_RULES,trigger RRL_LOAD_FLOOR_FACT_GUARD)as
 function compile_load(p_snapshot clob,p_vehicle number,p_rows in out nocopy json_array_t)return json_object_t;
 function checked_trip(p_trip number,p_vehicle number,p_extra_type number default null)return clob;
 function planning_counts(p_vehicle number,p_sts clob,p_base_counts clob,p_unknown number)return clob;
 procedure assert_load(p_vehicle number,p_trip number,p_frozen clob);
 procedure assert_departure(p_trip number,p_vehicle number,p_frozen clob);
 procedure persist_confirmation(p_operation varchar2,p_domain clob,p_actor varchar2);
 procedure assert_writing(p_operation varchar2);
end;
/


CREATE OR REPLACE package RRL_STOCK_LOAD_RECONCILE_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_LOAD_RECONCILE_READ authid definer as
 function preview_json(p_original varchar2) return clob;
end;
/


CREATE OR REPLACE package RRL_STOCK_LOAD_THERMAL authid definer
 accessible by(package RRL_STOCK_HU_LOAD_CORE,package RRL_STOCK_TRIP_DEPART_CMD,trigger RRL_LOAD_THERMAL_FACT_GUARD) as
 procedure compile_confirmation(p_members clob,p_vehicle number,p_context clob,p_domain out json_object_t,p_phase varchar2 default 'MANUAL_AT_LOADING');
 procedure assert_current(p_members clob,p_vehicle number,p_domain clob,p_phase varchar2 default 'MANUAL_AT_LOADING');
 procedure persist_confirmation(p_operation varchar2,p_domain clob,p_actor varchar2);
 procedure assert_writing(p_operation varchar2);
end;
/


CREATE OR REPLACE package RRL_STOCK_LOCATION_CORE authid definer 
 accessible by(package RRL_STOCK_IW_RECOVERY_REC,package RRL_STOCK_INTERWARE_REC,package RRL_STOCK_STORE_RETURN_REC_CMD,package RRL_STOCK_RECEIPT_REVERSE,package RRL_STOCK_INVENTORY_BIRTH,package RRL_STOCK_WAVE_LAUNCH_CMD,package RRL_STOCK_INVENTORY_CMD,package RRL_STOCK_MES_SUPPLY_CMD,package RRL_STOCK_MES_MOVEMENT_CORE,package RRL_STOCK_RECEIPT_CORE,package RRL_STOCK_RESERVATION_CMD,package RRL_STOCK_POSTING_API,package RRL_STOCK_MOVE_CORE, 
  package RRL_STOCK_RESERVE_CORE,package RRL_STOCK_RECEIPT_CORE,package RRL_STOCK_TRANSFER_CORE,package RRL_STOCK_EFFECT_CORE) as 
 procedure assert_receiving(p_cell varchar2,p_expected_warehouse number); 
 procedure assert_quarantine(p_cell varchar2,p_expected_warehouse number); 
 procedure assert_ordinary(p_cell varchar2,p_expected_warehouse number,p_role varchar2); 
end;
/


CREATE OR REPLACE package RRL_STOCK_LOCK_API authid definer as
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


CREATE OR REPLACE package RRL_STOCK_MATH authid definer as
 function quantity(p_text varchar2,p_scale number default 9) return number;
 function convert_exact(p_text varchar2,p_numerator number,p_denominator number,p_scale number) return number;
 procedure assert_base(p_value number,p_scale number);
end;
/


CREATE OR REPLACE package RRL_STOCK_MES_CANCEL_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_MES_CORE authid definer
 accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_TASK_CORE,package RRL_STOCK_TASK_DOMAIN) as
 procedure sync_warehouse_fact(p_task RRL_WAREHOUSE_TASK%rowtype,p_qty number,p_target_uid varchar2,p_residual number,p_actor varchar2);
end;
/


CREATE OR REPLACE package RRL_STOCK_MES_MOVEMENT_CORE authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure execute_movements(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_MES_MOVEMENT_PLAN authid definer
 accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_MES_MOVEMENT_CORE) as
 function signature(p_m RRL_MES_MOVEMENT%rowtype) return varchar2;
 procedure compile_movements(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_MES_SUPPLY_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_METADATA_TX authid definer as

 procedure begin_change(p_actor varchar2,p_permission varchar2);

 procedure end_change;

end;
/


CREATE OR REPLACE package RRL_STOCK_MOVE_CORE authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure manual_whole(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_NATIVE_API authid definer as
 procedure post(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_OPERATION_CORE authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure begin_operation(p_request clob,p_actor varchar2,p_operation varchar2,p_kind varchar2,p_replay out clob,p_plan clob default null);
 procedure finish_operation(p_operation varchar2,p_result clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_PALLET_QC_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_PALLET_TYPE_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API,trigger RRL_PALLET_FLOOR_GUARD)as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
 procedure assert_writing(p_uid varchar2,p_operation varchar2);
end;
/


CREATE OR REPLACE package RRL_STOCK_PALLET_UOM authid definer
 accessible by(package RRL_STOCK_INVENTORY_CMD,package RRL_STOCK_INTERNAL_CMD,package RRL_STOCK_TASK_PLAN,package RRL_STOCK_TASK_CORE) as
 procedure resolve_quantity(p_uid varchar2,p_input varchar2,p_quantity varchar2,
  p_base out varchar2,p_quantity_base out number,p_version out number,p_signature out varchar2);
end;
/


CREATE OR REPLACE package RRL_STOCK_PLAN_HELPER authid definer as
 procedure fence(p_plan in out nocopy json_array_t,p_kind varchar2,p_id varchar2,p_mode number default 4);
 procedure anchor(p_plan in out nocopy json_array_t,p_rank number,p_kind varchar2,p_a varchar2,p_b varchar2 default null);
 procedure row_key(p_plan in out nocopy json_array_t,p_table varchar2,p_id varchar2);
 procedure stock_closure(p_policies in out nocopy json_array_t,p_resources in out nocopy json_array_t,
  p_uid varchar2,p_article varchar2,p_from varchar2,p_to varchar2);
 function decimal_text(p_value number) return varchar2;
end;
/


CREATE OR REPLACE package RRL_STOCK_POOL_CMD authid definer accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_WAVE_LAUNCH_CMD) as
 procedure compile_wave_pool(p_ware number,p_wave number,p_resources in out nocopy json_array_t,p_pools out json_array_t);
 procedure consume_wave_pool(p_pools json_array_t,p_actor varchar2);
 procedure compile_command(p_request clob,p_operation varchar2,p_hints clob,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_POOL_READ authid definer as
 function snapshot_json(p_ware number,p_article varchar2) return clob;
 function line_snapshot_json(p_line number) return clob;
end;
/


CREATE OR REPLACE package RRL_STOCK_POSTING_API authid definer as
 procedure prepare_command(p_request clob,p_actor varchar2,p_replay out clob,p_hints clob default null);
 procedure execute_prepared(p_result out clob);
 procedure stage_birth(p_uid varchar2);
 procedure finish_birth_capture;
 procedure reset_connection;
end;
/


CREATE OR REPLACE package RRL_STOCK_QC_CASE authid definer accessible by(package RRL_STOCK_PALLET_QC_CMD,package RRL_STOCK_SHIPPING_CORE) as
 procedure project(p_domain clob,p_ready number,p_failed number,p_is_plan number,p_actor varchar2,p_operation varchar2,p_reason varchar2);
 function nested(p_domain clob) return number;
end;
/


CREATE OR REPLACE package RRL_STOCK_QC_GATE authid definer as
 function signature_version_for_plan(p_domain clob)return number;
 function signature_for_plan(p_domain clob) return varchar2;
 procedure assert_approved(p_domain clob);
 function status_json(p_identifier varchar2) return clob;
end;
/


CREATE OR REPLACE package RRL_STOCK_QC_ITEM authid definer as
 procedure resolve_barcode(p_code varchar2,p_article out varchar2,p_input_uom out varchar2);
 procedure validate_scan(p_domain clob,p_metadata clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_QC_MARK authid definer as
 function required_for_article(p_article varchar2) return number;
 function required_for_plan(p_domain clob) return number;
 procedure validate_scan(p_domain clob,p_metadata clob,p_unit_count out number);
end;
/


CREATE OR REPLACE package RRL_STOCK_QC_POLICY authid definer as
 procedure settings(p_warehouse number,p_mode out varchar2,p_independent out number);
 procedure settings_for_plan(p_domain clob,p_mode out varchar2,p_independent out number);
 function controller_allowed(p_domain clob,p_actor varchar2) return number;
 procedure assert_controller(p_domain clob,p_actor varchar2);
 procedure sampling(p_domain clob,p_bucket out number,p_percent out number,p_selected out number,p_rescan out number);
 function full_scan_required(p_domain clob) return number;
 procedure assign_sampling(p_domain clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_QC_WEIGHT authid definer as
 procedure calculate(p_domain clob,p_expected out number,p_tolerance out number);
end;
/


CREATE OR REPLACE package RRL_STOCK_QUALITY_ENTRY authid definer as
 function scan(p_pallet varchar2,p_errors number,p_note varchar2,p_picker varchar2,p_actor varchar2,p_operation varchar2) return number;
 function weight(p_kind varchar2,p_pallet varchar2,p_gross varchar2,p_wood varchar2,p_actor varchar2,p_operation varchar2) return number;
end;
/


CREATE OR REPLACE package RRL_STOCK_RECEIPT_CORE authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure execute_receipt(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_RECEIPT_PLAN authid definer
 accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_RECEIPT_CORE) as
 procedure compile_receipt(p_request clob,p_operation varchar2,p_hints clob,p_policies out clob,p_resources out clob,p_domain out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_RECEIPT_REVERSE authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_REPL_ADMISSION authid definer as

 function lot_key(p_uid varchar2) return varchar2;
 function reason(p_uid varchar2,p_target varchar2,p_ware number,p_article varchar2) return varchar2;

 function mode_for(p_task number) return varchar2;

 function policy_signature(p_task number) return varchar2;

 procedure assert_target(p_uid varchar2,p_target varchar2,p_ware number,p_article varchar2);

end;
/


CREATE OR REPLACE package RRL_STOCK_REPL_BIND authid definer
 accessible by(package RRL_STOCK_TASK_PLAN,package RRL_STOCK_TASK_CORE) as
 procedure plan_bind(p_task RRL_WAREHOUSE_TASK%rowtype,p_qty number,p_anchors in out nocopy json_array_t,p_plan out json_object_t);
 procedure execute_bind(p_task RRL_WAREHOUSE_TASK%rowtype,p_uid varchar2,p_reservation number,p_plan json_object_t,p_actor varchar2);
end;
/


CREATE OR REPLACE package RRL_STOCK_REPL_CAPACITY authid definer as
 function unit_volume(p_cell varchar2,p_article varchar2) return number;
 function remaining_base_quantity(p_cell varchar2,p_article varchar2,p_exclude_repl number default null) return number;
 procedure assert_arrival(p_repl number,p_base_quantity number);
end;
/


CREATE OR REPLACE package RRL_STOCK_REPL_CONTINUATION authid definer
 accessible by(package RRL_STOCK_TASK_PLAN,package RRL_STOCK_TASK_CORE) as
 procedure plan_next(p_task RRL_WAREHOUSE_TASK%rowtype,p_qty number,p_residual number,p_rows in out nocopy json_array_t,p_domain in out nocopy json_object_t);
 procedure create_next(p_task RRL_WAREHOUSE_TASK%rowtype,p_domain json_object_t,p_actor varchar2);
end;
/


CREATE OR REPLACE package RRL_STOCK_REPL_NEED authid definer as
 function target_coverage(p_pick number,p_cell varchar2,p_exclude number default null) return number;
 function remaining_for_task(p_pick number,p_cell varchar2) return number;
end;
/


CREATE OR REPLACE package RRL_STOCK_REPL_SHARED authid definer as
 function allowed(p_uid varchar2,p_cell varchar2,p_target varchar2,p_ware number,p_owner number) return number;
end;
/


CREATE OR REPLACE package RRL_STOCK_RESERVATION_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_RESERVE_CORE authid definer
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


CREATE OR REPLACE package RRL_STOCK_RETURN_DISPOSE authid definer accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_EFFECT_CORE) as
 procedure assert_scope(p_request varchar2,p_actor varchar2);
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
 procedure validate_consume(p_receipt varchar2,p_uid varchar2,p_cell varchar2,p_quantity number,p_ware number,p_actor varchar2);
end;
/


CREATE OR REPLACE PACKAGE          "RRL_STOCK_RETURN_REUSE" authid definer accessible by(package RRL_STOCK_STORE_RETURN_REC_CMD,package RRL_STOCK_STORE_RETURN_PUT,package RRL_STOCK_STORE_RETURN_CMD,package RRL_RETURN_REUSE_API) as
 procedure describe_source(p_lot varchar2,p_article varchar2,p_unit varchar2,p_qty number,p_proof out json_object_t);
 procedure describe_boxes(p_approval RRL_STORE_RETURN_APPROVAL%rowtype,p_metadata json_object_t,p_scan_uom varchar2,p_batch_source varchar2,p_ware number,p_proof out json_object_t);
 procedure persist_boxes(p_operation varchar2,p_actor varchar2,p_proof json_object_t);
 procedure assert_pick_target(p_receipt RRL_STORE_RETURN_RECEIPT%rowtype,p_target varchar2);
end;
/


CREATE OR REPLACE package RRL_STOCK_REVISION_ENTRY authid definer
 accessible by(package REVIZION) as
 function count_row(p_article varchar2,p_cell varchar2,p_quantity number,p_unit varchar2,p_row number,p_actor varchar2,p_operation varchar2) return varchar2;
 function count_document(p_cell varchar2,p_document number,p_quantity number,p_unit varchar2,p_actor varchar2,p_operation varchar2) return varchar2;
 function birth_legacy(p_facts clob,p_actor varchar2,p_operation varchar2) return varchar2;
end;
/


CREATE OR REPLACE package RRL_STOCK_SETTING_API authid definer as
 procedure set_compatibility(p_value varchar2,p_reason varchar2,p_actor varchar2);
end;
/


CREATE OR REPLACE package RRL_STOCK_SHIPPING_CORE authid definer
 accessible by(package RRL_STOCK_PALLET_QC_CMD,package RRL_STOCK_POSTING_API,package RRL_STOCK_QC_GATE,package RRL_STOCK_HU_SHIP_CMD,package RRL_STOCK_LOADING_READ,package RRL_STOCK_SINGLE_LOAD_CMD) as
 procedure compile_shipment(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob,p_skip_qc boolean default false);
 procedure execute_shipment(p_request clob,p_actor varchar2,p_result out clob);
 procedure execute_resolved(p_request clob,p_domain clob,p_offset number,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_SHORT_RECOVERY authid definer
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


CREATE OR REPLACE package RRL_STOCK_SINGLE_LOAD_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_STORE_CASE_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_STORE_CUSTODY_CMD authid definer accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_STORE_RECEIPT_CMD)as
 procedure assert_scope(p_receipt varchar2,p_actor varchar2);
 procedure declare_receipt(p_receipt varchar2,p_load varchar2,p_uid varchar2,p_resources in out nocopy json_array_t,p_operation varchar2 default null);
 procedure release_accepted(p_receipt varchar2,p_actor varchar2);
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_STORE_DISPOSITION authid definer accessible by(package RRL_STOCK_STORE_RECEIPT_CMD) as
 procedure resolve_counts(p_snapshot clob,p_metadata clob,p_lines out json_array_t,p_has_issue out boolean);
 procedure declare_rows(p_operation varchar2,p_lines json_array_t,p_has_issue boolean,r in out nocopy json_array_t);
 procedure persist(p_operation varchar2,p_domain json_object_t,p_actor varchar2,p_result out json_array_t);
end;
/


CREATE OR REPLACE package RRL_STOCK_STORE_RECEIPT_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_STORE_RECEIPT_READ authid definer as
 procedure require_receiver(p_actor varchar2,p_store varchar2);
 procedure describe_load(p_load varchar2,p_actor varchar2,p_store varchar2,p_domain out clob);
 function preview_json(p_load varchar2,p_actor varchar2,p_store varchar2) return clob;
end;
/


CREATE OR REPLACE package RRL_STOCK_STORE_RETURN_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure assert_actor(p_actor varchar2);
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_STORE_RETURN_CUST_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure assert_scope(p_request clob,p_actor varchar2);
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_STORE_RETURN_PUT authid definer accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_TASK_PLAN,package RRL_STOCK_TASK_CORE,package RRL_STOCK_TASK_DOMAIN) as
 procedure assert_scope(p_receipt varchar2,p_actor varchar2);
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
 procedure plan_task(p_task RRL_WAREHOUSE_TASK%rowtype,p_actor varchar2,p_resources in out nocopy json_array_t,p_domain in out nocopy json_object_t);
 procedure validate_task(p_task RRL_WAREHOUSE_TASK%rowtype,p_actor varchar2,p_frozen json_object_t);
 procedure complete_task(p_task RRL_WAREHOUSE_TASK%rowtype,p_quantity number,p_target_uid varchar2,p_actor varchar2);
end;
/


CREATE OR REPLACE package RRL_STOCK_STORE_RETURN_REC_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure assert_scope(p_pickup varchar2,p_actor varchar2);
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_STORE_RETURN_SAP_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_STORE_RETURN_TR_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_STORE_WEIGHT_CORE authid definer accessible by(package RRL_STOCK_STORE_RECEIPT_CMD) as
 procedure resolve_weight(p_source clob,p_metadata clob,p_actor varchar2,p_proof out json_object_t,p_has_issue out boolean);
 procedure declare_rows(p_operation varchar2,p_proof json_object_t,r in out nocopy json_array_t);
 procedure persist(p_operation varchar2,p_proof json_object_t,p_actor varchar2);
end;
/


CREATE OR REPLACE package RRL_STOCK_ST_ROW_CMD accessible by(package RRL_STOCK_POSTING_API)as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_SUP_RETURN authid definer accessible by(package RRL_STOCK_SHIPPING_CORE,package RRL_STOCK_EFFECT_CORE) as
 function describe_source(p_st number,p_supplier varchar2,p_ware number) return json_object_t;
 procedure declare_source(p_source json_object_t,p_operation varchar2,p_resources in out nocopy json_array_t);
 procedure validate_consume(p_receipt varchar2,p_uid varchar2,p_cell varchar2,p_quantity number,p_ware number,p_actor varchar2);
 procedure dispatched(p_source json_object_t,p_actor varchar2);
end;
/


CREATE OR REPLACE package RRL_STOCK_TARE_BOOK_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_TARE_CANCEL_CMD authid definer accessible by(package RRL_STOCK_POSTING_API)as
 procedure assert_scope(p_request clob,p_actor varchar2);
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_TARE_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_TARE_HANDOVER authid definer accessible by(package RRL_STOCK_TARE_CMD) as
 procedure describe_books(p_request clob,p_kind varchar2,p_offer varchar2,p_owner number,p_type number,p_condition varchar2,p_from_kind varchar2,p_trip number,p_vehicle number,p_qty number,p_books out json_array_t);
 procedure declare_books(p_books json_array_t,p_offer varchar2,p_resources in out nocopy json_array_t);
 procedure persist_offer(p_offer varchar2,p_books json_array_t);
 procedure transfer_books(p_books json_array_t,p_operation varchar2,p_actor varchar2);
end;
/


CREATE OR REPLACE package RRL_STOCK_TARE_LOSS authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_TARE_POLICY authid definer accessible by(package RRL_STOCK_TARE_CMD) as
 procedure describe_store(p_store varchar2,p_domain out json_object_t);
 procedure record_delivery(p_operation varchar2,p_domain json_object_t);
end;
/


CREATE OR REPLACE package RRL_STOCK_TARE_RESOLVE authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_TASK_CORE authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure execute_task(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_TASK_DOMAIN authid definer
 accessible by(package RRL_STOCK_TASK_CORE) as
 procedure sync_fact(p_task RRL_WAREHOUSE_TASK%rowtype,p_qty number,p_target_uid varchar2,p_residual number,p_actor varchar2);
end;
/


CREATE OR REPLACE package RRL_STOCK_TASK_PLAN authid definer
 accessible by(package RRL_STOCK_HU_TASK,package RRL_STOCK_POSTING_API,package RRL_STOCK_TASK_CORE) as
 procedure compile_task(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 function signature(p_task RRL_WAREHOUSE_TASK%rowtype) return varchar2;
end;
/


CREATE OR REPLACE package RRL_STOCK_TASK_SCAN authid definer as
 function profile_signature(p_article varchar2) return varchar2;
 procedure assert_draft(p_request clob,p_task number,p_uid varchar2,p_cell varchar2,p_actor varchar2);
end;
/


CREATE OR REPLACE package RRL_STOCK_TRANSFER_CORE authid definer
 accessible by(package RRL_STOCK_HU_CMD,package RRL_STOCK_CASE_RETURN_CMD,package RRL_STOCK_CASE_MOVE_CMD,package RRL_STOCK_CASE_PICK_CMD,package RRL_STOCK_INTERNAL_CMD,package RRL_STOCK_POSTING_API,package RRL_STOCK_TASK_CORE,
 package RRL_STOCK_MES_MOVEMENT_CORE,package RRL_STOCK_RECEIPT_CORE,package RRL_STOCK_MOVE_CORE,package RRL_STOCK_MES_CORE) as
 procedure move(p_uid varchar2,p_target_uid varchar2,p_from varchar2,p_to varchar2,p_qty number,
  p_uom varchar2,p_uom_version number,p_warehouse number,p_actor varchar2,p_line number,
  p_reservation number default null,p_units clob default null,p_new_reservation number default null,p_target_slot number default null,p_source_warehouse number default null,p_location_mode varchar2 default 'ORDINARY');
end;
/


CREATE OR REPLACE package RRL_STOCK_TRIP_DEPART_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_UNIT_CORE authid definer 
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


CREATE OR REPLACE package RRL_STOCK_UNLOAD_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure assert_scope(p_load varchar2,p_actor varchar2);
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_UOM_CONFIG authid definer as
 procedure publish(p_article varchar2,p_input varchar2,p_base varchar2,p_numerator number,p_denominator number,p_scale number,p_provenance varchar2);
end;
/


CREATE OR REPLACE package RRL_STOCK_WAVE_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_reserve(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_reserve(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_WAVE_FINISH_CMD authid definer as
 function snapshot_json(p_wave number) return clob;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_WAVE_LAUNCH_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_WAVE_PICK_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STOCK_WAVE_READY authid definer as
 function snapshot_json(p_wave number) return clob;
 procedure assert_released(p_wave number);
end;
/


CREATE OR REPLACE package RRL_STOCK_WRITE_GUARD authid definer as
 function enforcement_required return boolean;
 procedure require_effect(p_kind varchar2,p_uid varchar2 default null,p_cell varchar2 default null,p_row_id number default null);
 procedure require_unit(p_key varchar2,p_uid varchar2);
end;
/


CREATE OR REPLACE package RRL_STORE_ACCESS_RULES as
 procedure check_sts(p_vehicle number,p_sts clob,p_complete number,p_result out clob);
 procedure assert_members(p_vehicle number,p_members clob);
end;
/


CREATE OR REPLACE package RRL_STORE_AGG_SCAN authid definer accessible by(package RRL_STORE_MARK_CORE) as
 procedure normalize(p_proof clob,p_metadata clob,p_scans out clob);
end;
/


CREATE OR REPLACE package RRL_STORE_CALENDAR_API authid definer as
 function write_allowed(p_operation varchar2)return number;
 function config_write_allowed return number;
 procedure configure(p_ware number,p_store varchar2,p_body clob,p_actor varchar2,p_result out clob);
 procedure delivery_rule(p_ware number,p_store_id number,p_day date,p_offset out number,p_allowed out number,p_proof out clob);
 procedure context(p_ware number,p_store varchar2,p_day varchar2,p_actor varchar2,p_result out clob);
 procedure set_exception(p_operation varchar2,p_actor varchar2,p_body clob,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STORE_EVIDENCE_API authid definer as
 procedure register_photo(p_load varchar2,p_store varchar2,p_view varchar2,p_actor varchar2,p_mime varchar2,p_width number,p_height number,p_bytes blob,p_result out clob);
 function photos_json(p_load varchar2,p_store varchar2,p_actor varchar2) return clob;
end;
/


CREATE OR REPLACE package RRL_STORE_MARK_CORE authid definer accessible by(package RRL_STOCK_STORE_RECEIPT_READ,package RRL_STOCK_STORE_RECEIPT_CMD,package RRL_STORE_RETURN_UNIT_CORE)as
 function source_proof(p_domain json_object_t)return json_object_t;
 function preview(p_domain json_object_t)return clob;
 procedure verify_scans(p_domain json_object_t,p_metadata json_object_t,p_proof out json_object_t);
 procedure resolve_disposition(p_proof json_object_t,p_metadata json_object_t,p_lines json_array_t,p_units out json_array_t);
 procedure persist(p_operation varchar2,p_load varchar2,p_units json_array_t,p_actor varchar2);
 procedure declare_rows(p_domain json_object_t,p_policies in out nocopy json_array_t,p_resources in out nocopy json_array_t);
end;
/


CREATE OR REPLACE package RRL_STORE_ORDER_SCOPE authid definer as
 procedure actor_scope(p_actor varchar2,p_permission varchar2,p_ware out number,p_global out number);
 procedure assert_scope(p_actor varchar2,p_permission varchar2,p_ware number);
 procedure begin_source(p_actor varchar2,p_permission varchar2,p_ware number,p_order number default null);
 procedure begin_supply(p_actor varchar2,p_ware number,p_sender varchar2,p_order varchar2,p_message varchar2);
 procedure end_source;
end;
/


CREATE OR REPLACE package RRL_STORE_RETURN_UNIT_CORE authid definer as
 function approved_proof(p_approval varchar2)return clob;
 function custody_proof(p_approval varchar2,p_metadata json_object_t)return clob;
 function disposition_units(p_receipt varchar2,p_uid varchar2,p_uom varchar2,p_basis varchar2)return clob;
 function select_disposition_units(p_receipt varchar2,p_uid varchar2,p_uom varchar2,p_qty number,p_keys clob,p_basis varchar2)return clob;
 function accepted_units(p_receipt varchar2,p_uid varchar2,p_uom varchar2)return clob;
 function select_units(p_receipt varchar2,p_uid varchar2,p_uom varchar2,p_qty number,p_keys clob)return clob;
 procedure persist(p_approval varchar2,p_receipt varchar2,p_uid varchar2,p_cell varchar2,p_units clob);
end;
/


CREATE OR REPLACE package RRL_STORE_SCALE_API authid definer as
 procedure capture(p_source clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_STORE_UNLOAD_API authid definer as
 procedure start_unloading(p_request clob,p_actor varchar2,p_result out clob);
 function writing return boolean;
end;
/


CREATE OR REPLACE package RRL_STORE_UNLOAD_CORE authid definer as
 procedure validate_input(p_metadata json_object_t,p_domain json_object_t);
 procedure capture(p_request clob,p_actor varchar2);
 function writing return boolean;
end;
/


CREATE OR REPLACE package RRL_STORE_WINDOW_RULES as
 procedure material(p_source clob,p_result out clob);
 procedure resolve(p_source clob,p_address varchar2,p_arrival date,p_zone varchar2,p_duration number,
  p_open out date,p_close out date,p_service out date,p_kind out varchar2,p_error out varchar2);
end;
/


CREATE OR REPLACE package RRL_ST_DEFER_API authid definer as
 function write_allowed return number;
 procedure history(p_st varchar2,p_actor varchar2,p_after number,p_result out clob);
 procedure context(p_st varchar2,p_actor varchar2,p_result out clob);
 procedure apply_decision(p_operation varchar2,p_actor varchar2,p_body clob,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_ST_DEFER_CASE_WAIT authid definer as

 function snapshot(p_st varchar2,p_ware number,p_ignore_plan varchar2 default null,p_case_id number default null,p_nested_root varchar2 default null)return clob;

 procedure assert_command(p_request clob,p_actor varchar2);

 procedure plan_move(p_request clob,p_actor varchar2,p_resources in out nocopy json_array_t,p_domain in out nocopy json_object_t);

 procedure validate_move(p_request clob,p_actor varchar2,p_frozen json_object_t);

 procedure finish_move(p_request clob,p_actor varchar2,p_result in out clob);

end;
/


CREATE OR REPLACE package RRL_ST_DEFER_HU_WAIT authid definer
 accessible by(package RRL_ST_DEFER_PHYSICAL,package RRL_ST_DEFER_WAIT_API,package RRL_STOCK_HU_TASK,package RRL_ST_DEFER_PLACE_READ,package RRL_STOCK_HU_CMD)as
 function shared_wait_target(p_request clob,p_task number,p_target varchar2,p_ware number)return boolean;
 function snapshot_root(p_st varchar2,p_ware number,p_root varchar2,p_ignore_plan varchar2 default null)return clob;
 function snapshot(p_st varchar2,p_ware number,p_ignore_plan varchar2 default null)return clob;
 procedure request_plan(p_operation varchar2,p_decision varchar2,p_actor varchar2,p_request out clob,p_root varchar2 default null);
 procedure declare_plan(p_request clob,p_task number,p_resources in out nocopy json_array_t,p_domain in out nocopy json_object_t);
 procedure validate_plan(p_request clob,p_actor varchar2,p_frozen json_object_t,p_task number default null);
end;
/


CREATE OR REPLACE package RRL_ST_DEFER_PHYSICAL authid definer accessible by(package RRL_ST_DEFER_API,package RRL_ST_DEFER_WAIT_API,package RRL_ST_DEFER_WAIT_CORE)as
 function snapshot(p_st varchar2,p_ware number,p_ignore_plan varchar2 default null)return clob;
end;
/


CREATE OR REPLACE package RRL_ST_DEFER_PLACE_READ authid definer
 accessible by(package RRL_ST_DEFER_HU_WAIT,package RRL_ST_DEFER_WAIT_API,package RRL_ST_DEFER_CASE_WAIT)as
 function collect(p_st varchar2,p_ware number,p_ignore_plan varchar2 default null,p_display boolean default false)return clob;
 function selected(p_st varchar2,p_ware number,p_root varchar2,p_ignore_plan varchar2 default null)return clob;
 function manifest(p_st varchar2)return json_array_t;
end;
/


CREATE OR REPLACE package RRL_ST_DEFER_WAIT_API authid definer as

 function write_allowed return number;

 procedure plan_waiting(p_operation varchar2,p_decision varchar2,p_actor varchar2,p_result out clob,p_root varchar2 default null);

 procedure record_hu_plan(p_request clob,p_task number,p_frozen json_object_t,p_result in out clob);
 procedure read_places(p_decision varchar2,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_ST_DEFER_WAIT_CORE authid definer as
 procedure check_target(p_cell varchar2,p_ware number);
 function members(p_snapshot clob,p_uid varchar2)return clob;
 procedure plan_task(p_task RRL_WAREHOUSE_TASK%rowtype,p_actor varchar2,p_resources in out nocopy json_array_t,p_domain in out nocopy json_object_t);
 procedure validate_task(p_task RRL_WAREHOUSE_TASK%rowtype,p_actor varchar2,p_frozen json_object_t);
 procedure complete_task(p_task RRL_WAREHOUSE_TASK%rowtype,p_quantity number,p_target_uid varchar2,p_actor varchar2);
end;
/


CREATE OR REPLACE package RRL_ST_LAYOUT_READ as
 function scope_order(p_order number,p_actor varchar2,p_permission varchar2 default 'customer_order_view')return number;
 function snapshot(p_order number,p_row number,p_target number,p_actor varchar2)return clob;
end;
/


CREATE OR REPLACE package RRL_TARE_DAMAGE_TRACE authid definer accessible by(
 package RRL_STOCK_TARE_CMD,package RRL_STOCK_TARE_RESOLVE,package RRL_STOCK_TARE_LOSS,
 trigger RRL_TARE_DORIGIN_GUARD,trigger RRL_TARE_DPOSITION_GUARD,trigger RRL_TARE_DOFFER_GUARD,trigger RRL_TARE_DMOVE_GUARD)as
 function tracked_quantity(p_key raw)return number;
 function origin_exists(p_damage varchar2)return boolean;
 function offer_origin(p_offer varchar2)return varchar2;
 procedure check_transfer(p_damage varchar2,p_key raw,p_quantity number,p_physical number);
 procedure register_damage(p_operation varchar2,p_key raw,p_quantity number);
 procedure record_offer(p_operation varchar2,p_damage varchar2);
 procedure record_transfer(p_operation varchar2,p_damage varchar2,p_from raw,p_to raw,p_quantity number);
 procedure record_writeoff(p_operation varchar2,p_damage varchar2,p_key raw,p_quantity number);
 procedure assert_internal;
end;
/


CREATE OR REPLACE package RRL_TARE_LOAD_RECOVERY_API authid definer accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_TARE_BOOK_CMD,package RRL_STOCK_UNLOAD_CMD)as
 procedure assert_scope(p_request clob,p_actor varchar2);
 function describe_recovery(p_request clob,p_actor varchar2)return clob;
 procedure declare_recovery(p_domain clob,p_operation varchar2,r in out nocopy json_array_t);
 procedure record_recovery(p_domain clob,p_operation varchar2,p_actor varchar2);
end;
/


CREATE OR REPLACE package RRL_TARE_PARTICIPANT authid definer as
 procedure warehouse_actor(p_actor varchar2,p_owner number);
 procedure holder_actor(p_actor varchar2,p_kind varchar2,p_id varchar2,p_owner number,p_trip RRL_TRANSPORT_TASK%rowtype,p_right varchar2);
end;
/


CREATE OR REPLACE package RRL_TARE_PLANNING authid definer as
 function held_quantity(p_key raw) return number;
 procedure assert_available(p_key raw,p_physical number,p_required number);
 function case_booking(p_task number,p_ware number,p_type number) return varchar2;
 procedure require_case(p_task number,p_ware number,p_type number);
end;
/


CREATE OR REPLACE package RRL_TASK_RESOURCE_POLICY authid definer as
 function context_json(p_task number,p_action varchar2,p_actor varchar2,p_assignee varchar2,
  p_resource number default null,p_session number default null,p_equipment number default null) return clob;
end;
/


CREATE OR REPLACE package RRL_TRACEABILITY_API as
  function add_trace_event(
    p_event_type       varchar2,
    p_entity_type      varchar2,
    p_entity_id        varchar2,
    p_source_system    varchar2 default null,
    p_correlation_id   varchar2 default null,
    p_idempotency_key  varchar2 default null,
    p_payload_json     clob default null,
    p_created_by       varchar2 default null
  ) return number;

  function add_trace_edge(
    p_from_entity_type varchar2,
    p_from_entity_id   varchar2,
    p_to_entity_type   varchar2,
    p_to_entity_id     varchar2,
    p_edge_type        varchar2,
    p_quantity         number default null,
    p_unit_code        varchar2 default null,
    p_trace_event_id   number default null,
    p_created_by       varchar2 default null
  ) return number;

  function enqueue_event(
    p_event_type       varchar2,
    p_aggregate_type   varchar2,
    p_aggregate_id     varchar2,
    p_idempotency_key  varchar2,
    p_payload_json     clob,
    p_target_system    varchar2 default null,
    p_correlation_id   varchar2 default null,
    p_max_try_count    number default 10
  ) return number;

  function lock_next_outbox(
    p_worker_id        varchar2,
    p_target_system    varchar2 default null
  ) return number;

  procedure mark_outbox_done(
    p_event_outbox_id  number,
    p_status           varchar2 default 'DONE',
    p_error_text       varchar2 default null
  );

  procedure mark_outbox_error(
    p_event_outbox_id      number,
    p_error_text           varchar2,
    p_retry_delay_minutes  number default 5,
    p_dead_letter          number default 0
  );

  function add_adapter_request(
    p_system_code          varchar2,
    p_request_kind         varchar2,
    p_event_outbox_id      number default null,
    p_business_key         varchar2 default null,
    p_cert_alias           varchar2 default null,
    p_cert_thumbprint      varchar2 default null,
    p_signature_status     varchar2 default null,
    p_request_json         clob default null,
    p_status               varchar2 default 'STARTED',
    p_try_no               number default 1
  ) return number;

  procedure update_adapter_request(
    p_adapter_request_id   number,
    p_response_json        clob default null,
    p_external_request_id  varchar2 default null,
    p_external_document_id varchar2 default null,
    p_external_status      varchar2 default null,
    p_http_status          number default null,
    p_status               varchar2 default 'DONE',
    p_error_code           varchar2 default null,
    p_error_text           varchar2 default null
  );

  function create_quality_hold(
    p_entity_type      varchar2,
    p_entity_id        varchar2,
    p_reason_code      varchar2 default null,
    p_reason_text      varchar2 default null,
    p_created_by       varchar2 default null
  ) return number;

  procedure release_quality_hold(
    p_quality_hold_id  number,
    p_released_by      varchar2 default null,
    p_release_reason   varchar2 default null
  );
end RRL_TRACEABILITY_API;
/


CREATE OR REPLACE package RRL_TRACE_AGG_LIFECYCLE authid definer as
 function invalidate(p_operation varchar2,p_request clob,p_actor varchar2)return clob;
 procedure assert_write;
 procedure assert_scan(p_system varchar2,p_profile varchar2,p_hash varchar2);
end;
/


CREATE OR REPLACE package RRL_TRANSPORT_COST_API authid definer as

 procedure preview(p_trip number,p_ware number,p_price number,p_actor varchar2,p_result out clob);

 procedure conduct(p_request clob,p_actor varchar2,p_result out clob);

 procedure assert_writing;

end;
/


CREATE OR REPLACE package RRL_TRANSPORT_EDIT_API authid definer as
 procedure create_trip(p_type varchar2,p_day date,p_actor varchar2,p_trip out number);
 procedure update_trip(p_trip number,p_actor varchar2,p_body clob,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_TRANSPORT_NORM_API authid definer as
 procedure publish(p_request clob,p_actor varchar2,p_result out clob);
 function writing return boolean;
end;
/


CREATE OR REPLACE package RRL_TRANSPORT_PLAN_API authid definer as
 function apply_write_allowed(p_plan number)return number;
 procedure apply_plan(p_plan number,p_day date,p_dock varchar2,p_actor varchar2,p_result out clob);
 procedure assign_sts(p_tt number,p_sts clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_TRANSPORT_PLAN_RULES authid definer as
 procedure assert_actor(p_actor varchar2,p_ware number);
 procedure check_vehicle(p_vehicle_id number,p_sts clob,p_complete number,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_TT_MEMBERSHIP_CTX_API authid definer
 accessible by(function RRL_TT_ADD_PALL) as
 procedure begin_member(p_id number,p_trip number);
 procedure end_member;
end;
/


CREATE OR REPLACE package RRL_TT_OPERATION_PLAN_API authid definer as
 procedure generate(p_trip number,p_actor varchar2,p_result out clob);
 procedure write_fact(p_operation number,p_actor varchar2,p_body clob,p_result out clob);
 procedure assert_driver(p_driver number,p_actor varchar2);
 procedure mark_driver_fact(p_operation number,p_driver number,p_actor varchar2,p_action varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_TT_ROUTE_API authid definer as
 function write_allowed(p_operation varchar2)return number;
 procedure context(p_trip number,p_actor varchar2,p_result out clob);
 procedure apply_input(p_operation varchar2,p_actor varchar2,p_body clob,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_TT_ROUTE_SCHEDULE as
 procedure material(p_source clob,p_result out clob);
 procedure lock_material(p_source clob);
 procedure calculate(p_source clob,p_zone varchar2,p_result out clob);
 procedure assert_chain(p_segments clob,p_zone varchar2);
end;
/


CREATE OR REPLACE package RRL_TT_ROUTE_SOURCE authid definer as
 procedure snapshot(p_trip number,p_actor varchar2,p_source out clob,p_hash out varchar2);
 procedure durations(p_trip number,p_actor varchar2,p_drive out number,p_back out number,p_basis out varchar2);
end;
/


CREATE OR REPLACE package RRL_TT_TIME_API authid definer as
 function write_allowed(p_operation varchar2)return number;
 procedure context(p_trip number,p_actor varchar2,p_result out clob);
 procedure approve(p_operation varchar2,p_actor varchar2,p_body clob,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_VEHICLE_PROFILE_API authid definer as
 procedure configure(p_request clob,p_actor varchar2,p_result out clob);
 function describe_profile(p_vehicle number)return clob;
 procedure assert_writing;
 function check_floor_capacity(p_vehicle number,p_counts clob,p_unknown number)return clob;
end;
/


CREATE OR REPLACE package RRL_VEH_DEPART_SOURCE authid definer accessible by(
 package RRL_STOCK_TRIP_DEPART_CMD,trigger RRL_TT_VEH_SOURCE_GUARD)as
 procedure capture_source(p_operation varchar2,p_trip number,p_vehicle number,p_instant timestamp with time zone);
 procedure assert_writing;
end;
/


CREATE OR REPLACE package RRL_WAREHOUSE_MAP_API as
  function VALIDATE_DRAFT(
    p_canvas_id     number,
    p_pick_route_id number default null
  ) return clob;

  procedure PUBLISH_DRAFT(
    p_canvas_id     number,
    p_pick_route_id number default null,
    p_published_by  varchar2 default null
  );
end RRL_WAREHOUSE_MAP_API;
/


CREATE OR REPLACE package RRL_WAREHOUSE_TASK_ACCESS authid definer as
 procedure assert_scope(p_task number,p_actor varchar2,p_assignee varchar2 default null);
 procedure assert_completion(p_request clob,p_actor varchar2);
end;
/


CREATE OR REPLACE package RRL_WARE_DEPOT_API authid definer as
 function write_allowed return number;
 procedure material(p_ware number,p_result out clob);
 procedure context(p_ware number,p_actor varchar2,p_result out clob);
 procedure apply_setting(p_operation varchar2,p_actor varchar2,p_body clob,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_WAVE_EXEC_ACCESS authid definer as
 procedure assert_scope(p_wave number,p_actor varchar2,p_permission varchar2);
 procedure assert_command(p_request clob,p_actor varchar2);
 function deferred_snapshot_json(p_wave number) return clob;
 function mixed_snapshot_json(p_wave number) return clob;
end;
/


CREATE OR REPLACE package RRL_WAVE_TIME_API authid definer as
 function write_allowed(p_operation varchar2)return number;
 procedure context(p_wave number,p_actor varchar2,p_result out clob);
 procedure approve(p_operation varchar2,p_actor varchar2,p_body clob,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_WEIGHT_BOX_CAPACITY authid definer as
 function enabled(p_article varchar2)return number;
 function kg_volume_upper_bound(p_cell varchar2,p_article varchar2)return number;
 function physical_volume(p_uid varchar2,p_cell varchar2,p_quantity number,p_exact number default 1)return number;
 function reservation_volume(p_reservation number,p_quantity number)return number;
end;
/


CREATE OR REPLACE package RRL_WEIGHT_BOX_CHOICE_API authid definer as
 procedure approve_request(p_request clob,p_actor varchar2,p_result out clob);
 procedure cancel_choice(p_choice varchar2,p_actor varchar2,p_reason varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_WEIGHT_BOX_PLANNING_READ authid definer as
 function snapshot_json(p_row number,p_actor varchar2,p_permission varchar2 default 'pick_plan_create')return clob;
end;
/


CREATE OR REPLACE package RRL_WEIGHT_BOX_READ authid definer as
 function decode_json(p_scan varchar2)return clob;
 procedure assert_sku(p_article varchar2,p_gtin varchar2 default null);
end;
/


CREATE OR REPLACE package RRL_WEIGHT_CHOICE_DEMAND_READ authid definer
 accessible by(package RRL_STOCK_POOL_READ) as
 procedure adjustments(p_line number,p_unallocated number,p_pending out number,p_waived out number);
end;
/


CREATE OR REPLACE package RRL_WEIGHT_CHOICE_UNIT_READ authid definer
 accessible by(package RRL_STOCK_WAVE_LAUNCH_CMD,package RRL_STOCK_WAVE_CMD) as
 function selected_units(p_task number,p_uid varchar2,p_cell varchar2,p_qty number)return clob;
end;
/


CREATE OR REPLACE package RRL_WEIGHT_DEVIATION_READ authid definer as
 function waived_line(p_line number)return number;
end;
/


CREATE OR REPLACE package RRL_WEIGHT_PLAN_BIND authid definer accessible by(package RRL_PICKING_API)as
 function bound_plan(p_order number,p_strategy varchar2,p_actor varchar2)return number;
 function target_json(p_row number,p_actor varchar2)return clob;
 procedure finish_bind(p_choice varchar2,p_plan number,p_line number,p_actor varchar2);
end;
/


CREATE OR REPLACE package RRL_WH_FINAL_SCALE_ADMISSION authid definer accessible by(package RRL_STOCK_PALLET_QC_CMD,package RRL_STOCK_QC_GATE,package RRL_STOCK_HU_CMD,package RRL_STOCK_HU_READ,package RRL_STOCK_LOAD_BOX_CORE) as
 procedure assert_capture(p_request clob,p_domain clob);
 procedure claim_capture(p_request clob,p_domain clob,p_operation varchar2);
 function approved(p_domain clob,p_operation varchar2)return number;
 function preserve_case(p_task number)return number;
 function mass_json(p_task number)return clob;
end;
/


CREATE OR REPLACE package RRL_WH_SCALE_API authid definer as
 procedure capture(p_source clob,p_actor varchar2,p_result out clob);
end;
/


CREATE OR REPLACE package RRL_WORKLOAD_CONFIG_API authid definer as
 function write_allowed(p_operation varchar2)return number;
 procedure execute_command(p_operation varchar2,p_actor varchar2,p_action varchar2,p_body clob,p_result out clob);
end;
/


CREATE OR REPLACE package STORE_ADRESSES is
  function Update_cell(
    CELL1 varchar2,
    OTBOR1 integer,
    BLOCKED_FOR_REMAINS1 integer,
    BLOCKED_FOR_POPOLNENIE1 integer,
    X1 integer,
    Y1 integer,
    Z1 integer,
    BLOCKED_FOR_ACCEPT1 integer,
    WARE_ID1 integer,
    LIMIT_WEIGHT1 number,
    LIMIT_HEIGHT1 number,
    Y_VISOTA1 number,
    CELL_WEIGHT1 number,
    CELL_HEIGHT1 number,
    PICK_ORDER1 integer,
    LAST_USER_ID1 varchar2
  ) return int;
end STORE_ADRESSES;
/


CREATE OR REPLACE package TRANSPORT_PLN is
  function get_time(reg_f varchar2, rai_f varchar2, reg_2 varchar2, rai_2 varchar2) return int;
  function get_distance(reg_f varchar2, rai_f varchar2, reg_2 varchar2, rai_2 varchar2) return int;
  function get_time_m(AddrFrom varchar2, AddrTo varchar2) return number;
  function get_dist_m(AddrFrom varchar2, AddrTo varchar2) return number;
  function set_time(reg_f varchar2, rai_f varchar2, reg_2 varchar2, rai_2 varchar2, time1 number) return int;
  function set_distance(reg_f varchar2, rai_f varchar2, reg_2 varchar2, rai_2 varchar2, dist number) return int;
  function set_time_m(AddrFrom varchar2, AddrTo varchar2, time1 number) return int;
  function set_distance_m(AddrFrom varchar2, AddrTo varchar2, dist1 number) return int;
  function is_tt_just_out_go(tt_id int) return int;
  function upd_tt_perdiction(tt_id int) return int;
  function set_mail_sended(tt_id int) return int;
  function set_tt_closed(tt_id int) return int;
end TRANSPORT_PLN;
/


CREATE OR REPLACE package TRANSPORT_TASK is
  function PRINT_PALLET_WEIGHT( PALLET_UID2 varchar2 ) return varchar2;
  function can_print( tt_id int, user_id1 varchar2 ) return varchar2;
  function pallet_count( tt_id int ) return number;
  function tt_wares( tt_id int ) return varchar2;
  function stoim_pall_sb( pall_uid1 varchar2 ) return number;
  function stoim_tt( tt_id int ) return number;
  function test1 return int;
  function TT_UNREADY_COUNT( IDTT int ) return number;
  function TT_READY_PERC( IDTT int ) return number;
  function tt_unready_wares( tt_id int ) return varchar2;
  function TT_VODITEL_TEL( VODITEL_ID1 int ) return varchar2;
  function TT_REORDER_ADR( IDTT int ) return number;
  function RRL_PALLETS_STR( ST_NUMBER1 varchar2 ) return varchar2;
  function RRL_TT_PALLETS_STR( IDTT int ) return varchar2;
  function TT_TIME_OF_OTG( IDTT int ) return date;
  function SERVICE_LEVEL_OTG( IDTT int ) return number;
  function VODITEL_GET_INN( VOD_ID int ) return varchar2;
  function VODITEL_GET_TABEL_NUMB( VOD_ID int ) return varchar2;
  function VODITEL_SET_TABEL_NUMB( vod_id int, tabel_numb1 varchar2, inn1 varchar2 ) return int;
end TRANSPORT_TASK;
/

