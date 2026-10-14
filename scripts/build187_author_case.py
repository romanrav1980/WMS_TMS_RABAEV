from pathlib import Path
import json
s=Path("scripts/ni042_weight_box_capacity_case.py").read_text(encoding="utf-8")
s=s.replace('article="QW184"+tag.upper()','article="QW187"+tag.upper()').replace('lot="CASE184.QA:"','lot="CASE187.QA:"')
s=s.replace('import sys,json,re','import sys,json,re\nfrom datetime import datetime,timedelta,timezone')
idx=s.index('  operation="CASE.WEIGHT182:"')
extra="""  sender="QS187"+tag;group=sender.upper();secret=uuid4().hex;device="WH.SCALE187:"+tag
  q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,:secret,'Own warehouse scale gateway',:grp,:ware,0,0)",id=sender,secret=secret,grp=group,ware=ware);c.commit()
  def scale_call(client,method,path,body=None,status=200):
   r=client.request(method,"http://127.0.0.1:8088"+path,json=body);assert r.status_code==status,(r.status_code,r.text[:1600]);return r.json()
  scale_call(api,"POST","/api/admin/rights/groups",{"id":group,"name":"Own187 addressed scale sender"})
  scale_call(api,"POST",f"/api/admin/rights/groups/{group}/rights",{"right_name":"warehouse_scale_ingest","description":"Own software gateway"})
  def stamp(value):return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f+00:00")
  now=datetime.now(timezone.utc);scale_base="/api/inventory/warehouse-scales"
  policy={"warehouse_id":ware,"post_cell":dst,"sender_id":sender,"expected_version":0,"active":True,"device_mode":"TEST","basis":"GROSS","capacity_kg":"100","resolution_kg":"0.01","calibration_ref":"DEV187:"+tag,"calibrated_until":stamp(now+timedelta(days=1))}
  scale_call(api,"PUT",scale_base+"/devices/"+device,policy)
  q.execute("select CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id",id=case);content_version=int(q.fetchone()[0])
  now=datetime.now(timezone.utc)
  packet={"device_id":device,"capture_id":"SAMPLE187:"+tag,"post_cell":dst,"case_task_id":case,"case_line_id":line,
   "expected_content_version":content_version,"scan_source_cell":cell,"scan_container":carrier,"scan_product":labels[0],"device_policy_version":1,"calibration_ref":policy["calibration_ref"],
   "unit":"KG","basis":"GROSS","preset_tare_kg":"0","zero_confirmed":True,"zero_check_kg":"0","zero_check_at":stamp(now-timedelta(seconds=60)),"measured_at":stamp(now),
   "samples":[{"offset_ms":i*500,"weight_kg":"10.1"}for i in range(5)]}
  gateway=httpx.Client(auth=(sender,secret),timeout=30)
  scale_call(gateway,"POST",scale_base+"/captures",{**packet,"capture_id":"BAD187:"+tag,"samples":[*packet["samples"][:-1],{"offset_ms":2000,"weight_kg":"10.13"}]},409)
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=:w",w=ware);stock_before=q.fetchone()
  capture=scale_call(gateway,"POST",scale_base+"/captures",packet);assert capture["weight_kg"]=="10.1"and capture["device_mode"]=="TEST"and not capture["stock_posted"]
  assert scale_call(gateway,"POST",scale_base+"/captures",packet)==capture
  scale_call(gateway,"POST",scale_base+"/captures",{**packet,"zero_check_kg":"0.01"},409)
  assert scale_call(api,"GET",scale_base+"/captures/"+capture["capture_key"])==capture
  archived=scale_call(api,"GET",scale_base+f"/captures?task={case}&line={line}");assert archived["items"]==[capture]
  scale_call(api,"POST",scale_base+"/captures",packet,403)
  scale_call(gateway,"GET",scale_base+"/captures/"+capture["capture_key"],status=403)
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=:w",w=ware);assert q.fetchone()==stock_before
  try:q.execute("delete RRL_WH_SCALE_CAPTURE where CAPTURE_KEY=:p_key",p_key=capture["capture_key"]);raise AssertionError("Original scale capture deleted")
  except oracledb.DatabaseError as exc:c.rollback();assert exc.args[0].code==20863
  print("PASS187 current warehouse/address/CASE/version/dedicated sender/stable original10.1KG/TEST mode/hash/replay/conflict/unstable/foreign rights/append-only/no P-H effect",capture["capture_key"],flush=True)
"""
s=s[:idx]+extra+s[idx:]
s=s.replace('PASS184 actual weighted replenishment','PASS187 existing weighted replenishment')
# Restore sender lifecycle after native stock cleanup.
s += '\nwith oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as done:\n done.cursor().execute("update RUSERS set DELETED=1 where ID=:p_sender",p_sender=sender);done.commit()\n'
print(json.dumps({"scripts/ni042_warehouse_scale_archive_case.py":s},ensure_ascii=True))
