exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
from app.modules.delivery.api.store_receipt_routes import StoreReceiptRequest
from app.modules.inventory.public import normalize_unit_scan_codes,normalize_interwarehouse_scans
ctx=json.loads(Path('tmp/context671.json').read_text(encoding='utf-8'))
b=dict(operation_id=ctx['group_store_operation_id'],load_operation_id=ctx['group_second_load_operation_id'],store_address=ctx['group_onward']['members'][0]['final_address'],**ctx['group_store_metadata'])
v=StoreReceiptRequest.model_validate(b).model_dump(mode='json');print('DTOkeys',list(v))
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute('select CANONICAL_REQUEST from RRL_STOCK_OPERATION where OPERATION_ID=:op',op=b['operation_id']);x=q.fetchone()[0];print('OLDmeta keys',list(x['metadata']));print('source',x['source']);print('emptyvalues',[(k,vv)for k,vv in v.items()if vv in [None,'',[],False]])
