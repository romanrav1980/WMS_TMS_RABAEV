-- Count only usable coverage at the actual picking target, never storage or packed carrier stock.
create or replace package RRL_STOCK_REPL_NEED authid definer as
 function target_coverage(p_pick number,p_cell varchar2,p_exclude number default null) return number;
 function remaining_for_task(p_pick number,p_cell varchar2) return number;
end;
/
create or replace package body RRL_STOCK_REPL_NEED as
 function target_coverage(p_pick number,p_cell varchar2,p_exclude number default null) return number is
  v_total number:=0;v_count number:=0;v_ware number;v_article varchar2(160);v_type varchar2(30);v_order number;
 begin
  select co.WARE_ID,pt.ARTICUL,pt.TASK_TYPE,pt.CUSTOMER_ORDER_ID into v_ware,v_article,v_type,v_order from RRL_PICK_TASK pt
   join RRL_CUSTOMER_ORDER co on co.CUSTOMER_ORDER_ID=pt.CUSTOMER_ORDER_ID where pt.PICK_TASK_ID=p_pick;
  for sr in(select * from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE'
   and SOURCE_LINE_ID=p_pick and CUSTOMER_ORDER_ID=v_order and CELL=p_cell and ARTICUL=v_article and RESERVATION_DOMAIN='PICKING'
   and RESERVATION_KIND='HARD' and STATUS in('ACTIVE','ALLOCATED','PICKING')
   and (p_exclude is null or RESERVATION_ID!=p_exclude) order by RESERVATION_ID fetch first 201 rows only) loop
   v_count:=v_count+1;if v_count>200 then raise_application_error(-20881,'TARGET_COVERAGE_BOUND');end if;
   if RRL_STOCK_ELIGIBILITY.reason(sr.UID_PALLET,sr.CELL,v_ware,sr.BASE_QTY,null,null,
     case when v_type='CASE_PICK' then 'PICK' else 'ALLOCATE' end,sr.RESERVATION_ID,v_article) is null then
    v_total:=v_total+sr.BASE_QTY;
   end if;
  end loop;
  return v_total;
 end;
 function remaining_for_task(p_pick number,p_cell varchar2) return number is v_qty number;v_fact number;
 begin
  select QTY,nvl(FACT_QTY,0) into v_qty,v_fact from RRL_PICK_TASK where PICK_TASK_ID=p_pick;
  return greatest(0,v_qty-v_fact-target_coverage(p_pick,p_cell));
 end;
end;
/
