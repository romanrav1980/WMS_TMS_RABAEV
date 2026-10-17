create or replace package RRL_IW_HU_REC_CORE authid definer accessible by(package RRL_STOCK_INTERWARE_REC)as
 procedure declare_rows(p_domain json_object_t,p_operation varchar2,p_resources in out nocopy json_array_t);
 procedure restore(p_domain json_object_t,p_operation varchar2,p_actor varchar2);
end;
/
