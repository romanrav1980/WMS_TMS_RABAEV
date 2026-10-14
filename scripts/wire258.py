from pathlib import Path
import json
p=Path("api/wms_api_server/app/modules/transport/infrastructure/time_preflight.py")
s=p.read_text(encoding="utf-8");start=s.index("def trip_scope(");end=s.index("def trip_time_preview(")
snapshot='"""Current original trip scope and bounded temporal rows, no transaction ownership."""\nfrom typing import Any\nfrom ..contracts_plan import TransportPlanError\n\n'+s[start:end]
s=s[:start]+s[end:];s=s.replace('from .trip_time_approval import read_time_context','from .trip_time_approval import read_time_context\nfrom .time_snapshot import trip_scope, original_operations\nfrom .driver_day import read_driver_days')
s=s.replace('"operations":operations,"driver_rest":evaluate_driver_rest(operations),','"operations":operations,"driver_rest":evaluate_driver_rest(operations),\n            "driver_days":read_driver_days(cur,trip,actor,zone,header[2],operations),')
print(json.dumps({str(p):s,"api/wms_api_server/app/modules/transport/infrastructure/time_snapshot.py":snapshot},ensure_ascii=True))
