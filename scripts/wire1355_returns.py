from pathlib import Path
import json
files={}
p=Path("api/wms_api_server/app/modules/delivery/infrastructure/store_returns.py");s=p.read_text(encoding="utf-8");s='from .return_progress import return_progress\n'+s
old='            if len(lines)>200:'
new='''            progress=return_progress(q,[a["operation_id"]for a in approvals[:100]],actor)
            for approval in approvals[:100]:
                approval["progress"]=progress.get(approval["operation_id"],{"warehouse_progress_visible":False})
            if len(lines)>200:'''
assert old in s;s=s.replace(old,new);files[str(p)]=s
print(json.dumps(files,ensure_ascii=True))
