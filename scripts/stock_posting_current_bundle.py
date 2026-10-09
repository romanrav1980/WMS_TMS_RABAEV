"""Emit the maintained source bundle; never apply or repeatedly patch other scripts."""
import json
from pathlib import Path
d=Path("db/migrations/2026-10-08_stock_posting_core")
m=json.loads((d/"current_runtime_manifest.json").read_text(encoding="utf-8"))
for name in ("174_article_legacy.sql","174_article_adapter.sql","176_clear_entrypoint.sql",
             "193_revision_cell_each_legacy.sql","193_revision_cell_each_entry.sql"):
 if name not in m["additional_scripts"]:m["additional_scripts"].append(name)
out={str(d/"current_runtime_manifest.json"):json.dumps(m,indent=2)+"\n"}
out[str(d/m["contracts"])]="\n".join((d/name).read_text(encoding="utf-8").split("\n/\n",1)[0]+"\n/\n" for name in m["components"])
out[str(d/m["bundle"])]="@@"+m["contracts"]+"\n"+"\n".join("@@"+name for name in m["components"]+m["additional_scripts"])+"\n@@014b_recompile.sql\n"
print(json.dumps(out,ensure_ascii=True))
