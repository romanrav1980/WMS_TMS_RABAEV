exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.inventory.public import build_stock_posting_service
from app.modules.inventory.infrastructure.interwarehouse import Interwarehouse
from app.modules.inventory.infrastructure.interwarehouse_recovery_st import prepare_recovery_st
from app.modules.inventory.infrastructure.warehouse_hu import WarehouseHu
from app.modules.transport.public import assign_sts
from app.oracle_gateway import OracleGateway
import httpx
ctx=json.loads(Path("tmp/context390.json").read_text());found=json.loads(Path("tmp/context390_recovery.json").read_text());p=Path("tmp/context392.json");saved=json.loads(p.read_text())if p.exists()else{"source":ctx,"parts":[{}for _ in range(2)]}
gw=OracleGateway();svc=Interwarehouse(gw,build_stock_posting_service());hu=WarehouseHu(gw);tag=ctx["tag"]
def save():p.write_text(json.dumps(saved,indent=2),encoding="utf-8")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
 try:q.execute("update RRL_TR_VEHICLE set PALLETS=2 where NUM=:plate",plate="QL"+tag);c.commit()
 finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
if "custody"not in saved:saved["custody"]=svc.release_custody("IW392.CUSTODY:"+tag,ctx["receipt_operation"],"admin");save()
for index,part in enumerate(saved["parts"]):
 if "onward"not in part:
  if index==0:part["onward"]=svc.prepare_onward("IW392.ORIGINAL.ST:"+tag,ctx["receipt_operation"],"Исходная принятая часть вместе с найденными единицами","DEV392:original","admin",True)
  else:part["onward"]=prepare_recovery_st(gw,"IW392.FOUND.ST:"+str(index)+":"+tag,found["parts"][index-1]["receipt_operation_id"],ctx["target_trip"],"Консолидация найденной исходной единицы","DEV392:found"+str(index),"admin")
  save()
 if "assigned"not in part:assign_sts(gw,ctx["target_trip"],[part["onward"]["st_number"]],"admin");part["assigned"]=True;save()
top="IH392:"+tag
if "created"not in saved:saved["created"]=hu.command("HU_CREATE",top,"IW392.CREATE:"+tag,dict(cell=ctx["outbound"],warehouse=ctx["target_warehouse"],container_type="PALLET",tare_weight_kg="1",scan_container=top,scan_cell=ctx["outbound"]),"admin");save()
for index,part in enumerate(saved["parts"]):
 lot=part["onward"]["pallet_identifier"]
 if "attached"not in part:
  parent=hu.preview(top,"admin");child=hu.preview(lot,"admin")
  part["attached"]=hu.command("HU_ATTACH",top,"IW392.ATTACH:"+str(index)+":"+tag,dict(child_uid=lot,expected_version=parent["nodes"][0]["version"],expected_child_version=child["nodes"][0]["version"],scan_container=top,scan_child=lot,reason="Одна исходная поставка, три сохранённые истории СТ"),"admin");save()
 with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
  q=c.cursor();q.execute("select UNIT_ID from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:lot",lot=lot);ids={x[0]for x in q};assert len(ids)==(1 if index==0 else 2)
 part["scans"]=[code for unit in ctx["units"]if unit["unit_id"]in ids for code in unit["codes"]];save()
 with httpx.Client(auth=("admin","admin123"),timeout=40)as client:
  if "qc"not in part:
   st=part["onward"]["shipment_identifier"];r=client.get("http://127.0.0.1:8088/api/outgoing-quality/"+st);assert r.status_code==200,r.text
   r=client.post("http://127.0.0.1:8088/api/outgoing-quality/"+st+"/scan",json=dict(operation_id="IW392.QC:"+str(index)+":"+tag,expected_composition_signature=r.json()["composition_signature"],error_count=0,scans=part["scans"]));assert r.status_code==200,r.text;part["qc"]=r.json();save()
saved.update(root=top,tree=hu.preview(top,"admin"));save()
assert saved["tree"]["leaf_count"]==2
print("PREP392 originalaccepted1+found1+found1/3ST/oneTOP/same3keys6codes/QC/existingassignment")
