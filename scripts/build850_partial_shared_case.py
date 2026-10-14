from pathlib import Path
import json
s=Path("scripts/case840_second_arrival.py").read_text(encoding="utf-8")
s=s.replace("tmp/context840.json","tmp/context850.json").replace("SEQ840.","SEQ850.")
s=s.replace('"quantity":"8","expiry_date":"2030-01-01","price":0,"reason":"Second physical source for same existing owner"','"quantity":"12","expiry_date":"2030-01-01","price":0,"reason":"Second physical source for same existing owner"')
anchor='  meta("update RRL_CELLS set BLOCKED_FOR_REMAINS=0 where CELL=:c",c=dst)'
extra="""  q.execute("select PICK_TASK_ID,CUSTOMER_ORDER_ID,PICK_PLAN_ID,PICK_PLAN_LINE_ID from RRL_PICK_TASK where PICK_PLAN_ID=:plan",plan=plans[1]);pt2,co2,pp2,pl2=q.fetchone()
  q.execute("select RESERVATION_ID from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE'and SOURCE_DOC_ID=:w and SOURCE_LINE_ID=:pt and RESERVATION_KIND='HARD'and BASE_QTY>0 and STATUS in('ACTIVE','ALLOCATED','PICKING')",w=wave,pt=pt2)
  for(row_id,)in q.fetchall():post("RESERVATION_RELEASE",{"reason":"Private partial shared-owner split"},{"reservation_id":int(row_id)})
  second_ids=[]
  for source_uid in (lot,extra):
   result=post("RESERVATION_CREATE",{"reservation_kind":"HARD","reservation_scope":"QTY","reservation_domain":"PICKING","source_doc_type":"PICK_WAVE","source_doc_id":wave,"source_line_id":int(pt2),"customer_id":customer,"customer_order_id":int(co2),"pick_plan_id":int(pp2),"pick_plan_line_id":int(pl2),"qty":"4","unit_code":"EA","articul":article,"uid_pallet":source_uid,"cell":src,"ware_id":ware},{"type":"STOCK_RESERVATION"})
   second_ids.append(result["reservation_id"])
  q.execute("select PICK_WAVE_REPLENISH_TASK_ID from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_ID=:w and PICK_TASK_ID=:pt",w=wave,pt=pt2);rt2=int(q.fetchone()[0])
  meta("update RRL_PICK_WAVE_REPLENISH_TASK set SOURCE_RESERVATION_ID=:rid where PICK_WAVE_REPLENISH_TASK_ID=:rt",rid=second_ids[0],rt=rt2)
"""
assert anchor in s;s=s.replace(anchor,extra+anchor,1)
s=s.replace("(20,14)","(20,10)").replace("(20,10)\n  q.execute","(20,6)\n  q.execute")
# Keep the capacity-refusal pre-rebind sourceH10 expectation.
s=s.replace('assert q.fetchone()==(20,6)\n  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=extra,c=src);assert q.fetchone()==(8,6)\n  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=other,c=dst);assert q.fetchone()==(4,0)','assert q.fetchone()==(20,10)\n  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=extra,c=src);assert q.fetchone()==(12,10)\n  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=other,c=dst);assert q.fetchone()==(4,0)')
s=s.replace("(8,6)","(12,10)")
# The first move carries both owners' retained2+4.
s=s.replace("u=lot,c=dst);assert q.fetchone()==(20,10)","u=lot,c=dst);assert q.fetchone()==(20,6)")
s=s.replace(":a,10,'EA')",":a,14,'EA')").replace("assert q.fetchone()==(10,)","assert q.fetchone()==(14,)")
s=s.replace("q2==8","q2==12").replace('"fact_qty":"8"','"fact_qty":"12"')
s=s.replace('  second=q.fetchall();print(\'NEXT_RECONCILED\',second,flush=True);assert len(second)==1,second','''  second=q.fetchall();assert len(second)==1,second
  q.execute("select SOURCE_RESERVATION_ID,STATUS,DEMAND_BASE_QTY from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_REPLENISH_TASK_ID=:id",id=rt2)
  other_progress=q.fetchone();assert other_progress[2]==4 and other_progress[0] is not None,other_progress''')
s=s.replace('"stage":"TWO_PHYSICAL_ARRIVALS_TARGET_OWNER12_OTHER8_THIRD10"','"partial_shared_rt":rt2,"stage":"PARTIAL_SHARED_RESUMED_OWNER12_OTHER8_THIRD14"')
s=s.replace("PASS840 capacity refusal unchanged; target4+own6/6 ->two original whole20/8 arrivals; owner12/other8/third10 preserved; exact replay; cleanup follows","PASS850 partially covered shared owner requeued4; original next6 + shared whole12 second arrival; original12/other8/third14 preserved; same replay; cleanup follows")
print(json.dumps({"scripts/case850_partial_shared.py":s},ensure_ascii=True))
