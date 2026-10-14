from pathlib import Path
import json
t=Path("scripts/ni042_warehouse_scale_use_case.py").read_text(encoding="utf-8").replace("188","194")
t=t.replace("from app.config import get_settings","from app.config import get_settings\nfrom app.modules.platform.public import read_oracle_json")
a=t.index('  labels=');b=t.index('  q.execute("select min(CUSTOMER_ID)',a)
t=t[:a]+'''  labels=["(01)04012345678901(3103)008000(21)"+tag+"0","(01)04012345678901(3103)012000(21)"+tag+"1"]
  boxes=[{"barcode":labels[0],"codes":[],"gross_weight_kg":"8.3","volume_m3":"0.024","measurement_reference":"Own194 actual box8"},
         {"barcode":labels[1],"codes":[],"gross_weight_kg":"12.3","volume_m3":"0.036","measurement_reference":"Own194 actual box12"}]
  post("INVENTORY_REGISTER_LOT",{"uid":lot,"cell":src,"article":article,"quantity":"20","expiry_date":"2030-01-01","price":0,"reason":"Own194 actual whole boxes8/12",
    "birth_captures":{lot:{"capture_mode":"WEIGHTED_BOXES","policy_version":1,"weighted_boxes":boxes}}},{"revision_id":revision})
'''+t[b:]
t=t.replace(":article,9.8,'KG'",":article,10,'KG'")
a=t.index('  picking=PickingService()');b=t.index('\n finally:',a)
t=t[:a]+'''  q.execute("select CUSTOMER_ORDER_ROW_ID from RRL_CUSTOMER_ORDER_ROW where CUSTOMER_ORDER_ID=:p_order and ARTICUL=:p_article",p_order=order,p_article=article);row=int(q.fetchone()[0])
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=:p_ware",p_ware=ware);before=q.fetchone();assert before==(20,0)
  path="http://127.0.0.1:8088/api/picking/order-rows/"+str(row)+"/weighted-box-options"
  answer=api.get(path);assert answer.status_code==200,(answer.status_code,answer.text);options=answer.json()
  assert options["requested_order_quantity"]=="10"and options["remaining_row_quantity"]=="10"and options["tolerance_pct"]=="15"
  assert not options["choice_saved"]and options["no_split"]and options["approval_required"]
  assert sorted(x["net_weight_kg"]for x in options["boxes"])==["12","8"]
  assert all(x["exception_required"]and not x["within_tolerance"]and x["measurements_ready"]for x in options["boxes"])
  assert all(x["pallet_identifier"]==lot and x["source_cell"]==src for x in options["boxes"])
  assert api.get(path).json()==options
  try:q.callfunc("RRL_WEIGHT_BOX_PLANNING_READ.snapshot_json",oracledb.DB_TYPE_CLOB,[row,"Q1341a19738325"]);raise AssertionError("Foreign warehouse source exposed")
  except oracledb.DatabaseError as exc:c.rollback();assert exc.args[0].code==20882 and "WARE_FORBIDDEN"in str(exc)
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=:p_ware",p_ware=ware);assert q.fetchone()==before
  print("PASS194 original10/current whole8or12/exact net gross volume/source/version/default15/exception_required/no_split/stable signed read/current foreignWARE403/P20H0 unchanged",options["source_signature"],flush=True)
'''+t[b:]
a=t.index('\nwith oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as done:')
t=t[:a]+"\n"
print(json.dumps({"scripts/ni042_weight_box_planning_read_case.py":t},ensure_ascii=True))
