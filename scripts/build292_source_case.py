from pathlib import Path
import json
s=Path("scripts/ni061_marked_source_case.py").read_text(encoding="utf-8").replace("225","292")
s=s.replace('cfg=get_settings();tag=uuid4().hex[:10];','''cfg=get_settings()
if Path("tmp/context292.json").exists():raise SystemExit("Source292 already created; continue exact retained context")
tag=uuid4().hex[:10];''')
needle='  print("PASS292'
start=s.index(needle);end=s.index('\n finally:',start)
s=s[:start]+'''  context={"tag":tag,"article":article,"lot":lot,"warehouse":ware,"target_warehouse":target,"source_load":shipop,"plan_operation_id":plan_body["operation_id"],"source_trip":trip,"target_trip":target_trip,"inbound":inbound,"outbound":outbound,"barcode":gtin,"source_quantity":"3","units":units}
  Path("tmp/context292.json").write_text(json.dumps(context,indent=2),encoding="utf-8")
  print("SOURCE292 marked3/6codes/sourceP0/frozenplan; no hardware/gov ACK")
'''+s[end:]
needle=' try:\n  ctx=api'
assert needle in s;s=s.replace(needle,''' Path("tmp/source292_progress.json").write_text(json.dumps({"tag":tag,"article":article,"lot":lot,"warehouse":ware,"src":src,"dst":dst,"shipcell":shipcell,"task":task,"st":st,"st_uid":st_uid,"order":order,"wave":wave,"revision":revision,"trip":trip,"vehicle":vehicle,"dock":dock,"barcode":gtin,"units":units,"plan":plan,"pl":pl,"pt":pt,"ff":ff,"customer":customer,"driver":driver,"trtype":trtype},indent=2),encoding="utf-8")
 try:
  ctx=api''',1)
print(json.dumps({"scripts/source292_marked_case.py":s},ensure_ascii=True))
