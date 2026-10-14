exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
from app.modules.inventory.infrastructure.warehouse_hu import WarehouseHu
from app.oracle_gateway import OracleGateway
c=json.loads(Path('tmp/context671.json').read_text(encoding='utf-8'))
v=WarehouseHu(OracleGateway()).preview(c['root'],'admin');print({k:x for k,x in v.items()if k not in ('nodes','units','ancestors')});print([(x.get('uid'),x.get('kind'))for x in v['nodes']])
