from pathlib import Path
import json
out={};f=Path("db/migrations/2026-10-11_ni062_marked_custody")
p=f/"002_unit_source.sql";s=p.read_text(encoding="utf-8")
s=s.replace(" function custody_proof(p_approval varchar2,p_metadata json_object_t)return clob;"," function approved_proof(p_approval varchar2)return clob;\n function custody_proof(p_approval varchar2,p_metadata json_object_t)return clob;",1)
s=s.replace(" function custody_proof(p_approval varchar2,p_metadata json_object_t)return clob is"," function approved_proof(p_approval varchar2)return clob is",1)
s=s.replace("   if p_metadata.has('unit_scans')and p_metadata.get_array('unit_scans').get_size>0 then raise_application_error(-20886,'STORE_RETURN_ORDINARY_UNEXPECTED_UNIT_SCANS');end if;\n","",1)
s=s.replace("  RRL_STORE_MARK_CORE.resolve_disposition(proof,p_metadata,lines,resolved);\n  proof.put('units',resolved);return proof.to_clob;","  proof.put('supported',true);proof.put('expected_scan_count',n*proof.get_array('profiles').get_size);return proof.to_clob;",1)
i=s.index(" function accepted_units",s.index("package body"))
wrapper=""" function custody_proof(p_approval varchar2,p_metadata json_object_t)return clob is
  wire clob:=approved_proof(p_approval);proof json_object_t;qty number;lines json_array_t:=json_array_t();x json_object_t:=json_object_t();resolved json_array_t;
 begin
  if wire is null then
   if p_metadata.has('unit_scans')and p_metadata.get_array('unit_scans').get_size>0 then raise_application_error(-20886,'STORE_RETURN_ORDINARY_UNEXPECTED_UNIT_SCANS');end if;
   return null;
  end if;
  proof:=json_object_t.parse(wire);select BASE_QTY into qty from RRL_STORE_RETURN_APPROVAL where OPERATION_ID=p_approval;
  x.put('accepted',RRL_STOCK_PLAN_HELPER.decimal_text(qty));x.put('missing','0');x.put('refused','0');x.put('damaged','0');x.put('extra','0');lines.append(x);
  RRL_STORE_MARK_CORE.resolve_disposition(proof,p_metadata,lines,resolved);proof.put('units',resolved);return proof.to_clob;
 end;
"""
s=s[:i]+wrapper+s[i:];out[str(p)]=s
p=Path("api/wms_api_server/app/modules/delivery/infrastructure/return_custody.py");s=p.read_text(encoding="utf-8").replace("from ...inventory.public import normalize_unit_scan_codes","from ...inventory.public import normalize_unit_scan_codes\nfrom ...platform.public import read_oracle_json")
s=s.replace("        return self.gateway.fetch_all(", "        rows=self.gateway.fetch_all(")
s=s.replace("                   a.ARTICLE,a.LOT_UID", "                   RRL_STORE_RETURN_UNIT_CORE.approved_proof(t.APPROVAL_OPERATION_ID) MARKED_UNIT_CONTROL,\n                   a.ARTICLE,a.LOT_UID")
s=s.replace("                   to_char(h.GROSS_WEIGHT_KG", "                   RRL_STORE_RETURN_UNIT_CORE.approved_proof(t.APPROVAL_OPERATION_ID) MARKED_UNIT_CONTROL,\n                   to_char(h.GROSS_WEIGHT_KG")
s=s.replace('        """,{"store":store_address,"trip":task_id})','        """,{"store":store_address,"trip":task_id})\n        for row in rows:row["marked_unit_control"]=read_oracle_json(row.get("marked_unit_control")) if row.get("marked_unit_control") else None\n        return rows')
s=s.replace('        """,{"actor":actor,"trip":task_id})','        """,{"actor":actor,"trip":task_id})\n        for row in rows:row["marked_unit_control"]=read_oracle_json(row.get("marked_unit_control")) if row.get("marked_unit_control") else None\n        return rows');out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
