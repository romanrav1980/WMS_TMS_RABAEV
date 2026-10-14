exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.services.transport_service import TransportService
import time
service=TransportService();result={}
for name,params in [('page200',dict(unassigned_only=False,page_size=200)),('scoped',dict(unassigned_only=False,ware_id=9807,page_size=2))]:
 t=time.perf_counter();rows=service.list_available_sts(**params);result[name]={'seconds':round(time.perf_counter()-t,3),'count':len(rows)}
print(json.dumps(result))