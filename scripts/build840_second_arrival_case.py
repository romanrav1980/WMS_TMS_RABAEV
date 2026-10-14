from pathlib import Path
import json
s=Path("scripts/case835_sequential_sources.py").read_text(encoding="utf-8")
s=s.replace("tmp/context835.json","tmp/context840.json").replace("SEQ835.MOVE:","SEQ840.MOVE:")
# Capacity refusal must leave all original reservations untouched.
anchor='  reserve_wave_sources(gateway,wave,"admin",[rt])'
start=s.index(anchor,s.index('meta("update RRL_CELLS set BLOCKED_FOR_REMAINS=0'))
capacity="""  meta("update RRL_PICK_FACE set MAX_VOLUME=0.1 where PICK_FACE_ID=:id",id=face)
  service._enrich_replenishment_settings(wave,"admin");service._refresh_replenishment_deficit(wave,"admin")
  reserve_wave_sources(gateway,wave,"admin",[rt])
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=lot,c=src);assert q.fetchone()==(20,14)
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=extra,c=src);assert q.fetchone()==(8,6)
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=other,c=dst);assert q.fetchone()==(4,0)
  meta("update RRL_PICK_FACE set MAX_VOLUME=0.5 where PICK_FACE_ID=:id",id=face)
  service._enrich_replenishment_settings(wave,"admin");service._refresh_replenishment_deficit(wave,"admin")
"""
s=s[:start]+capacity+s[start:]
anchor='  ReplenishmentContinuation(gateway,sync_existing_wave_tasks).reconcile(ware,"admin")'
extra="""  # A separate existing order/wave owns the ten free arrived units. This forces
  # the first owner's remaining six to come from its second physical source.
  third_order=seq("RRL_CUSTOMER_ORDER_SQ");orders.append(third_order)
  meta("insert into RRL_CUSTOMER_ORDER(CUSTOMER_ORDER_ID,ORDER_NO,CUSTOMER_ID,WARE_ID) values(:id,:no,:c,:w)",id=third_order,no=lot+"THIRD",c=customer,w=ware)
  meta("insert into RRL_CUSTOMER_ORDER_ROW(CUSTOMER_ORDER_ROW_ID,CUSTOMER_ORDER_ID,LINE_NO,ARTICUL,ORDER_QTY,UNIT_CODE) values(RRL_CUSTOMER_ORDER_ROW_SQ.nextval,:o,1,:a,10,'EA')",o=third_order,a=article)
  third_plan=service.create_plan(PickingPlanCreateRequest(customer_order_id=third_order,created_by="admin"));plans.append(third_plan)
  third_wave=service.create_wave(PickWaveCreateRequest(wave_code=lot+"T",ware_id=ware,created_by="admin"))
  service.add_wave_plan(third_wave,PickWaveAddPlanRequest(pick_plan_id=third_plan,created_by="admin"))
  service.preview_wave(third_wave,PickWaveActionRequest(updated_by="admin"))
  post("WAVE_LAUNCH",{},{ "wave_id":third_wave},"SEQ840.THIRD:"+tag)
  q.execute("select nvl(sum(BASE_QTY),0)from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE'and SOURCE_DOC_ID=:w and RESERVATION_KIND='HARD'and STATUS in('ACTIVE','ALLOCATED','PICKING')",w=third_wave);assert q.fetchone()==(10,)
"""
assert anchor in s;s=s.replace(anchor,extra+anchor,1)
anchor='  q.execute("select nvl(sum(BASE_QTY),0)from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE=\'PICK_WAVE\'and SOURCE_DOC_ID=:w and SOURCE_LINE_ID=:pt and CELL=:dst'
start=s.index(anchor)
second="""  q.execute("select TASK_ID,UID_PALLET,FROM_CELL,TO_CELL,QTY from RRL_WAREHOUSE_TASK where TASK_SOURCE='WAVE'and SOURCE_DOC_ID=:w and SOURCE_TASK_ID=:rt and TASK_TYPE='REPLENISHMENT'and STATUS not in('DONE','CANCELLED')",w=wave,rt=int(next_rows[0][0]))
  second=q.fetchall();assert len(second)==1,second
  t2,u2,c2,d2,q2=second[0];assert u2==extra and q2==8,second
  moved2=post("TASK_COMPLETE",{"fact_qty":"8","scanned_pallet":u2,"scanned_from_cell":c2,"scanned_to_cell":d2},{"task_id":int(t2)},"SEQ840.SECOND:"+tag)
  assert post("TASK_COMPLETE",{"fact_qty":"8","scanned_pallet":u2,"scanned_from_cell":c2,"scanned_to_cell":d2},{"task_id":int(t2)},"SEQ840.SECOND:"+tag)==moved2
"""
s=s[:start]+second+s[start:]
s=s.replace("assert q.fetchone()==(8,0)","assert q.fetchone()==(0,0)",1)
s=s.replace('"stage":"CURRENT_TARGET_OWNER12_OTHER8"','"second_task":int(t2),"third_wave":int(third_wave),"stage":"TWO_PHYSICAL_ARRIVALS_TARGET_OWNER12_OTHER8_THIRD10"')
s=s.replace("PASS835 target4 + own6/6 -> own source2/6 -> whole20 receipt -> original next demand6 -> target own12/other8; same replay, untouched source8/H0; cleanup follows","PASS840 capacity refusal unchanged; target4+own6/6 ->two original whole20/8 arrivals; owner12/other8/third10 preserved; exact replay; cleanup follows")
# Every wave in this unique new private warehouse belongs to this one scenario.
s=s.replace("where SOURCE_DOC_TYPE='PICK_WAVE' and SOURCE_DOC_ID=:w and STATUS in('ACTIVE','ALLOCATED','PICKING') and BASE_QTY>0\",w=wave)","where SOURCE_DOC_TYPE='PICK_WAVE' and SOURCE_DOC_ID in(select PICK_WAVE_ID from RRL_PICK_WAVE where WARE_ID=:w) and STATUS in('ACTIVE','ALLOCATED','PICKING') and BASE_QTY>0\",w=ware)")
s=s.replace("where TASK_SOURCE='WAVE' and SOURCE_DOC_ID=:w and STATUS not in('DONE','CANCELLED')\",w=wave)","where TASK_SOURCE='WAVE' and SOURCE_DOC_ID in(select PICK_WAVE_ID from RRL_PICK_WAVE where WARE_ID=:w) and STATUS not in('DONE','CANCELLED')\",w=ware)")
s=s.replace("where PICK_WAVE_ID=:w and STATUS not in('DONE','CANCELLED')\",w=wave)","where PICK_WAVE_ID in(select PICK_WAVE_ID from RRL_PICK_WAVE where WARE_ID=:w) and STATUS not in('DONE','CANCELLED')\",w=ware)")
s=s.replace("update RRL_PICK_WAVE set STATUS='DONE' where PICK_WAVE_ID=:w\",w=wave)","update RRL_PICK_WAVE set STATUS='DONE' where WARE_ID=:w\",w=ware)")
print(json.dumps({"scripts/case840_second_arrival.py":s},ensure_ascii=True))
