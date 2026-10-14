import sys,json
from pathlib import Path
from pydantic import ValidationError
sys.path.insert(0,'api/wms_api_server')
from app.modules.transport.api.vehicle_profile_routes import VehicleProfileRequest,configure
from app.auth import AdminUser
base=dict(operation_id='OUTER.LOCAL:1',vehicle_id=1,expected_source_hash='A'*64,vehicle_size_class='TRUCK',cargo_length_mm=5000,cargo_width_mm=2000,cargo_height_mm=2000,expected_version=0,reason='Outer body fixture',evidence_reference='fixture only')
class Service:
 def configure(self,body,actor):return body
user=AdminUser('admin','admin','GLOBAL_ADMIN',{'*'})
assert 'outer_height_mm'not in configure(VehicleProfileRequest(**base),user,Service())
assert configure(VehicleProfileRequest(**base,outer_height_mm=None),user,Service())['outer_height_mm']is None
assert configure(VehicleProfileRequest(**base,outer_height_mm=3500,outer_length_mm=6500),user,Service())['outer_length_mm']==6500
for bad in [0,-1,1.5,'3500',True,1000001]:
 try:VehicleProfileRequest(**base,outer_height_mm=bad);raise AssertionError('bad accepted')
 except ValidationError:pass
print('PASS optional omission/preserve, explicitnull/clear, positiveinteger; invalid types/range rejected')
