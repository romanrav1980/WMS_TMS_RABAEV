exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from contextlib import contextmanager
from app.modules.inventory.infrastructure.interwarehouse_group_read import InterwarehouseGroupRead
from app.modules.inventory.contracts_store_returns import StoreReturnReceiveError
class ReadGateway:
 @contextmanager
 def transaction(self,label):
  with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
   c.call_timeout=10000
   try:yield c.cursor()
   finally:c.rollback()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select TARGET_WARE_ID,count(*)from RRL_IW_GROUP_PLAN group by TARGET_WARE_ID having count(*)>=1 order by count(*)desc fetch first 1 row only")
 source=q.fetchone()
 if source is None:raise RuntimeError("Need existing existing group source; no source factory permitted")
ware=int(source[0]);service=InterwarehouseGroupRead(ReadGateway())
full=service.queue(ware,"admin")
assert len(full)>=1
first=service.queue(ware,"admin",1)
second=service.queue(ware,"admin",1,first[-1]["operation_id"])
assert [x["operation_id"]for x in first+second]==[x["operation_id"]for x in full[:2]]
seen=[];cursor=None
for _ in range(201):
 page=service.queue(ware,"admin",10,cursor)
 seen.extend(x["operation_id"]for x in page)
 if len(page)<10:break
 cursor=page[-1]["operation_id"]
assert len(seen)==len(set(seen))and seen[:len(full)]==[x["operation_id"]for x in full]
for size,after in [(0,None),(201,None),(1,"NO_SUCH_GROUP_CURSOR_663")]:
 try:service.queue(ware,"admin",size,after);raise AssertionError("Expected rejection")
 except StoreReturnReceiveError as e:assert e.status==422
print(json.dumps({"status":"PASS","existing_sources":int(source[1]),"enumerated":len(seen),"distinct":len(set(seen)),"stock_changed":False,"invalid_cursor_rejected":True}))
