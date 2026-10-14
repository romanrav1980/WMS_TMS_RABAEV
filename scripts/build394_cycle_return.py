from pathlib import Path
import json
cycle=json.loads(Path("tmp/context392.json").read_text(encoding="utf-8"));original=cycle["source"];found=cycle["parts"][1]["onward"]
source={**original,"warehouse":original["target_warehouse"],"source_load":cycle["load_operation_id"],"source_trip":original["target_trip"],"lot":found["pallet_identifier"],"receive":original["receive_cell"],"pick":"QK394"+original["tag"],"units":[unit for unit in original["units"]if unit["unit_id"]in["2","3"]]}
bridge={"source":source,"receipt_operation_id":cycle["store_operation_id"],"address":found["final_address"]}
out={"tmp/context394_source.json":json.dumps(bridge,indent=2)}
t=Path("scripts/case387_marked_reuse.py").read_text(encoding="utf-8").replace("387","394").replace("386","394_source")
t=t.replace('assert len(keys)==3','assert len(keys)==2').replace('"quantity":"3"','"quantity":"2"').replace('"Quantity":"3"','"Quantity":"2"').replace('"full_box_count":"1"','"full_box_count":"2"').replace('"full_box_count":"2"},409','"full_box_count":"3"},409')
t=t.replace('q.fetchone()==(3,0)','q.fetchone()==(2,0)').replace('q.fetchone()==(3,3)','q.fetchone()==(2,2)').replace('q.fetchone()[0]==6','q.fetchone()[0]==6')
t=t.replace('set MAX_WEIGHT_KG=20,PALLETS=2','set MAX_WEIGHT_KG=20,PALLETS=3')
t=t.replace('"available_physical_quantity"]="3"','"available_physical_quantity"]="2"')
t=t.replace('q.execute("select PHYSICAL_UNIT_KEY from RRL_STORE_RECEIPT_UNIT where OPERATION_ID=:op and UNIT_DISPOSITION=\'ACCEPTED\'order by PHYSICAL_UNIT_KEY",op=source)','q.execute("select b.PHYSICAL_UNIT_KEY from RRL_STORE_RECEIPT_UNIT b join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=b.PHYSICAL_UNIT_KEY where b.OPERATION_ID=:op and b.UNIT_DISPOSITION=\'ACCEPTED\'and u.CURRENT_UID=:lot order by b.PHYSICAL_UNIT_KEY",op=source,lot=origin["lot"])')
at=t.index(' cells=["QS394')
t=t[:at]+''' if "pick_face"not in saved:
  def setup_pick():
   q.execute("select count(*)from RRL_CELLS where CELL=:cell",cell=origin["pick"])
   if not q.fetchone()[0]:
    q.execute("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT)values(:cell,:ware,0,0,0,1,0,0,0)",cell=origin["pick"],ware=ware)
    q.execute("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:cell),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",cell=origin["pick"])
   q.execute("insert into RRL_RECEIPT_SKU_RULE(WARE_ID,ARTICUL,PICK_CELL,MIN_SHELF_DAYS,SOURCE_PICK_MODE)values(:ware,:article,:cell,0,'AFTER_PUTAWAY')",ware=ware,article=origin["article"],cell=origin["pick"])
  config(setup_pick);saved["pick_face"]=True;save()
'''+t[at:]
needle=' approval={"operation_id":'
at=t.index(needle)
t=t[:at]+''' q.execute("select LINE_NO from RRL_STORE_RECEIPT_LINE where OPERATION_ID=:op and LOT_UID=:lot and ACCEPTED_BASE_QTY=2",op=source,lot=origin["lot"]);line_no=int(q.fetchone()[0])
'''+t[at:]
t=t.replace('"line_no":1,','"line_no":line_no,').replace('"OriginalLineNumber":"1"','"OriginalLineNumber":str(line_no)')
out["scripts/return394_cycle.py"]=t
print(json.dumps(out))
