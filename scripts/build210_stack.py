from pathlib import Path
import json
f=Path("db/migrations/2026-10-11_ni042_stack_stage");out={}
out[str(f/"001_schema.sql")]="""alter table RRL_SKU_RECEIPT_POLICY add(STACK_STAGE varchar2(10)default 'MAIN'not null);
alter table RRL_SKU_RECEIPT_POLICY add constraint RRL_SKU_STACK_STAGE_CK check(STACK_STAGE in('BASE','MAIN','TOP'));
alter table RRL_CASE_PICK_LINE add(STACK_STAGE varchar2(10)default 'MAIN'not null,STACK_POLICY_VERSION number default 0 not null);
alter table RRL_CASE_PICK_LINE add constraint RRL_CASE_STACK_STAGE_CK check(STACK_STAGE in('BASE','MAIN','TOP')and STACK_POLICY_VERSION>=0);
"""
out[str(f/"002_capture.sql")]="""create or replace trigger RRL_CASE_STACK_STAGE_CAPTURE before insert or update of STACK_STAGE,STACK_POLICY_VERSION on RRL_CASE_PICK_LINE for each row
begin
 if inserting then
  select nvl(max(STACK_STAGE),'MAIN'),nvl(max(POLICY_VERSION),0)into :new.STACK_STAGE,:new.STACK_POLICY_VERSION from RRL_SKU_RECEIPT_POLICY where ARTICUL=:new.ARTICUL;
 elsif :new.STACK_STAGE!=:old.STACK_STAGE or :new.STACK_POLICY_VERSION!=:old.STACK_POLICY_VERSION or :new.STACK_STAGE is null or :new.STACK_POLICY_VERSION is null then
  raise_application_error(-20863,'CASE_ISSUED_STACK_STAGE_IMMUTABLE');
 end if;
end;
/
"""
s=(f/"000_before_route.sql").read_text(encoding="utf-8")
s=s.replace("v_rank number;v_rows","v_stage number;v_next_stage number;v_group_max number:=0;v_rank number;v_rows")
anchor="  select PICK_SEQUENCE into v_rank from RRL_CASE_PICK_LINE where CASE_PICK_TASK_ID=p_case and CASE_PICK_LINE_ID=p_line;"
assert anchor in s
s=s.replace(anchor,"""  select PICK_SEQUENCE,case STACK_STAGE when 'BASE'then 1 when 'TOP'then 3 else 2 end into v_rank,v_stage from RRL_CASE_PICK_LINE where CASE_PICK_TASK_ID=p_case and CASE_PICK_LINE_ID=p_line;""")
anchor="  -- Legacy DIRECT cases without any assigned route keep the original contract."
assert anchor in s
s=s.replace(anchor,"""  -- Issued stages must fit the original one-way route; never reverse it by sorting weights.
  for point in(select PICK_SEQUENCE,
    min(case STACK_STAGE when 'BASE'then 1 when 'TOP'then 3 else 2 end) LO,
    max(case STACK_STAGE when 'BASE'then 1 when 'TOP'then 3 else 2 end) HI
   from RRL_CASE_PICK_LINE where CASE_PICK_TASK_ID=p_case and PICK_SEQUENCE is not null
    and nvl(STATUS,'NEW')!='CANCELLED'and(case when STATUS='SHORT_PICKED'then nvl(PICKED_QTY,0)else PLANNED_QTY end)>0
   group by PICK_SEQUENCE order by PICK_SEQUENCE)loop
   if point.LO<v_group_max then raise_application_error(-20886,'CASE_STACK_ROUTE_CONFLICT');end if;
   v_group_max:=point.HI;
  end loop;
  select min(case STACK_STAGE when 'BASE'then 1 when 'TOP'then 3 else 2 end)into v_next_stage
   from RRL_CASE_PICK_LINE where CASE_PICK_TASK_ID=p_case and nvl(STATUS,'NEW')not in('DONE','CANCELLED','SHORT_PICKED')and nvl(PICKED_QTY,0)<PLANNED_QTY
    and(PICK_SEQUENCE=v_rank or(v_known=0 and PICK_SEQUENCE is null));
  if v_next_stage is not null and v_stage!=v_next_stage then raise_application_error(-20886,'CASE_STACK_EARLIER_STAGE_UNFINISHED');end if;
"""+anchor)
s=s.replace("STATUS not in('DONE','CANCELLED','SHORT_PICKED')","nvl(STATUS,'NEW')not in('DONE','CANCELLED','SHORT_PICKED')")
# Avoid replacing the already normalized predicate twice.
s=s.replace("nvl(nvl(STATUS,'NEW'),'NEW')","nvl(STATUS,'NEW')")
out[str(f/"003_route.sql")]=s
p=Path("api/wms_api_server/app/modules/master_data/contracts.py");s=p.read_text(encoding="utf-8")
anchor="    serialized_weight_boxes: bool | None = None";assert anchor in s
out[str(p)]=s.replace(anchor,anchor+'\n    stack_stage: Literal["BASE", "MAIN", "TOP"] | None = None')
p=Path("api/wms_api_server/app/modules/master_data/infrastructure/receipt_policy.py");s=p.read_text(encoding="utf-8")
s=s.replace("p.ORDER_WEIGHT_TOLERANCE_PCT,","p.ORDER_WEIGHT_TOLERANCE_PCT,p.STACK_STAGE,")
s=s.replace('"configured": configured,','"configured": configured,\n                "stack_stage": row["stack_stage"] if configured else "MAIN",')
s=s.replace("select POLICY_VERSION,SERIALIZED_WEIGHT_BOXES,ORDER_WEIGHT_TOLERANCE_PCT from","select POLICY_VERSION,SERIALIZED_WEIGHT_BOXES,ORDER_WEIGHT_TOLERANCE_PCT,STACK_STAGE from")
s=s.replace("            if weighted:","            stage = request.stack_stage or (old[3] if old else \"MAIN\")\n            if weighted:")
s=s.replace('params = {"pct": tolerance','params = {"stage": stage, "pct": tolerance')
s=s.replace("ORDER_WEIGHT_TOLERANCE_PCT=:pct,","ORDER_WEIGHT_TOLERANCE_PCT=:pct,STACK_STAGE=:stage,")
s=s.replace("ORDER_WEIGHT_TOLERANCE_PCT,UPDATED_AT,UPDATED_BY)","ORDER_WEIGHT_TOLERANCE_PCT,STACK_STAGE,UPDATED_AT,UPDATED_BY)")
s=s.replace("values (:a,:v,:m,:w,:pct,systimestamp,:actor)","values (:a,:v,:m,:w,:pct,:stage,systimestamp,:actor)")
s=s.replace('payload = {"marking_required":','payload = {"stack_stage": stage, "marking_required":')
s=s.replace('"marking_required": request.marking_required,"serialized_weight_boxes": weighted,"order_weight_tolerance_pct": format(tolerance,"f"),\n                "profiles"','"marking_required": request.marking_required,"serialized_weight_boxes": weighted,"order_weight_tolerance_pct": format(tolerance,"f"),"stack_stage": stage,\n                "profiles"')
out[str(p)]=s
out[str(f/"apply.sql")]="@@001_schema.sql\n@@002_capture.sql\n@@003_route.sql\n"
out[str(f/"rollback.sql")]="""declare n number;begin select count(*)into n from RRL_SKU_RECEIPT_POLICY where STACK_STAGE!='MAIN';if n>0 then raise_application_error(-20863,'STACK_CONFIG_HISTORY_RETAIN_FORWARD_REPAIR');end if;select count(*)into n from RRL_CASE_PICK_LINE where STACK_STAGE!='MAIN';if n>0 then raise_application_error(-20863,'STACK_ISSUED_HISTORY_RETAIN_FORWARD_REPAIR');end if;end;
/
@@000_before_route.sql
drop trigger RRL_CASE_STACK_STAGE_CAPTURE;
alter table RRL_CASE_PICK_LINE drop constraint RRL_CASE_STACK_STAGE_CK;
alter table RRL_CASE_PICK_LINE drop(STACK_STAGE,STACK_POLICY_VERSION);
alter table RRL_SKU_RECEIPT_POLICY drop constraint RRL_SKU_STACK_STAGE_CK;
alter table RRL_SKU_RECEIPT_POLICY drop column STACK_STAGE;
"""
out[str(f/"verify.sql")]="select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME in('RRL_CASE_ROUTE_ADMISSION','RRL_CASE_STACK_STAGE_CAPTURE');\nselect OBJECT_NAME,OBJECT_TYPE from USER_OBJECTS where STATUS='INVALID'and OBJECT_NAME like 'RRL%';\n"
out["wiki/database/retailcase_ni042_stack_stage_design_20261011.md"]="""# NI04.2: этап укладки и выданный маршрут
210 / NS34-TC01/TC02. Existing global WMS SKU policy/card/version/audit owns explicit BASE foundation, MAIN middle, TOP light/fragile upper goods. MAIN compatibility default; no invented weight threshold or ABC mapping. Existing CASE line captures exact stage+policyversion at birth; later SKU config affects future rows only. Guard immutable metadata, no stock movement by trigger. Native route helper checks stage monotonicity along original saved linear route, refuses incompatible layout before stock effect instead of reversing physical route. Same point requires lower stage first. Actual heavy goods classified by responsible warehouse master-data user; no claim inferred load-bearing engineering. Reuse existing versioned card API and root CASE lock; all legacy MAIN lines preserve behavior. Fresh sources/additive columns/paired rollback only without staged history, otherwise forward repair.
"""
print(json.dumps(out,ensure_ascii=True))
