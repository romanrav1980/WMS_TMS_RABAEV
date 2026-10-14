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
