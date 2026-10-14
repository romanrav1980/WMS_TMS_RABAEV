exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.inventory.infrastructure.interwarehouse import Interwarehouse
from app.modules.inventory.public import build_stock_posting_service
from app.oracle_gateway import OracleGateway
p=Path('tmp/context406.json');saved=json.loads(p.read_text(encoding='utf-8'));tag=saved['first']['tag']
svc=Interwarehouse(OracleGateway(),build_stock_posting_service());op='GROUP430.CUSTODY:'+tag
if 'group_custody'not in saved:
 saved['group_custody']=svc.release_custody(op,saved['group_receipt_operation_id'],'admin');p.write_text(json.dumps(saved,indent=2),encoding='utf-8')
assert svc.release_custody(op,saved['group_receipt_operation_id'],'admin')==saved['group_custody']
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute('select CUSTODY_RELEASE_OPERATION_ID from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:load_id',load_id=saved['load_operation_id']);assert q.fetchone()[0]==op
 q.execute('select RRL_INTERWARE_DEPART_GATE.promises(:trip)from dual',trip=saved['group_plan']['target_trip_id'])
 from app.modules.platform.public import read_oracle_json
 promises=read_oracle_json(q.fetchone()[0]);assert any(x.get('grouped_cargo')and not x['physically_loaded']for x in promises)
 q.execute('select count(*)from RRL_EVENTS where OPERATION_ID=:op',op=op);assert q.fetchone()[0]==0
print('PASS430 whole grouped custody/source departure retained/no quantity/replay/targetgroup promise stillnotready')
