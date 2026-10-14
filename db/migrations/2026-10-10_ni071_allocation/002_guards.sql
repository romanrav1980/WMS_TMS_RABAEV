create or replace trigger RRL_LOG_EXP_ALLOC_GUARD before insert or update or delete on RRL_LOGISTICS_EXP_ALLOCATION for each row
declare n number;
begin
 if not inserting then raise_application_error(-20863,'LOGISTICS_EXPENSE_ALLOCATION_IMMUTABLE');end if;
 select count(*)into n from RRL_LOGISTICS_EXPENSE e join RRL_LOGISTICS_EXP_DECISION f on f.EXPENSE_OPERATION_ID=e.OPERATION_ID
 join RUSERS u on u.ID=:new.ACTOR and nvl(u.DELETED,0)=0
 where e.OPERATION_ID=:new.EXPENSE_OPERATION_ID and e.OBJECT_KIND='TRIP'
 and f.OPERATION_ID=:new.FINANCE_OPERATION_ID and f.PHASE='FINANCE' and f.OUTCOME='APPROVE'
 and f.DISTRIBUTION_BASIS=:new.DISTRIBUTION_BASIS and e.AMOUNT=:new.AMOUNT and e.CURRENCY=:new.CURRENCY
 and(u.WARE_ID=e.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN')and RRL_HAS_WRIGHT(u.ID,'calc_tt_price')=1;
 if n!=1 then raise_application_error(-20882,'LOGISTICS_APPROVED_BOUND_TRIP_ALLOCATION_REQUIRED');end if;
end;
/
create or replace trigger RRL_LOG_EXP_ALLOC_LINE_GUARD before insert or update or delete on RRL_LOGISTICS_EXP_ALLOC_LINE for each row
declare n number;
begin
 if not inserting then raise_application_error(-20863,'LOGISTICS_ALLOCATION_SOURCE_IMMUTABLE');end if;
 select count(*)into n from RRL_LOGISTICS_EXP_ALLOCATION a join RRL_LOGISTICS_EXPENSE e on e.OPERATION_ID=a.EXPENSE_OPERATION_ID
 join RRL_TT_HU_LOAD_FACT l on l.LOAD_OPERATION_ID=:new.LOAD_OPERATION_ID and l.TT_ID=e.OBJECT_ID and l.WARE_ID=e.WARE_ID and l.STATUS='DEPARTED'
 where a.OPERATION_ID=:new.OPERATION_ID and a.CURRENCY=:new.CURRENCY;
 if n!=1 then raise_application_error(-20886,'LOGISTICS_ALLOCATION_EXACT_LOAD_SOURCE_REQUIRED');end if;
end;
/
