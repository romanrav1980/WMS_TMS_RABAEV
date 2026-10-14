from pathlib import Path
import json
p=Path("api/wms_api_server/app/modules/transport/infrastructure/time_preflight.py")
s=p.read_text(encoding="utf-8")
s=s.replace("from ..contracts_plan import TransportPlanError","from ..contracts_plan import TransportPlanError\nfrom ..domain.driver_rest import evaluate_driver_rest")
s=s.replace('"operations":operations,"start_at":start_at', '"operations":operations,"driver_rest":evaluate_driver_rest(operations),"start_at":start_at')
print(json.dumps({str(p):s},ensure_ascii=True))
