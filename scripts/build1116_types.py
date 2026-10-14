from pathlib import Path
import json
b=Path("api/wms_api_server/app/modules/fulfillment");f={}
p=b/"infrastructure/automatic_preparation.py";s=p.read_text(encoding="utf-8").replace("import json\n","import json\nfrom typing import Any\nimport oracledb\n")
s=s.replace("lock_layout_inputs(cur,","lock_layout_inputs(cur: oracledb.Cursor,",1)
s=s.replace("def __init__(self, legacy):","def __init__(self, legacy: Any) -> None:")
s=s.replace("def _layout(self, cur,","def _layout(self, cur: oracledb.Cursor,").replace("def _saved(self, cur,","def _saved(self, cur: oracledb.Cursor,")
f[str(p)]=s
p=b/"infrastructure/legacy_preparation.py";s=p.read_text(encoding="utf-8").replace("def _prepare_locked(self, cur,","def _prepare_locked(self, cur: oracledb.Cursor,");f[str(p)]=s
p=b/"api/preparation_read_routes.py";s=p.read_text(encoding="utf-8").replace("import oracledb\n","import oracledb\nfrom collections.abc import Callable\n")
s=s.replace("def auto_call(method, order_id, body, user):","def auto_call(method: Callable[[int, dict, str], dict], order_id: int, body: dict, user: AdminUser) -> dict:");f[str(p)]=s
print(json.dumps(f,ensure_ascii=True))
