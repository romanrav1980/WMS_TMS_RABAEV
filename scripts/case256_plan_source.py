exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.transport.public import TransportPreflight,generate_existing_operations
from app.modules.platform.public import read_oracle_json
import httpx
ctx=json.loads(Path("tmp/context254.json").read_text(encoding="utf-8"));trip=ctx["target_trip"];tag=ctx["tag"];uid=ctx["uid"];g=OracleGateway();svc=TransportPreflight(g)
h=httpx.Client(auth=("admin","admin123"),timeout=35);base="http://127.0.0.1:8088"
def api(method,path,body=None):
 r=h.request(method,base+path,json=body);assert r.status_code==200,(r.status_code,r.text[:1800]);return r.json()
old=svc.time_context(trip,"admin");assert old["approval_status"]=="LEGACY_SOURCE_CONTRACT"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select CONTENT_VERSION from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:op",op="IW255.LOAD:"+tag);version=q.fetchone()[0]
api("POST","/api/transport/loading/unload",{"operation_id":"IW256.UNLOAD:"+tag,"load_operation_id":"IW255.LOAD:"+tag,"expected_version":version,"scan_container":uid,"scan_cell":ctx["outbound"],"scan_vehicle":"QL"+tag,"scan_dock":ctx["outbound"],"reason":"Own256 same source reversible v2 plan contract proof"})
generate_existing_operations(g,trip,"admin")
source=svc.time_context(trip,"admin")
body={"trip_id":trip,"expected_version":source["version"],"source_hash":source["source_hash"],"time_zone":"UTC","reason":"Own256 current material plan excludes execution progress"}
decision=svc.approve_time("TIME256:"+tag,body,"admin")
assert decision["source_contract_version"]==2 and decision["plan_source"]["source_contract_version"]==2
assert svc.time_context(trip,"admin")["approval_status"]=="APPROVED"
st=ctx["st255"]["shipment_identifier"]
quality=api("GET","/api/outgoing-quality/"+st)
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select SYSTEM_CODE,PROFILES_JSON,RAW_CODE from RRL_WMS_RECEIPT_CODE where UID_PALLET=:uid order by SYSTEM_CODE,CODE_HASH",uid=uid)
 scans=[{"system_code":system,"profile_code":profile["profile"],"code":raw.read()if hasattr(raw,"read")else raw}for system,profiles,raw in q.fetchall()for profile in read_oracle_json(profiles)]
api("POST","/api/outgoing-quality/"+st+"/scan",{"operation_id":"IW256.QC:"+tag,"expected_composition_signature":quality["composition_signature"],"error_count":0,"scans":scans})
preview=api("GET","/api/transport/loading/single-preview?shipment_identifier="+st)
api("POST","/api/transport/loading/confirm-single",{"operation_id":"IW256.LOAD:"+tag,"identifier":st,"expected_version":preview["expected_version"],"expected_composition_signature":preview["composition_signature"],"scan_container":uid,"scan_cell":ctx["outbound"],"transport_task_id":trip,"scan_vehicle":"QL"+tag,"scan_dock":ctx["outbound"],"measurements":{"origin":"MANUAL_CONFIRMED","content_version":preview["expected_version"],"gross_weight_kg":"10","width_m":"1","depth_m":"1","height_m":"1.5"}})
after=svc.time_context(trip,"admin");assert after["approval_status"]=="APPROVED"and after["source_hash"]==decision["source_hash"]
ready=svc.coordination(trip,"admin")
assert ready["status"]=="CURRENT_RECORDED_PHASES_COMPLETE"and not ready["blockers"],ready["blockers"]
assert not ready["operational_admission"]and not ready["departure_authorized"]
api("POST",f"/api/transport/loading/{trip}/depart",{"operation_id":"IW256.DEPART:"+tag})
final=svc.time_context(trip,"admin")
assert final["approval_status"]=="APPROVED"and final["source_hash"]==decision["source_hash"]
assert any(x["code"]=="COORDINATION_PLANNED_TRIP_REQUIRED"for x in svc.coordination(trip,"admin")["blockers"])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select count(*),sum(BASE_QTY)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:uid and STOCK_STATUS='ISSUED'",uid=uid);assert q.fetchone()==(3,3)
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
ctx["time256"]=decision;ctx["load256"]="IW256.LOAD:"+tag;Path("tmp/context254.json").write_text(json.dumps(ctx,ensure_ascii=True),encoding="utf-8")
print("PASS256 same original3units6codes/explicitunload-v2reconfirm-QC-reload no rebirth; unchanged materialplan remains approved afterload/depart; 255 same-snapshot phasescomplete before authoritative native depart/afterdepart phaseblocked; oldv1 journal preserved/no assumedsource/protected20-20")
