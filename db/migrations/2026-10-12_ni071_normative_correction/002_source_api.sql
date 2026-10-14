create or replace package RRL_NORM_COST_CORRECTION authid definer as
 function confirmed_total(p_cost varchar2)return number;
 procedure validate_report(p_cost varchar2,p_ware number,p_kind varchar2,p_object number,p_currency varchar2,p_delta number,p_expected number);
 procedure validate_decision(p_expense varchar2,p_phase varchar2,p_outcome varchar2);
end;
/
create or replace package body RRL_NORM_COST_CORRECTION as
 function confirmed_total(p_cost varchar2)return number is original_amount number;adjusted number;begin
  select json_value(r.RESULT_JSON,'$.total' returning number error on error)into original_amount
   from RRL_LOGISTICS_COST_RUN r join RRL_TRANSPORT_COST_CLAIM c on c.OPERATION_ID=r.OPERATION_ID where r.OPERATION_ID=p_cost;
  select nvl(sum(e.AMOUNT*e.ADJUSTMENT_SIGN),0)into adjusted from RRL_LOGISTICS_EXPENSE e
   join RRL_LOGISTICS_EXP_DECISION f on f.EXPENSE_OPERATION_ID=e.OPERATION_ID and f.PHASE='FINANCE'and f.OUTCOME='APPROVE'
   where e.COST_CORRECTION_OF_OP=p_cost;
  return original_amount+adjusted;
 exception when no_data_found then raise_application_error(-20886,'NORMATIVE_ORIGINAL_COST_REQUIRED');end;
 procedure validate_report(p_cost varchar2,p_ware number,p_kind varchar2,p_object number,p_currency varchar2,p_delta number,p_expected number)is
  v_ware number;v_trip number;v_currency varchar2(3);v_op varchar2(100);total number;
 begin
  select r.WARE_ID,r.TT_ID,r.CURRENCY,r.OPERATION_ID into v_ware,v_trip,v_currency,v_op
   from RRL_LOGISTICS_COST_RUN r where r.OPERATION_ID=p_cost
   and exists(select 1 from RRL_TRANSPORT_COST_CLAIM c where c.OPERATION_ID=r.OPERATION_ID)for update;
  if p_ware!=v_ware or p_kind!='TRIP'or p_object!=v_trip or p_currency!=v_currency then raise_application_error(-20886,'NORMATIVE_CORRECTION_ORIGINAL_IDENTITY');end if;
  total:=confirmed_total(p_cost);
  if p_expected is null or p_expected!=total or p_delta is null or p_delta=0 or total+p_delta<0 or total+p_delta>=1e18
   then raise_application_error(-20867,'NORMATIVE_CORRECTION_CURRENT_TOTAL');end if;
 exception when no_data_found then raise_application_error(-20886,'NORMATIVE_ORIGINAL_COST_REQUIRED');end;
 procedure validate_decision(p_expense varchar2,p_phase varchar2,p_outcome varchar2)is
  cost_op varchar2(100);ware number;kind varchar2(10);object_id number;currency_value varchar2(3);delta number;expected number;
 begin
  select COST_CORRECTION_OF_OP,WARE_ID,OBJECT_KIND,OBJECT_ID,CURRENCY,AMOUNT*ADJUSTMENT_SIGN,EXPECTED_CONFIRMED_TOTAL
   into cost_op,ware,kind,object_id,currency_value,delta,expected from RRL_LOGISTICS_EXPENSE where OPERATION_ID=p_expense;
  if cost_op is not null and p_phase='FINANCE'and p_outcome='APPROVE'then
   validate_report(cost_op,ware,kind,object_id,currency_value,delta,expected);
  end if;
 end;
end;
/
