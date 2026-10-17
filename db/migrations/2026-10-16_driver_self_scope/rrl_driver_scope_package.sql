create or replace package RRL_DRIVER_SCOPE authid definer as
 function allowed_account(p_actor varchar2,p_driver number)return number;
end;
/
