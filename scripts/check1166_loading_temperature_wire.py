exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.transport.api.loading_routes import LoadingRequest,SingleLoadingRequest,confirm,confirm_single
from types import SimpleNamespace
class Sink:
 def __init__(self):self.calls=[]
 def load(self,op,identifier,metadata,actor):self.calls.append((op,identifier,metadata,actor));return {"operation_id":op}
 def load_single(self,op,identifier,metadata,actor):return self.load(op,identifier,metadata,actor)
base={"operation_id":"WIRE1166","identifier":"OWN","expected_version":1,"scan_container":"OWN",
      "scan_cell":"CELL","transport_task_id":1,"scan_vehicle":"TRUCK","scan_dock":"DOCK",
      "measurements":{"origin":"MANUAL_CONFIRMED","content_version":1,"gross_weight_kg":"10","width_m":"1","depth_m":"1","height_m":"1"}}
service=Sink();user=SimpleNamespace(username="admin")
confirm(LoadingRequest(**base),user,service)
old=service.calls[-1][2];assert "temperature_confirmation"not in old and "temperature_confirmation"not in old["loading_context"]
thermal={"origin":"MANUAL_AT_LOADING","observed_c":"-3.125","vehicle_profile_version":1,"observation_reference":"OWN1166"}
confirm_single(SingleLoadingRequest(**{**base,"expected_composition_signature":"A"*64,"temperature_confirmation":thermal}),user,service)
assert service.calls[-1][2]["loading_context"]["temperature_confirmation"]==thermal
for bad in({"observed_c":2},{"observed_c":"NaN"},{"vehicle_profile_version":True},{"extra":1}):
 try:LoadingRequest(**{**base,"temperature_confirmation":{**thermal,**bad}})
 except ValueError:pass
 else:raise AssertionError("Invalid confirmation accepted")
print("PASS1166 old absent-block canonical fields unchanged; HU/single typed thermal block passed inside same loading context; invalid numbers/bool/extra rejected; no Oracle writes")
