import sys,json
from pathlib import Path
sys.path.insert(0,str(Path('api/wms_api_server').resolve()))
from types import SimpleNamespace
from fastapi import HTTPException
from app.modules.inventory.api.outgoing_quality_routes import control_label
class Service:
 def __init__(self,recorded):self.recorded=recorded
 def status(self,*args):return {'ready':True,'composition_signature':'A'*64,'shipment_identifier':'SAFE','weight_exemption':{'eligible':True,'exemption_basis':'SCANNED_ORIGINAL_STORAGE_IDENTIFIER','receipt_operation_id':'SOURCE<1>'},'weight_exemption_recorded':self.recorded}
try:
 control_label('SAFE','A'*64,SimpleNamespace(username='admin'),Service(False));raise AssertionError('Unrecorded exemption printed')
except HTTPException as e:assert e.status_code==409
response=control_label('SAFE','A'*64,SimpleNamespace(username='admin'),Service(True));assert response.status_code==200
assert 'SOURCE&lt;1&gt;' in response.body.decode() and 'SOURCE<1>' not in response.body.decode()
print(json.dumps({'unrecorded':409,'recorded':200,'html_escaped':True,'database_writes':0}))
