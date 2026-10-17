create or replace package RRL_STOCK_STORE_WEIGHT_CORE authid definer accessible by(package RRL_STOCK_STORE_RECEIPT_CMD) as
 procedure resolve_weight(p_source clob,p_metadata clob,p_actor varchar2,p_proof out json_object_t,p_has_issue out boolean);
 procedure declare_rows(p_operation varchar2,p_proof json_object_t,r in out nocopy json_array_t);
 procedure persist(p_operation varchar2,p_proof json_object_t,p_actor varchar2);
end;
/
