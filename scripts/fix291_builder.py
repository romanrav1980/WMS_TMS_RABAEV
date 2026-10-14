from pathlib import Path
import re,json
out={}
p=Path("scripts/wire291_partial.py");s=p.read_text(encoding="utf-8").replace("needle='if(unitScans.length)'",'needle=\'if(path==="/receive"&&unitScans.length)\'')
s=s.replace('if(el("iwPartialReceipt").checked)','if(path==="/receive"&&el("iwPartialReceipt").checked)')
out[p.as_posix()]=s
p=Path("db/migrations/2026-10-11_ni061_partial_receiving/002_partial_helper.sql");s=p.read_text(encoding="utf-8")
s=re.sub(r"(?<!['\\w])uid(?!['\\w])","v_target_uid",s);out[p.as_posix()]=s
print(json.dumps(out,ensure_ascii=True))
