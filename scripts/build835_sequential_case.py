from pathlib import Path
import json
s=Path("scripts/case632_multi_binding_partial.py").read_text(encoding="utf-8")
s=s.replace('"quantity":"8","expiry_date":"2030-01-01","price":0,"reason":"Existing target stock for multi-binding replacement"','"quantity":"4","expiry_date":"2030-01-01","price":0,"reason":"Existing target stock for sequential replacement"')
s=s.replace('assert q.fetchone()==(20,8)','assert q.fetchone()==(20,10)')
s=s.replace('assert q.fetchone()==(8,4)','assert q.fetchone()==(8,6)')
s=s.replace('assert q.fetchone()==(8,8)','assert q.fetchone()==(4,4)')
s=s.replace('tmp/context632.json','tmp/context835.json')
s=s.replace('"status":"REBIND_PASS"','"status":"SEQUENTIAL_REBIND_PASS"')
start=s.index('  print("PASS632')
end=s.index('\n finally:',start)
body="""  q.execute("select SOURCE_RESERVATION_ID,QTY,DEMAND_BASE_QTY,PALLET_UID from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_REPLENISH_TASK_ID=:rt",rt=rt)
  assert q.fetchone()==(ids[0],20,2,lot),"First retained whole source was not selected"
  from app.modules.resources.public import sync_existing_wave_tasks
  reserve_wave_sources(gateway,wave,"admin")
  sync_existing_wave_tasks(gateway,wave,"admin")
  q.execute("select TASK_ID,UID_PALLET,FROM_CELL,TO_CELL,QTY from RRL_WAREHOUSE_TASK where TASK_SOURCE='WAVE'and SOURCE_DOC_ID=:w and TASK_TYPE='REPLENISHMENT'and STATUS not in('DONE','CANCELLED')",w=wave)
  physical=q.fetchall();assert len(physical)==1,physical
  tid,puid,pfrom,pto,pqty=physical[0];assert puid==lot and pqty==20,physical
  moved=post("TASK_COMPLETE",{"fact_qty":"20","scanned_pallet":puid,"scanned_from_cell":pfrom,"scanned_to_cell":pto},{"task_id":int(tid)},"SEQ835.MOVE:"+tag)
  assert post("TASK_COMPLETE",{"fact_qty":"20","scanned_pallet":puid,"scanned_from_cell":pfrom,"scanned_to_cell":pto},{"task_id":int(tid)},"SEQ835.MOVE:"+tag)==moved
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=lot,c=dst);assert q.fetchone()==(20,10)
  q.execute("select PICK_WAVE_REPLENISH_TASK_ID,DEMAND_BASE_QTY,STATUS from RRL_PICK_WAVE_REPLENISH_TASK where PARENT_REPLENISH_TASK_ID=:rt",rt=rt)
  next_rows=q.fetchall();assert len(next_rows)==1 and next_rows[0][1]==6,next_rows
  from app.modules.inventory.infrastructure.replenishment_continuation import ReplenishmentContinuation
  ReplenishmentContinuation(gateway,sync_existing_wave_tasks).reconcile(ware,"admin")
  q.execute("select nvl(sum(BASE_QTY),0)from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE'and SOURCE_DOC_ID=:w and SOURCE_LINE_ID=:pt and CELL=:dst and RESERVATION_KIND='HARD'and STATUS in('ACTIVE','ALLOCATED','PICKING')",w=wave,pt=pt,dst=dst);assert q.fetchone()==(12,)
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=extra,c=src);assert q.fetchone()==(8,0)
  q.execute("select nvl(sum(BASE_QTY),0)from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE'and SOURCE_DOC_ID=:w and SOURCE_LINE_ID!=:pt and RESERVATION_KIND='HARD'and STATUS in('ACTIVE','ALLOCATED','PICKING')",w=wave,pt=pt);assert q.fetchone()==(8,)
  Path("tmp/context835.json").write_text(json.dumps({"wave":wave,"rt":rt,"task":int(tid),"next_rt":int(next_rows[0][0]),"article":article,"ware":ware,"target":dst,"source":src,"first_uid":lot,"second_uid":extra,"target_uid":other,"stage":"CURRENT_TARGET_OWNER12_OTHER8","stock_changed_only_by_original_TASK_COMPLETE":True},indent=2),encoding="utf-8")
  print("PASS835 target4 + own6/6 -> own source2/6 -> whole20 receipt -> original next demand6 -> target own12/other8; same replay, untouched source8/H0; cleanup follows",flush=True)"""
s=s[:start]+body+s[end:]
# Fresh isolated case, not a rerun of the protected original.
print(json.dumps({"scripts/case835_sequential_sources.py":s},ensure_ascii=True))
