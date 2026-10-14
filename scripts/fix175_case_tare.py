import json
from pathlib import Path
p=Path("scripts/ni041_case_relocation_existing_case.py");s=p.read_text(encoding="utf-8")
s=s.replace('orders=[];plans=[];wave=None;service=PickingService()','orders=[];plans=[];wave=None;service=PickingService();bookings=[];tare_types=set()')
anchor='  for ct,cl,carrier,qty,cell in lines:\n   cases.claim_task'
section="""  api175=httpx.Client(auth=("admin","admin123"),timeout=60)
  def tare_call(path,body):
   response=api175.post("http://127.0.0.1:8088/api/inventory/tare/"+path,json=body)
   assert response.status_code==200,(response.status_code,response.text[:1800]);return response.json()
  def tare_count(tare_type,quantity):
   response=api175.get(f"http://127.0.0.1:8088/api/inventory/tare/warehouses/{ware}/availability")
   assert response.status_code==200
   current=next(x for x in response.json()if x["pallet_type_id"]==tare_type)
   operation="QA175.TARE:"+uuid4().hex
   tare_call("count",{"operation_id":operation,"owner_ware_id":ware,"pallet_type_id":tare_type,"condition":"GOOD","observed_quantity":quantity,"expected_version":current["balance_version"]or 0,"reason":"Owned175 synthetic assembly container fixture","decision_reference":operation})
  for ct,cl,carrier,qty,cell in lines:
   q.execute("select PALLET_TYPE_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:p_id",p_id=int(ct));tare_type=q.fetchone()[0]
   if tare_type not in tare_types:tare_count(tare_type,"2");tare_types.add(tare_type)
   booking="QA175.TARE.BOOK:"+str(ct)
   tare_call("book",{"operation_id":booking,"place_kind":"CASE","place_id":str(ct)});bookings.append(booking)
   cases.claim_task"""
assert anchor in s;s=s.replace(anchor,section)
anchor='   print("Owned wave retained for explicit deferred decision; no fake DONE",wave,flush=True)'
section="""   for booking in bookings:
    tare_call("book-cancel",{"operation_id":booking+".CANCEL","booking_operation_id":booking})
   for tare_type in tare_types:tare_count(tare_type,"0")
   if bookings:
    post("WAVE_EXECUTION_FINISH",{"disposition":"RETURNED_TO_PLANNING","reason":"Owned175 CASE returned, booked tare released; original demand retained"},{"wave_id":wave},"QA175.WAVE.DEFER:"+str(wave))
   print("Owned wave completed only by native deferred decision when eligible",wave,flush=True)"""
assert anchor in s;s=s.replace(anchor,section)
print(json.dumps({str(p):s}))
