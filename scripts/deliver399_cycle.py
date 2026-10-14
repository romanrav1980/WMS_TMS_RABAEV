exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.transport_composition import build_transport_loading
from app.delivery_composition import build_delivery_receipt
from app.modules.delivery.infrastructure.order_delivery import OrderDelivery
from app.oracle_gateway import OracleGateway
p=Path("tmp/context398.json");saved=json.loads(p.read_text());source=saved["source"];loading=build_transport_loading();receiver=build_delivery_receipt()
def save():p.write_text(json.dumps(saved,indent=2),encoding="utf-8")
if "depart"not in saved:saved["depart"]=loading.depart("IW399.DEPART:"+source["tag"],source["target_trip"],"admin");save()
address=saved["parts"][0]["onward"]["final_address"]
if "store_receipt"not in saved:
 preview=receiver.preview(saved["load_operation_id"],address,"admin");saved["store_preview"]=preview;save()
 assert preview["marked_unit_control"]["physical_unit_count"]==2
 meta=dict(scan_place=preview["root_scan_identifier"],expected_composition_signature=preview["composition_signature"],before_cameras=True,observations=[],case_note="",scale_capture_key="",photo_ids=[],weight_act_confirmed=False,scans=[dict(code,disposition="ACCEPTED")for part in saved["parts"]for code in part["scans"]])
 op="STORE399.RECEIVE:"+source["tag"];result=receiver.confirm(op,saved["load_operation_id"],address,meta,"admin");saved.update(store_receipt=result,store_operation_id=op,store_metadata=meta);save()
assert receiver.confirm(saved["store_operation_id"],saved["load_operation_id"],address,saved["store_metadata"],"admin")==saved["store_receipt"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();st=saved["parts"][0]["onward"]["source_st_id"]
 q.execute("select CUSTOMER_ORDER_ID from RRL_CUSTOMER_ORDER_FULFILLMENT where LEGACY_SBORKA_PALLET_ID=:st",st=st);order=q.fetchone()[0]
 q.execute("select sum(FACT_QTY),count(*)from RRL_CUSTOMER_ORDER_FULFILLMENT where CUSTOMER_ORDER_ID=:id and STATUS='SHIPPED'",id=order);assert q.fetchone()==(2,1)
 snapshot=OrderDelivery(OracleGateway()).get(order);saved["order_delivery"]=snapshot
 quantity=snapshot["quantities"][0];assert quantity["accepted"]=="2"and quantity["unreceived"]=="0"and quantity["historical_transport_shortage"]=="1"and quantity["recovered_transport_quantity"]=="1"and quantity["confirmed_transport_shortage"]=="0",snapshot
 q.execute("select count(*)from RRL_WMS_RECEIPT_CODE where UID_PALLET=:lot",lot=source["old_birth_uid"]);assert q.fetchone()[0]==6
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),BUFFER_GETS,substr(SQL_TEXT,1,150)from V$SQL
 where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and SQL_TEXT not like '%V$SQL%'and(SQL_TEXT like 'INSERT INTO RRL_IW_RECOVERY_DISPATCH%'or SQL_TEXT like 'select%RRL_IW_RECOVERY%'or SQL_TEXT like 'SELECT%RRL_IW_RECOVERY%')
 order by ELAPSED_TIME desc fetch first 6 rows only""");saved["slow_sql"]=q.fetchall()
save()
print("PASS393 originalaccepted1+recovered1+1 inoneTOP/3ST/6oldQR/depart+STOREbuyer3/originalFF3once/history2-found2-net0/P20H20")
print(json.dumps(saved["slow_sql"],default=str))
