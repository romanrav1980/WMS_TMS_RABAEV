raise SystemExit("Retired authoring draft: use checked-in final SQL/fixture sources; do not regenerate over verified fixes.")
from pathlib import Path
import json
s=Path("scripts/ni042_case_mass_manifest_case.py").read_text(encoding="utf-8").replace("207","211")
s=s.replace('"marking_required":False,"serialized_weight_boxes":False,"profiles":[]','"marking_required":True,"serialized_weight_boxes":False,"profiles":[{"system_code":"CRPT","profile_code":"TOBACCO","profile_version":"DIR1","scan_mode":"UNIT"},{"system_code":"EGAIS","profile_code":"ALCOHOL","profile_version":"DIR1","scan_mode":"UNIT"}]')
s=s.replace('.text="20"','.text="12"').replace('"quantity":"20"','"quantity":"12"').replace('"gross_weight":"20"','"gross_weight":"12"').replace('qty==20','qty==12')
s=s.replace('for customer,quantity in zip(customers,(6,)):','for customer,quantity in zip(customers,(7,)):')
s=s.replace('==6','==7').replace('==[6]','==[7]').replace('==(6,6)','==(7,7)').replace('"quantity":"6"','"quantity":"7"').replace('==(14,0)','==(5,0)')
s=s.replace('assert result["marking_units"]==0','assert result["marking_units"]==12')
s=s.replace('21161011','20261011').replace('2110-01-01','2030-01-01')
needle=' from app.services.picking_service import PickingService'
extra=''' units=[{"unit_id":str(i),"quantity":"1","codes":[
   {"system_code":"CRPT","profile_code":"TOBACCO","code":gtin+tag[:5]+str(i).zfill(2)},
   {"system_code":"EGAIS","profile_code":"ALCOHOL","code":("QA"+tag+str(i)).ljust(68,"X")}]}for i in range(1,13)]
 body["units"]=units;body.pop("product_barcode",None)
'''
assert needle in s;s=s.replace(needle,extra+needle)
needle='   path=f"/api/case-pick/tasks/{case}/lines/{line}/confirm"'
extra='''   q.execute("select u.UNIT_ID,u.PHYSICAL_UNIT_KEY from RRL_WMS_RECEIPT_UNIT u join RRL_STOCK_RESERVATION r on r.RESERVATION_ID=u.HARD_RESERVATION_ID where r.SOURCE_DOC_TYPE='PICK_WAVE'and r.SOURCE_DOC_ID=:p_wave and r.SOURCE_LINE_ID=(select PICK_TASK_ID from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=:p_line)and r.BASE_QTY>0 order by u.PHYSICAL_UNIT_KEY",p_wave=wave,p_line=line)
   selected=q.fetchall();assert len(selected)==7
   scans=[code for unit_id,_ in selected for code in units[int(unit_id)-1]["codes"]]
   payload["unit_scans"]=scans
'''
assert needle in s;s=s.replace(needle,extra+needle)
s=s.replace('"0.400"','"0.450"').replace('"0.300"','"0.350"').replace('"0.4"','"0.45"').replace('"0.3"','"0.35"').replace('Decimal(".4")','Decimal(".45")').replace('Decimal(".3")','Decimal(".35")').replace('"1.4"','"1.45"').replace('"0.2"','"0.225"')
needle='  final_path="/api/outgoing-quality/"+identifier+"/final-weight"'
extra='''  scan_body={"operation_id":"SMALL211.SCAN:"+tag,"error_count":0,"scans":scans,"expected_composition_signature":before["composition_signature"]}
  scan_path="/api/outgoing-quality/"+identifier+"/scan"
  denied=qc_gateway.post(base+scan_path,json={**scan_body,"operation_id":"SMALL211.SCAN.BAD:"+tag,"scans":scans[:-1]})
  assert denied.status_code==409,(denied.status_code,denied.text[:1400])
  scan_result=qc_gateway.post(base+scan_path,json=scan_body);assert scan_result.status_code==200,(scan_result.status_code,scan_result.text[:1700])
  assert qc_gateway.post(base+scan_path,json=scan_body).json()==scan_result.json()
'''
assert needle in s;s=s.replace(needle,extra+needle)
needle='  box=preview["physical_boxes"][0]'
extra='''  assert preview["requires_marked_recipient_flow"]
  q.execute("select count(*),sum(BASE_QTY)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:p_uid and STOCK_STATUS='AVAILABLE'",p_uid=sscc);assert q.fetchone()==(5,5)
  q.execute("select count(*)from RRL_WMS_RECEIPT_CODE c join RRL_WMS_RECEIPT_UNIT u on u.UID_PALLET=c.UID_PALLET and u.UNIT_ID=c.UNIT_ID where u.CURRENT_UID=:p_uid and u.STOCK_STATUS='AVAILABLE'",p_uid=sscc);assert q.fetchone()[0]==10
  print("PASS211 marked small CASE actual7 physical/14 CRPT+EGAIS codes, source5/10 codes, independent exact QR scan+final .450-.100=.350, own control retained inHU/load, marked-store ordinary bypass remains blocked, no legal aggregation ACK",article,op,flush=True)
'''
s=s.replace(needle,extra+needle)
s=s.replace('assert q.fetchone()==(6,6)','assert q.fetchone()==(7,7)')
s=s.replace('"quantity":"6"','"quantity":"7"')
print(json.dumps({"scripts/ni042_marked_small_mass_case.py":s},ensure_ascii=True))
