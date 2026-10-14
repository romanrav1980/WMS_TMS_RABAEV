exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.delivery.infrastructure.store_returns import StoreReturns
from app.oracle_gateway import OracleGateway
import httpx
service=StoreReturns(OracleGateway(),lambda *args:None)
source="STORE.RECEIPT:cdbf4c0962"
ready=service.reuse_preview(source,1,"24","admin")
assert ready["source_eligible"]and not ready["currently_approvable"]and ready["available_for_approval"]=="0",ready
assert ready["source_proof"]["box_count"]=="1"and ready["source_proof"]["box_base_quantity"]=="24"
partial=service.reuse_preview(source,1,"12","admin")
assert not partial["source_eligible"]and partial["source_reason"]=="RETURN_REUSE_FULL_BOX_BASE_QUANTITY_CONFLICT",partial
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select CANONICAL_REQUEST from RRL_STOCK_OPERATION where OPERATION_ID='RET231.LEGACY:13508027ed'")
 from app.modules.platform.public import read_oracle_json
 old=read_oracle_json(q.fetchone()[0]);original=old["source"]
 legacy=service.reuse_preview(original["receipt_operation_id"],original["line_no"],"1","admin")
 assert not legacy["source_eligible"]and legacy["source_reason"]=="RETURN_REUSE_ORIGINAL_VERIFIED_BATCH_GOOD_BOX_REQUIRED",legacy
 try:service.reuse_preview(source,1,"24","SAP_FILE_GATEWAY")
 except Exception as e:assert getattr(e,"status",None)==403
 else:raise AssertionError("Gateway approval reader access")
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 q.execute("""select executions,round(elapsed_time/1000/nullif(executions,0),3),buffer_gets
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and executions>0 and SQL_TEXT not like '%V$SQL%'
 and SQL_TEXT like '%RRL_SAP_PALLET_RECEIPT%'order by last_active_time desc fetch first 3 rows only""");print("SQL290_MS",q.fetchall())
with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
 r=client.get("http://127.0.0.1:8088/api/delivery/store-returns/"+source+"/reuse-preview",params={"line_no":1,"quantity":"24"})
 assert r.status_code==200 and r.json()["source_eligible"]and not r.json()["currently_approvable"],r.text
print("PASS290 actualexistingSAPsourceBOX24 positive sourceproof/remaining0 distinct, BOX12 refused, legacybatch refused/gateway403/currentHTTP readonly/noqty/P20H20")
