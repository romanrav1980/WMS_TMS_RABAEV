exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import httpx
from concurrent.futures import ThreadPoolExecutor
base="http://127.0.0.1:8088/api/inventory/trace-manifests";origin="100007031097593489"
op="AGG462.OPEN:MANIFEST124.BOX1"
body=dict(operation_id=op,system_code="CRPT",profile_code="TOBACCO",code_hash="10385679679c3c81157494df2be36bc8e6bb367bb93d87f9331898ae6a6a4119",origin_pallet_identifier=origin,warehouse_id=10828603,reason_code="OPENED",document_reference="DEV462:physical-first-box-opened")
def post(payload):
 with httpx.Client(auth=("admin","admin123"),timeout=35)as client:
  return client.post(base+"/aggregations/invalidate",json=payload)
with httpx.Client(auth=("admin","admin123"),timeout=35)as client:
 url=base+"/warehouses/10828603/pallets/"+origin+"/aggregations"
 rows=client.get(url);assert rows.status_code==200,rows.text
 assert len(rows.json())==4,rows.text
 with ThreadPoolExecutor(max_workers=2)as pool:responses=list(pool.map(post,[body,body]))
 assert all(r.status_code==200 for r in responses),[r.text for r in responses]
 result=responses[0].json();assert responses[1].json()==result
 assert result["blocked_aggregate_count"]==2 and result["stock_changed"]is False,result
 conflict=post({**body,"reason_code":"REPACKED"});assert conflict.status_code==409,conflict.text
 rows=client.get(url);assert rows.status_code==200,rows.text
 assert sum(x["local_state"]=="INVALIDATED"for x in rows.json())==2,rows.text
 assert all(x["government_ack_verified"]is False and x["scan_admission_verified"]is False for x in rows.json())
 other=client.get(base+"/warehouses/6667491/pallets/"+origin+"/aggregations");assert other.status_code==404,other.text
 bad=post({**body,"operation_id":"AGG462.BAD:WARE","warehouse_id":6667491});assert bad.status_code==409,bad.text
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select count(*)from RRL_TRACE_AGG_INVALIDATION where OPERATION_ID=:op",op=op);assert q.fetchone()[0]==1
 q.execute("select count(*)from RRL_TRACE_AGG_BLOCK where INVALIDATION_OPERATION_ID=:op",op=op);assert q.fetchone()[0]==2
 q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA=:p_uid",p_uid=origin);assert q.fetchone()==(3,0)
 q.execute("select count(*)from RRL_EVENTS where UID_POLETA=:p_uid",p_uid=origin);assert q.fetchone()[0]==1
 q.execute("select count(*)from RRL_WMS_RECEIPT_CODE where UID_PALLET=:p_uid",p_uid=origin);assert q.fetchone()[0]==6
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=6667491");assert q.fetchone()==(20,20)
Path("tmp/context462.json").write_text(json.dumps(dict(body=body,result=result,rows=rows.json()),indent=2),encoding="utf-8")
print("PASS462 HTTP concurrent same-op 200/200 one fact/two affected aggregates/one journal; replay/conflict/custody; P3H0/event1/codes6/protected20 unchanged")
