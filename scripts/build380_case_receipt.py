from pathlib import Path
import json
t=Path("scripts/ni053_small_case_weight_receipt_case.py").read_text(encoding="utf-8").replace("208","380")
t=t.replace('import io,sys','import io,sys,json')
t=t.replace('load=sys.argv[1]if len(sys.argv)>1 else "SMALL207.LOAD:5ab68dd7"','load=json.loads(Path("tmp/context376.json").read_text())["load_operation_id"]')
t=t.replace('and not preview["requires_marked_recipient_flow"]','and preview["requires_marked_recipient_flow"]')
t=t.replace('"1.4"','"1.45"').replace('"0.2"','"0.225"').replace('"0.4"','"0.45"').replace('"1.199999999"','"1.224999999"').replace('"1.2"','"1.225"').replace('"-0.2"','"-0.225"').replace('==6','==7')
needle='  photos=[]'
t=t.replace(needle,'''  assert preview["marked_unit_control"]["supported"]and preview["marked_unit_control"]["physical_unit_count"]==7 and preview["marked_unit_control"]["expected_scan_count"]==14,preview
  source=json.loads(Path("tmp/context376.json").read_text())
  scans=[dict(code,disposition="ACCEPTED")for code in source["case_scans"]]
  photos=[]''')
t=t.replace('body["scale_capture_key"]=capture("1.225")','''body["scale_capture_key"]=capture("1.225")
  missing={**body,"operation_id":"STORE380.MISSING:"+tag,"scans":scans[:-1]}
  denied=call(shop,"POST","/api/delivery/store-receipts/confirm",missing,status=409)
  assert "STORE_MARK_EXACT_PROFILE_COVERAGE_REQUIRED"in denied["detail"]["message"],denied
  body["scans"]=scans''')
# Weight trial also needs complete profile coverage, otherwise it fails before the weight gate.
t=t.replace('refused=call(shop,','body["scans"]=scans\n  refused=call(shop,')
needle='  print("PASS380 existing departed'
at=t.index(needle)
t=t[:at]+'''  q.execute("select count(*),sum(BASE_QTY)from RRL_STORE_RECEIPT_UNIT where OPERATION_ID=:op",op=body["operation_id"]);assert q.fetchone()==(7,7)
  q.execute("select CUSTOMER_ORDER_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id",id=source["case"]);order=q.fetchone()[0]
  from app.modules.delivery.infrastructure.order_delivery import OrderDelivery
  from app.oracle_gateway import OracleGateway
  delivery=OrderDelivery(OracleGateway()).get(int(order));assert delivery["quantities"][0]["accepted"]=="7",delivery
  Path("tmp/context380.json").write_text(json.dumps({"source":source,"receipt_body":body,"result":result,"order_delivery":delivery,"receiver_id":receiver,"actors_retired_after_case":True},indent=2),encoding="utf-8")
'''+t[at:]
print(json.dumps({"scripts/case380_marked_small_receipt.py":t}))
