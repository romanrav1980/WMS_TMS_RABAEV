create or replace package RRL_STOCK_HU_PLACEMENT_CORE authid definer
 accessible by(package RRL_STOCK_HU_UNPACK_CMD,package RRL_STOCK_HU_SLOT_MOVE_CMD,package RRL_STOCK_CASE_MOVE_CMD,package RRL_STOCK_CASE_RETURN_CMD,package RRL_STOCK_SHIPPING_CORE,package RRL_STOCK_HU_REPACK_CMD) as
 procedure declare_existing_case(r in out nocopy json_array_t,p_case number);
 procedure release_case(p_case number,p_cell varchar2);
 procedure declare_place(r in out nocopy json_array_t,p_task number,p_sync number);
 procedure record_place(p_request clob,p_actor varchar2,p_uid varchar2,p_warehouse number,p_cell varchar2,p_task number,p_slot number,p_sync number,p_placement clob,p_case_task number default null);
end;
/

