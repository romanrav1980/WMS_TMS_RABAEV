import json
from pathlib import Path
s=Path("scripts/ni081_range_apply_existing_case.py").read_text(encoding="utf-8").replace("tag=uuid4().hex[:8]","tag='243f5283'")
start=s.index(' q.callproc("RRL_STOCK_CONFIG_API.begin_change"');end=s.index(' preview=reader.preview',start)
s=s[:start]+" wave=396;repl=1502\n"+s[end:]
s=s.replace('select STATUS,sum(nvl(l.PICKED_QTY,0))','select t.STATUS,sum(nvl(l.PICKED_QTY,0))').replace('group by STATUS','group by t.STATUS')
print(json.dumps({"scripts/ni081_range_apply_continue_case.py":s}))
