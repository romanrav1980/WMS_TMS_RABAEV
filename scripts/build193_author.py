from pathlib import Path
import json
t=Path("scripts/ni042_order_weight_decision_case.py").read_text(encoding="utf-8").replace("192","193")
t=t.replace("from hashlib import sha256","from hashlib import sha256\nfrom app.modules.platform.public import read_oracle_json") if False else t
a="from app.config import get_settings";t=t.replace(a,a+"\nfrom app.modules.platform.public import read_oracle_json")
a='  print("PASS193 exact9.6/10'
pos=t.index(a)
section='''  q.execute("select CUSTOMER_ORDER_ROW_ID from RRL_CUSTOMER_ORDER_ROW where CUSTOMER_ORDER_ID=:p_order and ARTICUL=:p_article",p_order=order,p_article=article);original_row=int(q.fetchone()[0])
  demand=read_oracle_json(q.callfunc("RRL_STOCK_POOL_READ.line_snapshot_json",oracledb.DB_TYPE_CLOB,[original_row]))
  assert demand["requested_base_quantity"]=="10"and demand["picked_quantity"]=="9.6"and demand["hard_quantity"]=="9.6"
  assert demand["accepted_weight_deviation_quantity"]==".4"or demand["accepted_weight_deviation_quantity"]=="0.4",demand
  assert demand["quantity"]=="0"and demand["quantity_semantics"]=="UNALLOCATED_BASE_AFTER_ACCEPTED_WEIGHT_DEVIATION",demand
  print("PASS193 accepted current deviation.4 suppresses repeat demand; original10/actual9.6/H9.6 remain explicit",flush=True)
'''
t=t[:pos]+section+t[pos:]
a='   q.execute("select RESERVATION_ID from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='
pos=t.index(a)
section='''   if "original_row"in locals():
    reopened=read_oracle_json(q.callfunc("RRL_STOCK_POOL_READ.line_snapshot_json",oracledb.DB_TYPE_CLOB,[original_row]))
    assert reopened["accepted_weight_deviation_quantity"]=="0"and reopened["picked_quantity"]=="0"and reopened["quantity"]=="10",reopened
    q.execute("select STATUS,WEIGHT_DECISION_OPERATION from RRL_CASE_PICK_SHORT where CASE_PICK_SHORT_ID=:p_short",p_short=short_id);assert q.fetchone()==("ACCEPTED",approval["operation_id"])
    print("PASS193 native CASE return removes current waiver/reopens original10, immutable approval retained",flush=True)
'''
t=t[:pos]+section+t[pos:]
print(json.dumps({"scripts/ni042_order_weight_demand_case.py":t},ensure_ascii=True))
