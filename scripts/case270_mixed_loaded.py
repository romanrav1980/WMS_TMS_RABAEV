exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.platform.public import read_oracle_json
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select ST_NUMBER,TRANSTASK_ID,CONDITION,PALLET_UID,ADDR from RRL_SBORKA_PALLETS where ID=641360");loaded=q.fetchone()
 q.execute("select ST_NUMBER,TRANSTASK_ID from RRL_SBORKA_PALLETS where ID=641361");pending=q.fetchone()
 assert loaded[1:3]==(33541,2)and pending[1]==33541
 q.execute("select v.ID,v.PALLETS,v.TR_TYPE from RRL_TR_VEHICLE v join RRL_TRANSPORT_TASK t on t.TRANSPORT=v.NUM where t.ID=33541");vehicle,places,tr_type=q.fetchone()
 q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
 try:
  q.execute("update RRL_TR_VEHICLE set PALLETS=2,TR_TYPE='15' where ID=:vehicle_id",vehicle_id=vehicle)
  q.execute("update RRL_SBORKA_PALLETS set ST_NUMBER=:st_number where ID=641361",st_number=loaded[0])
  sts=q.var(oracledb.DB_TYPE_CLOB);sts.setvalue(0,json.dumps([loaded[0]]));out=q.var(oracledb.DB_TYPE_CLOB)
  q.callproc("RRL_TRANSPORT_PLAN_API.assign_sts",[33541,sts,"admin",out]);result=read_oracle_json(out.getvalue())
  assert result["written_sts"]==0 and result["retained_loaded_sts"]==1,result
  q.execute("select ST_NUMBER,TRANSTASK_ID,CONDITION,PALLET_UID,ADDR from RRL_SBORKA_PALLETS where ID=641360");assert q.fetchone()==loaded
  q.execute("update RRL_SBORKA_PALLETS set TRANSTASK_ID=null where ID=641361")
  try:q.callproc("RRL_TRANSPORT_PLAN_API.assign_sts",[33541,sts,"admin",out])
  except oracledb.DatabaseError as e:assert "PLAN_PARTIALLY_LOADED_ST_FROZEN" in str(e),str(e)
  else:raise AssertionError("Partly loaded whole-ST writer bypass")
 finally:
  c.rollback();q.callproc("RRL_STOCK_CONFIG_API.end_change")
 q.execute("select ST_NUMBER,TRANSTASK_ID from RRL_SBORKA_PALLETS where ID=641361");assert q.fetchone()==pending
 q.execute("select PALLETS,TR_TYPE from RRL_TR_VEHICLE where ID=:vehicle_id",vehicle_id=vehicle);assert q.fetchone()==(places,tr_type)
 q.execute("select ST_NUMBER,TRANSTASK_ID,CONDITION,PALLET_UID,ADDR from RRL_SBORKA_PALLETS where ID=641360");assert q.fetchone()==loaded
print("PASS270 mixed same-trip loaded+pending group preserves exact loaded snapshot/skips whole-ST writer/new unassigned same-number pallet refused/all config-plan perturbations outerrollback restored")
