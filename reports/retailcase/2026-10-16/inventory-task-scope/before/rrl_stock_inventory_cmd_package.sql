create or replace package RRL_STOCK_INVENTORY_CMD authid definer

 accessible by(package RRL_STOCK_POSTING_API) as

 procedure compile_count(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);

 procedure execute_count(p_request clob,p_actor varchar2,p_result out clob);

end;
/
