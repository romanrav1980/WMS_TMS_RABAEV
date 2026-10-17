create or replace package RRL_HU_EXEC_ACCESS as
 procedure assert_request(p_request clob,p_actor varchar2);
end;
/
