from pathlib import Path
import json
p=Path("scripts/case840_second_arrival.py")
s=p.read_text(encoding="utf-8")
anchor='  ReplenishmentContinuation(gateway,sync_existing_wave_tasks).reconcile(ware,"admin")'
diagnostic="""  q.execute("select SOURCE_DOC_ID,SOURCE_LINE_ID,UID_PALLET,CELL,BASE_QTY,STATUS from RRL_STOCK_RESERVATION where ARTICUL=:a and RESERVATION_KIND='HARD'and BASE_QTY>0 order by RESERVATION_ID",a=article)
  print("PRE_NEXT_OWNERS",q.fetchall(),flush=True)
  q.execute("select rt.PICK_WAVE_REPLENISH_TASK_ID,rt.STATUS,rt.SOURCE_RESERVATION_ID,rt.TARGET_CELL_CODE,RRL_STOCK_REPL_NEED.remaining_for_task(rt.PICK_TASK_ID,rt.TARGET_CELL_CODE),RRL_STOCK_REPL_CAPACITY.remaining_base_quantity(rt.TARGET_CELL_CODE,rt.ARTICUL,rt.PICK_WAVE_REPLENISH_TASK_ID),RRL_STOCK_REPL_ADMISSION.mode_for(rt.PICK_WAVE_REPLENISH_TASK_ID),w.STATUS from RRL_PICK_WAVE_REPLENISH_TASK rt join RRL_PICK_WAVE w on w.PICK_WAVE_ID=rt.PICK_WAVE_ID where rt.PARENT_REPLENISH_TASK_ID=:id",id=rt)
  print("PRE_NEXT_ROW",q.fetchall(),flush=True)
  q.execute("select sr.RESERVATION_ID,RRL_STOCK_REPL_SHARED.allowed(sr.UID_PALLET,sr.CELL,:dst,:ware,sr.RESERVATION_ID),RRL_STOCK_ELIGIBILITY.reason(sr.UID_PALLET,sr.CELL,:ware,0,0,0,'REPLENISH',sr.RESERVATION_ID,sr.ARTICUL)from RRL_STOCK_RESERVATION sr where sr.UID_PALLET=:uid and sr.BASE_QTY>0 and sr.RESERVATION_KIND='HARD'",dst=dst,ware=ware,uid=extra)
  print("PRE_NEXT_ADMISSION",q.fetchall(),flush=True)
"""
assert anchor in s;s=s.replace(anchor,diagnostic+anchor,1)
s=s.replace("  second=q.fetchall();assert len(second)==1,second","  second=q.fetchall();print('NEXT_RECONCILED',second,flush=True);assert len(second)==1,second")
print(json.dumps({str(p):s},ensure_ascii=True))
