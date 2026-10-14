from pathlib import Path
import json
out={}
pairs={
"docker-compose.osrm.yml":("osrm/osrm-backend:latest","osrm/osrm-backend@sha256:af5d4a83fb90086a43b1ae2ca22872e6768766ad5fcbb07a29ff90ec644ee409"),
"docker-compose.valhalla.yml":("ghcr.io/gis-ops/docker-valhalla/valhalla:latest","ghcr.io/gis-ops/docker-valhalla/valhalla@sha256:060da5b92e6024a67f65135c236d918b021d63e73d1808a0d55b7e7cbd17240c")
}
for name,(old,new)in pairs.items():
 p=Path(name);s=p.read_text(encoding="utf-8");assert old in s;s=s.replace(old,new,1);out[name]=s
out["config/routing_runtime_provenance_20261011.json"]=json.dumps({"captured_at_utc":"2026-10-11T16:35:00Z","osrm":{"version":"5.26.0","image":pairs["docker-compose.osrm.yml"][1],"port":5000,"prepared_graph":"osrm-data/russia-latest.osrm"},"valhalla":{"version":"3.5.1","image":pairs["docker-compose.valhalla.yml"][1],"port":8002,"prepared_graph":"valhalla-data/valhalla_tiles.tar"},"map_scope":"Previously approved regional Ural extract; not global geography or live traffic","oracle":"Existing RABAEV/orcl unchanged","observed_directional_costs":json.loads(Path("tmp/context284.json").read_text(encoding="utf-8"))},indent=2)+"\n"
print(json.dumps(out,ensure_ascii=True))
