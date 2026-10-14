from pathlib import Path
import json
p=Path("api/wms_api_server/app/modules/transport/infrastructure/plan_preflight.py")
s=p.read_text(encoding="utf-8")
a=s.index("def dispatcher(");b=s.index("\ndef native_check(",a)
helper=s[a:b]
s=s[:a]+"from .preflight_scope import dispatcher\n\n"+s[b:]
out={str(p):s,"api/wms_api_server/app/modules/transport/infrastructure/preflight_scope.py":'from typing import Any\nfrom ..contracts_plan import TransportPlanError\n\n'+helper}
print(json.dumps(out,ensure_ascii=True))
