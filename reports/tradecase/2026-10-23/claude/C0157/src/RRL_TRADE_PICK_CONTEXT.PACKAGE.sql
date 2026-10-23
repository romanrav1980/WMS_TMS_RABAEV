package RRL_TRADE_PICK_CONTEXT authid definer
 accessible by(package RRL_STOCK_TASK_CORE,package RRL_PICKING_API,package RRL_TRADE_STOCK_GUARD,package RRL_STOCK_WAVE_LAUNCH_CMD,package RRL_STOCK_WAVE_CMD,package RRL_STOCK_WAVE_READY,package RRL_STOCK_CASE_PICK_CMD)as
 procedure enter_line(p_row number,p_actor varchar2);
 procedure clear_line;
 procedure enter_pick_task(p_task number,p_actor varchar2,p_write number default 1);
 function has_line return number;
 function reason(p_uid varchar2,p_cell varchar2,p_ware number,p_purpose varchar2 default 'ALLOCATE')return varchar2;
end;