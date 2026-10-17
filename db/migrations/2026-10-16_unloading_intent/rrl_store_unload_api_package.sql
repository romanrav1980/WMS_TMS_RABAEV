create or replace package RRL_STORE_UNLOAD_API authid definer as
 procedure start_unloading(p_request clob,p_actor varchar2,p_result out clob);
 procedure abandon_start(p_request clob,p_actor varchar2,p_result out clob);
 function writing return boolean;
end;
/
