exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.transport.public import TransportPreflight
service=TransportPreflight(OracleGateway())
a=service.time_context(33530,"admin")
assert a["version"]==0 and len(a["source"]["operations"])==12
print("PASS248 native current context original12/sourcehash; no writes")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select COLUMN_NAME,DATA_TYPE from USER_TAB_COLUMNS where TABLE_NAME='RRL_TRANSPORT_TASK' and COLUMN_NAME in('SHIPMENT_DATE','SHIPMENT_TIME','DOCK','USER_ID')");print(q.fetchall())
 q.execute("select ID,TRANSPORT,VODITEL_ID,DOCK,USER_ID,CONDITION from RRL_TRANSPORT_TASK where ID=33531");print(q.fetchall())
