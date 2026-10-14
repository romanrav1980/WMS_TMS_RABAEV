from pathlib import Path
import json
s=Path("scripts/ni042_marked_weighted_case.py").read_text(encoding="utf-8")
s=s.replace('article="QM183"+tag.upper()','article="QM185"+tag.upper()').replace('lot="CASE183.QA:"','lot="CASE185.QA:"')
needle='  print("PASS183 marked actual weighted barcode'
idx=s.index(needle)
s=s[:idx]+'''  # Real calculator on the current moved physical unit, before any shipment/control metadata.
  wire=q.var(oracledb.DB_TYPE_CLOB);wire.setvalue(0,json.dumps({"warehouse":ware,"legs":[{"uid":picked_uid,"article":article,"quantity":"9.8","base_uom":"KG"}]}))
  expected=q.var(oracledb.DB_TYPE_NUMBER);tolerance=q.var(oracledb.DB_TYPE_NUMBER)
  q.callproc("RRL_STOCK_QC_WEIGHT.calculate",[wire,expected,tolerance]);assert abs(expected.getvalue()-10.1)<1e-12 and abs(tolerance.getvalue()-5.05)<1e-12
  wire.setvalue(0,json.dumps({"warehouse":ware,"legs":[{"uid":picked_uid,"article":article,"quantity":"9.7","base_uom":"KG"}]}))
  try:q.callproc("RRL_STOCK_QC_WEIGHT.calculate",[wire,expected,tolerance]);raise AssertionError("Partial physical box mass accepted")
  except oracledb.DatabaseError as exc:assert exc.args[0].code==20887
  q.execute("select CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id",id=case);version=int(q.fetchone()[0])
  closed=request(f"/tasks/{case}/close-pallet",{"operation_id":"QC185.CLOSE:"+str(case),"expected_content_version":version,"reason":"Own185 actual weighted carrier"})
  sid=seq("RRL_SBORKA_PALLETS_SQ");ff=seq("RRL_CUSTOMER_ORDER_FULF_SQ");identifier="QC185.ST:"+tag
  meta("insert into RRL_SBORKA_PALLETS(ID,PALLET_UID,ST_NUMBER,WARE_ID,CONDITION,ADDR)values(:sid,:u,:u,:ware,0,'Own185 existing shipment fixture')",sid=sid,u=identifier,ware=ware)
  meta("insert into RRL_SBORKA_PALLET_ROWS(ID,PALLET_UID,ARTICUL,EI,QUANTITY)values(RRL_SBORKA_PALLET_ROWS_SQ.nextval,:u,:a,'KG',9.8)",u=identifier,a=article)
  meta("insert into RRL_CUSTOMER_ORDER_FULFILLMENT(FULFILLMENT_ID,CUSTOMER_ORDER_ID,LEGACY_SBORKA_PALLET_ID,PALLET_UID,STATUS,FACT_QTY)values(:fid,:ord,:sid,:u,'PLANNED',0)",fid=ff,ord=order,sid=sid,u=identifier)
  from app.modules.inventory.infrastructure.case_shipment_binding import bind_case_shipment
  bind_case_shipment(OracleGateway(),case,identifier,carrier,version,"admin")
  controller="QWC185"+tag;group=controller.upper()
  meta("insert into USER_GROUP(ID,NAME)values(:grp,'Own185 independent mass controller')",grp=group)
  meta("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED)values(:usr,'qa-test-only','Own185 independent controller',:grp,:ware,0)",usr=controller,grp=group,ware=ware)
  meta("insert into RIGHTS(ID,RIGHT1,USER_GROUP,DESCR)select nvl(max(ID),0)+1,'outgoing_pallet_check',:grp,'Own185 current controller'from RIGHTS",grp=group)
  from app.modules.inventory.infrastructure.outgoing_quality import OutgoingQuality
  quality=OutgoingQuality(OracleGateway());status=quality.status(identifier)
  check={"operation_id":"QC185.WEIGHT:"+tag,"quality_kind":"WEIGHT2","gross_weight":"10.1","wood_weight":"0","expected_composition_signature":status["composition_signature"],"scans":body["unit_scans"]}
  result=quality.check(identifier,check,controller);assert result["verified"]==1 and not result["ready"]
  assert quality.check(identifier,check,controller)==result
  print("PASS185 actual physical net9.8/gross10.1 -> independent native QC weight passes without norm/kg policy; actual lightest half5.05/partial mass refused/replay; scan approval separate",identifier,flush=True)
'''+s[idx:]
s=s.replace('PASS183 marked actual weighted barcode','PASS185 marked actual weighted barcode')
print(json.dumps({"scripts/ni051_physical_box_mass_case.py":s},ensure_ascii=True))
