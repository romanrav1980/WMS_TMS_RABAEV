create or replace package RRL_STOCK_HU_SLOT authid definer
 accessible by(package RRL_STOCK_HU_CMD,package RRL_STOCK_HU_UNPACK_CMD,package RRL_STOCK_HU_SLOT_MOVE_CMD,package RRL_STOCK_HU_REPACK_CMD) as
 function target_json(p_tree clob,p_metadata clob,p_ignored_task number,p_replace_root varchar2 default null,p_extra_weight number default 0,p_extra_volume number default 0) return clob;
end;
/

