import sys,json,copy
from pathlib import Path
import oracledb,httpx
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.oracle_gateway import OracleGateway
from app.modules.platform.public import read_oracle_json
from app.modules.transport.public import assign_sts
s=get_settings();tag="13508027ed";actor="TR226"+tag;uid="FULL.QA:"+tag;receipt="IW226.RECEIVE:"+tag+"0"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();c.call_timeout=15000;q.execute("select PASS from RUSERS where ID=:a",a=actor);secret=q.fetchone()[0]
 client=httpx.Client(auth=(actor,secret),timeout=35);admin=httpx.Client(auth=("admin","admin123"),timeout=35);base="http://127.0.0.1:8088"
 def api(h,method,path,body=None,status=200):
  r=h.request(method,base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:3000]);return r.json()
 for right in["outgoing_pallet_edit","transport_dispatch_edit","transport_dispatch_view","stock_posting_shipping","outgoing_pallet_check"]:
  api(admin,"POST","/api/admin/rights/groups/"+actor.upper()+"/rights",{"right_name":right,"description":"Own228 original marked second leg"})
 custody={"operation_id":"IW228.CUSTODY:"+tag,"receipt_operation_id":receipt}
 saved=api(client,"POST","/api/inventory/interwarehouse/release-custody",custody);assert not saved["stock_changed"]
 assert api(client,"POST","/api/inventory/interwarehouse/release-custody",custody)==saved
 q.execute("update RUSERS set WARE_ID=6667491 where ID=:a",a=actor);c.commit()
 try:api(client,"POST","/api/inventory/interwarehouse/release-custody",custody,403)
 finally:q.execute("update RUSERS set WARE_ID=51365792 where ID=:a",a=actor);c.commit()
 onward={"operation_id":"IW228.ONWARD:"+tag,"receipt_operation_id":receipt,"reason":"Own228 original marked physical units second existing leg","decision_reference":"IW228:"+tag,"accept_legacy_address":True}
 prepared=api(client,"POST","/api/inventory/interwarehouse/prepare-onward",onward)
 assert api(client,"POST","/api/inventory/interwarehouse/prepare-onward",onward)==prepared
 st=prepared["shipment_identifier"];trip=prepared["target_trip_id"]
 assign_sts(OracleGateway(),trip,[prepared["st_number"]],actor)
 q.execute("select SYSTEM_CODE,PROFILES_JSON,RAW_CODE from RRL_WMS_RECEIPT_CODE where UID_PALLET=:u order by SYSTEM_CODE,CODE_HASH",u=uid);scans=[]
 for system,profiles,raw in q.fetchall():
  for profile in read_oracle_json(profiles):scans.append({"system_code":system,"profile_code":profile["profile"],"code":raw.read()if hasattr(raw,"read")else raw})
 quality=api(client,"GET","/api/outgoing-quality/"+st)
 api(client,"POST","/api/outgoing-quality/"+st+"/scan",{"operation_id":"IW228.QC:"+tag,"expected_composition_signature":quality["composition_signature"],"error_count":0,"scans":scans})
 preview=api(client,"GET","/api/transport/loading/single-preview?shipment_identifier="+st)
 load={"operation_id":"IW228.LOAD:"+tag,"identifier":st,"expected_version":preview["expected_version"],"expected_composition_signature":preview["composition_signature"],"scan_container":uid,"scan_cell":"QO225"+tag,"transport_task_id":trip,"scan_vehicle":"QI228"+tag,"scan_dock":"QO225"+tag,"measurements":{"origin":"MANUAL_CONFIRMED","content_version":preview["expected_version"],"gross_weight_kg":"10","width_m":"1","depth_m":"1","height_m":"1.5"}}
 response=api(client,"POST","/api/transport/loading/confirm-single",load);assert api(client,"POST","/api/transport/loading/confirm-single",load)==response
 q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:x",u=uid,x="QO225"+tag);assert q.fetchone()==(0,0)
 q.execute("select count(*),sum(BASE_QTY),min(UNIT_VERSION),max(UNIT_VERSION)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:u and STOCK_STATUS='ISSUED'and HARD_RESERVATION_ID is null",u=uid);assert q.fetchone()==(3,3,10,10)
 q.execute("select count(*)from RRL_WMS_RECEIPT_CODE where UID_PALLET=:u",u=uid);assert q.fetchone()[0]==6
 q.execute("select count(*)from RRL_INTERWARE_ONWARD_DISPATCH where OPERATION_ID=:p",p=load["operation_id"]);assert q.fetchone()[0]==1
 q.execute("select STATUS,FACT_QTY from RRL_CUSTOMER_ORDER_FULFILLMENT where LEGACY_SBORKA_PALLET_ID=641362");assert q.fetchall()==[("SHIPPED",3)]
 q.execute("select count(*)from RRL_CUSTOMER_ORDER_FULFILLMENT where LEGACY_SBORKA_PALLET_ID=:s",s=prepared["st_id"]);assert q.fetchone()[0]==0
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 print("PASS228 original marked custody0/current wrongWARE403/old ST constructor/existing assign/current QC6/second LOAD native-3/source0/same3units6codes/version10/originalFF SHIPPED3 unchanged/no new fulfillment/protected20/20",st,trip,flush=True)
