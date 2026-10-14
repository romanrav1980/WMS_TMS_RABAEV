exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import httpx,secrets
ctx=json.loads(Path("tmp/context1238.json").read_text(encoding="utf-8"))
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");secret=q.fetchone()[0]
 actor="OWN1348_STORE"
 q.execute("select count(*)from RUSERS where ID=:actor",actor=actor)
 if q.fetchone()[0]==0:
  q.execute("insert into USER_GROUP(ID,NAME)values(:id,'Owned B05 store tare')",id=actor)
  q.execute("insert into RUSERS(ID,NAME,PASS,USER_GROUP,DELETED)values(:id,'Owned B05 store',:secret,:grp,0)",id=actor,secret=secrets.token_urlsafe(18),grp=actor);c.commit()
 q.execute("select PALLET_TYPE_ID,PALLET_TYPE_NAME from RRL_PALLET_TYPE t where ACTIVE=1 and not exists(select 1 from RRL_TARE_BALANCE b where b.OWNER_WARE_ID=9807 and b.PALLET_TYPE_ID=t.PALLET_TYPE_ID)order by PALLET_TYPE_ID fetch first 1 rows only")
 item=q.fetchone()
 q.execute("select PALLET_TYPE_ID,CONDITION_CODE,CUSTODIAN_KIND,CUSTODIAN_ID,QUANTITY from RRL_TARE_BALANCE where OWNER_WARE_ID=9807");print(json.dumps({"existing":q.fetchall(),"unused":item}))
with httpx.Client(base_url="http://127.0.0.1:8088",auth=("admin",secret),timeout=30)as client:
 for group in ["OWN1306_DRIVER",actor]:
  for right in ["tare_view","tare_offer","tare_accept"]+(["store_receipt_confirm"]if group==actor else[]):
   r=client.post("/api/admin/rights/groups/"+group+"/rights",json={"right_name":right,"description":"Owned B05 tare participant"});r.raise_for_status()
 r=client.post("/api/delivery/store-receipts/receivers",json={"store_address":ctx["store_address"],"username":actor});r.raise_for_status()
 if not Path("tmp/context1348.json").exists():
  assert item
  body={"operation_id":"TARE.COUNT.1348","owner_ware_id":9807,"pallet_type_id":item[0],"condition":"GOOD","observed_quantity":"6","expected_version":0,"reason":"Own dev B05 synthetic physical count","decision_reference":"OWN.B05.1348"}
  r=client.post("/api/inventory/tare/count",json=body);r.raise_for_status()
  data={"trip":33571,"warehouse":9807,"driver":10018,"vehicle":10059,"plate":"QC241ede877f6d1","store":ctx["store_address"],"type":item[0],"type_name":item[1],"count":r.json()}
  Path("tmp/context1348.json").write_text(json.dumps(data,ensure_ascii=True,indent=2),encoding="utf-8")
 print("Own B05 roles and six tare units ready")
