exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from decimal import Decimal
from app.modules.finance.infrastructure.reconciliation_stock_documents import stock_documents
from app.modules.finance.infrastructure.reconciliation_stock import stock_snapshot
CTE="""with RRL_REMAINS as(select level UID_POLETA,'CELL:A' CELL,'EA' BASE_UOM,0.3 REMAIN,0.4 HARD_RESERVED_BASE from dual connect by level<=25),
RRL_CELLS as(select 'CELL:A' CELL,9807 WARE_ID from dual),
RRL_PALLETS as(select level UID_PALLET,'ARTICLE:A' ARTICUL from dual connect by level<=25),
RRL_WMS_RECEIPT_UNIT as(select level CURRENT_UID,'CELL:A' CURRENT_CELL,cast(null as varchar2(20)) STOCK_STATUS,0.2 BASE_QTY,'EA' BASE_UOM,'UNIT:'||level PHYSICAL_UNIT_KEY from dual connect by level<=25),
RRL_SKU_RECEIPT_PROFILE as(select 'NONE' ARTICUL from dual where 1=0),
RRL_SKU_RECEIPT_POLICY as(select 'NONE' ARTICUL,0 MARKING_REQUIRED from dual where 1=0),
RRL_FINISHED_GOODS_SKU as(select 'NONE' ARTICUL,0 CRPT_REQUIRED from dual where 1=0) """
class SyntheticCursor:
 def __init__(self,q):self.q=q
 def execute(self,sql,params=None,**kw):return self.q.execute(CTE+sql,params or kw)
 def fetchall(self):return self.q.fetchall()
 def fetchone(self):return self.q.fetchone()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute('set transaction read only');wrapped=SyntheticCursor(q);stock=stock_snapshot(wrapped,9807)
 counts={'stock_quantity_invariants':sum(r['invalid_rows']for r in stock['by_base_uom']),'physical_unit_composition':stock['physical_unit_composition_conflicts']};assert counts=={'stock_quantity_invariants':25,'physical_unit_composition':25}
 docs=stock_documents(wrapped,9807,counts)
 for value in docs.values():
  assert len(value['stock_rows'])==20 and value['has_more'] and value['document_ids'][0]=='["1","CELL:A"]' and value['document_ids'][-1]=='["20","CELL:A"]'
  assert isinstance(value['stock_rows'][0]['physical_quantity'],str) and Decimal(value['stock_rows'][0]['physical_quantity'])==Decimal('0.3') and Decimal(value['stock_rows'][0]['hard_quantity'])==Decimal('0.4')
 result={'synthetic_read_only_cte':True,'counts':counts,'documents':docs};Path('reports/nicora/2026-10-13/codex/NI072/synthetic_stock_keys.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print('Oracle CTE PASS: 25 conflicts per type; bounded20, decimalstrings, stablekeys; no DML')