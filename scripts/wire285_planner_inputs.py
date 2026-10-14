from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/transport/infrastructure/profile_duration_cache.py");s=p.read_text(encoding="utf-8")
s=s.replace("import oracledb","import oracledb\nfrom ...platform.public import read_oracle_json",1)
s=s.replace("def planner_cost_cache(gateway: Any,addresses: list[str]) -> tuple[dict,dict,str]:", "def read_cost_cache(cur: Any,addresses: list[str]) -> tuple[dict,dict,str]:")
a=s.index("    with gateway.transaction(");b=s.index("\ndef profile_duration_cache",a)
block=s[a:b];lines=block.splitlines()
# Existing cursor ownership moves to outer planner-input snapshot.
block="\n".join(line[4:]if line.startswith("    ")else line for line in lines[2:])
s=s[:a]+block+"\n"+s[b:]
s=s.replace('if len(keys)>200:raise ValueError("VRP_ROAD_CACHE_ADDRESS_BOUND_200")','if len(keys)>201:raise ValueError("VRP_ROAD_CACHE_ADDRESS_BOUND_201")')
s+="""
def planner_cost_cache(gateway: Any,addresses: list[str]) -> tuple[dict,dict,str]:
    with gateway.transaction("Existing planner costs READ ONLY")as cur:
        cur.execute("set transaction read only");return read_cost_cache(cur,addresses)

def planner_inputs(gateway: Any,orders: list[Any]) -> tuple[dict,dict,str,dict | None]:
    with gateway.transaction("Existing planner costs and warehouse origin READ ONLY")as cur:
        cur.execute("set transaction read only")
        wares={o.ware_id for o in orders};origin=None
        if len(wares)==1:
            out=cur.var(oracledb.DB_TYPE_CLOB);cur.callproc("RRL_WARE_DEPOT_API.material",[next(iter(wares)),out])
            candidate=read_oracle_json(out.getvalue())
            if candidate["configured"]:origin=candidate
        addresses=[o.addr for o in orders if o.addr]+([origin["depot_address"]]if origin else [])
        distances,durations,provider=read_cost_cache(cur,addresses)
        return distances,durations,provider,origin
"""
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/transport/public.py");s=p.read_text(encoding="utf-8").replace("profile_duration_cache,planner_cost_cache","profile_duration_cache,planner_cost_cache,planner_inputs");out[str(p)]=s
p=Path("api/wms_api_server/app/services/transport_service.py");s=p.read_text(encoding="utf-8")
s=s.replace('        addr_list = [o.addr for o in orders if o.addr]\n        from ..modules.transport.public import planner_cost_cache\n        dist_cache,duration_cache,used_provider_name=planner_cost_cache(self.gateway,addr_list)','        from ..modules.transport.public import planner_inputs\n        dist_cache,duration_cache,used_provider_name,origin=planner_inputs(self.gateway,orders)')
s=s.replace('duration_cache=duration_cache or None,','duration_cache=duration_cache or None,origin=origin,',1)
s=s.replace('f"Загружено {matrix_pairs} пар, расчетный provider: {used_provider_name}"','f"Загружено {matrix_pairs} пар, provider: {used_provider_name}; адрес отправления: "+("настроен"if origin else "виртуальное депо")',1)
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
