from pathlib import Path
import json
s=Path("scripts/ni043_mes_sender_case.py").read_text(encoding="utf-8")
s=s.replace("admin=httpx.Client(auth=('admin','admin123'),timeout=35);base=", "admin=httpx.Client(auth=('admin','admin123'),timeout=35);active=admin;actor='QM127'+tag;group=actor.upper();secret=uuid4().hex;receiver=httpx.Client(auth=(actor,secret),timeout=35);base=")
s=s.replace("r=admin.request(method,base+path,json=body)","r=active.request(method,base+path,json=body)")
needle=" api('POST','/api/inventory/trace-manifests',manifest)"
assert needle in s
s=s.replace(needle,""" q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,:secret,'Own MES scope receiver',:grp,:ware,0,0)",id=actor,secret=secret,grp=group,ware=ware);c.commit()
 api('POST','/api/admin/rights/groups',{'id':group,'name':'Own MES scope receiver'})
 for right in ['trace_manifest_import','mes_wms_bridge_apply']:
  api('POST',f'/api/admin/rights/groups/{group}/rights',{'right_name':right,'description':'Own MES scope'})
 active=receiver
"""+needle,1)
needle=" result=api('POST',path,body);assert api('POST',path,body)==result"
assert needle in s
s=s.replace(needle,""" q.execute('update RUSERS set WARE_ID=9104 where ID=:id',id=actor);c.commit()
 denied=api('POST',path,body,403);assert denied['detail']['code']=='MES_CURRENT_WAREHOUSE_ACTOR_REQUIRED'
 q.execute('select count(*)from RRL_REMAINS where UID_POLETA=:lot_id',lot_id=uid);assert q.fetchone()==(0,)
 q.execute('update RUSERS set WARE_ID=:ware where ID=:id',ware=ware,id=actor);c.commit()
"""+needle,1)
s=s.replace(" print('PASS126", " q.execute('update RUSERS set DELETED=1 where ID=:id',id=actor);c.commit()\n print('PASS127 current native/API warehouse scope/nonadmin right/foreign403/no partial P/current source -> existing MES")
s=s.replace('"""Own native MES completion movement','"""Current nonadmin warehouse scope: own native MES completion movement')
print(json.dumps({"scripts/ni043_mes_scope_case.py":s},ensure_ascii=True))
