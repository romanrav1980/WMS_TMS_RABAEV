create or replace package RRL_STOCK_HU_CMD authid definer
 accessible by(package RRL_STOCK_HU_TASK,package RRL_STOCK_POSTING_API,package RRL_STOCK_HU_UNPACK_CMD,package RRL_STOCK_HU_SLOT_MOVE_CMD,package RRL_STOCK_HU_REPACK_CMD) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob,p_allow_slotted boolean default false,p_defer_wait_planning boolean default false);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
 procedure declare_tree(f in out nocopy json_array_t,r in out nocopy json_array_t,s clob);
end;

/
