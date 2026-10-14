exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.transport.public import update_existing_trip
for number in[291,292]:
 p=Path("tmp/context296_"+str(number)+".json");saved=json.loads(p.read_text());ctx=json.loads(Path("tmp/context"+str(number)+".json").read_text());plate="QT296"+ctx["tag"]
 with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
  q=c.cursor();q.execute("select TRANSPORT_TYPE,STOL,MAX_VEHICLE_TONS from RRL_ADDR where ADDR=:addr",addr=saved["onward_result"]["final_address"]);rows=q.fetchall();assert len(rows)==1,rows
  typ,hydro,tons=rows[0];assert typ=="15"and (tons is None or tons>=.1),rows
  q.execute("select ID from RRL_TR_VEHICLE where NUM=:plate",plate=plate);row=q.fetchone()
  if row is None:
   vehicle=int(q.callfunc("RRL_TR_VEHICLE_ADD",oracledb.DB_TYPE_NUMBER,[plate,typ,100,2,1 if hydro else 0,None]));c.commit()
   q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
   try:q.execute("update RRL_TR_VEHICLE set WORKING_NOW=1,BLOCKED=0,DELETED=0 where ID=:vehicle_id",vehicle_id=vehicle);c.commit()
   finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 update_existing_trip(OracleGateway(),ctx["target_trip"],dict(transport=plate,transtype=typ),"admin")
 saved["target_vehicle_number"]=plate;p.write_text(json.dumps(saved,indent=2),encoding="utf-8")
print("Own296 target vehicles match existing address type15 via original vehicle registration and validated trip editor; source archived vehicles unchanged")
