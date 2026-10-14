from pathlib import Path
import json
s=Path("scripts/ni033_case_http_close_flow.py").read_text(encoding="utf-8")
s=s.replace('article="QC167"+tag.upper()','article="QW182"+tag.upper()')
s=s.replace('lot="CASE167.QA:"+tag+', 'lot="CASE182.QA:"+tag+')
s=s.replace('barcode="BC167"+tag','barcode="04012345678901"')
s=s.replace("x.ABC_GROUP:='A';","x.ABC_GROUP:='A';x.TYPE_W:=3;x.UNIT_TYPE:='KG';")
old='  meta("insert into RRL_STOCK_UOM_CONVERSION'
a=s.index(old);b=s.index('\n  meta("insert into RRL_STOCK_POLICY_GUARD',a)
s=s[:a]+'''  meta("insert into RRL_STOCK_UOM_CONVERSION(ARTICUL,INPUT_UOM,BASE_UOM,POLICY_VERSION,NUMERATOR,DENOMINATOR,BASE_SCALE,PROVENANCE)values(:article,'KG','KG',1,1,1,6,'Own182 exact weighted CASE')",article=article)
  meta("insert into RRL_SKU_RECEIPT_POLICY(ARTICUL,POLICY_VERSION,MARKING_REQUIRED,SERIALIZED_WEIGHT_BOXES,UPDATED_BY)values(:article,1,0,1,'admin')",article=article)'''+s[b:]
# Correct synthetic barcode check digit explicitly; old barcode has invalid checksum.
s=s.replace('barcode="04012345678901"','barcode="04012345678904"')
a=s.index(' def post(');b=s.index(' def request(',a)
s=s[:a]+''' def post(kind,metadata,source,op=None):
  from app.modules.inventory.contracts_stock import StockCommand
  from app.modules.inventory.infrastructure.stock_posting_uow import StockPosting
  return StockPosting().post(StockCommand(operation_id=op or "QA182:"+uuid4().hex,command_type=kind,actor="admin",source=source,metadata=metadata,lines=()))
'''+s[b:]
s=s.replace('  post("INVENTORY_REGISTER_LOT",{"uid":lot,"cell":src,"article":article,"quantity":"2","expiry_date":"2030-01-01","price":0,"reason":"Own167 isolated real CASE API"},{"revision_id":revision})','''  labels=["(01)04012345678904(3103)009800(21)"+tag+str(i)for i in range(2)]
  post("INVENTORY_REGISTER_LOT",{"uid":lot,"cell":src,"article":article,"quantity":"19.6","expiry_date":"2030-01-01","price":0,"reason":"Own182 two serialized weight boxes","birth_captures":{lot:{"capture_mode":"WEIGHTED_BOXES","policy_version":1,"weighted_boxes":[{"barcode":v,"codes":[]}for v in labels]}}},{"revision_id":revision})''')
s=s.replace(",1,'EA')\",order_id=order",",9.8,'KG')\",order_id=order")
s=s.replace('operation="CASE.HTTP167:"+str(case)','operation="CASE.WEIGHT182:"+str(case)')
s=s.replace('  body={"operation_id":operation,"fact_qty":"1","scan_cell":cell,"scan_container":carrier,"scan_product":article,"offline_event_id":operation}','  body={"operation_id":operation,"scan_cell":cell,"scan_container":carrier,"weighted_box_barcode":labels[0]}')
s=s.replace('/lines/{line}/confirm','/lines/{line}/weighted-box')
s=s.replace('json={**body,"fact_qty":"2"}','json={**body,"weighted_box_barcode":labels[1]}')
a=s.index('  q.execute("select STATUS,CLOSED_AT,CONTENT_VERSION');b=s.index(' finally:',a)
# The inner finally belongs to old close fault injection; remove through outer cleanup marker.
b=s.index(' finally:\n  if wave is not None:',a)
s=s[:a]+'''  q.execute("select PICKED_QTY from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=:id",id=line);assert str(q.fetchone()[0])=="9.8"
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=:ware",ware=ware);p,h=q.fetchone();assert round(p,1)==19.6 and round(h,1)==9.8
  print("PASS182 actual weighted barcode -> existing CASE_CONFIRM9.8KG/one physical box/replay no second movement/changed barcode409/source total19.6 H9.8",operation,flush=True)
'''+s[b:]
# Close the wave only after the native carrier return and tare release.
a=s.index('   try:post("WAVE_CANCEL"');b=s.index('  if booking is not None:',a)
s=s[:a]+s[b:]
s=s.replace('  q.execute("select r.UID_POLETA,r.CELL,r.BASE_UOM,r.STOCK_VERSION', '''  if wave is not None:
   post("WAVE_EXECUTION_FINISH",{"disposition":"RETURNED_TO_PLANNING","reason":"Owned182 native carrier return/tare release; demand remains"},{"wave_id":wave})
  def physical_keys(uid,cell):
   q.execute("select PHYSICAL_UNIT_KEY from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:u and CURRENT_CELL=:c and STOCK_STATUS='AVAILABLE'",u=uid,c=cell);return [r[0]for r in q.fetchall()]
  q.execute("select r.UID_POLETA,r.CELL,r.BASE_UOM,r.STOCK_VERSION''')
s=s.replace('"unit_keys":[]}for uid,cell,unit,version in q.fetchall()]','"unit_keys":physical_keys(uid,cell)}for uid,cell,unit,version in q.fetchall()]')
# Avoid manual SOFT mutation; existing native finish owns completion.
s=s.replace('  for plan in plans:meta("update RRL_PICK_RESERVATION set RESERVATION_STATUS=\'RELEASED\'where PICK_PLAN_ID=:id and RESERVATION_STATUS=\'ACTIVE\'",id=plan)\n','')
print(json.dumps({"scripts/ni042_weighted_case_existing_case.py":s},ensure_ascii=True))
