from pathlib import Path
import json
out={};f=Path("db/migrations/2026-10-11_ni042_weight_decision")
p=f/"001_schema.sql";out[str(p)]=p.read_text(encoding="utf-8").replace("and100","and 100")
p=f/"002_decision.sql";t=p.read_text(encoding="utf-8")
t=t.replace("  if not j.get_boolean('within_tolerance')",'''  if m.get_string('expected_order_weight_signature')is null
   or m.get_string('expected_order_weight_signature')!=j.get_string('order_weight_signature')
   then raise_application_error(-20886,'WEIGHT_DECISION_ORDER_SNAPSHOT_CHANGED');end if;
  if not j.get_boolean('within_tolerance')''')
t=t.replace("before update of","before insert or delete or update of")
t=t.replace(" if :old.WEIGHT_DECISION_OPERATION is not null then",''' if inserting then
  if :new.WEIGHT_DECISION_OPERATION is not null or :new.WEIGHT_POLICY_VERSION is not null or :new.WEIGHT_TOLERANCE_PCT is not null
   or :new.WEIGHT_ORDER_REQUESTED_KG is not null or :new.WEIGHT_ORDER_PICKED_KG is not null then raise_application_error(-20863,'WEIGHT_DECISION_EXPLICIT_UPDATE_REQUIRED');end if;
  return;
 end if;
 if deleting then
  if :old.WEIGHT_DECISION_OPERATION is not null then raise_application_error(-20863,'WEIGHT_DECISION_HISTORY_IMMUTABLE');end if;
  return;
 end if;
 if :old.WEIGHT_DECISION_OPERATION is not null then''')
out[str(p)]=t
t=(f/"000_before_read.sql").read_text(encoding="utf-8")
t=t.replace("  RRL_CASE_TASK_ACCESS.assert_scope(p_task,p_actor,'case_pick_execute');","  if RRL_HAS_WRIGHT(p_actor,'case_pick_short_approve')=1 then RRL_CASE_TASK_ACCESS.assert_scope(p_task,p_actor,'case_pick_short_approve');else RRL_CASE_TASK_ACCESS.assert_scope(p_task,p_actor,'case_pick_execute');end if;")
t=t.replace("  return result_json.to_clob;","  result_json.put('order_weight_signature',rawtohex(sys.dbms_crypto.hash(result_json.to_clob,sys.dbms_crypto.hash_sh256)));\n  return result_json.to_clob;")
out[str(f/"003_read.sql")]=t
old=(f/"000_before_short.sql").read_text(encoding="utf-8");spec,body=old.split("create or replace package body",1);body="create or replace package body"+body
out[str(f/"004_short_contract.sql")]=spec
body=body.replace("inventory_id number;decision varchar2(20);","inventory_id number;decision varchar2(20);weight_wire clob;")
body=body.replace("decision not in('ACCEPT_SHORT','RESTORE')","decision not in('ACCEPT_SHORT','RESTORE','WEIGHT_TOLERANCE')")
a="  select RRL_INVENTORY_TASK_SQ.nextval into inventory_id from dual;"
assert body.count(a)==1
body=body.replace(a,'''  if decision='WEIGHT_TOLERANCE'then
   weight_wire:=RRL_CASE_WEIGHT_DECISION.current_json(p_request,ct.CASE_PICK_TASK_ID,l.CASE_PICK_LINE_ID,d.get_string('actor'));
   RRL_CASE_WEIGHT_DECISION.plan_order(l.CUSTOMER_ORDER_ID,l.ARTICUL,r);
   v.put('weight_order_snapshot',json_object_t.parse(weight_wire));
  end if;
'''+a)
body=body.replace("decision varchar2(20);confirm_mode","weight_wire clob;weight_j json_object_t;weight_pct number;weight_version number;weight_requested number;weight_picked number;decision varchar2(20);confirm_mode")
a="  a:=v.get_array('reservations');carrier:=v.get_array('carrier');"
assert body.count(a)==1
body=body.replace(a,'''  if decision='WEIGHT_TOLERANCE'then
   weight_wire:=RRL_CASE_WEIGHT_DECISION.current_json(p_request,task_id,line_id,p_actor);
   if dbms_lob.compare(weight_wire,v.get_object('weight_order_snapshot').to_clob)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: order weight decision');end if;
   weight_j:=json_object_t.parse(weight_wire);weight_pct:=weight_j.get_number('tolerance_pct');
   weight_version:=weight_j.get_number('policy_version');
   weight_requested:=RRL_STOCK_MATH.quantity(weight_j.get_string('requested_quantity'));
   weight_picked:=RRL_STOCK_MATH.quantity(weight_j.get_string('picked_quantity'));
  end if;
'''+a)
body=body.replace("if decision='RESTORE' or nvl(auto_inv,1)!=0 then","if decision='RESTORE' or(decision!='WEIGHT_TOLERANCE'and nvl(auto_inv,1)!=0)then")
a="  if decision='RESTORE' then\n   update RRL_CASE_PICK_LINE"
assert body.count(a)==1
body=body.replace(a,'''  if decision='WEIGHT_TOLERANCE'then
   update RRL_CASE_PICK_SHORT set WEIGHT_POLICY_VERSION=weight_version,WEIGHT_TOLERANCE_PCT=weight_pct,
    WEIGHT_ORDER_REQUESTED_KG=weight_requested,WEIGHT_ORDER_PICKED_KG=weight_picked,WEIGHT_DECISION_OPERATION=op
    where CASE_PICK_SHORT_ID=short_id;
  end if;
'''+a)
body=body.replace("case when decision='RESTORE' then 'RECOVERY_STARTED' else 'SHORT_ACCEPTED' end","case when decision='RESTORE'then 'RECOVERY_STARTED'when decision='WEIGHT_TOLERANCE'then 'WEIGHT_TOLERANCE_ACCEPTED'else 'SHORT_ACCEPTED'end")
body=body.replace("  j.put('recovery_state'","  if decision='WEIGHT_TOLERANCE'then j.put('weight_order_snapshot',weight_j);j.put('decision','WEIGHT_TOLERANCE');end if;\n  j.put('recovery_state'")
out[str(f/"004_short_body.sql")]=body
out[str(f/"apply.sql")]="@@001_schema.sql\n@@003_read.sql\n@@002_decision.sql\n@@004_short_contract.sql\n@@004_short_body.sql\n"
out[str(f/"rollback.sql")]="""declare n number;begin select count(*)into n from RRL_CASE_PICK_SHORT where WEIGHT_DECISION_OPERATION is not null;if n>0 then raise_application_error(-20863,'WEIGHT_DECISION_RETAIN_HISTORY_FORWARD_REPAIR');end if;end;
/
@@000_before_short.sql
@@000_before_read.sql
drop trigger RRL_CASE_WT_DECISION_GUARD;
drop package RRL_CASE_WEIGHT_DECISION;
alter table RRL_CASE_PICK_SHORT drop constraint RRL_CASE_WT_DECISION_CK;
alter table RRL_CASE_PICK_SHORT drop(WEIGHT_POLICY_VERSION,WEIGHT_TOLERANCE_PCT,WEIGHT_ORDER_REQUESTED_KG,WEIGHT_ORDER_PICKED_KG,WEIGHT_DECISION_OPERATION);
"""
p=Path("api/wms_api_server/app/schemas.py");t=p.read_text(encoding="utf-8")
a='    decision: Literal["ACCEPT_SHORT", "RESTORE"] = "ACCEPT_SHORT"';assert t.count(a)==1
t=t.replace(a,'''    decision: Literal["ACCEPT_SHORT", "RESTORE", "WEIGHT_TOLERANCE"] = "ACCEPT_SHORT"
    expected_weight_policy_version: int | None = Field(default=None, ge=0, strict=True)
    expected_content_version: int | None = Field(default=None, ge=0, strict=True)
    expected_order_weight_signature: str | None = Field(default=None, pattern=r"^[A-F0-9]{64}$")''')
out[str(p)]=t
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/case_short_commands.py");t=p.read_text(encoding="utf-8")
a='**({"decision": "RESTORE"} if getattr(request, "decision", "ACCEPT_SHORT") == "RESTORE" else {})'
assert a in t
t=t.replace(a,'''**({"decision": "RESTORE"} if request.decision == "RESTORE" else
            {"decision": "WEIGHT_TOLERANCE", "expected_weight_policy_version": request.expected_weight_policy_version,
             "expected_content_version": request.expected_content_version, "expected_order_weight_signature": request.expected_order_weight_signature}
            if request.decision == "WEIGHT_TOLERANCE" else {})''')
out[str(p)]=t
out["wiki/database/retailcase_ni042_weight_decision_design_20261011.md"]="""# NI04.2: явное завершение по допуску массы
192 extends existing CASE_SHORT_APPROVE with WEIGHT_TOLERANCE. Actual picked quantity remains immutable stock fact; same native owner releases only unused HARD, closes partial line, records exact original order-SKU mass/pct/version/current signed read snapshot and approval actor/reason. No false inventory discrepancy generated for ordinary weight deviation. Current CONFIG SHARE and declared original order/all SKU rows/all related PT/plan anchors protect concurrent calculation; source signed snapshot checked before/after planned locks. Original accepted metadata append-only guarded root TX/operation/canonical decision/source.
No automatic order waiver until separate193 pool integration proves current cancellation/return-aware demand. No over-plan pick/last-box exemption in192. Hardware precision unchanged; no marked unit opening.
"""
for name,line in [("wiki/index.md","- [Завершение по допуску массы: разработка](database/retailcase_ni042_weight_decision_design_20261011.md):192 existing short approval/native snapshots/current planned order resources; current demand waiver next."),
("wiki/log.md","2026-10-11:192 implementation begins from freshly captured live short/read/pool contracts; existing CASE_SHORT_APPROVE explicit weight decision, no second stock writer; paired history-protected rollback.")]:
 p=Path(name);out[str(p)]=p.read_text(encoding="utf-8")+"\n"+line+"\n"
print(json.dumps(out,ensure_ascii=True))
