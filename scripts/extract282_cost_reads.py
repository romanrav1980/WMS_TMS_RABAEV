from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/transport/public.py");s=p.read_text(encoding="utf-8").replace("from .infrastructure.profile_duration_cache import profile_duration_cache","from .infrastructure.profile_duration_cache import profile_duration_cache,planner_cost_cache");out[str(p)]=s
p=Path("api/wms_api_server/app/services/transport_service.py");s=p.read_text(encoding="utf-8")
start=s.index("        dist_cache = DistanceMatrixService(self.gateway).get_matrix_as_dict(addr_list)")
end=s.index("        explain_steps.append({",start)
s=s[:start]+"""        from ..modules.transport.public import planner_cost_cache
        dist_cache,duration_cache,used_provider_name=planner_cost_cache(self.gateway,addr_list)
        matrix_pairs=len(dist_cache)
"""+s[end:]
s=s.replace("        from .distance_matrix_service import DistanceMatrixService\n","",1)
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
