from pathlib import Path
import json
f={};root="db/migrations/2026-10-14_ni052_loading_floor/"
p=Path(root+"002_floor_api.sql");s=p.read_text(encoding="utf-8")
s=s.replace("d json_object_t;vehicle_no number;version_no number;n number;","d json_object_t;vehicle_no number;version_no number;type_no number;origin_value varchar2(24);reference_value varchar2(200);n number;")
point="  select count(*)into n from RRL_TT_HU_LOAD_FACT l join RRL_STOCK_OPERATION o"
assert s.count(point)==1
s=s.replace(point,"  type_no:=d.get_number('pallet_type_id');origin_value:=d.get_string('type_origin');reference_value:=d.get_string('source_reference');\n"+point,1)
s=s.replace("d.get_number('pallet_type_id'),d.get_string('type_origin'),d.get_string('source_reference'),p_actor,p_domain);","type_no,origin_value,reference_value,p_actor,p_domain);",1)
f[str(p)]=s;f[root+"apply_insert_correction.sql"]="@@002_floor_api.sql\n"
print(json.dumps(f))
