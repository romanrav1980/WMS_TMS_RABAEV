package RRL_TRADE_TOPUP_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API)as
 -- TRADE_TOPUP_CONFIRM: physical HARD hold of whole boxes + CONFIRMED + one SAP request, one StockPosting transaction.
 -- TRADE_TOPUP_RELEASE: release of this proposal's own holds only (dispatcher cancel or SAP rejection).
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
 procedure assert_access(p_request clob,p_actor varchar2);
end;