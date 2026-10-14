from pathlib import Path
import json,hashlib
f=Path("db/migrations/2026-10-11_ni042_scale_packet");s=(f/"000_before_store.sql").read_text(encoding="utf-8")
s=s.replace("j json_object_t;result_json json_object_t","j json_object_t;reading json_object_t;result_json json_object_t")
a=s.index("  if j.get_string('unit')");b=s.index("  select count(*) into n from RRL_TT_HU_LOAD_FACT",a)
s=s[:a]+"""  reading:=json_object_t.parse(RRL_SCALE_PACKET_READ.validate_json(p_source,device.CAPACITY_KG,device.RESOLUTION_KG));
  last_kg:=RRL_STOCK_MATH.quantity(reading.get_string('weight_kg'));
  min_kg:=RRL_STOCK_MATH.quantity(reading.get_string('sample_min_kg'));max_kg:=RRL_STOCK_MATH.quantity(reading.get_string('sample_max_kg'));
  sample_no:=reading.get_number('sample_count');span_ms:=reading.get_number('span_ms');
  measured_at:=RRL_SCALE_PACKET_READ.utc_stamp(reading.get_string('measured_at'));zero_at:=RRL_SCALE_PACKET_READ.utc_stamp(reading.get_string('zero_check_at'));
"""+s[b:]
out={str(f/"002_store_contract.sql"):s,str(f/"002_store_body.sql"):s[s.index("create or replace package body"):],
str(f/"apply.sql"):"-- MIGRATION_ID:2026-10-11-186-shared-scale-packet\n@@001_packet.sql\n@@002_store_body.sql\n@@../2026-10-08_stock_posting_core/014b_recompile.sql\n",
str(f/"rollback.sql"):"@@000_before_store.sql\n@@../2026-10-08_stock_posting_core/014b_recompile.sql\n",
str(f/"verify.sql"):"select object_name,object_type,status from user_objects where object_name in('RRL_SCALE_PACKET_READ','RRL_STORE_SCALE_API');\nselect name,line,text from user_errors where name in('RRL_SCALE_PACKET_READ','RRL_STORE_SCALE_API');\n"}
out[str(f/"checkpoint.json")]=json.dumps({"migration_id":"2026-10-11-186-shared-scale-packet","sha256":{p:hashlib.sha256(v.encode()).hexdigest()for p,v in out.items()},"before_sha256":hashlib.sha256((f/"000_before_store.sql").read_bytes()).hexdigest(),"recovery":"fresh original store scale capture and paired rollback; additive pure decoder; no DB copy"},indent=2)
print(json.dumps(out,ensure_ascii=True))
