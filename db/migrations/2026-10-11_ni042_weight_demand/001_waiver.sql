create or replace package RRL_WEIGHT_DEVIATION_READ authid definer as
 function waived_line(p_line number)return number;
end;
/
create or replace package body RRL_WEIGHT_DEVIATION_READ as
 function waived_line(p_line number)return number is
  o RRL_CUSTOMER_ORDER_ROW%rowtype;
  requested number:=0;actual number:=0;own_requested number:=0;own_actual number:=0;waived number:=0;mass number;
  num number;den number;scale number;n number:=0;decisions number:=0;
 begin
  select *into o from RRL_CUSTOMER_ORDER_ROW where CUSTOMER_ORDER_ROW_ID=p_line;
  select count(*)into n from RRL_CASE_PICK_SHORT sh join RRL_CASE_PICK_LINE l on l.CASE_PICK_LINE_ID=sh.CASE_PICK_LINE_ID
   join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_LINE_ID=l.PICK_PLAN_LINE_ID
   join RRL_PICK_TASK pt on pt.PICK_TASK_ID=l.PICK_TASK_ID
   where pl.CUSTOMER_ORDER_ROW_ID=p_line and sh.STATUS='ACCEPTED'and sh.WEIGHT_DECISION_OPERATION is not null
    and l.STATUS='SHORT_PICKED'and pt.STATUS='DONE';
  if n=0 then return 0;end if;
  if o.STATUS in('CANCELLED','REJECTED')then return 0;end if;
  n:=0;
  for cr in(select CUSTOMER_ORDER_ROW_ID,ORDER_QTY,UNIT_CODE from RRL_CUSTOMER_ORDER_ROW
   where CUSTOMER_ORDER_ID=o.CUSTOMER_ORDER_ID and ARTICUL=o.ARTICUL and STATUS not in('CANCELLED','REJECTED')
   order by CUSTOMER_ORDER_ROW_ID fetch first 201 rows only)loop
   n:=n+1;if n>200 then raise_application_error(-20881,'WEIGHT_WAIVER_ORDER_ROWS_BOUND');end if;
   select NUMERATOR,DENOMINATOR,BASE_SCALE into num,den,scale from RRL_STOCK_UOM_CONVERSION
    where ARTICUL=o.ARTICUL and INPUT_UOM=cr.UNIT_CODE and BASE_UOM='KG'
    order by POLICY_VERSION desc fetch first 1 row only;
   mass:=RRL_STOCK_MATH.convert_exact(RRL_STOCK_PLAN_HELPER.decimal_text(cr.ORDER_QTY),num,den,scale);
   requested:=requested+mass;if cr.CUSTOMER_ORDER_ROW_ID=p_line then own_requested:=mass;end if;
  end loop;
  n:=0;
  for pt in(select pt.PICK_TASK_ID,pt.FACT_QTY,pl.CUSTOMER_ORDER_ROW_ID from RRL_PICK_TASK pt
   join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_LINE_ID=pt.PICK_PLAN_LINE_ID
   join RRL_CUSTOMER_ORDER_ROW cr on cr.CUSTOMER_ORDER_ROW_ID=pl.CUSTOMER_ORDER_ROW_ID
   where cr.CUSTOMER_ORDER_ID=o.CUSTOMER_ORDER_ID and cr.ARTICUL=o.ARTICUL
    and cr.STATUS not in('CANCELLED','REJECTED')and pt.STATUS in('IN_PROGRESS','DONE')
   order by pt.PICK_TASK_ID fetch first 2001 rows only)loop
   n:=n+1;if n>2000 then raise_application_error(-20881,'WEIGHT_WAIVER_PICK_TASKS_BOUND');end if;
   if nvl(pt.FACT_QTY,0)<0 then raise_application_error(-20887,'WEIGHT_WAIVER_INVALID_PICK_FACT');end if;
   actual:=actual+nvl(pt.FACT_QTY,0);if pt.CUSTOMER_ORDER_ROW_ID=p_line then own_actual:=own_actual+nvl(pt.FACT_QTY,0);end if;
  end loop;
  for sh in(select sh.SHORT_QTY,sh.WEIGHT_TOLERANCE_PCT,sh.WEIGHT_ORDER_REQUESTED_KG
   from RRL_CASE_PICK_SHORT sh join RRL_CASE_PICK_LINE l on l.CASE_PICK_LINE_ID=sh.CASE_PICK_LINE_ID
   join RRL_CASE_PICK_TASK ct on ct.CASE_PICK_TASK_ID=l.CASE_PICK_TASK_ID
   join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_LINE_ID=l.PICK_PLAN_LINE_ID
   join RRL_PICK_TASK pt on pt.PICK_TASK_ID=l.PICK_TASK_ID
   join RRL_STOCK_OPERATION op on op.OPERATION_ID=sh.WEIGHT_DECISION_OPERATION
   where pl.CUSTOMER_ORDER_ROW_ID=p_line and sh.STATUS='ACCEPTED'and l.STATUS='SHORT_PICKED'
    and pt.STATUS='DONE'and ct.STATUS!='CANCELLED'and op.STATE='APPLIED'and op.COMMAND_TYPE='CASE_SHORT_APPROVE'
   order by sh.CASE_PICK_SHORT_ID fetch first 201 rows only)loop
   decisions:=decisions+1;if decisions>200 then raise_application_error(-20881,'WEIGHT_WAIVER_DECISIONS_BOUND');end if;
   if requested=sh.WEIGHT_ORDER_REQUESTED_KG and actual>0
    and actual>=requested*(1-sh.WEIGHT_TOLERANCE_PCT/100)
    and actual<=requested*(1+sh.WEIGHT_TOLERANCE_PCT/100)
    then waived:=waived+sh.SHORT_QTY;end if;
  end loop;
  return least(waived,greatest(own_requested-own_actual,0));
 exception when no_data_found then raise_application_error(-20868,'WEIGHT_WAIVER_CURRENT_ORDER_OR_KG_POLICY_REQUIRED');
 end;
end;
/
