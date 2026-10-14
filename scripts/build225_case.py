from pathlib import Path
import json
s=Path("scripts/ni052_fullpal_unload_case.py").read_text(encoding="utf-8")
s=s[:s.index("  import httpx")]
anchor=' q.execute("select min(CUSTOMER_ID)'
idx=s.index(anchor)
setup=""" old_article=article;article="QIW225"+tag.upper()
 barcode_prefix="046"+str(int(tag,16)%10000000000).zfill(10);gtin=barcode_prefix+str((10-sum(int(n)*(3 if i%2==0 else 1)for i,n in enumerate(reversed(barcode_prefix)))%10)%10)
 meta("declare x RRL_ARTICULS%rowtype;begin select *into x from RRL_ARTICULS where ACTICUL=:old;x.ACTICUL:=:a;x.BARCODE_SHT:=:bc;insert into RRL_ARTICULS values x;end;",old=old_article,a=article,bc=gtin)
 meta("insert into RRL_STOCK_UOM_CONVERSION(ARTICUL,INPUT_UOM,BASE_UOM,POLICY_VERSION,NUMERATOR,DENOMINATOR,BASE_SCALE,PROVENANCE)select :a,INPUT_UOM,BASE_UOM,POLICY_VERSION,NUMERATOR,DENOMINATOR,BASE_SCALE,'Own225 marked fullpal'from RRL_STOCK_UOM_CONVERSION where ARTICUL=:old",a=article,old=old_article)
 meta("insert into RRL_SKU_RECEIPT_POLICY(ARTICUL,POLICY_VERSION,MARKING_REQUIRED,UPDATED_BY)values(:a,1,1,'admin')",a=article)
 for system,profile in[("CRPT","TOBACCO"),("EGAIS","ALCOHOL")]:
  meta("insert into RRL_SKU_RECEIPT_PROFILE(ARTICUL,SYSTEM_CODE,PROFILE_CODE,PROFILE_VERSION,SCAN_MODE)values(:a,:s,:p,'QR1','UNIT')",a=article,s=system,p=profile)
 meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('SKU',:a),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",a=article)
 import httpx
 from datetime import datetime,timedelta,timezone
 admin_api=httpx.Client(auth=("admin","admin123"),timeout=35);base="http://127.0.0.1:8088"
 def api(method,path,body=None,status=200):
  r=admin_api.request(method,base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:2200]);return r.json()
 units=[{"unit_id":str(i),"quantity":"1","codes":[{"system_code":"CRPT","profile_code":"TOBACCO","code":gtin+tag[:5]+str(i).zfill(2)},{"system_code":"EGAIS","profile_code":"ALCOHOL","code":("QA"+tag+str(i)).ljust(68,"X")}]}for i in range(1,4)]
"""
s=s[:idx]+setup+s[idx:]
s=s.replace(' q.execute("select min(ID) from RRL_TR_VODITEL where ID>0");driver=q.fetchone()[0];assert driver',' driver=seq("RRL_TR_VODITEL_SQ");meta("insert into RRL_TR_VODITEL(ID,F,I,O,DELETED)values(:id,\'Own225\',\'Driver\',:tag,0)",id=driver,tag=tag)')
s=s.replace(' meta("insert into RRL_SBORKA_PALLETS(ID,PALLET_UID,ST_NUMBER,WARE_ID,CONDITION,TRANSTASK_ID) values(:id,:u,:u,:ware,0,:tt)",id=pending_st,u="TT.PENDING:"+tag,tt=trip)\n','')
start=s.index('  for u,cell in ((lot,src),(other,dst)):');end=s.index('  post("WAVE_PICK_RELEASE"',start)
s=s[:start]+"""  ctx=api("POST","/api/inventory/trace-manifests/inventory-context",{"source_document_id":revision,"article":article,"cell":src,"pallet_identifier":lot})
  born=api("POST","/api/inventory/stock-posting/inventory/lots",{"operation_id":"IW225.BIRTH:"+tag,"revision_id":revision,"uid":lot,"cell":src,"article":article,"quantity":"3","expiry_date":"2030-01-01","price":"0","reason":"Own225 exact physical marked units","capture":{"units":units,"aggregations":[],"expected_policy_version":ctx["policy_version"],"expected_profile_versions":ctx["profile_versions"]}})
  post("RESERVATION_CREATE",{"uid_pallet":lot,"cell":src,"articul":article,"qty":"3","unit_code":"EA","ware_id":ware,"reservation_kind":"HARD","reservation_scope":"PALLET","reservation_domain":"PICKING","source_doc_type":"PICK_WAVE","source_doc_id":wave,"source_line_id":pt,"customer_order_id":order,"customer_id":customer,"pick_plan_id":plan,"pick_plan_line_id":pl},{"type":"PICK_WAVE","id":wave})
"""+s[end:]
start=s.index('  try:post("PICK_PALLET_BIND_SHIPMENT"');end=s.index('  completed=post("TASK_COMPLETE"',start);s=s[:start]+s[end:]
start=s.index('  try:post("SHIP_PALLET"');end=s.index('  op="FULL.BIND:"',start);s=s[:start]+s[end:]
start=s.index('  meta("update RRL_SBORKA_PALLET_ROWS set EI=\'EA\'');end=s.index('  post("INTERNAL_MOVE"',start);s=s[:start]+s[end:]
anchor='  loading_context={';idx=s.index(anchor)
qc="""  from app.modules.inventory.infrastructure.outgoing_quality import OutgoingQuality
  qc=OutgoingQuality(OracleGateway());quality=qc.status(st_uid,"admin")
  scans=[code for unit in units for code in unit["codes"]]
  api("POST","/api/outgoing-quality/"+st_uid+"/scan",{"operation_id":"IW225.QC:"+tag,"expected_composition_signature":quality["composition_signature"],"error_count":0,"scans":scans})
  assert qc.status(st_uid,"admin")["ready"]
"""
s=s[:idx]+qc+s[idx:]
start=s.index('  for bad,reason in (');end=s.index('  shipop="SINGLE.FULL.LOAD:"',start);s=s[:start]+s[end:]
s=s.replace('shipop="SINGLE.FULL.LOAD:"+tag','shipop="IW225.LOAD:"+tag',1)
s+="""
  departed=loading.depart("IW225.DEPART:"+tag,trip,"admin")
  q.execute("select STATUS from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:p",p=shipop);assert q.fetchone()[0]=="DEPARTED"
  q.execute("select count(*),sum(BASE_QTY)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:u and STOCK_STATUS='ISSUED'and HARD_RESERVATION_ID is null",u=lot);assert q.fetchone()==(3,3)
  target=ware+50000000;inbound="QI225"+tag;outbound="QO225"+tag
  meta("insert into RRL_WARES(ID,NAME,PREFIX)values(:w,:n,'QI')",w=target,n="Own225 target "+tag)
  for dc in[inbound,outbound]:meta("insert into RRL_TT_DOCK(DOCK,WARE_ID,DOCK_IS_BLOCKED)values(:d,:w,0)",d=dc,w=target)
  target_trip=seq("RRL_TRANSPORT_TASK_SQ")
  meta("insert into RRL_TRANSPORT_TASK(ID,TRANSPORT,TRANSTYPE,CONDITION,SHIPMENT_DATE,VODITEL_ID,DOCK,DELETED)values(:id,:plate,:typ,'Спланирован',trunc(sysdate),:driver,:dock,0)",id=target_trip,plate="QL"+tag,typ=trtype,driver=driver,dock=outbound)
  now=datetime.now(timezone.utc);plan_body={"operation_id":"IW225.PLAN:"+tag,"source_load_operation_id":shipop,"target_warehouse_id":target,"target_trip_id":target_trip,"inbound_dock":inbound,"arrival_due":(now+timedelta(hours=1)).isoformat(),"ready_due":(now+timedelta(hours=2)).isoformat(),"reason":"Own225 exact marked source preserves original units","decision_reference":"IW225:"+tag}
  planned=api("POST","/api/inventory/interwarehouse/plan",plan_body);assert planned["unit_capture_required"]and planned["physical_unit_count"]==3 and planned["regulatory_ack_verified"]is False and not planned["stock_changed"],planned
  assert api("POST","/api/inventory/interwarehouse/plan",plan_body)==planned
  api("POST","/api/inventory/interwarehouse/plan",{**plan_body,"operation_id":"IW225.SECOND:"+tag},status=409)
  q.execute("select count(*)from RRL_EVENTS where OPERATION_ID=:p",p=plan_body["operation_id"]);assert q.fetchone()[0]==0
  q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA=:u",u=lot);assert q.fetchone()==(0,0)
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=6667491");assert q.fetchone()==(20,20)
  print("PASS225 marked original FULLPAL birth3/codes6/native pick-bind/current unique QC/native load/depart/immutable exact unit fingerprint interwarehouse plan/replay/source uniqueness/no plan goods effect/no governmentACK/protected13520/20",tag,article,lot,ware,target,shipop,plan_body["operation_id"],trip,target_trip,inbound,outbound,flush=True)
 finally:
  conn.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
"""
print(json.dumps({"scripts/ni061_marked_source_case.py":s},ensure_ascii=True))
