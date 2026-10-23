package RRL_TRADE_TOPUP_API authid definer as
 -- Non-stock decisions only. Confirmation and release of physical holds are StockPosting commands (RRL_TRADE_TOPUP_CMD).
 procedure save(p_request clob,p_actor varchar2,p_result out clob);
 procedure load_saved(p_ware number,p_trip varchar2,p_operation varchar2,p_request_hash varchar2,p_actor varchar2,p_result out clob);
 procedure decide(p_request clob,p_actor varchar2,p_result out clob);
 procedure sap_accept(p_request clob,p_actor varchar2,p_result out clob);
 function list_trip(p_ware number,p_trip varchar2,p_actor varchar2)return clob;
end;