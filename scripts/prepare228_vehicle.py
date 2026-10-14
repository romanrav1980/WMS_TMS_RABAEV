exec(open("scripts/inspect226.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.transport.infrastructure.trip_edit import update_existing_trip
plate="QI22813508027ed"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select ID from RRL_TR_VEHICLE where NUM=:p",p=plate);row=q.fetchone()
 if not row:
  vehicle=int(q.callfunc("RRL_TR_VEHICLE_ADD",oracledb.DB_TYPE_NUMBER,[plate,"15",100,1,0,None]));c.commit()
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:q.execute("update RRL_TR_VEHICLE set WORKING_NOW=1,BLOCKED=0,DELETED=0 where ID=:i",i=vehicle);c.commit()
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 else:vehicle=row[0]
 print(update_existing_trip(OracleGateway(),33543,{"transport":plate,"transtype":"15"},"admin"))
 print("Own compatible228 vehicle",vehicle,plate,"first original LF10049 retained")
