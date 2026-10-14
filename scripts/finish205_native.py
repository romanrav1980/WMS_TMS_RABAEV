from pathlib import Path
import json
out={};f=Path("db/migrations/2026-10-11_ni042_final_qc")
p=f/"002_admission.sql";s=p.read_text(encoding="utf-8")
s=s.replace("signature_value varchar2(64);n number;\n begin\n  if required", "signature_value varchar2(64);n number;tx_id_value varchar2(100);\n begin\n  tx_id_value:=dbms_transaction.local_transaction_id(false);\n  if required")
s=s.replace("and sys_context('RRL_STOCK_WRITE_CTX','TX_ID')=dbms_transaction.local_transaction_id(false)))", "and sys_context('RRL_STOCK_WRITE_CTX','TX_ID')=tx_id_value))")
out[str(p)]=s
s=(f/"000_before_root.sql").read_text(encoding="utf-8")
needle="  if g_kind in('CASE_PICK_CONFIRM','CASE_CARRIER_MOVE','CASE_CARRIER_RETURN','CASE_SHORT_APPROVE')then"
assert s.count(needle)==2
s=s.replace(needle,"  if g_kind='OUTGOING_PALLET_CHECK'then RRL_OUTGOING_QC_ACCESS.assert_identifier(json_object_t.parse(p_request).get_object('source').get_string('pallet_identifier'),p_actor);end if;\n"+needle)
out[str(f/"007_root.sql")]=s
p=f/"apply.sql";s=p.read_text(encoding="utf-8");s+="@@008_scope.sql\n@@007_root.sql\n";out[str(p)]=s
p=f/"rollback.sql";s=p.read_text(encoding="utf-8").replace("@@000_before_qc.sql","@@000_before_root.sql\n@@000_before_qc.sql")
s+="drop package RRL_OUTGOING_QC_ACCESS;\n";out[str(p)]=s
out[str(f/"009_finish.sql")]="@@002_admission.sql\n@@008_scope.sql\n@@007_root.sql\n"
print(json.dumps(out,ensure_ascii=True))
