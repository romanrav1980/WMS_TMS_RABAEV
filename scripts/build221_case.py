from pathlib import Path
import json
s=Path("scripts/resume220_case.py").read_text(encoding="utf-8");prefix=s[:s.index(' returned={')]
prefix=prefix.replace("from app.config import get_settings","from app.config import get_settings\nfrom app.transport_composition import build_transport_loading\nfrom app.modules.inventory.infrastructure.outgoing_quality import OutgoingQuality\nfrom app.oracle_gateway import OracleGateway")
body="""
 admin_api=httpx.Client(auth=("admin","admin123"),timeout=35);qc=OutgoingQuality(OracleGateway());loading=build_transport_loading();st="FULL.ST:"+tag
 before=qc.status(st,"admin");assert not before["ready"]and before["rescan_required"]
 q.execute("select a.BARCODE_SHT from RRL_ARTICULS a join RRL_PALLETS p on p.ARTICUL=a.ACTICUL where p.UID_PALLET=:u",u=lot);barcode=q.fetchone()[0]
 scan={"operation_id":"FULL221.QC:"+tag,"expected_composition_signature":before["composition_signature"],"error_count":0,"item_scans":[{"scan_id":"ITEM221:"+str(i),"barcode":barcode,"quantity":"1"}for i in range(3)]}
 api(admin_api,"POST","/api/outgoing-quality/"+st+"/scan",scan);assert qc.status(st,"admin")["ready"]
 current=loading.preview_single(st);load_id="FULL221.LOAD:"+tag
 load={"operation_id":load_id,"identifier":st,"expected_version":current["expected_version"],"expected_composition_signature":current["composition_signature"],"scan_container":lot,"scan_cell":shipcell,"transport_task_id":trip,"scan_vehicle":"QL"+tag,"scan_dock":dock,"measurements":{"origin":"MANUAL_CONFIRMED","content_version":current["expected_version"],"gross_weight_kg":"10","width_m":"1","depth_m":"1","height_m":"1.5"}}
 api(admin_api,"POST","/api/transport/loading/confirm-single",load)
 previous="TARE220.RECOVERY:"+tag;chain=[previous]
 for cycle in range(2):
  outbound={"operation_id":"TARE221.OUT:"+str(cycle)+":"+tag,"task_id":trip,"owner_ware_id":ware,"pallet_type_id":1,"condition":"GOOD","from_kind":"WAREHOUSE","from_id":str(ware),"to_kind":"VEHICLE","to_id":str(vehicle),"quantity":"1","scan_vehicle":"QL"+tag,"booking_operation_ids":[previous]}
  api(sender_api,"POST","/api/inventory/tare/offer",outbound)
  accepted={"operation_id":"TARE221.OUT.ACCEPT:"+str(cycle)+":"+tag,"offer_operation_id":outbound["operation_id"],"accepted_quantity":"1","scan_vehicle":"QL"+tag}
  api(driver_api,"POST","/api/inventory/tare/accept",accepted)
  returned={"operation_id":"TARE221.BACK:"+str(cycle)+":"+tag,"task_id":trip,"owner_ware_id":ware,"pallet_type_id":1,"condition":"GOOD","from_kind":"VEHICLE","from_id":str(vehicle),"to_kind":"WAREHOUSE","to_id":str(ware),"quantity":"1","scan_vehicle":"QL"+tag}
  api(driver_api,"POST","/api/inventory/tare/offer",returned)
  api(sender_api,"POST","/api/inventory/tare/accept",{"operation_id":"TARE221.BACK.ACCEPT:"+str(cycle)+":"+tag,"offer_operation_id":returned["operation_id"],"accepted_quantity":"1","scan_vehicle":"QL"+tag})
  recovery={"operation_id":"TARE221.RECOVER:"+str(cycle)+":"+tag,"place_kind":"HU","place_id":lot,"pallet_type_id":1,"expected_warehouse_id":ware,"load_recovery":{"load_operation_id":load_id,"original_booking_operation_id":previous,"return_offer_operation_id":returned["operation_id"],"expected_load_version":current["expected_version"],"scan_place":lot}}
  result=api(sender_api,"POST","/api/inventory/tare/book",recovery);assert api(sender_api,"POST","/api/inventory/tare/book",recovery)==result
  q.execute("select STATUS,CLOSED_OPERATION_ID from RRL_TARE_BOOK where OPERATION_ID=:p",p=previous);assert q.fetchone()==("TRANSFERRED",accepted["operation_id"])
  q.execute("select PHYSICAL_QTY,ASSEMBLY_QTY,AVAILABLE_QTY from RRL_TARE_AVAILABILITY where OWNER_WARE_ID=:w",w=ware);assert q.fetchone()==(1,1,0)
  q.execute("select STATUS from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:p",p=load_id);assert q.fetchone()[0]=="LOADED"
  previous=recovery["operation_id"];chain.append(previous)
 # Same original load now has two accepted outbound associations. Direct first child is
 # TRANSFERRED, only the second descendant HELD: old direct rule would refuse.
 q.execute("select STATUS from RRL_TARE_BOOK where OPERATION_ID=:p",p=chain[1]);assert q.fetchone()[0]=="TRANSFERRED"
 unload={"operation_id":"FULL221.UNLOAD:"+tag,"load_operation_id":load_id,"expected_version":current["expected_version"],"scan_container":lot,"scan_cell":shipcell,"scan_vehicle":"QL"+tag,"scan_dock":dock,"reason":"Own221 repeated accepted tare recovery on same original loaded full pallet"}
 result=api(sender_api,"POST","/api/transport/loading/unload",unload);assert api(sender_api,"POST","/api/transport/loading/unload",unload)==result
 q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=lot,c=shipcell);assert q.fetchone()==(3,3)
 q.execute("select sum(BASE_QTY)from RRL_EVENTS where OPERATION_ID=:p",p=load_id);assert q.fetchone()[0]==-3
 q.execute("select sum(BASE_QTY)from RRL_EVENTS where OPERATION_ID=:p",p=unload["operation_id"]);assert q.fetchone()[0]==3
 q.execute("select STATUS from RRL_TARE_BOOK where OPERATION_ID=:p",p=chain[-1]);assert q.fetchone()[0]=="HELD"
 q.execute("select sum(QUANTITY)from RRL_TARE_BALANCE where OWNER_WARE_ID=:w",w=ware);assert q.fetchone()[0]==1
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=6667491");assert q.fetchone()==(20,20)
 print("PASS221 same original fullpal reload/native-3, two accepted tare handover-return-recovery cycles on SAME LOADED source, first descendantTRANSFERRED/lastHELD, bounded lineage native unload+3/P3H3/replay/all original histories preserved/physical tare total1/protected13520/20",load_id,chain,flush=True)
"""
print(json.dumps({"scripts/ni063_repeated_load_recovery_case.py":prefix+body},ensure_ascii=True))
