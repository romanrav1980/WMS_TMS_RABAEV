from pathlib import Path
import json
s=Path("scripts/ni042_weighted_case_existing_case.py").read_text(encoding="utf-8").replace('article="QW182"+tag.upper()','article="QM183"+tag.upper()').replace('lot="CASE182.QA:"','lot="CASE183.QA:"')
s=s.replace("values(:article,1,0,1,'admin')","values(:article,1,1,1,'admin')")
needle='  meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key(\'SKU\',:article)'
idx=s.index(needle)
s=s[:idx]+'''  meta("insert into RRL_SKU_RECEIPT_PROFILE(ARTICUL,SYSTEM_CODE,PROFILE_CODE,PROFILE_VERSION,SCAN_MODE)values(:article,'CRPT','DAIRY','WB1','UNIT')",article=article)
'''+s[idx:]
s=s.replace('{"barcode":v,"codes":[]}for v in labels','{"barcode":v,"codes":[{"system_code":"CRPT","profile_code":"DAIRY","code":"(01)04012345678901(21)"+v.split("(21)")[1]+"(91)TESTKEY(92)TESTSIGNATURE"}],"gross_weight_kg":"10.100","volume_m3":"0.030","measurement_reference":"OWN183:manual declared fixture"}for v in labels')
s=s.replace('"weighted_box_barcode":labels[0]}','"weighted_box_barcode":labels[0],"unit_scans":[{"system_code":"CRPT","profile_code":"DAIRY","code":"(01)04012345678901(21)"+labels[0].split("(21)")[1]+"(91)TESTKEY(92)TESTSIGNATURE"}]}')
s=s.replace('  result=request(f"/tasks/{case}/lines/{line}/weighted-box",body)','''  denied=api.post(base+f"/tasks/{case}/lines/{line}/weighted-box",json={**body,"operation_id":operation+":NOQR","unit_scans":[]});assert denied.status_code==409
  result=request(f"/tasks/{case}/lines/{line}/weighted-box",body)''')
s=s.replace('  print("PASS182 actual weighted barcode', '''  q.execute("select GROSS_WEIGHT_KG,BOX_VOLUME_M3,WEIGHT_LABEL_SCAN from RRL_WMS_RECEIPT_UNIT where HARD_RESERVATION_ID is not null and CURRENT_UID in(select LOT_UID from RRL_CASE_CARRIER_LOT where CASE_PICK_TASK_ID=:id)",id=case);gross,volume,raw=q.fetchone();assert round(gross,3)==10.1 and round(volume,3)==.03 and raw==labels[0]
  preview=api.get("http://127.0.0.1:8088/api/receiving/pallets/"+result["facts"][0]["uid"]+"/composition")
  assert preview.status_code==200,preview.text[:1200]
  assert preview.json()["units"][0]["gross_weight_kg"]=="10.1"
  print("PASS183 marked actual weighted barcode''')
# actual native result facts key uncertain; remove direct preview assumption, use owned carrier-lot lookup.
s=s.replace('  preview=api.get("http://127.0.0.1:8088/api/receiving/pallets/"+result["facts"][0]["uid"]+"/composition")','  q.execute("select LOT_UID from RRL_CASE_CARRIER_LOT where CASE_PICK_TASK_ID=:id",id=case);picked_uid=q.fetchone()[0]\n  preview=api.get("http://127.0.0.1:8088/api/receiving/pallets/"+picked_uid+"/composition")')
print(json.dumps({"scripts/ni042_marked_weighted_case.py":s},ensure_ascii=True))
