raise SystemExit("Retired authoring draft: use checked-in final SQL/fixture sources; do not regenerate over verified fixes.")
from pathlib import Path
import json
s=Path("scripts/ni042_issued_route_case.py").read_text(encoding="utf-8").replace("209","210")
s=s.replace('s=get_settings();tag=sys.argv[1]if len(sys.argv)>1 else uuid4().hex[:10]','conflict="--conflict"in sys.argv\ns=get_settings();tag=uuid4().hex[:10]')
needle=' try:\n  post("INVENTORY_REGISTER_LOT"'
extra=''' for sku,stage in ((article,"TOP"if conflict else"BASE"),(article2,"BASE"if conflict else"TOP")):
  r=api.put("http://127.0.0.1:8088/api/finished-goods/skus/"+sku+"/receiving-policy",json={"expected_version":0,"marking_required":False,"stack_stage":stage,"profiles":[]})
  assert r.status_code==200,(r.status_code,r.text[:1200]);assert r.json()["stack_stage"]==stage
'''
assert needle in s;s=s.replace(needle,extra+needle)
needle='  # Future slotting changes do not rewrite the issued route.'
extra='''  q.execute("select STACK_STAGE,STACK_POLICY_VERSION from RRL_CASE_PICK_LINE where CASE_PICK_TASK_ID=:id order by PICK_SEQUENCE",id=case)
  issued=q.fetchall();assert issued==([("TOP",1),("BASE",1)]if conflict else[("BASE",1),("TOP",1)]),issued
  for sku,stage in ((article,"BASE"if conflict else"TOP"),(article2,"TOP"if conflict else"BASE")):
   r=api.put("http://127.0.0.1:8088/api/finished-goods/skus/"+sku+"/receiving-policy",json={"expected_version":1,"marking_required":False,"stack_stage":stage,"profiles":[]})
   assert r.status_code==200,(r.status_code,r.text[:1200])
  # An old client changes unrelated policy without clearing the new stage.
  r=api.put("http://127.0.0.1:8088/api/finished-goods/skus/"+article+"/receiving-policy",json={"expected_version":2,"marking_required":False,"profiles":[]})
  assert r.status_code==200 and r.json()["stack_stage"]==("BASE"if conflict else"TOP"),r.text[:1200]
  q.execute("select STACK_STAGE,STACK_POLICY_VERSION from RRL_CASE_PICK_LINE where CASE_PICK_TASK_ID=:id order by PICK_SEQUENCE",id=case);assert q.fetchall()==issued
  try:q.execute("update RRL_CASE_PICK_LINE set STACK_STAGE='MAIN'where CASE_PICK_LINE_ID=:id",id=line);raise AssertionError("Issued stage rewritten")
  except oracledb.DatabaseError as exc:c.rollback();assert exc.args[0].code==20863
'''
s=s.replace(needle,extra+needle)
start=s.index('  operation="CASE.HTTP210:"');end=s.index('\n finally:',start);positive=s[start:end]
s=s[:start]+'''  if conflict:
   bad={"operation_id":"CASE210.CONFLICT:"+str(case),"fact_qty":"1","scan_cell":cell,"scan_container":carrier,"scan_product":article}
   r=api.post(base+f"/tasks/{case}/lines/{line}/confirm",json=bad)
   assert r.status_code==409 and "CASE_STACK_ROUTE_CONFLICT"in r.text,(r.status_code,r.text[:1500])
   q.execute("select nvl(sum(PICKED_QTY),0)from RRL_CASE_PICK_LINE where CASE_PICK_TASK_ID=:id",id=case);assert q.fetchone()[0]==0
   print("PASS210 incompatible issued TOP then BASE refused before first stock; future SKU changes do not rewrite issued stages",case,flush=True)
  else:
'''+ '\n'.join(' '+x for x in positive.splitlines())+s[end:]
s=s.replace('    if lots:post("CASE_CARRIER_RETURN",{"destinations":destinations,','    post("CASE_CARRIER_RETURN",{"allow_empty":not bool(lots),"destinations":destinations,')
a=s.index('   try:post("WAVE_CANCEL"');b=s.index('  if booking is not None:',a);s=s[:a]+s[b:]
needle='  q.execute("select r.UID_POLETA,r.CELL,r.BASE_UOM'
s=s.replace(needle,'  if wave is not None:post("WAVE_EXECUTION_FINISH",{"disposition":"RETURNED_TO_PLANNING","reason":"Own210 returned fixture leaves original demand"},{"wave_id":wave})\n'+needle)
s=s.replace('   print("PASS210 distinct physical cells','   print("PASS210 BASE before TOP/frozen policy1/future swapped policies preserved/old client retains stage/raw rewrite20863/distinct physical cells')
print(json.dumps({"scripts/ni042_stacking_stage_case.py":s},ensure_ascii=True))
