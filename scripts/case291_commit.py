exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from concurrent.futures import ThreadPoolExecutor
import httpx,copy
ctx=json.loads(Path("tmp/context291.json").read_text(encoding="utf-8"));tag=ctx["tag"]
base="http://127.0.0.1:8088";body=ctx["receipt_body"]
with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
 if "receipt_result"not in ctx:
  bodies=[dict(body,operation_id=ctx["receipt_operation"],plan_operation_id=ctx["plan_operation_id"]),
          dict(body,operation_id="IW291.LOSER:"+tag,plan_operation_id=ctx["plan_operation_id"],receipt_pallet_identifier="IP291.LOSER:"+tag)]
  def send(b):
   with httpx.Client(auth=("admin","admin123"),timeout=30)as session:
    r=session.post(base+"/api/inventory/interwarehouse/receive",json=b);return b,r.status_code,r.json()
  with ThreadPoolExecutor(max_workers=2)as pool:results=list(pool.map(send,bodies))
  assert sorted(r[1]for r in results)==[200,409],results
  winner=next(r for r in results if r[1]==200)
  ctx["actual_receipt_body"]=winner[0];ctx["receipt_operation"]=winner[0]["operation_id"];ctx["receipt_result"]=winner[2]
  Path("tmp/context291.json").write_text(json.dumps(ctx,indent=2),encoding="utf-8")
 repeated=client.post(base+"/api/inventory/interwarehouse/receive",json=ctx["actual_receipt_body"])
 assert repeated.status_code==200 and repeated.json()==ctx["receipt_result"],repeated.text
 changed=client.post(base+"/api/inventory/interwarehouse/receive",json={**ctx["actual_receipt_body"],"quantity":"2"})
 assert changed.status_code==409,changed.text
 custody=client.post(base+"/api/inventory/interwarehouse/release-custody",json={"operation_id":"IW291.CUSTODY:"+tag,"receipt_operation_id":ctx["receipt_operation"]})
 assert custody.status_code==409 and "INTERWARE_UNRESOLVED_PARTIAL_CARRIER_CUSTODY"in custody.text,custody.text
 placed=client.post(base+"/api/inventory/interwarehouse/placement",json={"operation_id":"IW291.PUT:"+tag,"receipt_operation_id":ctx["receipt_operation"]})
 assert placed.status_code==200,placed.text
 ctx["placement_result"]=placed.json()
 Path("tmp/context291.json").write_text(json.dumps(ctx,indent=2),encoding="utf-8")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select ROOT_UID,ORIGINAL_ROOT_UID,BASE_QTY,EXPECTED_BASE_QTY from RRL_INTERWARE_RECEIPT where PLAN_OPERATION_ID=:plan_id",plan_id=ctx["plan_operation_id"])
 rows=q.fetchall();assert len(rows)==1 and rows[0][1:]==(ctx["lot"],1,3),rows
 q.execute("select CUSTODY_RELEASED_AT from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:load_id",load_id=ctx["source_load"]);assert q.fetchone()==(None,)
 q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA=:lot_id",lot_id=ctx["receipt_result"]["pallet_identifier"]);assert q.fetchone()==(1,0)
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=6667491");assert q.fetchone()==(20,20)
print("PASS291 actual concurrent200/409 one receiptP1/newUID/expected3/short2, exactreplay/collision, custodycannotreleaseunreceived2; existingplacementplan created/protected20-20")
