from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/transport/public.py");s=p.read_text(encoding="utf-8")+"\nfrom .domain.road_matrix import osrm_costs,valhalla_costs\n";out[str(p)]=s
p=Path("api/wms_api_server/app/services/routing.py");s=p.read_text(encoding="utf-8")
s=s.replace("    @abstractmethod\n    def build_matrix(", "    def build_cost_matrix(self,points: list[tuple[float,float]]) -> tuple[list[list[float]],list[list[float]] | None]:\n        return self.build_matrix(points),None\n\n    @abstractmethod\n    def build_matrix(",1)
start=s.index("    def build_matrix(",s.index("class OsrmProvider"));end=s.index("# ---------------------------------------------------------------------------\n# Valhalla",start)
s=s[:start]+"""    def build_matrix(self,points: list[tuple[float,float]]) -> list[list[float]]:
        return self.build_cost_matrix(points)[0]

    def build_cost_matrix(self,points: list[tuple[float,float]]) -> tuple[list[list[float]],list[list[float]]]:
        from ..modules.transport.public import osrm_costs
        if not 1<=len(points)<=200:raise ValueError("ROAD_MATRIX_POINT_BOUND_200")
        coords_str=";".join(f"{lon},{lat}"for lat,lon in points)
        url=f"{OSRM_URL}/table/v1/driving/{coords_str}?annotations=distance,duration"
        response=httpx.get(url,timeout=_OSRM_TIMEOUT);response.raise_for_status()
        return osrm_costs(response.json(),len(points))


"""+s[end:]
start=s.index("    def build_matrix(",s.index("class ValhallaProvider"));end=s.index("# ---------------------------------------------------------------------------\n# Fallback chain",start)
s=s[:start]+"""    def build_matrix(self,points: list[tuple[float,float]]) -> list[list[float]]:
        return self.build_cost_matrix(points)[0]

    def build_cost_matrix(self,points: list[tuple[float,float]]) -> tuple[list[list[float]],list[list[float]]]:
        from ..modules.transport.public import valhalla_costs
        if not 1<=len(points)<=200:raise ValueError("ROAD_MATRIX_POINT_BOUND_200")
        locations=[{"lat":lat,"lon":lon}for lat,lon in points]
        response=httpx.post(f"{VALHALLA_URL}/sources_to_targets",json={"sources":locations,"targets":locations,"costing":"truck"},timeout=_VALHALLA_TIMEOUT)
        response.raise_for_status();return valhalla_costs(response.json(),len(points))


"""+s[end:];out[str(p)]=s
p=Path("api/wms_api_server/app/services/distance_matrix_service.py");s=p.read_text(encoding="utf-8")
s=s.replace("matrix = provider.build_matrix(points)","matrix,durations = provider.build_cost_matrix(points)")
s=s.replace("DURATION_MIN = :dur,","DURATION_MIN = :dur,\n                           DURATION_BASIS = :duration_basis,")
s=s.replace("DURATION_MIN, SOURCE, UPDATED_AT)","DURATION_MIN, DURATION_BASIS, SOURCE, UPDATED_AT)")
s=s.replace(":dur, :source, SYSDATE)",":dur, :duration_basis, :source, SYSDATE)")
s=s.replace("duration_min = round(dist_km / 50.0 * 60, 0)","duration_min = durations[i][j]if durations is not None else round(dist_km / 50.0 * 60, 0)")
s=s.replace('"dur":       duration_min,','"dur":       duration_min,\n                        "duration_basis":"ROAD_PROFILE_ESTIMATE"if durations is not None else "SPEED_50_ESTIMATE",')
out[str(p)]=s
out["db/migrations/2026-10-11_ni081_road_duration/001_schema.sql"]="""alter table RRL_ADDR_DISTANCE_MATRIX add(DURATION_BASIS varchar2(30)default 'SPEED_50_ESTIMATE'not null);
alter table RRL_ADDR_DISTANCE_MATRIX add constraint RRL_ADDR_DM_DUR_BASIS_C check(DURATION_BASIS in('SPEED_50_ESTIMATE','ROAD_PROFILE_ESTIMATE'));
"""
out["db/migrations/2026-10-11_ni081_road_duration/rollback.sql"]="alter table RRL_ADDR_DISTANCE_MATRIX drop constraint RRL_ADDR_DM_DUR_BASIS_C;\nalter table RRL_ADDR_DISTANCE_MATRIX drop column DURATION_BASIS;\n"
print(json.dumps(out,ensure_ascii=True))
