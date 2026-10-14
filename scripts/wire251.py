from pathlib import Path
import json
p=Path("api/wms_api_server/app/modules/transport/infrastructure/loading.py");s=p.read_text(encoding="utf-8")
a=s.index("    def status(");b=s.index("    def load(",a)
out={str(p):s[:a]+"""    def status(self, task_id: int, actor: str) -> dict[str, Any]:
        from .loading_status import loading_status
        return loading_status(self.gateway, task_id, actor)

"""+s[b:]}
p=Path("api/wms_api_server/app/modules/transport/contracts.py");s=p.read_text(encoding="utf-8")
assert s.count("def status(self, task_id: int)")==1
out[str(p)]=s.replace("def status(self, task_id: int)","def status(self, task_id: int, actor: str)")
p=Path("api/wms_api_server/app/modules/transport/api/loading_routes.py");s=p.read_text(encoding="utf-8")
assert s.count("service.status(task_id)")==1;out[str(p)]=s.replace("service.status(task_id)","service.status(task_id, user.username)")
print(json.dumps(out,ensure_ascii=True))
