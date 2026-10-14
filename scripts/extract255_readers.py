from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/transport/infrastructure/loading_status.py");s=p.read_text(encoding="utf-8")
needle='    with gateway.transaction("Current physical trip loading READ ONLY snapshot") as cur:\n        cur.execute("set transaction read only")\n'
assert s.count(needle)==1
a=s.index("def loading_status(")
prefix=s[:a]
body=s[s.index(needle)+len(needle):]
body="\n".join(line[4:]if line.startswith("    ")else line for line in body.splitlines())+"\n"
out[str(p)]=prefix+"""def loading_status(gateway: Any, trip: int, actor: str) -> dict[str, Any]:
    with gateway.transaction("Current physical trip loading READ ONLY snapshot") as cur:
        cur.execute("set transaction read only")
        return read_loading_status(cur, trip, actor)

def read_loading_status(cur: Any, trip: int, actor: str) -> dict[str, Any]:
"""+body
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_incoming.py");s=p.read_text(encoding="utf-8")
needle='        with self.gateway.transaction("Interwarehouse trip incoming readiness") as cur:\n            cur.execute("set transaction read only")\n'
assert s.count(needle)==1
a=s.index("    def read(");body=s[s.index(needle)+len(needle):]
body="\n".join(line[8:]if line.startswith("        ")else line for line in body.splitlines())+"\n"
out[str(p)]=s[:a]+"""    def read(self,trip_id: int,actor: str) -> dict[str,Any]:
        with self.gateway.transaction("Interwarehouse trip incoming readiness") as cur:
            cur.execute("set transaction read only")
            return read_incoming_snapshot(cur, trip_id, actor)

def read_incoming_snapshot(cur: Any,trip_id: int,actor: str) -> dict[str,Any]:
"""+body
p=Path("api/wms_api_server/app/modules/inventory/public.py");s=p.read_text(encoding="utf-8")
needle="from .infrastructure.interwarehouse_incoming import InterwarehouseIncoming"
out[str(p)]=s+"\nfrom .infrastructure.interwarehouse_incoming import read_incoming_snapshot as read_interwarehouse_incoming_snapshot\n"
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_incoming.sql");s=p.read_text(encoding="utf-8")
needle=" th.DECISION_KIND TEMPERATURE_DECISION"
assert s.count(needle)==1
s=s.replace(needle,needle+",\n receipt_op.STATE RECEIPT_OPERATION_STATE,placement_op.STATE PLACEMENT_OPERATION_STATE,\n to_char(placement.CREATED_AT,'YYYY-MM-DD\"T\"HH24:MI:SS.FF6TZH:TZM') PLACED_AT,\n to_char(RRL_INTERWARE_ROUTING.ready_due(p.OPERATION_ID),'YYYY-MM-DD\"T\"HH24:MI:SS.FF6TZH:TZM') READY_DUE")
needle="left join RRL_INTERWARE_ONWARD_BIND"
assert s.count(needle)==1
s=s.replace(needle,"left join RRL_STOCK_OPERATION receipt_op on receipt_op.OPERATION_ID=r.OPERATION_ID\nleft join RRL_STOCK_OPERATION placement_op on placement_op.OPERATION_ID=placement.OPERATION_ID\n"+needle)
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
