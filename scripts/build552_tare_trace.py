import json
from pathlib import Path
f="db/migrations/2026-10-12_ni063_damage_custody/";out={}
def change(v,a,b):
 assert v.count(a)==1,(a,v.count(a))
 return v.replace(a,b)
v=Path(f+"000_before_tare.sql").read_text(encoding="utf-8")
v=change(v,"v_books json_array_t:=json_array_t();","v_books json_array_t:=json_array_t();v_damage varchar2(100);")
v=change(v,"p_domain.put('offer_operation_id',offer.OPERATION_ID);","v_damage:=RRL_TARE_DAMAGE_TRACE.offer_origin(offer.OPERATION_ID);\n   p_domain.put('offer_operation_id',offer.OPERATION_ID);")
v=change(v,"v_tt:=s.get_number('task_id');v_qty:=integer_qty(m.get_string('quantity'));","v_tt:=s.get_number('task_id');v_qty:=integer_qty(m.get_string('quantity'));v_damage:=s.get_string('damage_operation_id');")
v=change(v,"if kind='TARE_COUNT' and(m.get_number('expected_version')","if v_condition='DAMAGED' then\n if kind='TARE_COUNT' then\n  if v_qty<RRL_TARE_DAMAGE_TRACE.tracked_quantity(v_to)+RRL_TARE_PLANNING.held_quantity(v_to)then raise_application_error(-20886,'TARE_COUNT_BELOW_DAMAGE_CUSTODY');end if;\n else RRL_TARE_DAMAGE_TRACE.check_transfer(v_damage,v_from,v_qty,v_from_qty);end if;\n elsif v_damage is not null then raise_application_error(-20886,'TARE_DAMAGE_CONDITION_REQUIRED');end if;\n p_domain.put('damage_operation_id',v_damage);\n if kind='TARE_COUNT' and(m.get_number('expected_version')")
v=change(v,"if kind in('TARE_OFFER','TARE_ACCEPT') then RRL_STOCK_TARE_HANDOVER.declare_books","if v.get_string('damage_operation_id')is not null then RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_RESOLUTION',v.get_string('damage_operation_id'));end if;\n if kind in('TARE_OFFER','TARE_ACCEPT') then RRL_STOCK_TARE_HANDOVER.declare_books")
v=change(v,"RRL_STOCK_TARE_HANDOVER.persist_offer(op,v.get_array('booked_places'));","RRL_STOCK_TARE_HANDOVER.persist_offer(op,v.get_array('booked_places'));\n  RRL_TARE_DAMAGE_TRACE.record_offer(op,v.get_string('damage_operation_id'));")
v=change(v,"j.put('status','POSTED');j.put('tare_balance_changed',true);","if kind='TARE_ACCEPT' then RRL_TARE_DAMAGE_TRACE.record_transfer(op,v.get_string('damage_operation_id'),v_from,v_to,v_qty);end if;\n  j.put('status','POSTED');j.put('tare_balance_changed',true);")
out[f+"003_tare_command.sql"]=v
v=Path(f+"000_before_resolve.sql").read_text(encoding="utf-8")
v=change(v,"select nvl(sum(QUANTITY),0) into v_used","if m.get_number('writeoff_warehouse_id')is not null then\n   if m.get_number('writeoff_warehouse_id')!=v_owner or not RRL_TARE_DAMAGE_TRACE.origin_exists(v_damage)then raise_application_error(-20886,'TARE_TRACED_OWNER_WAREHOUSE_REQUIRED');end if;\n   RRL_TARE_PARTICIPANT.warehouse_actor(p_actor,v_owner);\n   v_holder:='WAREHOUSE';v_id:=RRL_STOCK_PLAN_HELPER.decimal_text(v_owner);\n  end if;\n  select nvl(sum(QUANTITY),0) into v_used")
v=change(v,"RRL_TARE_PLANNING.assert_available(v_from,v_from_qty,v_qty);","RRL_TARE_PLANNING.assert_available(v_from,v_from_qty,v_qty);\n if kind='TARE_WRITE_OFF' then\n  RRL_TARE_DAMAGE_TRACE.check_transfer(case when RRL_TARE_DAMAGE_TRACE.origin_exists(v_damage)then v_damage else null end,v_from,v_qty,v_from_qty);\n end if;")
v=change(v,"j.put('operation_id',op);j.put('quantity',v.get_string('quantity'));","if kind='TARE_DAMAGE' then RRL_TARE_DAMAGE_TRACE.register_damage(op,v_to,v_qty);\n else RRL_TARE_DAMAGE_TRACE.record_writeoff(op,v_damage,v_from,v_qty);end if;\n j.put('operation_id',op);j.put('quantity',v.get_string('quantity'));")
out[f+"004_resolution_command.sql"]=v
v=Path(f+"000_before_loss.sql").read_text(encoding="utf-8")
v=change(v,"RRL_TARE_PLANNING.assert_available(v_key,v_p,v_qty);","RRL_TARE_PLANNING.assert_available(v_key,v_p,v_qty);\n  if v_condition='DAMAGED' then RRL_TARE_DAMAGE_TRACE.check_transfer(null,v_key,v_qty,v_p);end if;")
out[f+"005_loss_command.sql"]=v
v=Path(f+"002_trace_api.sql").read_text(encoding="utf-8")
v=change(v,"p_physical-tracked_quantity(p_key)","p_physical-tracked_quantity(p_key)-RRL_TARE_PLANNING.held_quantity(p_key)")
out[f+"002_trace_api.sql"]=v
print(json.dumps(out))
