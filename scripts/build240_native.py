from pathlib import Path
import json
f=Path("db/migrations/2026-10-11_ni061_thermal");out={}
p=f/"002_thermal.sql";s=p.read_text(encoding="utf-8")
s=s.replace("trip number;locked_trip number;","trip number;locked_trip number;observation nvarchar2(200):=d.get_string('observation_reference');reason nvarchar2(500):=d.get_string('reason');reference varchar2(60):=d.get_string('decision_reference');")
s=s.replace("values(op,plan_id,rev+1,kind,observed,d.get_string('observation_reference'),tlo,thi,lo,hi,d.get_string('reason'),d.get_string('decision_reference'),p_actor,hash_value,p_request,p_result)","values(op,plan_id,rev+1,kind,observed,observation,tlo,thi,lo,hi,reason,reference,p_actor,hash_value,p_request,p_result)")
out[str(p)]=s
s=(f/"000_before_rrl_stock_interware_put.sql").read_text(encoding="utf-8")
s=s.replace("unit_distinct number;","unit_distinct number;thermal json_object_t;stored_thermal varchar2(100);stored_lo number;stored_hi number;")
s=s.replace("v_target:=plan.OUTBOUND_DOCK;","""RRL_INTERWARE_THERMAL.assert_release(plan.OPERATION_ID);
 thermal:=json_object_t.parse(RRL_INTERWARE_THERMAL.mode_json(plan.OPERATION_ID));
 if p_task is not null then
  select TEMP_DECISION_OPERATION_ID,TASK_TEMP_MIN,TASK_TEMP_MAX into stored_thermal,stored_lo,stored_hi from RRL_INTERWARE_PUT_PLAN where TASK_ID=p_task;
  if nvl(stored_lo,-1000)!=nvl(thermal.get_number('task_temp_min'),-1000)or nvl(stored_hi,-1000)!=nvl(thermal.get_number('task_temp_max'),-1000)then raise_application_error(-20886,'INTERWARE_TASK_TEMPERATURE_REPLAN_REQUIRED');end if;
  thermal.put('task_decision_operation_id',stored_thermal);
 end if;
 v_target:=plan.OUTBOUND_DOCK;
 RRL_INTERWARE_THERMAL.assert_cell(thermal.to_clob,receipt.WARE_ID,v_target);""",1)
s=s.replace("p_domain:=json_object_t();if unit_snapshot","p_domain:=json_object_t();p_domain.put('temperature',thermal);if unit_snapshot",1)
s=s.replace("v_unit varchar2(20);v_qty number;","v_unit varchar2(20);v_qty number;temp_op varchar2(100);temp_lo number;temp_hi number;",1)
s=s.replace("insert into RRL_INTERWARE_PUT_PLAN(OPERATION_ID,RECEIPT_OPERATION_ID,TASK_ID,TARGET_CELL,ACTOR)values(op,v_receipt,v_task,v_to,p_actor);","""temp_op:=v.get_object('temperature').get_string('decision_operation_id');temp_lo:=v.get_object('temperature').get_number('task_temp_min');temp_hi:=v.get_object('temperature').get_number('task_temp_max');
 insert into RRL_INTERWARE_PUT_PLAN(OPERATION_ID,RECEIPT_OPERATION_ID,TASK_ID,TARGET_CELL,ACTOR,TEMP_DECISION_OPERATION_ID,TASK_TEMP_MIN,TASK_TEMP_MAX)values(op,v_receipt,v_task,v_to,p_actor,temp_op,temp_lo,temp_hi);""")
s=s.replace("j.put('operation_id',op);j.put('task_id'","j.put('temperature',v.get_object('temperature'));j.put('operation_id',op);j.put('task_id'",1)
out[str(f/"004_placement.sql")]=s
s=(f/"000_before_rrl_interware_depart_gate.sql").read_text(encoding="utf-8").replace("count_value:=count_value+1;","RRL_INTERWARE_THERMAL.assert_release(p.OPERATION_ID);count_value:=count_value+1;",1)
out[str(f/"005_depart_gate.sql")]=s
out[str(f/"006_recompile.sql")]="\n".join("alter package "+name+" compile body;"for name in["RRL_STOCK_TASK_PLAN","RRL_STOCK_TASK_CORE","RRL_STOCK_TASK_DOMAIN","RRL_STOCK_POSTING_API"])
print(json.dumps(out,ensure_ascii=True))
