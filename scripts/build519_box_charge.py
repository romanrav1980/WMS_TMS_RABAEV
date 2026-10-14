import json
from pathlib import Path
v=Path("scripts/ni052_loading_case.py").read_text(encoding="utf-8")
needle='  ship_body["loading_context"]=loading_context'
assert v.count(needle)==1
v=v.replace(needle,'''  loading_context["measurements"]["gross_weight_kg"]="3"
  loading_context["physical_boxes"]=[{"box_uid":box,"scan_box":box,"content_version":tree(box)["nodes"][0]["version"],
    "origin":"MANUAL_CONFIRMED","gross_weight_kg":"2","measurement_ref":"DEV519.BOX:"+tag}]
  clock=tree(box)["nodes"][0]["packing_start"]
  assert clock["warehouse"]==ware and clock["instant"]
  ship_body["loading_context"]=loading_context''')
needle=' finally:\n  q.execute("select PARENT_UID'
assert v.count(needle)==1
v=v.replace(needle,'''  from app.modules.finance.infrastructure.logistics_costs import LogisticsCosts
  finance=LogisticsCosts(OracleGateway())
  finance.configure_period("POLICY519:"+tag,ware,"CASE_ASSEMBLY","UTC",0,"Own519 first actual BOX packing date","DEV519.UTC","admin")
  preview=finance.assembly_period(trip,ware,"UTC","admin")
  assert preview["complete"]and preview["lines"][0]["source_kind"]=="BOX_PACKING",preview
  day=preview["business_dates"][0]
  finance.rate(ware,"GEL","2.25",day,0,"Own519 physical BOX source","DEV519.RATE","admin")
  charged=finance.calculate("COST519:"+tag,trip,ware,"GEL","admin")
  assert charged["amount"]=="2.25"and charged["lines"][0]["rate_date"]==day,charged
  assert finance.calculate("COST519:"+tag,trip,ware,"GEL","admin")==charged
  q.execute("select RESULT_JSON from RRL_STOCK_OPERATION where OPERATION_ID=:op",op=shipop)
  wire=q.fetchone()[0];wire=wire.read()if hasattr(wire,"read")else wire
  Path("tmp/context519.json").write_text(json.dumps({"tag":tag,"warehouse":ware,"trip":trip,"box":box,"load":shipop,"clock":clock,"preview":preview,"charge":charged,"shipping_body":ship_body}),encoding="utf-8")
  print("PASS519 actual ordinary BOX first scanned packing ->frozen LOAD/DEPART ->shared native assembly date ->BOX1 charge2.25/replay/no second goods effect",flush=True)
 finally:
  q.execute("select PARENT_UID''')
print(json.dumps({"scripts/case519_ordinary_box_charge.py":v}))
