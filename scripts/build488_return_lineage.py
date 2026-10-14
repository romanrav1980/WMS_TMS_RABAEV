import json
from pathlib import Path
d=Path("db/migrations/2026-10-12_ni062_return_basis");out={}
for name,file in [("RRL_STOCK_STORE_RETURN_REC_CMD","009_receipt_basis.sql"),("RRL_STOCK_STORE_RETURN_TR_CMD","010_transport_basis.sql"),("RRL_STOCK_STORE_RETURN_CUST_CMD","011_custody_basis.sql")]:
 p=d/("000_before_"+name.lower()+"_package_body.sql");s=p.read_text(encoding="utf-8")
 marker="p_domain:=json_object_t();"
 assert s.count(marker)==1,(name,s.count(marker))
 s=s.replace(marker,marker+"if approved.RETURN_BASIS!='ACCEPTED'then p_domain.put('return_basis',approved.RETURN_BASIS);end if;")
 if name=="RRL_STOCK_STORE_RETURN_REC_CMD":
  marker="j.put('operation_id',op);"
  assert s.count(marker)==1
  s=s.replace(marker,"if v.has('return_basis')then j.put('return_basis',v.get_string('return_basis'));j.put('customer_accepted_quantity_changed',false);end if;"+marker)
 out[str(d/file)]=s
p=d/"000_before_rrl_return_reuse_api_package_body.sql";s=p.read_text(encoding="utf-8")
s=s.replace("where RECEIPT_OPERATION_ID=p_receipt and LINE_NO=p_line;","where RECEIPT_OPERATION_ID=p_receipt and LINE_NO=p_line and RETURN_BASIS='ACCEPTED';")
out[str(d/"012_reuse_basis.sql")]=s
p=d/"apply.sql";s=p.read_text(encoding="utf-8").replace("@@007_compile.sql","@@009_receipt_basis.sql\n@@010_transport_basis.sql\n@@011_custody_basis.sql\n@@012_reuse_basis.sql\n@@007_compile.sql");out[str(p)]=s
for fname in ["return_transport.py","return_custody.py","store_cases.py"]:
 p=Path("api/wms_api_server/app/modules/delivery/infrastructure")/fname;s=p.read_text(encoding="utf-8")
 if fname=="return_transport.py":
  s=s.replace("a.DISPOSITION,f.STORE_ADDR","a.DISPOSITION,a.RETURN_BASIS,f.STORE_ADDR")
  # trip read has only transport facts: join immutable approval to expose the basis.
  s=s.replace("select t.OPERATION_ID,t.APPROVAL_OPERATION_ID,t.TT_ID","select t.OPERATION_ID,t.APPROVAL_OPERATION_ID,a.RETURN_BASIS,t.TT_ID")
  s=s.replace("from RRL_STORE_RETURN_TRANSPORT t where TT_ID=:trip","from RRL_STORE_RETURN_TRANSPORT t join RRL_STORE_RETURN_APPROVAL a on a.OPERATION_ID=t.APPROVAL_OPERATION_ID where t.TT_ID=:trip")
 elif fname=="return_custody.py":s=s.replace("a.ARTICLE,a.LOT_UID,a.BASE_UOM,","a.ARTICLE,a.LOT_UID,a.BASE_UOM,a.RETURN_BASIS,")
 else:s=s.replace("select a.OPERATION_ID,a.LINE_NO,a.DISPOSITION,","select a.OPERATION_ID,a.LINE_NO,a.RETURN_BASIS,a.DISPOSITION,")
 out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/return_receiving_reads.py");s=p.read_text(encoding="utf-8").replace("a.ARTICLE,a.LOT_UID,a.BASE_UOM,a.DISPOSITION,t.STORE_ADDR","a.ARTICLE,a.LOT_UID,a.BASE_UOM,a.DISPOSITION,a.RETURN_BASIS,t.STORE_ADDR");out[str(p)]=s
print(json.dumps(out))
