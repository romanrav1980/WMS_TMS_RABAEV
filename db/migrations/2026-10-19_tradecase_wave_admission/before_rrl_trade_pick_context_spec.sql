create or replace package RRL_TRADE_PICK_CONTEXT authid definer
 accessible by(package RRL_PICKING_API,package RRL_TRADE_STOCK_GUARD)as
 procedure enter_line(p_row number,p_actor varchar2);
 procedure clear_line;
 function reason(p_uid varchar2,p_cell varchar2,p_ware number)return varchar2;
end;

/
