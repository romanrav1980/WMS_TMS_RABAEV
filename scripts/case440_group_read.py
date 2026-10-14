exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.inventory.infrastructure.interwarehouse_incoming import InterwarehouseIncoming
from app.modules.inventory.infrastructure.interwarehouse_group_read import InterwarehouseGroupRead
from app.oracle_gateway import OracleGateway
ctx=json.loads(Path('tmp/context406.json').read_text(encoding='utf-8'))
value=InterwarehouseIncoming(OracleGateway()).read(ctx['group_plan']['target_trip_id'],'admin')
assert value['expected_deliveries']==2 and value['ready_deliveries']==2 and value['incoming_ready'],value
detail=InterwarehouseGroupRead(OracleGateway()).detail(ctx['group_plan_operation_id'],'admin')
assert detail['placement_task_status']=='DONE' and detail['placement_task_id']==ctx['group_put_plan']['task_id']
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for source in(ctx['first'],ctx['second']):
  q.execute("select sum(FACT_QTY),count(*)from RRL_CUSTOMER_ORDER_FULFILLMENT where CUSTOMER_ORDER_ID=:order_id and STATUS='SHIPPED'",order_id=source['order']);assert q.fetchone()==(3,1)
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS cell on cell.CELL=r.CELL where cell.WARE_ID=6667491");assert q.fetchone()==(20,20)
 q.execute("select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),BUFFER_GETS,substr(SQL_TEXT,1,130)from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and SQL_TEXT not like '%V$SQL%'and(SQL_TEXT like '%RRL_IW_GROUP_DISPATCH%'or SQL_TEXT like '%RRL_IW_GROUP_ST_BIND%')order by ELAPSED_TIME desc fetch first 8 rows only")
 print(json.dumps(q.fetchall(),default=str))
print('PASS440 groupedincoming2/ready2 afteractualdepart/sourceFF3once each/groupPUT task1HU/DONE/protected20')
