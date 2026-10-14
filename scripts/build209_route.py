from pathlib import Path
import json
f=Path("db/migrations/2026-10-11_ni042_route_sequence");out={}
out[str(f/"001_admission.sql")]="""create or replace package RRL_CASE_ROUTE_ADMISSION authid definer accessible by(package RRL_STOCK_CASE_PICK_CMD) as
 procedure assert_next(p_case number,p_line number);
end;
/
create or replace package body RRL_CASE_ROUTE_ADMISSION as
 procedure assert_next(p_case number,p_line number) is
  v_rank number;v_rows number;v_known number;v_pending_unknown number;v_next number;v_passed number;
 begin
  select PICK_SEQUENCE into v_rank from RRL_CASE_PICK_LINE where CASE_PICK_TASK_ID=p_case and CASE_PICK_LINE_ID=p_line;
  select count(*),count(PICK_SEQUENCE),
   sum(case when PICK_SEQUENCE is null and STATUS not in('DONE','CANCELLED','SHORT_PICKED')and nvl(PICKED_QTY,0)<PLANNED_QTY then 1 else 0 end),
   min(case when STATUS not in('DONE','CANCELLED','SHORT_PICKED')and nvl(PICKED_QTY,0)<PLANNED_QTY then PICK_SEQUENCE end),
   max(case when nvl(PICKED_QTY,0)>0 then PICK_SEQUENCE end)
  into v_rows,v_known,v_pending_unknown,v_next,v_passed
  from RRL_CASE_PICK_LINE where CASE_PICK_TASK_ID=p_case;
  if v_rows>200 then raise_application_error(-20881,'CASE_ROUTE_LINE_BOUND_200');end if;
  -- Legacy DIRECT cases without any assigned route keep the original contract.
  if v_known=0 then return;end if;
  if v_rank is null or v_pending_unknown>0 then raise_application_error(-20886,'CASE_ROUTE_ASSIGNED_SEQUENCE_REQUIRED');end if;
  if v_passed is not null and v_rank<v_passed then raise_application_error(-20886,'CASE_ROUTE_BACKTRACK_FORBIDDEN');end if;
  if v_next is not null and v_rank!=v_next then raise_application_error(-20886,'CASE_ROUTE_EARLIER_POINT_UNFINISHED');end if;
 end;
end;
/
"""
s=(f/"000_before_case.sql").read_text(encoding="utf-8")
anchor="  select * into l from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=line_id and CASE_PICK_TASK_ID=task_id;"
assert s.count(anchor)==1
s=s.replace(anchor,anchor+"\n  RRL_CASE_ROUTE_ADMISSION.assert_next(task_id,line_id);")
anchor="  select * into l from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=line_id for update;"
assert s.count(anchor)==1;s=s.replace(anchor,anchor+"\n  RRL_CASE_ROUTE_ADMISSION.assert_next(task_id,line_id);")
out[str(f/"002_case.sql")]=s
out[str(f/"apply.sql")]="@@001_admission.sql\n@@002_case.sql\n"
out[str(f/"rollback.sql")]="@@000_before_case.sql\ndrop package RRL_CASE_ROUTE_ADMISSION;\nalter package RRL_STOCK_CASE_RETURN_CMD compile body;\nalter package RRL_STOCK_SHIPPING_CORE compile body;\nalter package RRL_STOCK_CASE_SHORT_CMD compile body;\nalter package RRL_STOCK_CASE_MOVE_CMD compile body;\nalter package RRL_STOCK_POSTING_API compile body;\n"
out[str(f/"verify.sql")]="select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME in('RRL_CASE_ROUTE_ADMISSION','RRL_STOCK_CASE_PICK_CMD')order by NAME,TYPE,LINE;\nselect OBJECT_NAME,OBJECT_TYPE from USER_OBJECTS where STATUS='INVALID' and OBJECT_NAME like 'RRL%';\n"
out["wiki/database/nicora_ni042_route_sequence_design_20261011.md"]="""# NI04.2: исполнение выданного линейного маршрута
Ticket209 / NS34-TC01/TC02. Existing PICK_ROUTE_CELL.PICK_SEQUENCE, TASK/WAVE/CASE copied sequence and linear topology040 are retained. Missing runtime enforcement found in current native CASE_PICK_CONFIRM: no sequence check. Owner fulfillment; sole physical transaction RRL_STOCK_POSTING_API. Add private bounded CASE route admission before compile and again under existing CASE row mutex: unfinished earlier point blocks later point; accepted later physical pick blocks backward movement. Same-rank lines can be processed in any order. Pending absence/replenishment continues to block until existing decision/recovery; no automatic bypass. Current topology/slotting is not reread or used to rewrite issued source/order. All-null legacy/DIRECT case retains original behavior; mixed missing sequence refuses. No heavy-first planner invented by sorting item weights against physical route. Actual laying stages/route compatibility are subsequent slice. Recovery fresh paired source rollback/no DB copy.
"""
print(json.dumps(out,ensure_ascii=True))
