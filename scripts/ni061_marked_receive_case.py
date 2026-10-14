"""Continue immutable225 original source, never create a second shipment."""
import sys,json,copy
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import oracledb,httpx
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.modules.platform.public import read_oracle_json
s=get_settings();tag="13508027ed";uid="FULL.QA:"+tag;plan="IW225.PLAN:"+tag;cell="QI226"+tag;actor="TR226"+tag
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 c.call_timeout=15000;q=c.cursor()
 def meta(sql,**b):
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:q.execute(sql,b);c.commit()
  except BaseException:c.rollback();raise
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 q.execute("select count(*)from RRL_CELLS where CELL=:x",x=cell)
 if not q.fetchone()[0]:
  meta("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT,BLOCKED_FOR_ACCEPT,BLOCKED_FOR_REMAINS,BLOCKED_FOR_POPOLNENIE)values(:x,51365792,0,0,0,0,0,0,0,0,1,1)",x=cell)
  meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:x),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",x=cell)
 q.execute("select PASS from RUSERS where ID=:a",a=actor);row=q.fetchone()
 if not row:
  from uuid import uuid4
  secret=uuid4().hex
  q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'Own226',:g,51365792,0,0)",a=actor,p=secret,g=actor.upper());c.commit()
 else:secret=row[0]
 admin=httpx.Client(auth=("admin","admin123"),timeout=35);client=httpx.Client(auth=(actor,secret),timeout=35);base="http://127.0.0.1:8088"
 def api(client,method,path,body=None,status=200):
  r=client.request(method,base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:3000]);return r.json()
 api(admin,"POST","/api/admin/rights/groups/"+actor.upper()+"/rights",{"right_name":"interwarehouse_receive","description":"Own226 marked target receiving"})
 path="/api/inventory/interwarehouse"
 manifest=api(client,"GET",path+"/plans/"+plan+"/units");assert manifest["physical_unit_count"]==3
 q.execute("select a.BARCODE_SHT from RRL_ARTICULS a join RRL_PALLETS p on p.ARTICUL=a.ACTICUL where p.UID_PALLET=:u",u=uid);barcode=q.fetchone()[0]
 q.execute("select SYSTEM_CODE,PROFILES_JSON,RAW_CODE from RRL_WMS_RECEIPT_CODE where UID_PALLET=:u order by SYSTEM_CODE,CODE_HASH",u=uid)
 scans=[]
 for system,profiles,raw in q.fetchall():
  for profile in read_oracle_json(profiles):scans.append({"system_code":system,"profile_code":profile["profile"],"code":raw.read()if hasattr(raw,"read")else raw})
 assert len(scans)==6
 unload={"operation_id":"IW226.UNLOAD:"+tag,"plan_operation_id":plan,"scan_pallet":uid,"scan_vehicle":"QL"+tag,"scan_dock":"QI225"+tag}
 result=api(client,"POST",path+"/unload",unload);assert result["stock_changed"]is False
 assert api(client,"POST",path+"/unload",unload)==result
 body={"operation_id":"IW226.RECEIVE:"+tag,"plan_operation_id":plan,"scan_pallet":uid,"scan_cell":cell,"scan_article":barcode,"article":"QIW225"+tag.upper(),"quantity":"3","base_uom":"EA","scans":scans}
 bad=copy.deepcopy(body);bad["operation_id"]="IW226.MISSING:"+tag;bad["scans"]=scans[:-1]
 api(client,"POST",path+"/receive",bad,409)
 bad=copy.deepcopy(body);bad["operation_id"]="IW226.DUPLICATE:"+tag;bad["scans"][-1]=scans[0]
 api(client,"POST",path+"/receive",bad,409)
 # Real native same transaction rollback: quantities AND original unit binding return together.
 from hashlib import sha256
 from app.modules.inventory.domain.mark_identity import canonical_mark
 metadata={k:v for k,v in body.items()if k not in("operation_id","plan_operation_id","scans")}
 metadata["unit_scans"]=[{"system_code":x["system_code"],"profile_code":x["profile_code"],"code_hash":sha256(canonical_mark(x["system_code"],x["profile_code"],x["code"])["identity"].encode()).hexdigest()}for x in scans]
 command={"contract_version":2,"operation_id":"IW226.ROLLBACK:"+tag,"command_type":"INTERWARE_RECEIVE","actor":actor,"source":{"plan_operation_id":plan},"lines":[],"units":[],"metadata":metadata}
 out=q.var(oracledb.DB_TYPE_CLOB)
 try:
  q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(command),actor,out,None])
  if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:x",u=uid,x=cell);assert q.fetchone()==(3,0)
  q.execute("select count(*)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:u and CURRENT_CELL=:x and STOCK_STATUS='AVAILABLE'and UNIT_VERSION=8 and HARD_RESERVATION_ID is null",u=uid,x=cell);assert q.fetchone()[0]==3
 finally:c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 q.execute("select count(*)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:u and STOCK_STATUS='ISSUED'and UNIT_VERSION=7",u=uid);assert q.fetchone()[0]==3
 def receive(index):
  value=copy.deepcopy(body);value["operation_id"]+=str(index)
  with httpx.Client(auth=(actor,secret),timeout=35)as h:return h.post(base+path+"/receive",json=value),value
 with ThreadPoolExecutor(max_workers=2)as pool:results=list(pool.map(receive,[0,1]))
 assert sorted(r.status_code for r,b in results)==[200,409],[(r.status_code,r.text[:2500])for r,b in results]
 response,winner=next((r.json(),b)for r,b in results if r.status_code==200)
 assert api(client,"POST",path+"/receive",winner)==response
 q.execute("update RUSERS set WARE_ID=6667491 where ID=:a",a=actor);c.commit()
 try:
  api(client,"POST",path+"/receive",winner,403);api(client,"GET",path+"/plans/"+plan+"/units",status=403)
 finally:q.execute("update RUSERS set WARE_ID=51365792 where ID=:a",a=actor);c.commit()
 assert api(client,"POST",path+"/receive",winner)==response
 q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:x",u=uid,x=cell);assert q.fetchone()==(3,0)
 q.execute("select count(*),sum(BASE_QTY),min(UNIT_VERSION),max(UNIT_VERSION)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:u and CURRENT_CELL=:x and STOCK_STATUS='AVAILABLE'and HARD_RESERVATION_ID is null",u=uid,x=cell);assert q.fetchone()==(3,3,8,8)
 q.execute("select count(*)from RRL_EVENTS where OPERATION_ID=:p",p=winner["operation_id"]);assert q.fetchone()[0]==1
 q.execute("select count(*)from RRL_WMS_RECEIPT_CODE where UID_PALLET=:u",u=uid);assert q.fetchone()[0]==6
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 print("PASS226 original marked225 -> unload0 -> same original units3/codes6 target P3H0/version8; missing/duplicate409/native full rollback/concurrent one winner/replay/current wrongWARE403/protected20/20",winner["operation_id"],flush=True)
