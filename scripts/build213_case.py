from pathlib import Path
import json
a=Path("scripts/ni042_marked_small_mass_case.py").read_text(encoding="utf-8")
b=Path("scripts/ni052_standalone_case_unload_case.py").read_text(encoding="utf-8")
prefix=a[:a.index("  current_tree=hu_tree()")]
suffix=b[b.index('  packing("HU_DETACH","SMALL212.STANDALONE:'): ]
s=(prefix+suffix).replace("211","213").replace("212","213")
s=s.replace('gross_weight_kg":"0.4"','gross_weight_kg":"0.45"').replace('==(6,6)','==(7,7)').replace("==6","==7").replace("==-6","==-7")
needle='  print("PASS213 standalone'
i=s.find(needle)
# Additional exact physical unit/code evidence after actual accepted unload.
anchor='  q.execute("select sum(BASE_QTY)from RRL_EVENTS where OPERATION_ID=:p_op",p_op=load_id);assert q.fetchone()[0]==-7'
extra="""
  q.execute("select count(*),sum(BASE_QTY),count(distinct HARD_RESERVATION_ID)from RRL_WMS_RECEIPT_UNIT u join RRL_CASE_CARRIER_LOT lot on lot.LOT_UID=u.CURRENT_UID where lot.CASE_PICK_TASK_ID=:p_case and STOCK_STATUS='AVAILABLE'and HARD_RESERVATION_ID is not null",p_case=case);assert q.fetchone()==(7,7,1)
  q.execute("select count(*)from RRL_WMS_RECEIPT_CODE code join RRL_WMS_RECEIPT_UNIT u on code.UID_PALLET=u.UID_PALLET and code.UNIT_ID=u.UNIT_ID join RRL_CASE_CARRIER_LOT lot on lot.LOT_UID=u.CURRENT_UID where lot.CASE_PICK_TASK_ID=:p_case and STOCK_STATUS='AVAILABLE'",p_case=case);assert q.fetchone()[0]==14
  print("PASS213 restored exact7 original physical units/14 CRPT+EGAIS codes/HARD same original wave owner/no government state inferred",flush=True)
"""
assert anchor in s;s=s.replace(anchor,anchor+extra)
print(json.dumps({"scripts/ni052_marked_case_unload_case.py":s},ensure_ascii=True))
