from pathlib import Path
import json
s=Path("scripts/ni042_direct_receiving_case.py").read_text(encoding="utf-8").replace("199","201")
s=s.replace('"marking_required":False','"marking_required":True').replace('"profiles":[]','"profiles":[{"system_code":"CRPT","profile_code":"TOBACCO","profile_version":"DIR1","scan_mode":"UNIT"},{"system_code":"EGAIS","profile_code":"ALCOHOL","profile_version":"DIR1","scan_mode":"UNIT"}]')
s=s.replace('.text="20"','.text="12"').replace('"quantity":"20"','"quantity":"12"').replace('"gross_weight":"20"','"gross_weight":"12"')
s=s.replace('zip(customers,(12,8))','zip(customers,(5,7))')
s=s.replace('assert q.fetchone()[0]==20','assert q.fetchone()[0]==12').replace('qty==20','qty==12')
s=s.replace('sorted(r[4]for r in rows)==[8,12]','sorted(r[4]for r in rows)==[5,7]')
s=s.replace('assert result["marking_units"]==0','assert result["marking_units"]==12')
anchor=' from app.services.picking_service import PickingService'
before=''' units=[{"unit_id":str(i),"quantity":"1","codes":[
   {"system_code":"CRPT","profile_code":"TOBACCO","code":gtin+tag[:5]+str(i).zfill(2)},
   {"system_code":"EGAIS","profile_code":"ALCOHOL","code":("QA"+tag+str(i)).ljust(68,"X")}]}for i in range(1,13)]
 body["units"]=units;body.pop("product_barcode",None)
'''
assert anchor in s;s=s.replace(anchor,before+anchor)
anchor='  task=result["task_id"]'
i=s.index(anchor);end=s.index('\n',i)
s=s[:end]+'''
  q.execute("select count(*),sum(BASE_QTY)from RRL_WMS_RECEIPT_UNIT where UID_PALLET=:p_uid",p_uid=sscc);assert q.fetchone()==(12,12)
  q.execute("select count(*)from RRL_WMS_RECEIPT_CODE where UID_PALLET=:p_uid",p_uid=sscc);assert q.fetchone()[0]==24
'''+s[end:]
anchor='   path=f"/api/case-pick/tasks/{case}/lines/{line}/confirm"'
before='''   q.execute("select u.UNIT_ID,u.PHYSICAL_UNIT_KEY from RRL_WMS_RECEIPT_UNIT u join RRL_STOCK_RESERVATION r on r.RESERVATION_ID=u.HARD_RESERVATION_ID where r.SOURCE_DOC_TYPE='PICK_WAVE'and r.SOURCE_DOC_ID=:p_wave and r.SOURCE_LINE_ID=(select PICK_TASK_ID from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=:p_line)and r.BASE_QTY>0 order by u.PHYSICAL_UNIT_KEY",p_wave=wave,p_line=line)
   selected=q.fetchall();assert len(selected)==int(quantity)
   scans=[code for unit_id,_ in selected for code in units[int(unit_id)-1]["codes"]]
   payload["unit_scans"]=scans
'''
assert anchor in s;s=s.replace(anchor,before+anchor)
anchor='   from app.services.case_pick_service import CasePickService'
before='''   denied=api.post(base+path,json={**payload,"operation_id":payload["operation_id"]+":EAN","unit_scans":[]});assert denied.status_code==409,(denied.status_code,denied.text)
'''
assert anchor in s;s=s.replace(anchor,before+anchor)
a=s.index('  print("PASS201 actual SAP')
b=s.index('\n',a)
s=s[:a]+'''  q.execute("select count(*)from RRL_WMS_RECEIPT_UNIT u join RRL_CASE_CARRIER_LOT lot on lot.LOT_UID=u.CURRENT_UID join RRL_CASE_PICK_TASK ct on ct.CASE_PICK_TASK_ID=lot.CASE_PICK_TASK_ID where ct.PICK_WAVE_ID=:p_wave",p_wave=wave);assert q.fetchone()[0]==12
  q.execute("select l.CUSTOMER_ORDER_ID,count(*),sum(u.BASE_QTY)from RRL_CASE_CARRIER_LOT lot join RRL_CASE_PICK_LINE l on l.CASE_PICK_LINE_ID=lot.CASE_PICK_LINE_ID join RRL_WMS_RECEIPT_UNIT u on u.CURRENT_UID=lot.LOT_UID where l.PICK_WAVE_ID=:p_wave group by l.CUSTOMER_ORDER_ID order by l.CUSTOMER_ORDER_ID",p_wave=wave);allocated=q.fetchall();assert [tuple(x[1:])for x in allocated]==[(5,5),(7,7)],allocated
  print("PASS201 real SAP12 physical units/24 codes/two WMS profiles/current DIRECT/original stores5+7/exact sourceHARD/unit QR required/EAN-only409/no replenishment/no unit assigned twice/source0/CASE12/replay/no legalACK",article,wave,flush=True)'''+s[b:]
# Native fixture cleanup must enumerate actual remaining physical keys, including returned child lots.
anchor='   counts=[{"uid":uid'
a=s.index(anchor);b=s.index('\n',a)
s=s[:a]+'''   stock_rows=q.fetchall();counts=[]
   for uid,cell,unit,v in stock_rows:
    q.execute("select PHYSICAL_UNIT_KEY from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:p_uid and CURRENT_CELL=:p_cell and STOCK_STATUS='AVAILABLE'",p_uid=uid,p_cell=cell)
    counts.append({"uid":uid,"cell":cell,"article":article,"unit":unit,"quantity":"0","expected_stock_version":int(v),"unit_keys":[x[0]for x in q.fetchall()]})'''+s[b:]
print(json.dumps({"scripts/ni042_marked_direct_receiving_case.py":s},ensure_ascii=True))
