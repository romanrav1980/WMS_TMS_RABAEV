package RRL_TRADE_STOCK_GUARD authid definer as
 function owner_allowed(p_actor varchar2,p_ware number,p_owner varchar2,p_write number default 0) return number;
 procedure assert_owner(p_actor varchar2,p_ware number,p_owner varchar2,p_write number default 0);
 function reason(p_uid varchar2,p_cell varchar2,p_ware number,p_purpose varchar2) return varchar2;
 procedure assert_command_stock(p_uid varchar2,p_request clob,p_actor varchar2);
 procedure assert_cell(p_cell varchar2);
end;