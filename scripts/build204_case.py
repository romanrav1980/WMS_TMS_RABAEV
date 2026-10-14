from pathlib import Path
import json
s=Path("scripts/ni042_case_sscc_case.py").read_text(encoding="utf-8-sig").replace("203","204")
s=s.replace("import sys,json,xml", "from datetime import datetime,timezone,timedelta\nimport sys,json,xml")
s=s.replace("case_types=set()","case_types=set();sender=None")
needle='   call("POST",f"/api/case-pick/tasks/{case}/claim"'
pos=s.index(needle)
new="""   sender="QS204"+tag;group=sender.upper();secret=uuid4().hex;device="WH.FINAL204:"+tag
   q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,:secret,'Own final scale gateway',:grp,:ware,0,0)",id=sender,secret=secret,grp=group,ware=ware);c.commit()
   call("POST","/api/admin/rights/groups",{"id":group,"name":"Own204 final scale sender"})
   call("POST",f"/api/admin/rights/groups/{group}/rights",{"right_name":"warehouse_scale_ingest","description":"Own software gateway"})
   def stamp(value):return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f+00:00")
   scale_base="/api/inventory/warehouse-scales";now=datetime.now(timezone.utc)
   policy={"warehouse_id":ware,"post_cell":receive,"sender_id":sender,"expected_version":0,"active":True,"device_mode":"TEST","basis":"GROSS","capacity_kg":"100","resolution_kg":"0.001","calibration_ref":"DEV204:"+tag,"calibrated_until":stamp(now+timedelta(days=1))}
   call("PUT",scale_base+"/devices/"+device,policy)
   scale_gateway=httpx.Client(auth=(sender,secret),timeout=35)
   def scale_call(packet,status=200):
    response=scale_gateway.post(base+scale_base+"/final-captures",json=packet);assert response.status_code==status,(response.status_code,response.text[:1800]);return response.json()
   def final_packet(purpose,weight,version,tare_key=None):
    now=datetime.now(timezone.utc)
    return {"device_id":device,"capture_id":purpose+"204:"+tag,"post_cell":receive,"case_task_id":case,
      "expected_content_version":version,"scan_container":carrier,"purpose":purpose,
      **({"tare_capture_key":tare_key}if tare_key else{}),
      "device_policy_version":1,"calibration_ref":policy["calibration_ref"],"unit":"KG","basis":"GROSS","preset_tare_kg":"0",
      "zero_confirmed":True,"zero_check_kg":"0","zero_check_at":stamp(now-timedelta(seconds=10)),"measured_at":stamp(now),
      "samples":[{"offset_ms":i*500,"weight_kg":weight}for i in range(5)]}
   tare_packet=final_packet("EMPTY_TARE","0.100",label["content_version"])
   scale_call({**tare_packet,"capture_id":"BAD204:"+tag,"samples":[*tare_packet["samples"][:-1],{"offset_ms":2000,"weight_kg":"0.110"}]},409)
   tare_capture=scale_call(tare_packet);assert scale_call(tare_packet)==tare_capture
   scale_call({**tare_packet,"zero_check_kg":"0.001"},409)
   call("POST",scale_base+"/final-captures",tare_packet,status=403)
   scale_call({**tare_packet,"capture_id":"BAD.GROSS204:"+tag,"purpose":"FINAL_GROSS"},409)
   print("PASS204 empty SSCC tare archive/stable exact.100/current sender/TEST/replay/changed-body/unstable/closed-source refusals",tare_capture["capture_key"],flush=True)
"""
s=s[:pos]+new+s[pos:]
needle='  from app.modules.master_data.infrastructure.quality_weight_policy'
pos=s.index(needle)
new="""  gross_packet=final_packet("FINAL_GROSS","0.400",version,tare_capture["capture_key"])
  scale_call({**gross_packet,"capture_id":"BAD.VERSION204:"+tag,"expected_content_version":version-1},409)
  scale_call({**gross_packet,"capture_id":"BAD.TARE204:"+tag,"tare_capture_key":"F"*64},409)
  final_capture=scale_call(gross_packet);assert scale_call(gross_packet)==final_capture
  assert final_capture["net_weight_kg"]=="0.3"and final_capture["tare_weight_kg"]=="0.1"
  final_list=call("GET",scale_base+f"/final-captures?task={case}")
  assert len(final_list["items"])==2
  old_list=call("GET",scale_base+f"/captures?task={case}&line={line}");assert old_list["items"]==[]
  assert call("GET",scale_base+"/captures/"+final_capture["capture_key"])==final_capture
  try:q.execute("update RRL_WH_SCALE_CAPTURE set WEIGHT_KG=1 where CAPTURE_KEY=:key",key=final_capture["capture_key"]);raise AssertionError("Final archive altered")
  except oracledb.DatabaseError as exc:c.rollback();assert exc.args[0].code==20863
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:uid and CELL=:cell",uid=sscc,cell=receive);assert q.fetchone()==(14,0)
  print("PASS204 closed whole CASE/current composition/final gross.400/measured tare.100/net.300/list separated/immutable/no P-H change",final_capture["capture_key"],flush=True)
"""
s=s[:pos]+new+s[pos:]
# Freeze reference weight policy before final composition signature, otherwise next205 should refuse it.
old='  gross_packet=final_packet'
start=s.index(old)
policy_start=s.index('  from app.modules.master_data.infrastructure.quality_weight_policy',start)
policy_end=s.index('  from app.modules.inventory.infrastructure.outgoing_quality',policy_start)
policy=s[policy_start:policy_end];s=s[:policy_start]+s[policy_end:];s=s[:start]+policy+s[start:]
needle='  print("Own204 native return/release/count completed;'
pos=s.index(needle);s=s[:pos]+"""  if sender is not None:q.execute("update RUSERS set DELETED=1 where ID=:sender",sender=sender);c.commit()
"""+s[pos:]
print(json.dumps({"scripts/ni042_final_scale_case.py":s},ensure_ascii=True))
