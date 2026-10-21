"""Exercise replay authority before and after restoring the native access body."""
import json
from pathlib import Path
import sys
import oracledb
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from tools.mcp.tms_mcp_server import oracle_connection
OUT=ROOT/'runtime/test-evidence/tradecase/2026-10-22/T06'
stage=sys.argv[1];report=dict(stage=stage,status='FAIL',physical_writes=0,checks=[])
try:
    with oracle_connection()as c:
        q=c.cursor();q.execute("select CANONICAL_REQUEST from RRL_STOCK_OPERATION where OPERATION_ID='HP22e73b21aff0.stock.attach'and STATE='APPLIED'")
        request=q.fetchone()[0];request=request if isinstance(request,dict)else json.loads(request.read()if hasattr(request,'read')else request)
        for actor in ['admin','NO_HU_OWNER_GRANT']:
            reason=None
            try:q.callproc('RRL_HU_EXEC_ACCESS.assert_request',[json.dumps(request),actor])
            except oracledb.DatabaseError as exc:reason=str(exc.args[0]).split('\n',1)[0]
            expected=None if actor=='admin'else'HU_CURRENT_WARE_EXECUTION_FORBIDDEN'if stage=='rollback'else'TRADE_OWNER_ACCESS_DENIED'
            assert reason is None if expected is None else expected in(reason or''),(stage,actor,reason)
            report['checks'].append(dict(actor=actor,reason=reason))
        q.execute("select count(*)from USER_OBJECTS where STATUS='INVALID'");assert q.fetchone()[0]==0
        report['status']='PASS'
finally:(OUT/('hu-replay-'+stage+'.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
