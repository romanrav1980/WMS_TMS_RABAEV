"""Native eligibility only; no loading/stock writer is called by this probe."""
import json
from pathlib import Path
import sys
import oracledb
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from tools.mcp.tms_mcp_server import oracle_connection
OUT=ROOT/'runtime/test-evidence/tradecase/2026-10-22/T07';OUT.mkdir(exist_ok=True)
fixture=json.loads((OUT.parent/'T06/hu-pack-state.json').read_text(encoding='utf-8'))
stage=sys.argv[1];enabled=stage!='rollback';report=dict(status='FAIL',stage=stage,checks=[],physical_writes=0)
try:
    with oracle_connection()as c:
        q=c.cursor();q.execute("select user,sys_context('USERENV','SERVICE_NAME')from dual");assert q.fetchone()==('RABAEV','orcl')
        for label,root,bulk,expected in [
            ('PALLET rejected by explicit bulk action',fixture['containers'][0]['uid'],True,'BULK_LOADING_INDEPENDENT_BOX_REQUIRED'if enabled else'TRADE_PICKED_SHIPMENT_BINDING_REQUIRED'),
            ('BOX still needs original shipment binding',fixture['containers'][2]['uid'],True,'TRADE_PICKED_SHIPMENT_BINDING_REQUIRED'),
            ('ordinary PALLET retains original checks',fixture['containers'][0]['uid'],None,'TRADE_PICKED_SHIPMENT_BINDING_REQUIRED'),
            ('false marker does not change ordinary command',fixture['containers'][0]['uid'],False,'TRADE_PICKED_SHIPMENT_BINDING_REQUIRED')]:
            metadata={}if bulk is None else dict(bulk_box_scan=bulk)
            body=json.dumps(dict(command_type='HU_SHIP',source=dict(uid=root),metadata=metadata));reason=None
            try:q.callproc('RRL_TRADE_STOCK_GUARD.assert_command_stock',[fixture['stock_uid'],body,'admin'])
            except oracledb.DatabaseError as exc:reason=str(exc.args[0]).split('\n',1)[0]
            assert expected in(reason or''),(label,reason)
            report['checks'].append(dict(label=label,reason=reason))
        q.execute("select count(*)from USER_OBJECTS where STATUS='INVALID'");assert q.fetchone()[0]==0
        q.execute('select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=219023232');assert q.fetchone()==(10,0)
        report['status']='PASS'
finally:(OUT/('bulk-guard-'+stage+'.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
