import json
from pathlib import Path
r=Path(__file__).resolve().parents[1];p=r/"scripts/ni033_mixed_wave_fixture.py";s=p.read_text(encoding="utf-8")
start=s.index(' q.execute("select count(*)from RRL_PICK_WAVE')
end=s.index(' task=seq(',start)
s=s[:start]+''' q.execute("select PICK_WAVE_ID from RRL_PICK_WAVE where WAVE_CODE='MIXED172.QA:00cdc0ef51'")
 wave=int(q.fetchone()[0])
 q.execute("select PALLET_TYPE_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=1034");box_type=q.fetchone()[0]
 q.execute("select min(CUSTOMER_ID)from RRL_CUSTOMER");customer=q.fetchone()[0]
 result={"ware":ware,"article":article,"wave":wave,"source_cell":src,"case_cell":pick,"target_cell":gate,"revision":233,"full_uid":"MIXED172.FULL:"+tag,"case_uid":"MIXED172.CASE:"+tag,"shipment":"MIXED172.ST:"+tag,"controller":"QA172_KRO"}
 for key,kind in[("full","FULL_PALLET"),("empty","CASE_PICK")]:
  q.execute("""select wo.CUSTOMER_ORDER_ID,pl.CUSTOMER_ORDER_ROW_ID,wo.PICK_PLAN_ID,pl.PICK_PLAN_LINE_ID,pt.PICK_TASK_ID,wt.PICK_WAVE_TASK_ID
   from RRL_PICK_WAVE_ORDER wo join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_ID=wo.PICK_PLAN_ID
   join RRL_PICK_TASK pt on pt.PICK_PLAN_LINE_ID=pl.PICK_PLAN_LINE_ID
   join RRL_PICK_WAVE_TASK wt on wt.PICK_TASK_ID=pt.PICK_TASK_ID and wt.PICK_WAVE_ID=wo.PICK_WAVE_ID
   where wo.PICK_WAVE_ID=:p_wave and pt.TASK_TYPE=:p_kind""",p_wave=wave,p_kind=kind)
  data=q.fetchall();assert len(data)==1
  result[key]=dict(zip(("order","row","plan","line","pt","wt"),map(int,data[0])))
'''+s[end:]
s=s.replace("RRL_CUSTOMER_ORDER_FUL_SQ","RRL_CUSTOMER_ORDER_FULF_SQ")
print(json.dumps({str(p.relative_to(r)):s}))
