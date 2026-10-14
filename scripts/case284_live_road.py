exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.services.routing import OsrmProvider,ValhallaProvider
points=[(56.8389,60.5975),(56.8519,60.6122)]
result={}
for provider in [OsrmProvider(),ValhallaProvider()]:
 distance,duration=provider.build_cost_matrix(points)
 assert len(distance)==2 and all(duration[i][j]>0 and distance[i][j]>0 for i,j in[(0,1),(1,0)])
 result[provider.name]={"distance_km":distance,"duration_min":duration,"duration_basis":"ROAD_PROFILE_ESTIMATE","traffic_verified":False}
Path("tmp/context284.json").write_text(json.dumps(result),encoding="utf-8")
print("LIVE_ROAD284",json.dumps(result))
print("PASS284 actual existinglocalOSRM andValhalla directionalduration responses/currentnewdecoder onpreparedUralmap; no cachebulkrefresh/no quantity or realtrip admission")
