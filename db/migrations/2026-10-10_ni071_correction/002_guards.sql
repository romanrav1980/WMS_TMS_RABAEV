create or replace trigger RRL_LOG_EXPENSE_GUARD before insert or update or delete on RRL_LOGISTICS_EXPENSE for each row
declare n number;v_total number;v_previous number;
begin
 if not inserting then raise_application_error(-20863,'LOGISTICS_EXPENSE_IMMUTABLE');end if;
 select count(*)into n from RUSERS u where u.ID=:new.ACTOR and nvl(u.DELETED,0)=0 and(u.WARE_ID=:new.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN')and RRL_HAS_WRIGHT(u.ID,'edit_bill_tt')=1;
 if n!=1 then raise_application_error(-20882,'LOGISTICS_EXPENSE_BOUND_REPORTER_REQUIRED');end if;
 if :new.CORRECTION_OF_OP is null then
  if :new.ADJUSTMENT_SIGN!=1 or :new.EXPECTED_CONFIRMED_TOTAL is not null then raise_application_error(-20886,'LOGISTICS_ORDINARY_EXPENSE_POSITIVE_REQUIRED');end if;
  select count(*)into n from RRL_LOGISTICS_EXP_ARTICLE a where a.CODE=:new.ARTICLE_CODE and a.VERSION_NO=:new.ARTICLE_VERSION and a.NAME=:new.ARTICLE_NAME and a.ACTIVE_FLAG=1 and a.INCLUDED_IN_RATE=0 and a.OBJECT_SCOPE in(:new.OBJECT_KIND,'BOTH');
  if n!=1 then raise_application_error(-20886,'LOGISTICS_EXTRA_ACTIVE_ARTICLE_REQUIRED');end if;
 else
  select AMOUNT into v_total from RRL_LOGISTICS_EXPENSE e where e.OPERATION_ID=:new.CORRECTION_OF_OP and e.CORRECTION_OF_OP is null
  and e.ARTICLE_CODE=:new.ARTICLE_CODE and e.ARTICLE_VERSION=:new.ARTICLE_VERSION and e.ARTICLE_NAME=:new.ARTICLE_NAME
  and e.WARE_ID=:new.WARE_ID and e.OBJECT_KIND=:new.OBJECT_KIND and e.OBJECT_ID=:new.OBJECT_ID and e.CURRENCY=:new.CURRENCY for update;
  select count(*)into n from RRL_LOGISTICS_EXP_DECISION where EXPENSE_OPERATION_ID=:new.CORRECTION_OF_OP and PHASE='FINANCE' and OUTCOME='APPROVE';if n!=1 then raise_application_error(-20886,'LOGISTICS_CORRECTION_ORIGINAL_APPROVAL_REQUIRED');end if;
  select nvl(sum(c.AMOUNT*c.ADJUSTMENT_SIGN),0)into v_previous from RRL_LOGISTICS_EXPENSE c join RRL_LOGISTICS_EXP_DECISION f on f.EXPENSE_OPERATION_ID=c.OPERATION_ID and f.PHASE='FINANCE' and f.OUTCOME='APPROVE' where c.CORRECTION_OF_OP=:new.CORRECTION_OF_OP;
  v_total:=v_total+v_previous;
  if :new.EXPECTED_CONFIRMED_TOTAL is null or v_total!=:new.EXPECTED_CONFIRMED_TOTAL or v_total+:new.AMOUNT*:new.ADJUSTMENT_SIGN<0 or v_total+:new.AMOUNT*:new.ADJUSTMENT_SIGN>=1000000000000000000 then raise_application_error(-20886,'LOGISTICS_CORRECTION_CURRENT_TOTAL_REQUIRED');end if;
 end if;
 if :new.OBJECT_KIND='TRIP' then select count(*)into n from RRL_TRANSPORT_TASK where ID=:new.OBJECT_ID;
 else select count(*)into n from RRL_TR_VEHICLE where ID=:new.OBJECT_ID;end if;
 if n!=1 then raise_application_error(-20886,'LOGISTICS_EXPENSE_EXISTING_OBJECT_REQUIRED');end if;
exception when no_data_found then raise_application_error(-20886,'LOGISTICS_CORRECTION_ORIGINAL_IDENTITY_REQUIRED');
end;
/
create or replace trigger RRL_LOG_EXP_DECISION_GUARD before insert or update or delete on RRL_LOGISTICS_EXP_DECISION for each row
declare v_kind varchar2(10);v_basis varchar2(20);v_actor nvarchar2(50);v_outcome varchar2(10);v_root varchar2(100);v_delta number;v_expected number;v_total number;v_previous number;
begin
 if not inserting then raise_application_error(-20863,'LOGISTICS_EXPENSE_DECISION_IMMUTABLE');end if;
 select e.OBJECT_KIND,e.CORRECTION_OF_OP,e.AMOUNT*e.ADJUSTMENT_SIGN,e.EXPECTED_CONFIRMED_TOTAL into v_kind,v_root,v_delta,v_expected
 from RRL_LOGISTICS_EXPENSE e join RUSERS u on u.ID=:new.ACTOR and nvl(u.DELETED,0)=0
 where e.OPERATION_ID=:new.EXPENSE_OPERATION_ID and(u.WARE_ID=e.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN')and RRL_HAS_WRIGHT(u.ID,case :new.PHASE when 'LOGIST' then 'calc_tt_price' else 'create_tt_price'end)=1;
 if v_kind='VEHICLE' and :new.DISTRIBUTION_BASIS!='NONE' then raise_application_error(-20886,'LOGISTICS_VEHICLE_EXPENSE_NOT_DISTRIBUTED');end if;
 if v_kind='TRIP' and :new.OUTCOME='APPROVE' and :new.DISTRIBUTION_BASIS='NONE' then raise_application_error(-20886,'LOGISTICS_TRIP_DISTRIBUTION_REQUIRED');end if;
 if v_root is not null then
  select AMOUNT into v_total from RRL_LOGISTICS_EXPENSE where OPERATION_ID=v_root and CORRECTION_OF_OP is null for update;
  select DISTRIBUTION_BASIS into v_basis from RRL_LOGISTICS_EXP_DECISION where EXPENSE_OPERATION_ID=v_root and PHASE='FINANCE' and OUTCOME='APPROVE';
  if :new.OUTCOME='APPROVE' and :new.DISTRIBUTION_BASIS!=v_basis then raise_application_error(-20886,'LOGISTICS_CORRECTION_ORIGINAL_BASIS_REQUIRED');end if;
  if :new.PHASE='FINANCE' and :new.OUTCOME='APPROVE' then
   select nvl(sum(c.AMOUNT*c.ADJUSTMENT_SIGN),0)into v_previous from RRL_LOGISTICS_EXPENSE c join RRL_LOGISTICS_EXP_DECISION f on f.EXPENSE_OPERATION_ID=c.OPERATION_ID and f.PHASE='FINANCE' and f.OUTCOME='APPROVE' where c.CORRECTION_OF_OP=v_root;
   v_total:=v_total+v_previous;
   if v_expected is null or v_total!=v_expected or v_total+v_delta<0 or v_total+v_delta>=1000000000000000000 then raise_application_error(-20886,'LOGISTICS_CORRECTION_FINAL_TOTAL_REQUIRED');end if;
  end if;
 end if;
 if :new.PHASE='FINANCE' then
  select ACTOR,DISTRIBUTION_BASIS,OUTCOME into v_actor,v_basis,v_outcome from RRL_LOGISTICS_EXP_DECISION where EXPENSE_OPERATION_ID=:new.EXPENSE_OPERATION_ID and PHASE='LOGIST';
  if v_outcome!='APPROVE' or v_actor=:new.ACTOR then raise_application_error(-20882,'LOGISTICS_INDEPENDENT_FINANCE_REQUIRED');end if;
  if :new.OUTCOME='APPROVE' and :new.DISTRIBUTION_BASIS!=v_basis then raise_application_error(-20886,'LOGISTICS_ORIGINAL_APPROVED_BASIS_REQUIRED');end if;
 end if;
exception when no_data_found then raise_application_error(-20882,'LOGISTICS_EXPENSE_BOUND_PHASE_REQUIRED');
end;
/
