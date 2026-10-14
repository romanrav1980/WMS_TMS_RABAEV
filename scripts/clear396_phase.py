from pathlib import Path
import json
p=Path("tmp/context396.json");ctx=json.loads(p.read_text())
for field in["receipt_operation","receipt_metadata","receipt_result","receive_cell","selected_unit_key","placement_result","placement_complete_result"]:ctx.pop(field,None)
p.write_text(json.dumps(ctx,indent=2),encoding="utf-8")
