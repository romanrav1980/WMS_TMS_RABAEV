from pathlib import Path
import json
s=Path("scripts/ni042_weight_box_capture_case.py").read_text(encoding="utf-8")
s=s.replace('article="QW179"+tag.upper()','article="QW183"+tag.upper()').replace('uid="WEIGHT179:"+tag','uid="WEIGHT183:"+tag').replace('009800','004250').replace('"9.8"','"4.25"').replace('"9.7"','"4.24"').replace('WEIGHT179.','WEIGHT183.').replace('9.8KG','4.25KG')
s=s.replace('marking_required=False,serialized_weight_boxes=True,profiles=[]','marking_required=True,serialized_weight_boxes=True,profiles=[{"system_code":"CRPT","profile_code":"DAIRY","profile_version":"WB1","scan_mode":"UNIT"}]')
s=s.replace('and not policy["marking_required"]','and policy["marking_required"]')
s=s.replace('"codes":[]','"codes":[{"system_code":"CRPT","profile_code":"DAIRY","code":"(01)"+gtin+"(21)"+tag+"(91)TESTKEY(92)TESTSIGNATURE"}],"gross_weight_kg":"4.500","volume_m3":"0.030","measurement_reference":"OWN183:manual software fixture"')
s=s.replace(');assert q.fetchone()[0]==0\n  for candidate',');assert q.fetchone()[0]==1\n  q.execute("select GROSS_WEIGHT_KG,BOX_VOLUME_M3,MEASUREMENT_REFERENCE,WEIGHT_LABEL_SCAN from RRL_WMS_RECEIPT_UNIT where UID_PALLET=:p_uid",p_uid=uid);gross,volume,reference,raw=q.fetchone();assert Decimal(str(gross))==Decimal("4.5")and Decimal(str(volume))==Decimal(".03")and reference and raw==scan\n  for candidate')
s=s.replace('no government codes','one applicable CRPT code/no legal ACK').replace('codes0','codes1').replace('PASS179','PASS183')
print(json.dumps({"scripts/ni042_weight_box_dimensions_case.py":s},ensure_ascii=True))
