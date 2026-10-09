-- Own one whole-command transaction. Never retry an uncertain commit on this connection.
create or replace package RRL_STOCK_NATIVE_API authid definer as
 procedure post(p_request clob,p_actor varchar2,p_result out clob);
end;
/
