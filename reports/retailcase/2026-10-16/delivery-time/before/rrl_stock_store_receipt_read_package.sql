create or replace package RRL_STOCK_STORE_RECEIPT_READ authid definer as
 procedure require_receiver(p_actor varchar2,p_store varchar2);
 procedure describe_load(p_load varchar2,p_actor varchar2,p_store varchar2,p_domain out clob);
 function preview_json(p_load varchar2,p_actor varchar2,p_store varchar2) return clob;
end;
/
