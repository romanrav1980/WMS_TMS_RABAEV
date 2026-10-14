create or replace package RRL_STOCK_INTERWARE_PART authid definer accessible by(package RRL_STOCK_INTERWARE_REC) as 
 procedure describe_partial(p_metadata json_object_t,p_original_uid varchar2,p_original_qty number,p_unit varchar2,p_article varchar2,p_domain in out json_object_t); 
 procedure describe_selected_units(p_metadata json_object_t,p_domain in out json_object_t); 
 procedure create_pallet(p_domain json_object_t,p_operation varchar2); 
end;
/
