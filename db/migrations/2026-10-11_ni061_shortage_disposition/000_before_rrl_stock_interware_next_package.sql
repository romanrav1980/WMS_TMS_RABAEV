create or replace package RRL_STOCK_INTERWARE_NEXT authid definer accessible by(package RRL_STOCK_SHIPPING_CORE) as 
 function describe_source(p_st number,p_ware number) return json_object_t; 
 procedure declare_source(p_source json_object_t,p_operation varchar2,p_resources in out nocopy json_array_t); 
 procedure validate_load(p_source json_object_t,p_actor varchar2); 
 procedure dispatched(p_source json_object_t,p_actor varchar2); 
end;
/
