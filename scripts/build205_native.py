from pathlib import Path
import json
f=Path("db/migrations/2026-10-11_ni042_final_qc");out={}
p=f/"002_admission.sql";s=p.read_text(encoding="utf-8")
s=s.replace("key_value varchar2(64);signature_value varchar2(64);n number;gross number;", "key_value varchar2(64);signature_value varchar2(64);task_no number;n number;gross number;")
s=s.replace("  select *into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=dom.get_number('case_task');","  task_no:=dom.get_number('case_task');\n  select *into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=task_no;")
s=s.replace("if sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)","if sys_context('RRL_STOCK_WRITE_CTX','TX_ID')is null or sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)")
s=s.replace("package RRL_WH_FINAL_SCALE_ADMISSION authid definer as","package RRL_WH_FINAL_SCALE_ADMISSION authid definer accessible by(package RRL_STOCK_PALLET_QC_CMD,package RRL_STOCK_QC_GATE) as")
out[str(p)]=s
s=(f/"000_before_qc.sql").read_text(encoding="utf-8")
needle="   v_gross:=RRL_STOCK_MATH.quantity(m.get_string('gross_weight'));"
assert s.count(needle)==1
s=s.replace(needle,"   RRL_WH_FINAL_SCALE_ADMISSION.assert_capture(p_request,p_domain);\n"+needle)
needle="  quality(p_request,v_id,passed,shipped,expected,tolerance,p_domain,v_reason,v_units,v_items);"
assert s.count(needle)==1
s=s.replace(needle,needle+"""
  if d.get_object('metadata').has('final_scale_capture')then
   RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','WH.FINAL.SCALE.USE:'||d.get_object('metadata').get_string('final_scale_capture'));
  end if;""")
needle="  RRL_STOCK_QC_POLICY.assert_controller(v.to_clob,p_actor);"
assert s.count(needle)==1
s=s.replace(needle,needle+"\n  RRL_WH_FINAL_SCALE_ADMISSION.claim_capture(p_request,v.to_clob,op);")
out[str(f/"004_qc.sql")]=s
s=(f/"000_before_gate.sql").read_text(encoding="utf-8")
needle="  if v_marked=1 and (not scan_ok or v_mark_proved!=1)"
assert s.count(needle)==1
s=s.replace(needle,"""  if weight_ok and RRL_WH_FINAL_SCALE_ADMISSION.approved(p_domain,v_weight_op)!=1 then weight_ok:=false;end if;
"""+needle)
out[str(f/"005_gate.sql")]=s
s=(f/"000_before_archive.sql").read_text(encoding="utf-8").replace("ct.STATUS not in('WAIT_CONTROL','READY_TO_SHIP')","ct.STATUS not in('WAIT_CONTROL','CONTROL_IN_PROGRESS','CONTROLLED','READY_TO_SHIP')")
out[str(f/"006_archive.sql")]=s
out[str(f/"apply.sql")]="@@001_schema.sql\n@@002_admission.sql\n@@003_guard.sql\n@@004_qc.sql\n@@005_gate.sql\n@@006_archive.sql\n"
out[str(f/"rollback.sql")]="""declare n number;begin select count(*)into n from RRL_WH_FINAL_SCALE_USE;if n>0 then raise_application_error(-20863,'FINAL_QC_HISTORY_REQUIRES_FORWARD_REPAIR');end if;end;
/
@@000_before_qc.sql
@@000_before_gate.sql
@@000_before_archive.sql
drop trigger RRL_WH_FINAL_SCALE_USE_GUARD;
drop package RRL_WH_FINAL_SCALE_ADMISSION;
drop table RRL_WH_FINAL_SCALE_USE;
"""
out[str(f/"verify.sql")]="select name,type,line,text from user_errors where name not like 'BIN$%';\nselect object_name,object_type,status from user_objects where status='INVALID'and object_name not like 'BIN$%';\n"
print(json.dumps(out,ensure_ascii=True))
