create or replace trigger RRL_IW_THERMAL_GUARD before insert or update or delete on RRL_INTERWARE_THERMAL_FACT for each row
declare n number;begin
 if not inserting then raise_application_error(-20863,'INTERWARE_THERMAL_FACT_IMMUTABLE');end if;
 RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
 select count(*)into n from RRL_INTERWARE_PLAN p join RUSERS u on u.ID=:new.ACTOR where p.OPERATION_ID=:new.PLAN_OPERATION_ID and nvl(u.DELETED,0)=0 and RRL_HAS_WRIGHT(u.ID,'transport_dispatch_edit')=1 and(u.WARE_ID=p.TARGET_WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN');
 if n!=1 then raise_application_error(-20882,'INTERWARE_CURRENT_TARGET_DISPATCHER_REQUIRED');end if;
end;
/
