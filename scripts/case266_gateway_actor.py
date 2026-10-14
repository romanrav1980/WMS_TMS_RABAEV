exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.workers.sap_artmas_worker import process_batch
from app.modules.fulfillment.infrastructure.store_orders import StoreOrders
from app.oracle_gateway import OracleGateway
from uuid import uuid4
ctx=json.loads(Path("tmp/context264.json").read_text(encoding="utf-8"));root=Path("tmp/gateway266")/uuid4().hex
(root/"inbox").mkdir(parents=True);(root/"inbox"/"same-source.xml").write_bytes(ctx["raw_closed"].encode())
out=process_batch(root,20,0,"store")
assert len(out)==1 and out[0].get("customer_order_id")==ctx["held"]["customer_order_id"]and out[0]["admission_status"]=="PENDING_CALENDAR",out
assert len(list((root/"archive").glob("*.xml")))==1 and len(list((root/"archive").glob("*.result.json")))==1
assert not list((root/"inbox").glob("*.xml"))and not list((root/"error").glob("*.xml"))
svc=StoreOrders(OracleGateway())
try:svc.get(ctx["held"]["customer_order_id"],"SAP_FILE_GATEWAY")
except PermissionError:pass
else:raise AssertionError("Integrationwide grant leaked to view")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select RRL_HAS_WRIGHT(ID,'sap_article_import'),RRL_HAS_WRIGHT(ID,'sap_supply_import'),RRL_HAS_WRIGHT(ID,'sap_store_order_import'),RRL_HAS_WRIGHT(ID,'sap_store_all_ware'),RRL_HAS_WRIGHT(ID,'warehouse_receipt_confirm'),RRL_HAS_WRIGHT(ID,'wms_admin_login'),RRL_HAS_WRIGHT(ID,'customer_order_import')from RUSERS where ID='SAP_FILE_GATEWAY'and DELETED=0")
 assert q.fetchone()==(1,1,1,1,0,0,0)
 q.execute("select count(*)from RRL_SAP_STORE_ORDER");assert q.fetchone()==(2,)
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
print("PASS266 realexistingworker privateXMLdirectory/currentserviceactor/explicitSAPwideScope/replayold264held source onearchive-result/source2/no shell-receipt-ST rights/currenthumanview denied/protected20-20/no goods or demandbirth")
