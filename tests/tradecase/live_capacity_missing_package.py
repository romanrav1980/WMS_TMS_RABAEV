"""Remove owned package metadata only inside a caller rollback and verify the native read admission."""
from pathlib import Path
import json,sys
sys.path[:0]=['.','api/wms_api_server']
from tools.mcp.tms_mcp_server import oracle_connection
from app.modules.integrations.infrastructure.trade_capacity import _box
from app.modules.integrations.contracts_trade_transport import TradeTransportError
f=json.loads(Path('runtime/test-evidence/tradecase/2026-10-19/T08/capacity-fixture.json').read_text());a=f['a'];out={'checks':[],'physical_writes':0}
with oracle_connection()as c:
 q=c.cursor();q.execute('select COUNT_SHT_IN_KOR,BRUTTO_WEIGHT_OF_KOR,DIMKOR_X,DIMKOR_Y,DIMKOR_Z from RRL_ARTICULS where ACTICUL=:a',a=a['article']);before=list(q.fetchone());q.callproc('RRL_STOCK_CONFIG_API.begin_change',['admin','warehouse_settings_edit'])
 try:
  q.execute('update RRL_ARTICULS set DIMKOR_X=null where ACTICUL=:a',a=a['article'])
  try:_box(q,a['warehouse_id'],'A')
  except TradeTransportError as exc:assert exc.code=='TRADE_CAPACITY_PACKAGE_MEASUREMENTS_REQUIRED';out['checks']+=['missing_native_dimension_blocks_preview']
  else:raise AssertionError('Missing dimension allowed')
 finally:c.rollback();q.callproc('RRL_STOCK_CONFIG_API.end_change')
 q.execute('select COUNT_SHT_IN_KOR,BRUTTO_WEIGHT_OF_KOR,DIMKOR_X,DIMKOR_Y,DIMKOR_Z from RRL_ARTICULS where ACTICUL=:a',a=a['article']);assert list(q.fetchone())==before;out['checks']+=['caller_rollback_restores_package'];assert _box(q,a['warehouse_id'],'A')['dimensions']
 out.update(status='PASS',limits='One owned SKU, caller rollback only; pallet place and stacking acceptance remain open')
Path('runtime/test-evidence/tradecase/2026-10-19/T08/capacity-missing-package.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
