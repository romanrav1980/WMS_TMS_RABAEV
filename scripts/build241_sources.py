from pathlib import Path
import json
s=Path("scripts/ni053_marked_disposition_source.py").read_text(encoding="utf-8")
s=s.replace('target=ware+50000000;inbound=', 'target=json.loads(Path("tmp/context241a.json").read_text(encoding="utf-8"))["target_ware"];inbound=',1)
s=s.replace('  meta("insert into RRL_WARES(ID,NAME,PREFIX)values(:w,:n,\'QI\')",w=target,n="Own225 target "+tag)','  # Existing own241 receiving warehouse reused for second source; no duplicated warehouse.',1)
print(json.dumps({"scripts/source241b.py":s},ensure_ascii=True))
