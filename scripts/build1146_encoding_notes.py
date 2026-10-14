from pathlib import Path
import json
files={}
for name in ("scripts/build1145_thermal_report.py","wiki/runbooks/retailcase_active_work.md"):
 p=Path(name);text=p.read_text(encoding="utf-8").replace(chr(0x421)+chr(0x2026),"S-ellipsis")
 if name.endswith("build1145_thermal_report.py"):
  text=text.replace("warehouse"+chr(0x62D2)+chr(0x5426),"склад отклонён")
 files[name]=text
print(json.dumps(files,ensure_ascii=True))
