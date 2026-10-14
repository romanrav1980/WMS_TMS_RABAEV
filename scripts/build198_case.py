from pathlib import Path
import json
s=Path("scripts/ni042_weight_unit_pin_case.py").read_text(encoding="utf-8").replace("QW197","QW198").replace("CASE197.QA","CASE198.QA").replace("WEIGHT197.CHOICE","WEIGHT198.CHOICE").replace("QA197","QA198").replace("CASE.WEIGHT197","CASE.WEIGHT198")
anchor='  from fastapi import HTTPException'
before='''  def demand():
   return read_oracle_json(q.callfunc("RRL_STOCK_POOL_READ.line_snapshot_json",oracledb.DB_TYPE_CLOB,[row]))
  pending=demand()
  assert pending["requested_base_quantity"]=="10"and pending["quantity"]=="0"and pending["weight_choice_pending_quantity"]=="10",pending
  assert pending["accepted_weight_deviation_quantity"]=="0"
'''
assert anchor in s;s=s.replace(anchor,before+anchor)
anchor='  q.execute("select PALLET_TYPE_ID'
before='''  secured=demand()
  assert secured["quantity"]=="0"and secured["weight_choice_pending_quantity"]==str(max(0,10-selected)),secured
  assert secured["accepted_weight_deviation_quantity"]=="0"
'''
assert anchor in s;s=s.replace(anchor,before+anchor)
anchor='  print("PASS197'
idx=s.index(anchor)
s=s[:idx]+'''  fulfilled=demand()
  assert fulfilled["requested_base_quantity"]=="10"and fulfilled["quantity"]=="0",fulfilled
  assert fulfilled["weight_choice_pending_quantity"]=="0"and fulfilled["accepted_weight_deviation_quantity"]==str(max(0,10-selected)),fulfilled
  assert PickingService().create_plan(PickingPlanCreateRequest(customer_order_id=order,created_by="admin"))==plan
  print("PASS198 pending SOFT/HARD original demand excluded once/actual selected box completed/current accepted gap/original10 retained/no duplicate plan",fulfilled,flush=True)
'''+s[idx:]
anchor='  if booking is not None:'
assert anchor in s;s=s.replace(anchor,'''  returned=demand()
  assert returned["requested_base_quantity"]=="10"and returned["quantity"]=="10",returned
  assert returned["weight_choice_pending_quantity"]=="0"and returned["accepted_weight_deviation_quantity"]=="0",returned
  print("PASS198 returned CASE/PT invalidates waiver and pending/original10 reopens/immutable choice history retained",flush=True)
'''+anchor)
print(json.dumps({"scripts/ni042_weight_choice_demand_case.py":s},ensure_ascii=True))
