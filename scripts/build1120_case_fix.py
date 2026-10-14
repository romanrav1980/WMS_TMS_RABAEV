from pathlib import Path
import json
p=Path("scripts/case1118_auto_preparation.py");s=p.read_text(encoding="utf-8")
s="\n".join(x for x in s.splitlines()if 'RRL_REMAINS where ARTICUL'not in x)+"\n"
print(json.dumps({str(p):s},ensure_ascii=True))
