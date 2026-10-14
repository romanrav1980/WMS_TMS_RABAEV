from pathlib import Path
import json
out={};f=Path("db/migrations/2026-10-11_ni042_weight_choice_plan")
p=f/"001_bind.sql";t=p.read_text(encoding="utf-8")
t=t.replace("choices number;used_choices number;","choices number;used_choices number;valid_choices number;")
t=t.replace("  if used_choices!=choices then raise_application_error(-20886,'WEIGHT_PLAN_MIXED_EXISTING_AND_NEW_CHOICES');end if;","  if used_choices!=choices then return 0;end if;")
t=t.replace("select count(distinct c.PICK_PLAN_ID),max(c.PICK_PLAN_ID),max(p.PLAN_STRATEGY)into n,plan_id,strategy_value","select count(distinct c.PICK_PLAN_ID),max(c.PICK_PLAN_ID),max(p.PLAN_STRATEGY),count(*)into n,plan_id,strategy_value,valid_choices")
t=t.replace("p.STATUS in('DRAFT','PLANNED_FULL','PLANNED_PARTIAL');","p.STATUS in('DRAFT','PLANNED_FULL','PLANNED_PARTIAL','RELEASED','DONE')\n    and exists(select 1 from RRL_PICK_TASK pt where pt.PICK_PLAN_LINE_ID=c.PICK_PLAN_LINE_ID and pt.STATUS not in('CANCELLED','FAILED'));")
t=t.replace("  if n!=1 then raise_application_error", "  if n!=1 or valid_choices!=used_choices then raise_application_error",1)
t=t.replace("CUSTOMER_ORDER_ROW_ID=p_row and STATUS in('ACCEPTED','USED')","case when STATUS in('ACCEPTED','USED')then CUSTOMER_ORDER_ROW_ID end=p_row")
a="  if c.STATUS!='ACCEPTED'then raise_application_error(-20886,'WEIGHT_PLAN_EXISTING_CHOICE_ALREADY_USED');end if;"
b="""  if c.STATUS='USED'then
   select count(*)into n from RRL_PICK_PLAN p where p.PICK_PLAN_ID=c.PICK_PLAN_ID
    and p.STATUS in('DRAFT','PLANNED_FULL','PLANNED_PARTIAL','RELEASED','DONE')
    and exists(select 1 from RRL_PICK_TASK pt where pt.PICK_PLAN_LINE_ID=c.PICK_PLAN_LINE_ID and pt.STATUS not in('CANCELLED','FAILED'));
   if n!=1 then raise_application_error(-20886,'WEIGHT_PLAN_RETIRE_RETURNED_CHOICE_BEFORE_REPLANNING');end if;
   result_json.put('already_planned',true);return result_json.to_clob;
  end if;"""
assert a in t;t=t.replace(a,b)
out[str(p)]=t
old=(f/"000_before_picking.sql").read_text(encoding="utf-8");spec,body=old.split("create or replace package body",1);body="create or replace package body"+body
out[str(f/"002_picking_contract.sql")]=spec
a="v_fenced boolean:=false;v_mutating boolean:=false;"
assert body.count(a)==1
body=body.replace(a,a+"v_bound_plan number;v_weight_wire clob;v_weight_choice json_object_t;v_weight_id varchar2(100);v_weight_uid varchar2(150);v_weight_cell varchar2(60);")
a="    select RRL_PICK_PLAN_SQ.nextval into v_pick_plan_id from dual;"
assert body.count(a)==1
body=body.replace(a,"""    if v_release='ACTIVE'then
     v_bound_plan:=RRL_WEIGHT_PLAN_BIND.bound_plan(p_customer_order_id,v_strategy,p_created_by);
     if v_bound_plan>0 then RRL_PICK_PLAN_ADMISSION.end_plan;return v_bound_plan;end if;
    end if;
"""+a)
a="      v_requested_line_qty:=nvl(l.ORDER_QTY,0);";assert body.count(a)==1
body=body.replace(a,a+"v_weight_wire:=null;v_weight_choice:=null;v_weight_id:=null;v_weight_uid:=null;v_weight_cell:=null;")
a="      v_remaining := v_requested_line_qty;";assert body.count(a)==1
body=body.replace(a,a+"""
      if v_release='ACTIVE'then
       v_weight_wire:=RRL_WEIGHT_PLAN_BIND.target_json(l.CUSTOMER_ORDER_ROW_ID,p_created_by);
       if v_weight_wire is not null then
        v_weight_choice:=json_object_t.parse(v_weight_wire);
        if v_weight_choice.has('already_planned')and v_weight_choice.get_boolean('already_planned')then continue;end if;
        v_remaining:=RRL_STOCK_MATH.quantity(v_weight_choice.get_string('quantity'));
        v_weight_id:=v_weight_choice.get_string('choice_id');v_weight_uid:=v_weight_choice.get_string('source_uid');v_weight_cell:=v_weight_choice.get_string('source_cell');
       end if;
      end if;
""")
a="         where r.REMAIN > 0";assert body.count(a)==1
body=body.replace(a,a+"\n           and(v_weight_id is null or(r.UID_POLETA=v_weight_uid and r.CELL=v_weight_cell))")
a="              v_reserve_qty := least(v_remaining, v_candidate_available);";assert body.count(a)==1
body=body.replace(a,a+"""
              if v_weight_id is not null and v_reserve_qty!=RRL_STOCK_MATH.quantity(v_weight_choice.get_string('quantity'))then
               raise_application_error(-20886,'WEIGHT_PLAN_SELECTED_WHOLE_BOX_SOURCE_NOT_FREE');end if;
""")
a="      if v_line_shortage > 0 then";assert body.count(a)==1
body=body.replace(a,"""      if v_weight_id is not null then
       RRL_WEIGHT_PLAN_BIND.finish_bind(v_weight_id,v_pick_plan_id,v_line_id,p_created_by);
       log_decision(v_pick_plan_id,v_line_id,'WEIGHT_BOX_CHOICE','Approved exact whole-box planning target',v_weight_wire,p_created_by);
      end if;
"""+a)
body=body.replace("v_line_shortage, 'NO_FREE_STOCK',\n          'Free stock is not enough after active reservations',","v_line_shortage, case when v_weight_id is not null then 'WEIGHT_BOX_CHOICE_PENDING'else 'NO_FREE_STOCK'end,\n          case when v_weight_id is not null then 'Approved final whole-box deviation; physical execution pending'else 'Free stock is not enough after active reservations'end,")
out[str(f/"002_picking_body.sql")]=body
# Preserve original choice archive while allowing only the private planner context to bind it.
t=(f/"000_before_guard.sql").read_text(encoding="utf-8")
t=t.replace("begin\n if deleting", """declare binding_context boolean;
begin
 binding_context:=sys_context('RRL_WEIGHT_PLAN_CTX','TX_ID')is not null
  and sys_context('RRL_WEIGHT_PLAN_CTX','TX_ID')=dbms_transaction.local_transaction_id(false)
  and sys_context('RRL_WEIGHT_PLAN_CTX','CHOICE_ID')=:new.CHOICE_ID
  and sys_context('RRL_WEIGHT_PLAN_CTX','ACTOR')is not null;
 if deleting""",1)
a=" if sys_context('RRL_WEIGHT_CHOICE_CTX','TX_ID')is null";assert a in t
t=t.replace(a," if not binding_context and(sys_context('RRL_WEIGHT_CHOICE_CTX','TX_ID')is null",1)
a="or sys_context('RRL_WEIGHT_CHOICE_CTX','CHOICE_ID')!=:new.CHOICE_ID\n  then"
t=t.replace(a,"or sys_context('RRL_WEIGHT_CHOICE_CTX','CHOICE_ID')!=:new.CHOICE_ID)\n  then")
a="  if sys_context('RRL_WEIGHT_CHOICE_CTX','PHASE')is null or sys_context('RRL_WEIGHT_CHOICE_CTX','PHASE')!='CANCEL'"
assert a in t
t=t.replace(a,"""  if binding_context then
   if :old.STATUS!='ACCEPTED'or :new.STATUS!='USED'or :new.PICK_PLAN_ID is null or :new.PICK_PLAN_LINE_ID is null
    or :new.USED_AT is null or :new.CANCELLED_BY is not null or :new.CANCELLED_AT is not null or :new.CANCEL_REASON is not null
    then raise_application_error(-20863,'WEIGHT_CHOICE_PRIVATE_PLANNER_BIND_REQUIRED');end if;
  else
"""+a)
# close the new branch before outer end-if
a="   then raise_application_error(-20863,'WEIGHT_CHOICE_VALID_CANCELLATION_REQUIRED');end if;\n end if;"
assert a in t;t=t.replace(a,"   then raise_application_error(-20863,'WEIGHT_CHOICE_VALID_CANCELLATION_REQUIRED');end if;\n  end if;\n end if;")
out[str(f/"003_guard.sql")]=t
out[str(f/"004_index.sql")]="create index RRL_WEIGHT_CHOICE_ORDER_I on RRL_PICK_WEIGHT_CHOICE(CUSTOMER_ORDER_ID,STATUS,PICK_PLAN_ID);\n"
out[str(f/"apply.sql")]="@@001_bind.sql\n@@002_picking_contract.sql\n@@002_picking_body.sql\n@@003_guard.sql\n@@004_index.sql\n"
out[str(f/"rollback.sql")]="""declare n number;begin select count(*)into n from RRL_PICK_WEIGHT_CHOICE where STATUS='USED';if n>0 then raise_application_error(-20863,'WEIGHT_PLAN_RETAIN_BOUND_HISTORY_FORWARD_REPAIR');end if;end;
/
@@000_before_picking.sql
@@000_before_guard.sql
drop context RRL_WEIGHT_PLAN_CTX;
drop package RRL_WEIGHT_PLAN_BIND;
drop index RRL_WEIGHT_CHOICE_ORDER_I;
"""
out["wiki/database/retailcase_ni042_weight_choice_plan_design_20261011.md"]="""# NI04.2: выбранная коробка в существующем плане
196 extends existing RRL_PICKING_API.create_plan only. Original order/requested quantity retained, exact chosen net8or12 becomes actual planned task+existing SOFT from approved source UID/cell. Immutable195 choice bound to new original plan/line in same transaction; private accessible-by planner package/own TX namespace/declared original order+row+source stock locks protects binding. Original ordinary planner unchanged when no choice.
Existing active bound plan replay returns its ID/same strategy; returned/cancelled choice must retire before replacement. Other active already-bound rows skipped while new approved row can plan. Under-target gap labelled approved deviation pending, not false free-stock shortage. Future197 pins exact physical HARD unit;198 current pending/fulfilled deviation accounting and used-choice cancellation.
"""
for name,line in [("wiki/index.md","- [Выбранная коробка в существующем плане: разработка](database/retailcase_ni042_weight_choice_plan_design_20261011.md):196 old plan/SOFT exact target/source/atomic private binding/original request retained."),
("wiki/log.md","2026-10-11:196 starts from fresh live RRL_PICKING_API/choice/guard checkpoint; existing native planner consumes immutable whole-box choice, target differs original without changing original order; no second allocator or stock writer.")]:
 p=Path(name);out[str(p)]=p.read_text(encoding="utf-8")+"\n"+line+"\n"
print(json.dumps(out,ensure_ascii=True))
