exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.inventory.infrastructure.labels import ReceiptLabels
from app.oracle_gateway import OracleGateway
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select l.LABEL_ID,l.SSCC,l.STATUS,o.WARE_ID from RRL_RECEIPT_LABEL l join RRL_SAP_SUPPLY_ORDER o on o.ORDER_ID=l.ORDER_ID order by l.LABEL_ID fetch first 1 row only")
 row=q.fetchone()
 if row is None:raise RuntimeError("No existing receiving label fixture; create no new physical stock")
 label,sscc,status,ware=row
 q.execute("""select ID from RUSERS where nvl(DELETED,0)=0 and upper(nvl(trim(USER_GROUP),'NONE'))!='GLOBAL_ADMIN'
 and nvl(WARE_ID,-1)!=:ware and RRL_HAS_WRIGHT(ID,'warehouse_receipt_confirm')=1 order by ID fetch first 1 row only""",ware=ware)
 actor=q.fetchone()
service=ReceiptLabels(OracleGateway())
html=service.document(label,"html","admin");zpl=service.document(label,"zpl","admin")
assert "<"in html and "^XA"in zpl
if actor:
 for command in(lambda:service.document(label,"html",actor[0]),lambda:service.confirm(label,sscc,actor[0])):
  try:command();raise AssertionError("Foreign warehouse should be forbidden")
  except PermissionError:pass
else:
 try:service.document(label,"html","NO_SUCH_LABEL_ACTOR_678");raise AssertionError("Missing actor should be forbidden")
 except PermissionError:pass
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select STATUS from RRL_RECEIPT_LABEL where LABEL_ID=:label_id",label_id=label);assert q.fetchone()[0]==status
print(json.dumps({"status":"PASS","html_zpl_existing_label":True,"foreign_actor_present":bool(actor),"label_status_unchanged":True,"stock_commands":0}))
