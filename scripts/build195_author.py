from pathlib import Path
import json
t=Path("scripts/ni042_weight_box_planning_read_case.py").read_text(encoding="utf-8").replace("194","195")
t=t.replace('api=httpx.Client(auth=("admin","admin123"),timeout=30)', 'api=httpx.Client(auth=("admin","admin123"),timeout=30);approver=None') if False else t
a='  print("PASS195 original10/current whole8or12'
pos=t.index(a)
section='''  approver="QA195"+tag;group=approver.upper();secret=uuid4().hex
  q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:p_id,:p_secret,'Own195 weight exception approver',:p_group,:p_ware,0,0)",
    p_id=approver,p_secret=secret,p_group=group,p_ware=ware);c.commit()
  r=api.post("http://127.0.0.1:8088/api/admin/rights/groups",json={"id":group,"name":"Own195 approval only"});assert r.status_code==200,(r.status_code,r.text)
  r=api.post("http://127.0.0.1:8088/api/admin/rights/groups/"+group+"/rights",json={"right_name":"case_pick_short_approve","description":"Own195 commercial final box decision"});assert r.status_code==200,(r.status_code,r.text)
  manager=httpx.Client(auth=(approver,secret),timeout=30)
  r=manager.get(path);assert r.status_code==403,(r.status_code,r.text)
  approval_path=path.replace("weighted-box-options","weighted-box-approval-preview")
  r=manager.get(approval_path);assert r.status_code==200,(r.status_code,r.text);scope=r.json();assert scope["source_signature"]==options["source_signature"]
  chosen=next(x for x in scope["boxes"]if x["net_weight_kg"]=="8")
  body={"choice_id":"WEIGHT195.CHOICE:"+tag,"customer_order_row_id":row,"physical_unit_key":chosen["physical_unit_key"],
    "weighted_box_barcode":labels[0],"source_signature":scope["source_signature"],"choice_mode":"LAST_WHOLE_BOX",
    "reason":"Approve exact8KG final sealed box against10KG original order; no splitting"}
  choice_url="http://127.0.0.1:8088/api/picking/weighted-box-choices"
  for change in ({"choice_mode":"WITHIN_TOLERANCE"},{"source_signature":"0"*64},{"weighted_box_barcode":labels[1]}):
   r=manager.post(choice_url,json={**body,**change,"choice_id":body["choice_id"]+":BAD:"+uuid4().hex[:4]});assert r.status_code==409,(r.status_code,r.text)
  r=manager.post(choice_url,json=body);assert r.status_code==200,(r.status_code,r.text);accepted=r.json()
  assert accepted["selected_net_weight_kg"]=="8"and accepted["status"]=="ACCEPTED"and not accepted["stock_changed"]and not accepted["plan_created"]
  assert manager.post(choice_url,json=body).json()==accepted
  r=manager.post(choice_url,json={**body,"reason":body["reason"]+":CHANGED"});assert r.status_code==409
  r=manager.post(choice_url,json={**body,"choice_id":body["choice_id"]+":OTHER"});assert r.status_code==409,(r.status_code,r.text)
  q.execute("select STATUS,NET_WEIGHT_KG,ORIGINAL_ORDER_KG,TOLERANCE_PCT from RRL_PICK_WEIGHT_CHOICE where CHOICE_ID=:p_id",p_id=body["choice_id"]);assert q.fetchone()==("ACCEPTED",8,10,15)
  try:q.execute("update RRL_PICK_WEIGHT_CHOICE set NET_WEIGHT_KG=12 where CHOICE_ID=:p_id",p_id=body["choice_id"]);raise AssertionError("Original choice rewritten")
  except oracledb.DatabaseError as exc:c.rollback();assert exc.args[0].code==20863
  cancel_url=choice_url+"/"+body["choice_id"]+"/cancel";cancel_body={"reason":"Retire own software decision before native fixture cleanup"}
  r=manager.post(cancel_url,json=cancel_body);assert r.status_code==200,(r.status_code,r.text);cancelled=r.json()
  assert manager.post(cancel_url,json=cancel_body).json()==cancelled
  q.execute("select STATUS,NET_WEIGHT_KG,SOURCE_SIGNATURE from RRL_PICK_WEIGHT_CHOICE where CHOICE_ID=:p_id",p_id=body["choice_id"]);assert q.fetchone()==("CANCELLED",8,scope["source_signature"])
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=:p_ware",p_ware=ware);assert q.fetchone()==before
  q.execute("update RUSERS set DELETED=1 where ID=:p_id",p_id=approver);c.commit()
  print("PASS195 approval-only actor/no plan-create right/current signed exact8-vs10/explicit exception/default15 unchanged/replay/conflicts/wrong label/stale signature/active uniqueness/immutable original/cancel history/no P-H effect",body["choice_id"],flush=True)
'''
t=t[:pos]+section+t[pos:]
print(json.dumps({"scripts/ni042_weight_box_choice_case.py":t},ensure_ascii=True))
