exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
import uuid,httpx
from concurrent.futures import ThreadPoolExecutor
base="http://127.0.0.1:8088/api/inventory/interwarehouse"
with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
 for number in[291,292]:
  p=Path("tmp/context299_"+str(number)+".json");ctx=json.loads(p.read_text())
  body=dict(ctx["metadata"],request_operation_id=ctx["request_operation_id"])
  if "approval_operation_id"not in ctx:
   def send(b):
    with httpx.Client(auth=("admin","admin123"),timeout=30)as h:
     r=h.post(base+"/recovery-approvals",json=b);return b,r.status_code,r.json()
   with ThreadPoolExecutor(max_workers=2)as pool:results=list(pool.map(send,[dict(body,operation_id="IW299.APPROVE:"+uuid.uuid4().hex)for _ in range(2)]))
   assert sorted(x[1]for x in results)==[200,409],results
   win=next(x for x in results if x[1]==200);ctx["approval_operation_id"]=win[0]["operation_id"];ctx["approval_result"]=win[2];p.write_text(json.dumps(ctx,ensure_ascii=False,indent=2),encoding="utf-8")
  r=client.post(base+"/recovery-approvals",json=dict(body,operation_id=ctx["approval_operation_id"]));assert r.status_code==200 and r.json()==ctx["approval_result"],r.text
  r=client.post(base+"/recovery-approvals",json=dict(body,operation_id=ctx["approval_operation_id"],quantity="1"));assert r.status_code==409,r.text
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select count(*)from RRL_INTERWARE_RECOVERY_RECEIPT");assert q.fetchone()==(0,)
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=6667491");assert q.fetchone()==(20,20)
print("PASS299 independent approval ordinary+marked exactlost2/concurrent200-409/replay/collision/no physical receipt or stock birth/protected20-20")
