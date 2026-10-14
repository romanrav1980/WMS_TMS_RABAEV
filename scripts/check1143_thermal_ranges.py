import sys
from pathlib import Path
sys.path.insert(0,str(Path("api/wms_api_server").resolve()))
from app.modules.inventory.infrastructure.shipping_temperature_read import read_shipping_temperature_requirements
class Cursor:
 def __init__(self,rows,user=(9807,"GLOBAL_ADMIN")):self.rows=rows;self.user=user;self.calls=[]
 def execute(self,sql,*args,**kw):self.calls.append(sql)
 def fetchone(self):return self.user
 def fetchall(self):return self.rows
rows=[(9807,"A","A","2","6"),(9807,"B","B","3","5")]
v=read_shipping_temperature_requirements(Cursor(rows),[1,2],"admin")
assert v["all_ranges_configured"] and v["common_min_c"]=="3" and v["common_max_c"]=="5"
assert not v["vehicle_temperature_verified"] and not v["operational_admission"]
v=read_shipping_temperature_requirements(Cursor([(9807,"A","A","2","3"),(9807,"B","B","4","6")]),[1,2],"admin")
assert v["ranges_conflict"] and not v["operational_admission"]
v=read_shipping_temperature_requirements(Cursor([(9807,"A","A","6","2")]),[1],"admin");assert not v["all_ranges_configured"]
try:read_shipping_temperature_requirements(Cursor(rows,user=(9999,"USER")),[1,2],"foreign")
except PermissionError:pass
else:raise AssertionError("Foreign scope accepted")
try:read_shipping_temperature_requirements(Cursor(rows),[True],"admin")
except ValueError:pass
else:raise AssertionError("bool ID accepted")
print("PASS1143 exact common range/conflict/invalid range/current foreign denial/no temperature admission")
