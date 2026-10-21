"""Native guard admission only; never execute a stock writer in this probe."""
import json
from pathlib import Path
import sys
import oracledb
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from tools.mcp.tms_mcp_server import oracle_connection
OUT=ROOT/'runtime/test-evidence/tradecase/2026-10-22/T06'
stage=sys.argv[1];enabled=stage!='rollback'
state=json.loads((OUT/'hu-pack-state.json').read_text(encoding='utf-8'))
report=dict(stage=stage,status='FAIL',checks=[],physical_writes=0)
try:
    with oracle_connection()as c:
        q=c.cursor();q.execute("select user,sys_context('USERENV','SERVICE_NAME')from dual");assert q.fetchone()==('RABAEV','orcl')
        for kind in ['HU_ATTACH','HU_DETACH','HU_MOVE']:
            for actor in ['admin','NO_HU_OWNER_GRANT']:
                wire=json.dumps(dict(command_type=kind,source=dict(uid=state['containers'][2]['uid']),metadata={}))
                reason=None
                try:q.callproc('RRL_TRADE_STOCK_GUARD.assert_command_stock',[state['stock_uid'],wire,actor])
                except oracledb.DatabaseError as exc:reason=str(exc.args[0]).split('\n',1)[0]
                expected=('TRADE_ORDER_BINDING_REQUIRED'if not enabled or kind=='HU_MOVE'else None if actor=='admin'else'TRADE_OWNER_ACCESS_DENIED')
                assert (reason is None if expected is None else expected in (reason or '')),(kind,actor,reason,expected)
                report['checks'].append(dict(command=kind,actor=actor,reason=reason))
        q.execute("select count(*)from USER_OBJECTS where STATUS='INVALID'");assert q.fetchone()[0]==0
        q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=219023232");assert q.fetchone()==(10,0)
        report['status']='PASS'
finally:(OUT/('hu-guard-'+stage+'.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
