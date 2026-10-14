from pathlib import Path
import json
p=Path("scripts/check1143_thermal_ranges.py");s=p.read_text(encoding="utf-8").replace("def execute(self,sql,**kw):","def execute(self,sql,*args,**kw):")
print(json.dumps({str(p):s},ensure_ascii=True))
