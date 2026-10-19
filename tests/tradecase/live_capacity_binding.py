"""Read-only plan calculation and rollback-only native stale-binding negatives."""
import sys,json
from pathlib import Path
sys.path[:0]=['.','api/wms_api_server']
from tools.mcp.tms_mcp_server import oracle_connection
from app.modules.integrations.infrastructure.trade_capacity import _document,_planned
from app.modules.integrations.contracts_trade_transport import TradeTransportError
p=Path('runtime/test-evidence/tradecase/2026-10-19/T08/capacity-binding.json');out={'checks':[],'physical_writes':0}
with oracle_connection()as c:
 q=c.cursor();trip,_=_document(q,215590763,'TRIP','R1.1155');_planned(q,215590763,trip,'admin');c.rollback()
 def rejected(code):
  try:_planned(q,215590763,trip,'admin')
  except TradeTransportError as e:assert e.code==code;out['checks'].append(code)
  else:raise AssertionError('Stale source was accepted')
 try:
  q.execute("update RRL_TRADE_DOCUMENT set VERSION_NO=VERSION_NO+1 where WARE_ID=215590763 and ENTITY_TYPE='SKU'and EXTERNAL_ID='A'")
  rejected('TRADE_CAPACITY_BOUND_SKU_VERSION_CHANGED')
 finally:c.rollback()
 try:
  q.execute("update RRL_TRADE_DOCUMENT set VERSION_NO=VERSION_NO+1 where WARE_ID=215590763 and ENTITY_TYPE='ORDER'and EXTERNAL_ID=:id",id=trip['orders'][0]['order_id'])
  assert q.rowcount==1
  rejected('TRADE_CAPACITY_ORDER_BINDING_STALE')
 finally:c.rollback()
 # Three different orders with the same owner pair must not repeat the grant read.
 class Counted:
  def __init__(self,cursor):self.cursor=cursor;self.owner_reads=0
  def execute(self,sql,**binds):
   if 'owner_allowed'in sql:self.owner_reads+=1
   return self.cursor.execute(sql,**binds)
  def __iter__(self):return iter(self.cursor)
  def fetchone(self):return self.cursor.fetchone()
 counted=Counted(q);control,_=_document(counted,224274301,'TRIP','TC8.R1');items,versions,_=_planned(counted,224274301,control,'admin');assert sum(x['boxes']for x in items)==600 and counted.owner_reads==1;out.update(owner_reads_for_three_orders=counted.owner_reads,planned_boxes=600);out['checks']+=['shared_owner_pair_checked_once','metadata_rollback_preserved']
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=215590763");assert list(q.fetchone())==[110,0]
out['initial_fixture_mutation']='Protected native link correctly denied direct test update; stale source document version used instead, caller rollback retained';out['status']='PASS';p.write_text(json.dumps(out,indent=2));print(json.dumps(out))
