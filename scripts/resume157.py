import json
from pathlib import Path
p=Path("scripts/ni081_range_proposal_existing_case.py");s=p.read_text(encoding="utf-8")
s=s.replace("tag=uuid4().hex[:8]","tag='52470cc7'")
start=s.index(' q.callproc("RRL_STOCK_CONFIG_API.begin_change"');end=s.index(' costs=[',start)
s=s[:start]+''' route=146;faces=[518,519]
 q.execute("select PICK_FACE_ID from RRL_PICK_FACE where WARE_ID=:ware and PICK_ROUTE_ID=:route and ACTIVE=1 order by PICK_FACE_ID",ware=ware,route=route)
 assert [row[0]for row in q.fetchall()]==faces
''' +s[end:]
print(json.dumps({"scripts/ni081_range_proposal_continue_case.py":s}))
