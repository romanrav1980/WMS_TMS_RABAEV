create or replace package RRL_PICKER_TIME_AUTH authid definer accessible by(package RRL_PICKER_TIME_API,package RRL_PICKER_TIME_READ) as
 procedure actor_required(p_actor varchar2);
 procedure ware_required(p_actor varchar2,p_ware number);
 procedure source_permission(p_actor varchar2,p_kind varchar2,p_ware number);
 procedure session_required(p_actor varchar2,p_session number,p_active boolean,p_ware out number,p_resource out number);
 function source_allowed(p_actor varchar2,p_kind varchar2,p_id number,p_session number,p_ware number,p_resource number)return number;
end;
/
