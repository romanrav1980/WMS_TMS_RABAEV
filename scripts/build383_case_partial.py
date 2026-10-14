from pathlib import Path
import json
t=Path("scripts/case380_marked_small_receipt.py").read_text(encoding="utf-8").replace("380","383")
t=t.replace('load=json.loads(Path("tmp/context376.json").read_text())["load_operation_id"]','load="SMALL211.LOAD:8258e0ab"')
a=t.index('  source=json.loads(Path("tmp/context376.json")');b=t.index('  photos=[]',a)
t=t[:a]+'''  from app.modules.platform.public import read_oracle_json
  source={"case":1112,"load_operation_id":load}
  q.execute("select LOT_UID from RRL_CASE_CARRIER_LOT where CASE_PICK_TASK_ID=1112");lot=q.fetchone()[0]
  q.execute("select PHYSICAL_UNIT_KEY,UNIT_ID,UID_PALLET from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:lot and STOCK_STATUS='ISSUED'order by UNIT_ID",lot=lot);members=q.fetchall();assert len(members)==7
  scans=[]
  for index,(key,unit_id,birth)in enumerate(members[:5]):
   disposition="ACCEPTED"if index<3 else "REFUSED"if index==3 else "DAMAGED"
   q.execute("select SYSTEM_CODE,RAW_CODE,PROFILES_JSON from RRL_WMS_RECEIPT_CODE where UID_PALLET=:birth and UNIT_ID=:unit_id order by SYSTEM_CODE",birth=birth,unit_id=unit_id)
   for system,raw,profiles in q.fetchall():
    code=raw.read()if hasattr(raw,"read")else raw
    for profile in read_oracle_json(profiles):scans.append(dict(system_code=system,profile_code=profile["profile"],code=code,disposition=disposition))
  assert len(scans)==10
'''+t[b:]
a=t.index('  body={"operation_id":');b=t.index('  Path("tmp/progress383.json")',a)
t=t[:a]+'''  body={"operation_id":"STORE383.RECEIPT:"+tag,"load_operation_id":load,"store_address":address,"scan_place":preview["root_scan_identifier"],"expected_composition_signature":preview["composition_signature"],"before_cameras":True,"photo_ids":photos,"scale_capture_key":capture("1.45"),"scans":scans,
        "observations":[{"lot_uid":lot,"accepted":"3","missing":"2","refused":"1","damaged":"1","extra":"0"}],"case_note":"Own synthetic CASE partial receipt: three accepted, two absent, one refused, one damaged"}
  wrong=[dict(x)for x in scans];wrong[1]["disposition"]="REFUSED"
  denied=call(shop,"POST","/api/delivery/store-receipts/confirm",{**body,"operation_id":"STORE383.CONFLICT:"+tag,"scans":wrong},status=409)
  assert "STORE_MARK_ONE_UNIT_DISPOSITION_REQUIRED"in denied["detail"]["message"],denied
  from app.modules.inventory.public import StockCommand,normalize_unit_scan_codes
  from app.modules.platform.public import read_oracle_json
  meta={key:value for key,value in body.items()if key not in("operation_id","load_operation_id","store_address","scans")}
  meta["unit_scans"]=normalize_unit_scan_codes(scans)
  trial="STORE383.ROLL:"+tag
  wire=StockCommand(operation_id=trial,command_type="STORE_RECEIPT",actor=receiver,source={"load_operation_id":load,"store_address":address},metadata=meta,lines=()).canonical_json()
  c.commit();out=q.var(oracledb.DB_TYPE_CLOB)
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[wire,receiver,out,None])
   if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
   q.execute("select count(*),sum(BASE_QTY)from RRL_STORE_RECEIPT_UNIT where OPERATION_ID=:op",op=trial);assert q.fetchone()==(7,7)
  finally:c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
  q.execute("select count(*)from RRL_STORE_RECEIPT_FACT where LOAD_OPERATION_ID=:op",op=load);assert q.fetchone()[0]==0
'''+t[b:]
t=t.replace('result["status"]=="ACCEPTED"','result["status"]=="PARTIALLY_ACCEPTED"').replace('result["weight"]["delta_kg"]=="-0.225"','result["weight"]["delta_kg"]=="0"').replace('for x in result["accepted_lines"])==7','for x in result["accepted_lines"])==3').replace('delivery["quantities"][0]["accepted"]=="7"','delivery["quantities"][0]["accepted"]=="3"')
needle='  Path("tmp/context383.json")'
at=t.index(needle)
t=t[:at]+'''  q.execute("select UNIT_DISPOSITION,count(*),sum(BASE_QTY)from RRL_STORE_RECEIPT_UNIT where OPERATION_ID=:op group by UNIT_DISPOSITION order by UNIT_DISPOSITION",op=body["operation_id"]);assert q.fetchall()==[("ACCEPTED",3,3),("DAMAGED",1,1),("MISSING",2,2),("REFUSED",1,1)]
'''+t[at:]
t=t.replace('PASS383 markedCASE7/.450-.100=.350 +outer1=1.45/14oldQR/nonadmin3views/synthetic1.225/.225inclusive/epsilon-and-profile refusals/accepted7/replay/outbox1/no stock/no GovACK','PASS383 actual oldmarkedCASE7 ->accepted3/missing2/refused1/damaged1/10QR of5present/oneunitconflict denied/nativewhole rollback/nonadmin3photos/replay/oneoutbox/no stock/no GovACK')
print(json.dumps({"scripts/case383_partial_marked_case.py":t}))
