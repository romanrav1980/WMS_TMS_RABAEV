from pathlib import Path
import json,re
base=Path("db/migrations/2026-10-08_stock_posting_core")
p=base/"current_runtime_manifest.json";m=json.loads(p.read_text(encoding="utf-8"));files={}
old="../2026-10-14_ni022_case_type/003_root.sql";new="../2026-10-14_ni022_prepared_row_move/007_current_root.sql"
spec=(base/old).read_text(encoding="utf-8").split("create or replace package body",1)[0]
files[str(base/new)]=spec+(base/"../2026-10-14_ni022_prepared_row_move/006_fullpal_scope.sql").read_text(encoding="utf-8")
assert old in m["components"] or new in m["components"]
m["components"]=[new if x==old else x for x in m["components"]]
for key,values in {
"packages":["RRL_ST_LAYOUT_READ","RRL_STOCK_ST_ROW_CMD"],
"components":["../2026-10-14_ni033_pick_article_identity/001_picking.sql","../2026-10-14_ni022_prepared_row_move/001_read.sql","../2026-10-14_ni022_prepared_row_move/003_command.sql"],
"additional_scripts":["../2026-10-14_ni033_pick_article_identity/apply.sql","../2026-10-14_ni022_prepared_row_move/apply.sql"]
}.items():
 for value in values:
  if value not in m[key]:m[key].append(value)
files[str(p)]=json.dumps(m,indent=2)+"\n"
print(json.dumps(files,ensure_ascii=True))
