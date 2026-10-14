import json
from pathlib import Path
out={}
d=Path("db/migrations/2026-10-12_ni062_return_basis")
p=d/"000_before_rrl_stock_store_return_sap_cmd_package_body.sql";s=p.read_text(encoding="utf-8")
s=s.replace("or m.get_string('disposition') is null","or nvl(m.get_string('return_basis'),'ACCEPTED')!=approved.RETURN_BASIS\n or m.get_string('disposition') is null",1)
s=s.replace("xmltable('/WarehouseStoreReturn[@version=\"1\"]'","xmltable('/WarehouseStoreReturn[@version=\"1\" or @version=\"2\"]'")
s=s.replace("columns sender varchar2(100)","columns contract_version varchar2(10)path '@version',return_basis varchar2(10)path 'OriginalReceiptDisposition',sender varchar2(100)",1)
s=s.replace("where x.sender=v_sender","where((x.contract_version='1'and x.return_basis is null and approved.RETURN_BASIS='ACCEPTED')or(x.contract_version='2'and x.return_basis=approved.RETURN_BASIS))\n and x.sender=v_sender",1)
s=s.replace("p_domain:=json_object_t();p_domain.put('approval_operation_id',v_approval);","p_domain:=json_object_t();if approved.RETURN_BASIS!='ACCEPTED'then p_domain.put('return_basis',approved.RETURN_BASIS);end if;p_domain.put('approval_operation_id',v_approval);")
s=s.replace("j.put('operation_id',op);","if v.has('return_basis')then j.put('return_basis',v.get_string('return_basis'));end if;j.put('operation_id',op);")
out[str(d/"008_sap_basis.sql")]=s
p=d/"apply.sql";s=p.read_text(encoding="utf-8").replace("@@007_compile.sql","@@008_sap_basis.sql\n@@007_compile.sql");out[str(p)]=s
p=Path("api/wms_api_server/app/modules/integrations/domain/store_return.py");s=p.read_text(encoding="utf-8")
s=s.replace('if root.tag!="WarehouseStoreReturn" or root.attrib!={"version":"1"}:', 'version=root.attrib.get("version")\n    if root.tag!="WarehouseStoreReturn" or version not in {"1","2"} or root.attrib!={"version":version}:')
s=s.replace("Expected WarehouseStoreReturn version1 without namespaces","Expected WarehouseStoreReturn version1 or2 without namespaces")
s=s.replace('    if len(root)!=len(fields)', '    if version=="2":fields["OriginalReceiptDisposition"]=10\n    if len(root)!=len(fields)',1)
s=s.replace('    sender,message=values["Sender"],values["MessageId"]','    basis=values.get("OriginalReceiptDisposition","ACCEPTED")\n    if basis not in {"ACCEPTED","REFUSED","DAMAGED"}:\n        raise ValueError("Original receipt disposition must be ACCEPTED/REFUSED/DAMAGED")\n    sender,message=values["Sender"],values["MessageId"]')
s=s.replace('"metadata":{"sender":sender,','"metadata":{**({"return_basis":basis}if version=="2"else {}),"sender":sender,')
out[str(p)]=s
print(json.dumps(out))
