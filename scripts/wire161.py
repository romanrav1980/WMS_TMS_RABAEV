import json
from pathlib import Path
out={}
p=Path("api/wms_api_server/app/modules/resources/infrastructure/workload_monitor.py");s=p.read_text(encoding="utf-8")
s=s.replace("from ..domain.workload_intervals import interval_load,outside_view","from ..domain.workload_intervals import interval_load,outside_view\nfrom ..domain.workload_recommendations import workload_recommendations")
s=s.replace('"native_current_presence":presence,','"recommendations":workload_recommendations(intervals,work),"native_current_presence":presence,')
out[str(p)]=s
print(json.dumps(out))
