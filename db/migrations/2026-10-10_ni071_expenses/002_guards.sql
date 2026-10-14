create or replace trigger RRL_LOG_EXP_ARTICLE_GUARD before insert or update or delete on RRL_LOGISTICS_EXP_ARTICLE for each row
begin
 if deleting then raise_application_error(-20863,'LOGISTICS_ARTICLE_RETAIN_HISTORY');end if;
 if RRL_HAS_WRIGHT(:new.ACTOR,'create_tt_price')!=1 then raise_application_error(-20882,'LOGISTICS_ARTICLE_FINANCE_REQUIRED');end if;
 if :new.CODE='WAREHOUSE_PICKING' then raise_application_error(-20886,'LOGISTICS_INCLUDED_BOX_WORK_NOT_EXTRA');end if;
 if inserting and :new.VERSION_NO!=1 then raise_application_error(-20886,'LOGISTICS_ARTICLE_INITIAL_VERSION_REQUIRED');end if;
 if updating and(:new.CODE!=:old.CODE or :new.VERSION_NO!=:old.VERSION_NO+1)then raise_application_error(-20886,'LOGISTICS_ARTICLE_VERSION_REQUIRED');end if;
end;
/
create or replace trigger RRL_LOG_EXPENSE_GUARD before insert or update or delete on RRL_LOGISTICS_EXPENSE for each row
declare n number;
begin
 if not inserting then raise_application_error(-20863,'LOGISTICS_EXPENSE_IMMUTABLE');end if;
 select count(*)into n from RUSERS u join RRL_LOGISTICS_EXP_ARTICLE a on a.CODE=:new.ARTICLE_CODE
 where u.ID=:new.ACTOR and nvl(u.DELETED,0)=0 and(u.WARE_ID=:new.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN')
 and RRL_HAS_WRIGHT(u.ID,'edit_bill_tt')=1 and a.VERSION_NO=:new.ARTICLE_VERSION and a.NAME=:new.ARTICLE_NAME
 and a.ACTIVE_FLAG=1 and a.INCLUDED_IN_RATE=0 and a.OBJECT_SCOPE in(:new.OBJECT_KIND,'BOTH');
 if n!=1 then raise_application_error(-20882,'LOGISTICS_EXPENSE_BOUND_REPORTER_AND_EXTRA_ARTICLE_REQUIRED');end if;
 if :new.OBJECT_KIND='TRIP' then select count(*)into n from RRL_TRANSPORT_TASK where ID=:new.OBJECT_ID;
 else select count(*)into n from RRL_TR_VEHICLE where ID=:new.OBJECT_ID;end if;
 if n!=1 then raise_application_error(-20886,'LOGISTICS_EXPENSE_EXISTING_OBJECT_REQUIRED');end if;
end;
/
create or replace trigger RRL_LOG_EXP_DECISION_GUARD before insert or update or delete on RRL_LOGISTICS_EXP_DECISION for each row
declare n number;v_kind varchar2(10);v_basis varchar2(20);v_actor nvarchar2(50);v_outcome varchar2(10);
begin
 if not inserting then raise_application_error(-20863,'LOGISTICS_EXPENSE_DECISION_IMMUTABLE');end if;
 select e.OBJECT_KIND into v_kind from RRL_LOGISTICS_EXPENSE e join RUSERS u on u.ID=:new.ACTOR and nvl(u.DELETED,0)=0
 where e.OPERATION_ID=:new.EXPENSE_OPERATION_ID and(u.WARE_ID=e.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN')
 and RRL_HAS_WRIGHT(u.ID,case :new.PHASE when 'LOGIST' then 'calc_tt_price' else 'create_tt_price'end)=1;
 if v_kind='VEHICLE' and :new.DISTRIBUTION_BASIS!='NONE' then raise_application_error(-20886,'LOGISTICS_VEHICLE_EXPENSE_NOT_DISTRIBUTED');end if;
 if v_kind='TRIP' and :new.OUTCOME='APPROVE' and :new.DISTRIBUTION_BASIS='NONE' then raise_application_error(-20886,'LOGISTICS_TRIP_DISTRIBUTION_REQUIRED');end if;
 if :new.PHASE='FINANCE' then
  select ACTOR,DISTRIBUTION_BASIS,OUTCOME into v_actor,v_basis,v_outcome from RRL_LOGISTICS_EXP_DECISION where EXPENSE_OPERATION_ID=:new.EXPENSE_OPERATION_ID and PHASE='LOGIST';
  if v_outcome!='APPROVE' or v_actor=:new.ACTOR then raise_application_error(-20882,'LOGISTICS_INDEPENDENT_FINANCE_REQUIRED');end if;
  if :new.OUTCOME='APPROVE' and :new.DISTRIBUTION_BASIS!=v_basis then raise_application_error(-20886,'LOGISTICS_ORIGINAL_APPROVED_BASIS_REQUIRED');end if;
 end if;
exception when no_data_found then raise_application_error(-20882,'LOGISTICS_EXPENSE_BOUND_PHASE_REQUIRED');
end;
/
