package RRL_ACCESS_API as
 function is_admin(p_actor nvarchar2) return number;
 function allowed(p_actor nvarchar2,p_permission varchar2,p_kind varchar2,p_id varchar2,p_owner nvarchar2 default null) return number;
 function explanation(p_actor nvarchar2,p_permission varchar2,p_kind varchar2,p_id varchar2) return clob;
 procedure assert_allowed(p_actor nvarchar2,p_permission varchar2,p_kind varchar2,p_id varchar2,p_owner nvarchar2 default null);
 procedure assert_independent(p_actor nvarchar2,p_author nvarchar2,p_process varchar2);
 procedure execute_command(p_actor nvarchar2,p_operation varchar2,p_hash varchar2,p_json clob,p_result out clob);
end RRL_ACCESS_API;