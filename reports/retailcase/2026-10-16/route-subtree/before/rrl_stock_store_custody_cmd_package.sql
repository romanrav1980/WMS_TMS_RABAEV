create or replace package RRL_STOCK_STORE_CUSTODY_CMD authid definer accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_STORE_RECEIPT_CMD)as
 procedure assert_scope(p_receipt varchar2,p_actor varchar2);
 procedure declare_receipt(p_receipt varchar2,p_load varchar2,p_uid varchar2,p_resources in out nocopy json_array_t,p_operation varchar2 default null);
 procedure release_accepted(p_receipt varchar2,p_actor varchar2);
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/
