from pathlib import Path
import json
out={};f=Path("db/migrations/2026-10-11_ni042_weight_choice_demand")
out[str(f/"001_reader.sql")]="""create or replace package RRL_WEIGHT_CHOICE_DEMAND_READ authid definer
 accessible by(package RRL_STOCK_POOL_READ) as
 procedure adjustments(p_line number,p_unallocated number,p_pending out number,p_waived out number);
end;
/
create or replace package body RRL_WEIGHT_CHOICE_DEMAND_READ as
 procedure adjustments(p_line number,p_unallocated number,p_pending out number,p_waived out number)is
  c RRL_PICK_WEIGHT_CHOICE%rowtype;o RRL_CUSTOMER_ORDER_ROW%rowtype;
  n number;requested number:=0;actual number:=0;own_actual number:=0;own_requested number:=0;
  num number;den number;scale number;mass number;tasks number:=0;done_tasks number:=0;pending_tasks number:=0;
  selected_actual number:=0;soft_qty number:=0;physical_proof number:=0;source_json json_object_t;original_actual number;
 begin
  p_pending:=0;p_waived:=0;
  if p_unallocated<=0 then return;end if;
  select count(*)into n from RRL_PICK_WEIGHT_CHOICE
   where case when STATUS in('ACCEPTED','USED')then CUSTOMER_ORDER_ROW_ID end=p_line and STATUS='USED';
  if n=0 then return;end if;
  if n!=1 then raise_application_error(-20887,'WEIGHT_CHOICE_DEMAND_SINGLE_ACTIVE_ROW_REQUIRED');end if;
  select *into c from RRL_PICK_WEIGHT_CHOICE
   where case when STATUS in('ACCEPTED','USED')then CUSTOMER_ORDER_ROW_ID end=p_line and STATUS='USED';
  select *into o from RRL_CUSTOMER_ORDER_ROW where CUSTOMER_ORDER_ROW_ID=p_line;
  if o.STATUS in('CANCELLED','REJECTED')or o.CUSTOMER_ORDER_ID!=c.CUSTOMER_ORDER_ID or o.ARTICUL!=c.ARTICLE then return;end if;
  n:=0;
  for cr in(select CUSTOMER_ORDER_ROW_ID,ORDER_QTY,UNIT_CODE from RRL_CUSTOMER_ORDER_ROW
   where CUSTOMER_ORDER_ID=o.CUSTOMER_ORDER_ID and ARTICUL=o.ARTICUL and STATUS not in('CANCELLED','REJECTED')
   order by CUSTOMER_ORDER_ROW_ID fetch first 201 rows only)loop
   n:=n+1;if n>200 then raise_application_error(-20881,'WEIGHT_CHOICE_DEMAND_ROWS_BOUND');end if;
   select NUMERATOR,DENOMINATOR,BASE_SCALE into num,den,scale from RRL_STOCK_UOM_CONVERSION
    where ARTICUL=o.ARTICUL and INPUT_UOM=cr.UNIT_CODE and BASE_UOM='KG'order by POLICY_VERSION desc fetch first 1 row only;
   mass:=RRL_STOCK_MATH.convert_exact(RRL_STOCK_PLAN_HELPER.decimal_text(cr.ORDER_QTY),num,den,scale);
   requested:=requested+mass;if cr.CUSTOMER_ORDER_ROW_ID=p_line then own_requested:=mass;end if;
  end loop;
  if requested!=c.ORIGINAL_ORDER_KG then return;end if;
  n:=0;
  for pt in(select pt.PICK_TASK_ID,pt.STATUS,pt.FACT_QTY,pt.QTY,pt.PICK_PLAN_LINE_ID,pl.CUSTOMER_ORDER_ROW_ID
   from RRL_PICK_TASK pt join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_LINE_ID=pt.PICK_PLAN_LINE_ID
   join RRL_CUSTOMER_ORDER_ROW cr on cr.CUSTOMER_ORDER_ROW_ID=pl.CUSTOMER_ORDER_ROW_ID
   where cr.CUSTOMER_ORDER_ID=o.CUSTOMER_ORDER_ID and cr.ARTICUL=o.ARTICUL and cr.STATUS not in('CANCELLED','REJECTED')
   order by pt.PICK_TASK_ID fetch first 2001 rows only)loop
   n:=n+1;if n>2000 then raise_application_error(-20881,'WEIGHT_CHOICE_DEMAND_TASKS_BOUND');end if;
   if pt.STATUS in('IN_PROGRESS','DONE')then
    actual:=actual+nvl(pt.FACT_QTY,0);
    if pt.CUSTOMER_ORDER_ROW_ID=p_line then own_actual:=own_actual+nvl(pt.FACT_QTY,0);end if;
   end if;
   if pt.PICK_PLAN_LINE_ID=c.PICK_PLAN_LINE_ID and pt.STATUS not in('CANCELLED','FAILED')then
    tasks:=tasks+1;if pt.QTY!=c.NET_WEIGHT_KG then return;end if;
    if pt.STATUS='DONE'then done_tasks:=done_tasks+1;selected_actual:=selected_actual+nvl(pt.FACT_QTY,0);
    elsif pt.STATUS in('NEW','ASSIGNED','IN_PROGRESS')then pending_tasks:=pending_tasks+1;end if;
   end if;
  end loop;
  if tasks!=1 then return;end if;
  source_json:=json_object_t.parse(c.SOURCE_JSON);
  original_actual:=RRL_STOCK_MATH.quantity(source_json.get_string('picked_order_quantity'));
  if done_tasks=1 and selected_actual=c.NET_WEIGHT_KG and actual=original_actual+c.NET_WEIGHT_KG then
   select count(*)into physical_proof from RRL_CASE_PICK_LINE l join RRL_CASE_PICK_TASK ct on ct.CASE_PICK_TASK_ID=l.CASE_PICK_TASK_ID
    join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=c.PHYSICAL_UNIT_KEY
    where l.PICK_PLAN_LINE_ID=c.PICK_PLAN_LINE_ID and l.PICKED_QTY=c.NET_WEIGHT_KG and ct.STATUS!='CANCELLED'
     and u.BASE_QTY=c.NET_WEIGHT_KG;
   if physical_proof=1 and(c.CHOICE_MODE='LAST_WHOLE_BOX'or
    (actual>=requested*(1-c.TOLERANCE_PCT/100)and actual<=requested*(1+c.TOLERANCE_PCT/100)))then
    p_waived:=least(p_unallocated,greatest(own_requested-own_actual,0));
   end if;
  elsif pending_tasks=1 then
   select nvl(sum(RESERVED_QTY),0)into soft_qty from RRL_PICK_RESERVATION
    where PICK_PLAN_LINE_ID=c.PICK_PLAN_LINE_ID and RESERVATION_STATUS='ACTIVE'and RESERVATION_LEVEL='SOFT';
   select count(*)into physical_proof from RRL_WMS_RECEIPT_UNIT u join RRL_STOCK_RESERVATION sr on sr.RESERVATION_ID=u.HARD_RESERVATION_ID
    where u.PHYSICAL_UNIT_KEY=c.PHYSICAL_UNIT_KEY and u.BASE_QTY=c.NET_WEIGHT_KG
     and sr.PICK_PLAN_LINE_ID=c.PICK_PLAN_LINE_ID and sr.RESERVATION_KIND='HARD'and sr.STATUS in('ACTIVE','ALLOCATED','PICKING');
   if soft_qty=c.NET_WEIGHT_KG or physical_proof=1 then p_pending:=p_unallocated;end if;
  end if;
 exception when no_data_found then raise_application_error(-20868,'WEIGHT_CHOICE_CURRENT_ORDER_OR_KG_REQUIRED');
 end;
end;
/
"""
s=(f/"000_before_pool.sql").read_text(encoding="utf-8")
s=s.replace("requested number;waived_qty number;hard_qty number;","requested number;waived_qty number;choice_pending number;choice_waived number;hard_qty number;")
anchor="   x:=json_object_t();x.put('picked_hard_overlap'"
assert anchor in s
s=s.replace(anchor,"   RRL_WEIGHT_CHOICE_DEMAND_READ.adjustments(o.CUSTOMER_ORDER_ROW_ID,qty,choice_pending,choice_waived);\n   waived_qty:=waived_qty+choice_waived;qty:=greatest(0,qty-choice_pending-choice_waived);\n"+anchor)
s=s.replace("  x.put('accepted_weight_deviation_quantity',","  x.put('weight_choice_pending_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(choice_pending));\n  x.put('accepted_weight_deviation_quantity',")
s=s.replace("case when waived_qty>0 then","case when choice_pending>0 then 'UNALLOCATED_BASE_AFTER_PENDING_WEIGHT_CHOICE'when waived_qty>0 then")
out[str(f/"002_pool.sql")]=s
out[str(f/"apply.sql")]="@@001_reader.sql\n@@002_pool.sql\n"
out[str(f/"rollback.sql")]="@@000_before_pool.sql\ndrop package RRL_WEIGHT_CHOICE_DEMAND_READ;\n"
out["wiki/database/nicora_ni042_weight_choice_demand_design_20261011.md"]="""# NI04.2: потребность после утверждённой целой коробки
198 pure existing pool reader: current USED choice with original active PT and SOFT/HARD suppresses only unallocated demand as pending intent; exposes separate pending quantity, no physical fact/shipment. Completed exact selected CASE/PT mass under preserved approval may waive own remaining gap, original requested unchanged. Current full order SKU requested equals frozen approval, current picked total equals frozen previous actual+box net; original CASE notcancelled/physical key/net/line mass proof required. LAST_WHOLE_BOX explicit exception allows outsidepct; WITHIN must remaininside. Cancel/return PT invalidates pending+waiver, original demand reopens. No balances updated.
"""
for p,line in[("wiki/index.md","- [Проект потребности после целой коробки](database/nicora_ni042_weight_choice_demand_design_20261011.md):198 pure pending vs fulfilled deviation/current original order/return reopening."),
("wiki/log.md","2026-10-11:198 design original demand/pending approved box vs actual completed deviation; current task/source/order proof and return invalidation; no physical effect.")]:
 path=Path(p);out[p]=path.read_text(encoding="utf-8")+"\n"+line+"\n"
print(json.dumps(out,ensure_ascii=True))
