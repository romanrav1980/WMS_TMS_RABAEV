from pathlib import Path
p=Path("scripts/ni032_partial_target_supply_case.py");v=p.read_text(encoding="utf-8")
prefix=v.split("  # Represents physically available supply")[0]
cleanup=v.rsplit(" finally:",1)[1]
body="""
  post("INVENTORY_REGISTER_LOT",{"uid":other,"cell":dst,"article":article,"quantity":"8","expiry_date":"2030-01-01","price":0,"reason":"Existing target stock for multi-binding replacement"},{"revision_id":revision})
  meta("update RRL_CELLS set BLOCKED_FOR_REMAINS=1 where CELL=:c",c=dst)
  service._enrich_replenishment_settings(wave,"admin");service._refresh_replenishment_deficit(wave,"admin")
  from app.modules.inventory.infrastructure.wave_commands import reserve_wave_sources
  gateway=OracleGateway();reserve_wave_sources(gateway,wave,"admin")
  extra=lot+"B"
  post("INVENTORY_REGISTER_LOT",{"uid":extra,"cell":src,"article":article,"quantity":"8","expiry_date":"2030-01-01","price":0,"reason":"Second physical source for same existing owner"},{"revision_id":revision})
  q.execute("select PICK_TASK_ID,CUSTOMER_ORDER_ID,PICK_PLAN_ID,PICK_PLAN_LINE_ID from RRL_PICK_TASK where PICK_PLAN_ID=:plan",plan=plans[0]);pt,co,pp,pl=q.fetchone()
  q.execute("select RESERVATION_ID from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE'and SOURCE_DOC_ID=:w and SOURCE_LINE_ID=:pt and RESERVATION_KIND='HARD'and BASE_QTY>0 and STATUS in('ACTIVE','ALLOCATED','PICKING')",w=wave,pt=pt);old=[r[0]for r in q];assert len(old)==1
  post("RESERVATION_RELEASE",{"reason":"Own explicit source rebalance"},{"reservation_id":int(old[0])})
  ids=[]
  for source_uid in (lot,extra):
   result=post("RESERVATION_CREATE",{"reservation_kind":"HARD","reservation_scope":"QTY","reservation_domain":"PICKING","source_doc_type":"PICK_WAVE","source_doc_id":wave,"source_line_id":int(pt),"customer_id":customer,"customer_order_id":int(co),"pick_plan_id":int(pp),"pick_plan_line_id":int(pl),"qty":"6","unit_code":"EA","articul":article,"uid_pallet":source_uid,"cell":src,"ware_id":ware},{"type":"STOCK_RESERVATION"})
   ids.append(result["reservation_id"])
  q.execute("select PICK_WAVE_REPLENISH_TASK_ID from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_ID=:w and PICK_TASK_ID=:pt",w=wave,pt=pt);rt=int(q.fetchone()[0])
  meta("update RRL_PICK_WAVE_REPLENISH_TASK set SOURCE_RESERVATION_ID=:rid where PICK_WAVE_REPLENISH_TASK_ID=:rt",rid=ids[0],rt=rt)
  meta("update RRL_CELLS set BLOCKED_FOR_REMAINS=0 where CELL=:c",c=dst)
  service._enrich_replenishment_settings(wave,"admin");service._refresh_replenishment_deficit(wave,"admin")
  reserve_wave_sources(gateway,wave,"admin",[rt])
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=lot,c=src);assert q.fetchone()==(20,8)
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=extra,c=src);assert q.fetchone()==(8,4)
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=other,c=dst);assert q.fetchone()==(8,8)
  q.execute("select RESERVE_REQUEST_JSON from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_REPLENISH_TASK_ID=:rt",rt=rt);wire=q.fetchone()[0];wire=json.loads(wire.read()if hasattr(wire,"read")else wire)
  from app.modules.inventory.contracts_stock import StockCommand
  from app.modules.inventory.infrastructure.stock_posting_uow import StockPosting
  command=StockCommand(operation_id=wire["operation_id"],command_type=wire["command_type"],actor=wire["actor"],lines=(),source=wire["source"],metadata=wire["metadata"])
  first=StockPosting().post(command);assert StockPosting().post(command)==first
  Path("tmp/context632.json").write_text(json.dumps({"wave":wave,"rt":rt,"article":article,"source_uid":lot,"continuation_uid":extra,"target_uid":other,"source_cell":src,"target_cell":dst,"operation_id":wire["operation_id"],"status":"REBIND_PASS"},indent=2),encoding="utf-8")
  print("PASS632 one owner6+6 -> existing target8H8 + remaining source8H4; other owner8 unchanged; P unchanged/exact replay")
"""
out=prefix+body+" finally:"+cleanup
import json;print(json.dumps({"scripts/case632_multi_binding_partial.py":out},ensure_ascii=True))

