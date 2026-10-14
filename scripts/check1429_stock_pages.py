exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
from contextlib import contextmanager
from app.modules.finance.infrastructure.stock_conflict_page import stock_conflict_page,decode_cursor
from app.modules.finance.contracts import LogisticsCostError
from urllib.request import Request,urlopen
from urllib.error import HTTPError
import base64
CTE="""with RRL_REMAINS as(select rpad('UID:',170,'X')||lpad(ceil(level/2),3,'0') UID_POLETA,'CELL:'||mod(level,2) CELL,'EA' BASE_UOM,0.3 REMAIN,0.4 HARD_RESERVED_BASE from dual connect by level<=52),
RRL_CELLS as(select 'CELL:'||mod(level,2) CELL,9807 WARE_ID from dual connect by level<=2),
RRL_PALLETS as(select rpad('UID:',170,'X')||lpad(level,3,'0') UID_PALLET,'ARTICLE' ARTICUL from dual connect by level<=26),
RRL_WMS_RECEIPT_UNIT as(select rpad('UID:',170,'X')||lpad(ceil(level/2),3,'0') CURRENT_UID,'CELL:'||mod(level,2) CURRENT_CELL,'STORED' STOCK_STATUS,0.2 BASE_QTY,'EA' BASE_UOM,'UNIT:'||level PHYSICAL_UNIT_KEY from dual connect by level<=52),
RRL_SKU_RECEIPT_PROFILE as(select 'NONE' ARTICUL from dual where 1=0),RRL_SKU_RECEIPT_POLICY as(select 'NONE' ARTICUL,0 MARKING_REQUIRED from dual where 1=0),RRL_FINISHED_GOODS_SKU as(select 'NONE' ARTICUL,0 CRPT_REQUIRED from dual where 1=0) """
class Wrapped:
 def __init__(self,q):self.q=q
 def execute(self,sql,params=None):return self.q.execute((CTE if sql.startswith('select r.UID_POLETA') else '')+sql,params or {})
 def fetchall(self):return self.q.fetchall()
 def fetchone(self):return self.q.fetchone()
class Gateway:
 def __init__(self,c):self.c=c
 @contextmanager
 def transaction(self,label):
  try:yield Wrapped(self.c.cursor())
  finally:self.c.rollback()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 result={}
 for metric in ['stock_quantity_invariants','physical_unit_composition']:
  pages=[];keys=[];cursor=None
  while True:
   page=stock_conflict_page(Gateway(c),9807,metric,cursor,20,'admin');pages.append(len(page['rows']))
   keys.extend((r['uid_pallet'],r['cell'])for r in page['rows']);cursor=page['next_cursor']
   if not page['has_more']:break
  assert pages==[20,20,12] and len(keys)==len(set(keys))==52 and all(len(uid)>160 for uid,cell in keys)
  result[metric]={'pages':pages,'unique_keys':len(set(keys)),'long_uid_preserved':True}
 q=c.cursor();q.execute("select COLUMN_NAME,NULLABLE from USER_TAB_COLUMNS where TABLE_NAME='RRL_REMAINS' and COLUMN_NAME in('UID_POLETA','CELL')");result['key_nullability']=q.fetchall()
headers={'Authorization':'Basic '+base64.b64encode(b'admin:admin123').decode()}
for name,url in [('live','http://127.0.0.1:8088/api/finance/day-reconciliation/warehouses/9807/stock-conflicts?metric=stock_quantity_invariants'),('invalid_cursor','http://127.0.0.1:8088/api/finance/day-reconciliation/warehouses/9807/stock-conflicts?metric=stock_quantity_invariants&after=broken'),('unknown_warehouse','http://127.0.0.1:8088/api/finance/day-reconciliation/warehouses/999999999/stock-conflicts?metric=stock_quantity_invariants')]:
 try:
  with urlopen(Request(url,headers=headers),timeout=20) as r:result[name]={'status':r.status,'body':json.load(r)}
 except HTTPError as e:result[name]={'status':e.code}
assert result['live']['status']==200 and result['invalid_cursor']['status']==422 and result['unknown_warehouse']['status']==403
Path('tmp/result1429.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))
