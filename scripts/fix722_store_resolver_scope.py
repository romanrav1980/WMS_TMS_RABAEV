from pathlib import Path
import json
p=Path("db/migrations/2026-10-12_ni053_store_aggregation/003_mark.sql");s=p.read_text(encoding="utf-8")
old="begin p_proof:=source_proof(p_domain);end;"
new="declare v_wire clob;begin p_proof:=source_proof(p_domain);RRL_STORE_AGG_SCAN.normalize(p_proof.to_clob,p_metadata.to_clob,v_wire);p_proof.put('validated_store_scans',json_array_t.parse(v_wire));end;"
assert s.count(old)==1;s=s.replace(old,new)
old="declare v_wire clob;begin RRL_STORE_AGG_SCAN.normalize(p_proof.to_clob,p_metadata.to_clob,v_wire);scans:=json_array_t.parse(v_wire);end;"
new="if p_proof.has('validated_store_scans')then scans:=p_proof.get_array('validated_store_scans');elsif p_metadata.has('unit_scans')then scans:=p_metadata.get_array('unit_scans');end if;"
assert s.count(old)==1;s=s.replace(old,new)
print(json.dumps({str(p):s,"db/migrations/2026-10-12_ni053_store_aggregation/apply_scope722.sql":"@@003_mark.sql\n"}))
