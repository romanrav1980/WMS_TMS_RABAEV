exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.finance.infrastructure.day_reviews import DayReviews
from app.modules.finance.contracts import LogisticsCostError
from datetime import date
from uuid import uuid4
svc=DayReviews(OracleGateway());tag=uuid4().hex[:12];peer="INS698_"+tag
ware=5265051;day=date(2026,10,12);zone="Asia/Tbilisi"
ctx=svc.context(ware,day,zone,"admin")
review_body={"warehouse_id":ware,"business_date":day.isoformat(),"timezone_region":zone,"expected_version":ctx["version"],"source_hash":ctx["source_hash"],"reason":"Bounded698 independent inspection declarations; no stock change"}
review=svc.record("DR698:"+tag,review_body,"admin")
body={"review_operation_id":review["operation_id"],"source_hash":ctx["source_hash"],"inspection_role":"WAREHOUSE_CHIEF","observed_empty":True,"note":"Chief observed empty zone; frozen topology evidence remains authoritative"}
op="DI698:"+tag
Path("tmp/context698.json").write_text(json.dumps({"peer":peer,"review":review,"body":body,"operation":op}),encoding="utf-8")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("""declare u RUSERS%rowtype;begin select *into u from RUSERS where ID='admin';u.ID:=:actor;u.WARE_ID:=:ware;u.DELETED:=0;insert into RUSERS values u;end;""",actor=peer,ware=ware);c.commit()
try:
 chief=svc.inspect(op,body,"admin")
 assert svc.inspect(op,body,"admin")==chief
 assert svc.resolve_inspection(op,body,"admin")==chief
 for other_actor,other_op,other_body in [
  ("admin",op,{**body,"note":"Changed immutable operation content"}),
  ("admin",op+".SELF",{**body,"inspection_role":"DISPATCHER"}),
  (peer,op+".DUP",body),
  (peer,op+".STALE",{**body,"inspection_role":"DISPATCHER","source_hash":"0"*64})]:
  try:svc.inspect(other_op,other_body,other_actor)
  except LogisticsCostError as e:assert e.status==409,(e.status,str(e))
  else:raise AssertionError("Rejected conflict was accepted")
 second=svc.inspect(op+".D",{**body,"inspection_role":"DISPATCHER","note":"Dispatcher independent declaration; no automatic closure"},peer)
 value=svc.inspection(review["operation_id"],"admin")
 assert value["paired_independent_declarations"] and value["both_declared_empty"]
 assert not value["day_closed"] and not value["stock_changed"] and not value["external_obligations_closed"]
 assert value["shipping_zone_confirmed_for_frozen_review"]==value["source_shipping_zone_empty_at_review"]
 with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
  q=c.cursor()
  try:q.execute("delete from RRL_DAY_INSPECTION where OPERATION_ID=:op",op=op)
  except oracledb.DatabaseError as e:assert e.args[0].code==20863
  else:raise AssertionError("Immutable history deletion")
  c.rollback()
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
  q.execute("select executions,round(elapsed_time/1000/nullif(executions,0),3),round(buffer_gets/nullif(executions,0),1)from V$SQL where sql_text like '%FROM RRL_DAY_INSPECTION WHERE%' and executions>0 order by last_active_time desc fetch first 4 rows only")
  print("SQL",q.fetchall())
 Path("tmp/result698.json").write_text(json.dumps(value,default=str),encoding="utf-8")
 print("PASS698 independent pair/exact replay/resolve/conflicts/self-signing/immutable history/P20H20/no closure")
finally:
 with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
  c.cursor().execute("update RUSERS set DELETED=1 where ID=:actor",actor=peer);c.commit()
