from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/transport/domain/road_matrix.py");s=p.read_text(encoding="utf-8")
s+="""

def validate_points(points: list[tuple[float,float]]) -> None:
    if not 1<=len(points)<=200:raise ValueError("ROAD_MATRIX_POINT_BOUND_200")
    for point in points:
        if not isinstance(point,(tuple,list))or len(point)!=2:raise ValueError("ROAD_MATRIX_COORDINATE_SHAPE")
        lat,lon=point
        if any(isinstance(v,bool)or not isinstance(v,(int,float))for v in point):raise ValueError("ROAD_MATRIX_COORDINATE_TYPE")
        if not(-90<=lat<=90 and -180<=lon<=180):raise ValueError("ROAD_MATRIX_COORDINATE_RANGE")
"""
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/transport/public.py");s=p.read_text(encoding="utf-8").replace("from .domain.road_matrix import osrm_costs,valhalla_costs","from .domain.road_matrix import osrm_costs,valhalla_costs,validate_points");out[str(p)]=s
p=Path("api/wms_api_server/app/services/routing.py");s=p.read_text(encoding="utf-8")
s=s.replace("from ..modules.transport.public import osrm_costs","from ..modules.transport.public import osrm_costs,validate_points")
s=s.replace("from ..modules.transport.public import valhalla_costs","from ..modules.transport.public import valhalla_costs,validate_points")
s=s.replace('        if not 1<=len(points)<=200:raise ValueError("ROAD_MATRIX_POINT_BOUND_200")','        validate_points(points)')
s=s.replace('url=f"{OSRM_URL}/table/v1/driving/{coords_str}?annotations=distance,duration"', 'radii=";".join("1000"for _ in points)\n        url=f"{OSRM_URL}/table/v1/driving/{coords_str}?annotations=distance,duration&radiuses={radii}"')
s=s.replace('locations=[{"lat":lat,"lon":lon}for lat,lon in points]', 'locations=[{"lat":lat,"lon":lon,"radius":1000,"search_cutoff":1000}for lat,lon in points]')
s=s.replace('"costing":"truck"},timeout=_VALHALLA_TIMEOUT)', '"costing":"truck","units":"kilometers"},timeout=_VALHALLA_TIMEOUT)')
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
