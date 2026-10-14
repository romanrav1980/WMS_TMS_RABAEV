import sys
sys.path.insert(0,'api/wms_api_server')
from app.services.geofencing import check_geofences,_GEO_STATE
class G:
 def fetch_all(self,*args):return [{'addr_id':'OWN/STORE','addr':'OWN/STORE','latitude':0,'longitude':0,'radius_m':200,'task_id':t}for t in(1,2)]
 def execute(self,*args):raise AssertionError('GPS must not write unrelated unload fact')
_GEO_STATE.clear();events=check_geofences(999,0,0,G());assert len(events)==2 and all(e['operational_fact_applied']is False for e in events)
assert check_geofences(999,0,0,G())==[]
assert len(check_geofences(999,1,1,G()))==2
print('PASS GPS observations use trip/address identity; no operational write')
