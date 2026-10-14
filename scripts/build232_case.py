from pathlib import Path
import json
s=Path("scripts/ni053_marked_disposition_source.py").read_text(encoding="utf-8")
s=s[:s.index("  target=ware+50000000;")]
s+='  print("SOURCE232_JSON:"+json.dumps({"tag":tag,"uid":lot,"article":article,"source_ware":ware,"source_trip":trip,"load":shipop,"order":order}),flush=True)\n finally:\n  conn.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")\n'
print(json.dumps({"scripts/ni053_final_custody_source.py":s}))
