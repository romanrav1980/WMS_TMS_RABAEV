from pathlib import Path
import json
p=Path("scripts/source316_nested_case.py");s=Path("scripts/source311_marked_case.py").read_text(encoding="utf-8").replace("311","316")
a=s.index('  shipop="IW316.LOAD:"');b=s.index('\n\n\n  departed=',a)
replacement='''  from app.modules.inventory.infrastructure.warehouse_hu import WarehouseHu
  hu=WarehouseHu(OracleGateway());ship_root="IH316:"+tag;ship_inner="IB316:"+tag
  for identifier,kind,tare in[(ship_root,"PALLET","1"),(ship_inner,"BOX","0.2")]:
   hu.command("HU_CREATE",identifier,"IW316.CREATE:"+identifier,dict(cell=shipcell,warehouse=ware,container_type=kind,tare_weight_kg=tare,scan_container=identifier,scan_cell=shipcell),"admin")
  for parent,child in[(ship_inner,lot),(ship_root,ship_inner)]:
   ptree=hu.preview(parent,"admin");ctree=hu.preview(child,"admin")
   hu.command("HU_ATTACH",parent,"IW316.ATTACH:"+child,dict(child_uid=child,expected_version=ptree["nodes"][0]["version"],expected_child_version=ctree["nodes"][0]["version"],scan_container=parent,scan_child=child,reason="Первое плечо целого товара в неизменённой физической матрёшке"),"admin")
  tree=hu.preview(ship_root,"admin");quality=qc.status(st_uid,"admin")
  api("POST","/api/outgoing-quality/"+st_uid+"/scan",dict(operation_id="IW316.QC.PACK:"+tag,expected_composition_signature=quality["composition_signature"],error_count=0,scans=scans))
  ship_body=dict(expected_version=tree["nodes"][0]["version"],scan_container=ship_root,scan_cell=shipcell,
   loading_context=dict(transport_task_id=trip,scan_vehicle="QL"+tag,scan_dock=dock,measurements=dict(origin="MANUAL_CONFIRMED",content_version=tree["nodes"][0]["version"],gross_weight_kg="12",width_m="1",depth_m="1",height_m="1.5")))
  shipop="IW316.LOAD:"+tag;shipped=loading.load(shipop,ship_root,ship_body,"admin")
  assert loading.load(shipop,ship_root,ship_body,"admin")==shipped
  q.execute("select TT_ID,ROOT_UID,VEHICLE_ID,VEHICLE_NUMBER,DOCK,STATUS from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:op",op=shipop);assert q.fetchone()==(trip,ship_root,vehicle,"QL"+tag,dock,"LOADED")
'''
s=s[:a]+replacement+s[b:]
s=s.replace('"source_quantity":"3","units":units,','"source_quantity":"3","physical_root":ship_root,"inner_root":ship_inner,"units":units,',1)
print(json.dumps({p.as_posix():s}))
