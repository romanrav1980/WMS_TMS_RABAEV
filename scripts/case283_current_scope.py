exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.inventory.infrastructure.store_return_receiving import StoreReturnReceiving
from app.modules.inventory.contracts_store_returns import StoreReturnReceiveError
from app.oracle_gateway import OracleGateway
ctx=json.loads(Path("tmp/context264.json").read_text(encoding="utf-8"))
# Reuse the retired own calendar actor; never expose or reset credentials.
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select ID,WARE_ID,DELETED,USER_GROUP from RUSERS where ID like 'CAL264%'and DELETED=1");candidates=q.fetchall();assert len(candidates)==1,candidates
 actor,oldware,deleted,group=candidates[0];q.execute("select count(*)from RUSERS where USER_GROUP=:group_id",group_id=group);assert q.fetchone()==(1,)
 rights=["warehouse_return_receive","warehouse_settings_edit"];old={}
 for right in rights:
  q.execute("select count(*)from RIGHTS where USER_GROUP=:group_id and RIGHT1=:right_code",group_id=group,right_code=right);old[right]=q.fetchone()[0]
 def config(fn):
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:fn();c.commit()
  except BaseException:c.rollback();raise
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 def activate():
  q.execute("update RUSERS set DELETED=0,WARE_ID=13583852 where ID=:actor",actor=actor)
  for right in rights:
   if not old[right]:q.execute("insert into RIGHTS(USER_GROUP,RIGHT1)values(:group_id,:right_code)",group_id=group,right_code=right)
 config(activate)
 service=StoreReturnReceiving(OracleGateway(),lambda *args:None)
 try:
  assert service.page(13583852,"",20,actor)["warehouse_id"]==13583852
  assert service.policy(13583852,actor)["ware_id"]==13583852
  for read in [lambda:service.page(5265051,"",20,actor),lambda:service.policy(5265051,actor),
               lambda:service.configure_reuse(5265051,"NO_SOURCE283",0,actor)]:
   try:read()
   except StoreReturnReceiveError as e:assert e.status==403
   else:raise AssertionError("Foreign warehouse read/config allowed")
 finally:
  def restore():
   q.execute("update RUSERS set DELETED=:deleted,WARE_ID=:warehouse_id where ID=:actor",deleted=deleted,warehouse_id=oldware,actor=actor)
   for right in rights:
    if not old[right]:q.execute("delete from RIGHTS where USER_GROUP=:group_id and RIGHT1=:right_code",group_id=group,right_code=right)
  config(restore)
print("PASS283 actual current nonadminWARE ownqueue/policy, foreignqueue/policy/config403 beforemutation; reused retired ownactor restored/no stock")
