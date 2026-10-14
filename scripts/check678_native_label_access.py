exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.inventory.infrastructure.labels import ReceiptLabels
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("set transaction read only")
 q.execute("select WARE_ID from RRL_SAP_SUPPLY_ORDER order by ORDER_ID fetch first 1 row only");ware=int(q.fetchone()[0])
 ReceiptLabels._scope(q,ware,"admin")
 try:ReceiptLabels._scope(q,ware,"NO_SUCH_LABEL_ACTOR_678");raise AssertionError("Expected current actor rejection")
 except PermissionError:pass
 q.execute("select count(*)from RRL_RECEIPT_LABEL");labels=int(q.fetchone()[0])
print(json.dumps({"status":"PASS","native_scope_admin_allowed":True,"unknown_actor_forbidden":True,"existing_labels":labels,"html_and_used_replay_verified":False,"stock_changed":False}))
