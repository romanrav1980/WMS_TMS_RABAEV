create or replace package body RRL_DRIVER_SCOPE as
 function allowed_account(p_actor varchar2,p_driver number)return number is n number;begin
  if p_actor is null or p_driver is null then return 0;end if;
  select count(*)into n from RUSERS u join RRL_TR_VODITEL d on d.ID=p_driver
   where u.ID=p_actor and nvl(u.DELETED,0)=0 and nvl(d.DELETED,0)=0
    and upper(trim(u.USER_GROUP))!='GLOBAL_ADMIN'and(
     RRL_HAS_WRIGHT(u.ID,'driver_return_accept')=1 or
     RRL_ACCESS_API.allowed(u.ID,'driver_return_accept','DRIVER',RRL_STOCK_PLAN_HELPER.decimal_text(p_driver),u.ID)=1);
  return case when n=1 then 1 else 0 end;
 end;
end;
/
