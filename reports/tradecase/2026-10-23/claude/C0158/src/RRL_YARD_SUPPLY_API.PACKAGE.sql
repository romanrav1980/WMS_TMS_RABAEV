package RRL_YARD_SUPPLY_API authid definer
 accessible by(package RRL_YARD_VISIT_API,trigger RRL_YARD_SUPPLY_GUARD)as
 function write_allowed return number;
 procedure check_request(p_ware number,p_sources clob,p_actor varchar2);
 procedure create_links(p_ware number,p_visit number,p_sources clob,p_actor varchar2);
 procedure assert_visit(p_ware number,p_visit number,p_actor varchar2,p_write number,p_frozen number default 0);
 function supply_ids(p_visit number)return clob;
end;