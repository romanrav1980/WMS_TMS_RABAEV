"""One isolated tare-only cycle on retained trip519; never recreate its goods."""
exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
import httpx
base="http://127.0.0.1:8088";p="/api/inventory/tare";path=Path("tmp/context553.json")
admin=httpx.Client(auth=("admin","admin123"),timeout=35)
def call(client,method,route,body=None,status=200):
 r=client.request(method,base+route,json=body);assert r.status_code==status,(route,r.status_code,r.text[:1300]);return r.json()
if path.exists():ctx=json.loads(path.read_text(encoding="utf-8"));assert not ctx.get("done"),"Already completed; no second physical fixture"
else:
 tag=uuid4().hex[:8]
 with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
  q=c.cursor();q.execute("select t.ID,t.VODITEL_ID,v.ID,v.NUM from RRL_TRANSPORT_TASK t join RRL_TR_VEHICLE v on v.NUM=t.TRANSPORT where t.ID=33622")
  trip,driver,vehicle,plate=q.fetchone()
  q.execute("select min(ADDR)from RRL_SBORKA_PALLETS where TRANSTASK_ID=:trip",trip=trip);store=q.fetchone()[0];assert store
  q.execute("select min(PALLET_TYPE_ID)from RRL_PALLET_TYPE t where ACTIVE=1 and not exists(select 1 from RRL_TARE_BALANCE b where b.OWNER_WARE_ID=14526684 and b.PALLET_TYPE_ID=t.PALLET_TYPE_ID)")
  type_id=q.fetchone()[0];assert type_id
 ctx=dict(tag=tag,warehouse=14526684,trip=trip,driver=driver,vehicle=vehicle,plate=plate,store=store,type=type_id,
          users=[dict(id="QS553"+tag,secret=uuid4().hex,group="GS553"+tag),dict(id="QD553"+tag,secret=uuid4().hex,group="GD553"+tag)],steps={})
 path.write_text(json.dumps(ctx),encoding="utf-8")
def save():path.write_text(json.dumps(ctx),encoding="utf-8")
tag=ctx["tag"];ware=ctx["warehouse"];type_id=ctx["type"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 c.call_timeout=15000;q=c.cursor()
 if not ctx.get("actors_ready"):
  for i,u in enumerate(ctx["users"]):
   q.execute("select count(*)from RUSERS where ID=:actor",actor=u["id"])
   if q.fetchone()[0]==0:q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,DELETED,PRAVO_ADMIN_LOGIN)values(:actor,:secret,'Own553 tare custody',:grp,0,0)",actor=u["id"],secret=u["secret"],grp=u["group"])
  c.commit()
  for i,u in enumerate(ctx["users"]):
   call(admin,"POST","/api/admin/rights/groups",{"id":u["group"],"name":"Own553 tare custody"})
   for right in ["tare_view","tare_offer","tare_accept"]+(["store_receipt_confirm","tare_damage","tare_writeoff"]if i==0 else["driver_return_accept"]):
    call(admin,"POST",f'/api/admin/rights/groups/{u["group"]}/rights',{"right_name":right,"description":"Own553 tare custody"})
  call(admin,"POST","/api/delivery/store-receipts/receivers",{"store_address":ctx["store"],"username":ctx["users"][0]["id"]})
  ctx["actors_ready"]=True;save()
 shop=httpx.Client(auth=(ctx["users"][0]["id"],ctx["users"][0]["secret"]),timeout=35)
 driver_api=httpx.Client(auth=(ctx["users"][1]["id"],ctx["users"][1]["secret"]),timeout=35)
 binding=call(admin,"GET",f'/api/transport/driver-bindings/{ctx["driver"]}')
 if "original_binding"not in ctx:ctx["original_binding"]=binding;save()
 changed=call(admin,"PUT",f'/api/transport/driver-bindings/{ctx["driver"]}',{"user_id":ctx["users"][1]["id"],"active":True,"expected_version":binding["binding_version"]})
 binding_version=changed["binding_version"]
 def post(client,route,body):
  key=body["operation_id"]
  if key in ctx["steps"]:return ctx["steps"][key]
  result=call(client,"POST",p+route,body)
  assert call(client,"POST",p+route,body)==result
  ctx["steps"][key]=result;save();return result
 def transfer(sender,receiver,condition,fkind,fid,tkind,tid,suffix,damage=None):
  offer={"operation_id":"TRACE553.OFFER:"+tag+":"+suffix,"task_id":ctx["trip"],"owner_ware_id":ware,"pallet_type_id":type_id,"condition":condition,"from_kind":fkind,"from_id":str(fid),"to_kind":tkind,"to_id":str(tid),"quantity":"2","scan_vehicle":ctx["plate"]}
  if damage:offer["damage_operation_id"]=damage
  post(sender,"/offer",offer)
  return post(receiver,"/accept",{"operation_id":"TRACE553.ACCEPT:"+tag+":"+suffix,"offer_operation_id":offer["operation_id"],"accepted_quantity":"2","scan_vehicle":ctx["plate"]})
 try:
  post(admin,"/count",{"operation_id":"TRACE553.COUNT:"+tag,"owner_ware_id":ware,"pallet_type_id":type_id,"condition":"GOOD","observed_quantity":"2","expected_version":0,"reason":"Own553 observed test assets","decision_reference":"DEV553:"+tag})
  transfer(admin,driver_api,"GOOD","WAREHOUSE",ware,"VEHICLE",ctx["vehicle"],"OUT")
  if not ctx.get("return_policy_ready"):
   policy=call(admin,"GET",p+"/return-policy?scope_kind=STORE&scope_key="+httpx.QueryParams({"s":ctx["store"]})["s"])
   ctx["original_return_policy"]=policy;save()
   if policy["policy_version"]==0:
    ctx["configured_return_policy"]=call(admin,"PUT",p+"/return-policy",{"scope_kind":"STORE","scope_key":ctx["store"],"return_mode":"SAME_DAY","return_days":None,"timezone_region":"UTC","expected_version":0})
   ctx["return_policy_ready"]=True;save()
  transfer(driver_api,shop,"GOOD","VEHICLE",ctx["vehicle"],"STORE",ctx["store"],"STORE")
  damage="TRACE553.DAMAGE:"+tag
  post(shop,"/damage",{"operation_id":damage,"owner_ware_id":ware,"pallet_type_id":type_id,"custodian_kind":"STORE","custodian_id":ctx["store"],"delivery_accept_operation_id":"TRACE553.ACCEPT:"+tag+":STORE","quantity":"2","reason":"Own553 damaged units inspection","decision_reference":"DEV553.DAMAGE:"+tag})
  if not ctx.get("denials_before_return"):
   call(shop,"POST",p+"/offer",{"operation_id":"TRACE553.BAD.OFFER:"+tag,"task_id":ctx["trip"],"owner_ware_id":ware,"pallet_type_id":type_id,"condition":"DAMAGED","from_kind":"STORE","from_id":ctx["store"],"to_kind":"VEHICLE","to_id":str(ctx["vehicle"]),"quantity":"2","scan_vehicle":ctx["plate"]},409)
   call(admin,"POST",p+"/writeoff",{"operation_id":"TRACE553.EARLY:"+tag,"damage_operation_id":damage,"writeoff_warehouse_id":ware,"quantity":"2","reason":"Must first return assets","decision_reference":"DEV553.EARLY:"+tag},409)
   ctx["denials_before_return"]=True;save()
  transfer(shop,driver_api,"DAMAGED","STORE",ctx["store"],"VEHICLE",ctx["vehicle"],"BACK",damage)
  transfer(driver_api,admin,"DAMAGED","VEHICLE",ctx["vehicle"],"WAREHOUSE",ware,"WARE",damage)
  if not ctx.get("before_writeoff"):
   q.execute("select sum(QUANTITY)from RRL_TARE_DAMAGE_POSITION where DAMAGE_OPERATION_ID=:damage",damage=damage);assert q.fetchone()==(2,)
   q.execute("select OUTSTANDING_QTY from RRL_TARE_STORE_DEBT where CLAIM_KEY=:damage",damage=damage);assert q.fetchone()==(0,)
   custody=call(admin,"GET",p+f"/warehouses/{ware}/damage-custody")
   row=next(r for r in custody["items"]if r["damage_operation_id"]==damage)
   assert(row["custodian_kind"],row["custodian_id"],row["tracked_quantity"])==("WAREHOUSE",str(ware),"2"),row
   call(admin,"POST",p+"/count",{"operation_id":"TRACE553.BAD.COUNT:"+tag,"owner_ware_id":ware,"pallet_type_id":type_id,"condition":"DAMAGED","observed_quantity":"0","expected_version":2,"reason":"Cannot hide tracked units","decision_reference":"DEV553.BAD:"+tag},409)
   call(shop,"POST",p+"/writeoff",{"operation_id":"TRACE553.SELF:"+tag,"damage_operation_id":damage,"writeoff_warehouse_id":ware,"quantity":"2","reason":"Cannot approve own damage","decision_reference":"DEV553.SELF:"+tag},403)
   ctx["before_writeoff"]=True;save()
  if not ctx.get("race"):
   bodies=[{"operation_id":"TRACE553.WRITE:"+tag+":"+str(i),"damage_operation_id":damage,"writeoff_warehouse_id":ware,"quantity":"2","reason":"Independent returned-damage disposal decision","decision_reference":"DEV553.WRITE:"+tag}for i in range(2)]
   def write(body):
    with httpx.Client(auth=("admin","admin123"),timeout=35)as client:
     r=client.post(base+p+"/writeoff",json=body);return r.status_code,r.json()
   with ThreadPoolExecutor(max_workers=2)as pool:results=list(pool.map(write,bodies))
   assert sorted(x[0]for x in results)==[200,409],results
   winner=next(i for i,r in enumerate(results)if r[0]==200)
   assert call(admin,"POST",p+"/writeoff",bodies[winner])==results[winner][1]
   ctx["race"]={"winner":bodies[winner],"result":results[winner][1]};save()
  q.execute("select sum(QUANTITY)from RRL_TARE_BALANCE where OWNER_WARE_ID=:ware and PALLET_TYPE_ID=:type_id",ware=ware,type_id=type_id);assert q.fetchone()==(0,)
  q.execute("select sum(QUANTITY)from RRL_TARE_DAMAGE_POSITION where DAMAGE_OPERATION_ID=:damage",damage=damage);assert q.fetchone()==(0,)
  q.execute("select count(*)from RRL_TARE_DAMAGE_MOVE where DAMAGE_OPERATION_ID=:damage",damage=damage);assert q.fetchone()==(2,)
  q.execute("select nvl(sum(QUANTITY),0)from RRL_TARE_RESOLUTION where DAMAGE_OPERATION_ID=:damage and RESOLUTION_KIND='WRITE_OFF'",damage=damage);assert q.fetchone()==(2,)
  q.execute("select count(*)from RRL_EVENTS where OPERATION_ID like :prefix",prefix="TRACE553.%"+tag+"%");assert q.fetchone()==(0,)
  ctx["done"]=True;save()
  print("PASS553 GOOD2 -> store DAMAGE2 -> confirmed driver return2 -> warehouse2 -> independent concurrent writeoff2 once. Current tracked positions0; store debt0; two immutable moves; replay/no goods effects.")
 finally:
  original=ctx["original_binding"];current=call(admin,"GET",f'/api/transport/driver-bindings/{ctx["driver"]}')
  call(admin,"PUT",f'/api/transport/driver-bindings/{ctx["driver"]}',{"user_id":original.get("user_id")or ctx["users"][1]["id"],"active":bool(original.get("active",False)),"expected_version":current["binding_version"]})
  if ctx.get("done"):
   for u in ctx["users"]:q.execute("update RUSERS set DELETED=1 where ID=:actor",actor=u["id"])
   c.commit()
