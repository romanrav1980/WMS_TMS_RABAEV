from pathlib import Path
import json
s=Path("scripts/ni052_single_load_slot_release_case.py").read_text(encoding="utf-8");prefix=s[:s.index(' admin_api=')]
body="""
 admin_api=httpx.Client(auth=("admin","admin123"),timeout=35);st="FULL.ST:"+tag
 api(admin_api,"POST",f"/api/admin/rights/groups/{sender.upper()}/rights",{"right_name":"outgoing_pallet_check","description":"Own224 current warehouse QC"})
 old_load="FULL223.LOAD:"+tag
 q.execute("select CONTENT_VERSION from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:p",p=old_load);v=q.fetchone()[0]
 unload={"operation_id":"FULL224.UNLOAD:"+tag,"load_operation_id":old_load,"expected_version":v,"scan_container":lot,"scan_cell":shipcell,"scan_vehicle":"QL"+tag,"scan_dock":dock,"reason":"Own224 original warehouse reloaded full pallet for scoped loading","target_slot_id":221,"scanned_to_slot_code":"UL222:"+tag+":CURRENT"}
 api(sender_api,"POST","/api/transport/loading/unload",unload)
 path="/api/transport/loading/single-preview?shipment_identifier="+st
 preview=api(sender_api,"GET",path);assert preview["root"]==lot
 load={"operation_id":"FULL224.LOAD:"+tag,"identifier":st,"expected_version":preview["expected_version"],"expected_composition_signature":preview["composition_signature"],"scan_container":lot,"scan_cell":shipcell,"transport_task_id":trip,"scan_vehicle":"QL"+tag,"scan_dock":dock,"measurements":{"origin":"MANUAL_CONFIRMED","content_version":preview["expected_version"],"gross_weight_kg":"10","width_m":"1","depth_m":"1","height_m":"1.5"}}
 q.execute("update RUSERS set WARE_ID=6667491 where ID=:p",p=sender);conn.commit()
 try:
  api(sender_api,"GET",path,status=403)
  api(sender_api,"POST","/api/transport/loading/confirm-single",load,status=403)
 finally:q.execute("update RUSERS set WARE_ID=:w where ID=:p",w=ware,p=sender);conn.commit()
 q.execute("select count(*)from RRL_STOCK_OPERATION where OPERATION_ID=:p",p=load["operation_id"]);assert q.fetchone()[0]==0
 q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=lot,c=shipcell);assert q.fetchone()==(3,3)
 before=api(sender_api,"GET","/api/outgoing-quality/"+st);assert not before["ready"]and before["rescan_required"]
 q.execute("select a.BARCODE_SHT from RRL_ARTICULS a join RRL_PALLETS p on p.ARTICUL=a.ACTICUL where p.UID_PALLET=:u",u=lot);barcode=q.fetchone()[0]
 scan={"operation_id":"FULL224.QC:"+tag,"expected_composition_signature":before["composition_signature"],"error_count":0,"item_scans":[{"scan_id":"ITEM224:"+str(i),"barcode":barcode,"quantity":"1"}for i in range(3)]}
 api(sender_api,"POST","/api/outgoing-quality/"+st+"/scan",scan)
 preview=api(sender_api,"GET",path);load.update(expected_version=preview["expected_version"],expected_composition_signature=preview["composition_signature"]);load["measurements"]["content_version"]=preview["expected_version"]
 result=api(sender_api,"POST","/api/transport/loading/confirm-single",load);assert api(sender_api,"POST","/api/transport/loading/confirm-single",load)==result
 q.execute("update RUSERS set WARE_ID=6667491 where ID=:p",p=sender);conn.commit()
 try:
  api(sender_api,"GET",path,status=403)
  api(sender_api,"POST","/api/transport/loading/confirm-single",load,status=403)
 finally:q.execute("update RUSERS set WARE_ID=:w where ID=:p",w=ware,p=sender);conn.commit()
 assert api(sender_api,"POST","/api/transport/loading/confirm-single",load)==result
 q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=lot,c=shipcell);assert q.fetchone()==(0,0)
 q.execute("select count(*)from RRL_RECEIPT_SLOT_CLAIM where UID_PALLET=:u",u=lot);assert q.fetchone()[0]==0
 q.execute("select sum(BASE_QTY)from RRL_EVENTS where OPERATION_ID=:p",p=load["operation_id"]);assert q.fetchone()[0]==-3
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=6667491");assert q.fetchone()==(20,20)
 print("PASS224 current nonadmin OWN warehouse preview/QC/load/native-3/replay; foreign current warehouse read/first-post/saved replay403 then own saved replay exact/P0H0/slot free/no refused operation/protected13520/20",load["operation_id"],flush=True)
"""
print(json.dumps({"scripts/ni052_single_load_scope_case.py":prefix+body},ensure_ascii=True))
