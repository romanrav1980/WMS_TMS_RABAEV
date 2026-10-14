from pathlib import Path
import json
p=Path("db/migrations/2026-10-10_ni081_workload_config/004_metadata_permission.sql")
s=p.read_text(encoding="utf-8").replace("'trace_manifest_import','resource_shift_edit'","'trace_manifest_import','resource_shift_edit','customer_rule_edit'")
root=Path("db/migrations/2026-10-11_ni022_calendar")
out={str(root/"004_metadata_permission.sql"):s,str(root/"004b_metadata_body.sql"):s[s.lower().index("create or replace package body"):]}
p=root/"002_api.sql";api=p.read_text(encoding="utf-8").replace("RRL_STOCK_CONFIG_API.begin_change","RRL_STOCK_METADATA_TX.begin_change").replace("RRL_STOCK_CONFIG_API.end_change","RRL_STOCK_METADATA_TX.end_change");out[str(p)]=api
p=root/"apply.sql";out[str(p)]="@@001_schema.sql\n@@004b_metadata_body.sql\n@@002_api.sql\n@@003_guards.sql\n"
p=root/"rollback.sql";out[str(p)]=p.read_text(encoding="utf-8")+"\n@@../2026-10-10_ni081_workload_config/004_metadata_permission.sql\n"
print(json.dumps(out,ensure_ascii=True))
