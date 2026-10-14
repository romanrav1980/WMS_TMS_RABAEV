create or replace trigger RRL_SUP_HANDOVER_GUARD before insert or update or delete on RRL_SUP_RETURN_HANDOVER for each row
declare n number;
begin
 if not inserting then raise_application_error(-20863,'SUP_RETURN_HANDOVER_IMMUTABLE');end if;
 RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
 select count(*)into n from RRL_STORE_RETURN_SUP_DISPATCH d
 join RRL_STORE_RETURN_RECEIPT r on r.OPERATION_ID=d.RECEIPT_OPERATION_ID
 join RRL_TT_HU_LOAD_FACT l on l.LOAD_OPERATION_ID=d.OPERATION_ID and l.ROOT_UID=d.UID_PALLET
 join RUSERS u on u.ID=:new.ACTOR and nvl(u.DELETED,0)=0
 where d.OPERATION_ID=:new.DISPATCH_OPERATION_ID and l.STATUS='DEPARTED'
 and(u.WARE_ID=r.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN')
 and RRL_HAS_WRIGHT(u.ID,'warehouse_return_dispatch')=1;
 if n!=1 then raise_application_error(-20882,'SUP_RETURN_DEPARTED_BOUND_REPORTER_REQUIRED');end if;
end;
/
create or replace trigger RRL_SUP_CONFIRM_GUARD before insert or update or delete on RRL_SUP_RETURN_CONFIRM for each row
declare n number;
begin
 if not inserting then raise_application_error(-20863,'SUP_RETURN_CONFIRM_IMMUTABLE');end if;
 RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
 select count(*)into n from RRL_SUP_RETURN_HANDOVER h
 join RRL_STORE_RETURN_SUP_DISPATCH d on d.OPERATION_ID=h.DISPATCH_OPERATION_ID
 join RRL_STORE_RETURN_RECEIPT r on r.OPERATION_ID=d.RECEIPT_OPERATION_ID
 join RUSERS u on u.ID=:new.ACTOR and nvl(u.DELETED,0)=0
 where h.OPERATION_ID=:new.HANDOVER_OPERATION_ID and h.ACTOR!=u.ID
 and(u.WARE_ID=r.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN')
 and RRL_HAS_WRIGHT(u.ID,'store_return_approve')=1;
 if n!=1 then raise_application_error(-20882,'SUP_RETURN_INDEPENDENT_BOUND_SC_REQUIRED');end if;
end;
/
