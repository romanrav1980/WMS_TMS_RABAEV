exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import httpx
p=Path("tmp/context464.json");ctx=json.loads(p.read_text(encoding="utf-8"))
body=dict(operation_id="IW464.RECEIVE:"+ctx["tag"],plan_operation_id=ctx["plan_operation_id"],scan_pallet=ctx["lot"],scan_cell="IR464"+ctx["tag"],scan_article=ctx["barcode"],article=ctx["article"],quantity="3",base_uom="EA",aggregation_scans=ctx["aggregations"])
with httpx.Client(auth=("admin","admin123"),timeout=35)as client:
 response=client.post("http://127.0.0.1:8088/api/inventory/interwarehouse/receive",json=body)
 assert response.status_code==200,response.text
 result=response.json()
 assert result["physical_unit_count"]==3 and result["regulatory_ack_verified"]is False,result
 repeat=client.post("http://127.0.0.1:8088/api/inventory/interwarehouse/receive",json=body);assert repeat.status_code==200 and repeat.json()==result,repeat.text
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA=:p_uid",p_uid=ctx["lot"]);assert q.fetchone()==(3,0)
 q.execute("select count(*)from RRL_WMS_RECEIPT_CODE where UID_PALLET=:p_uid",p_uid=ctx["lot"]);assert q.fetchone()[0]==6
ctx.update(receive_cell=body["scan_cell"],receipt_body=body,receipt_result=result,receipt_operation=body["operation_id"])
print(json.dumps({str(p):json.dumps(ctx,indent=2)}))
