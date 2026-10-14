import json
from pathlib import Path
r=Path(__file__).resolve().parents[1];p=r/"scripts/ni033_wave_defer_existing_case.py";s=p.read_text(encoding="utf-8")
s=s.replace('op="WAVE.DEFER169:402"','op="WAVE.DEFER169:402.ROLLBACK"')
start=s.index(" if not already:");end=s.index(" with ThreadPoolExecutor",start)
s=s[:start]+''' q.execute("select RRL_WAVE_EXEC_ACCESS.deferred_snapshot_json(401)from dual");raw=q.fetchone()[0];snap=json.loads(raw.read()if hasattr(raw,"read")else raw);assert snap["eligible"],snap
 command=StockCommand(operation_id="WAVE.DEFER169:401.UNCOMMITTED",command_type="WAVE_EXECUTION_FINISH",actor="admin",lines=(),source={"wave_id":401},metadata={"disposition":body["disposition"],"reason":body["reason"]})
 result=q.var(oracledb.DB_TYPE_CLOB);request=q.var(oracledb.DB_TYPE_CLOB);request.setvalue(0,command.canonical_json())
 q.callproc("RRL_STOCK_POSTING_API.prepare_command",[request,"admin",result,None]);assert result.getvalue()is None
 try:
  q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[result])
  q.execute("select STATUS from RRL_PICK_WAVE where PICK_WAVE_ID=401");assert q.fetchone()[0]=="DONE"
 finally:
  c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 q.execute("select STATUS from RRL_PICK_WAVE where PICK_WAVE_ID=401");assert q.fetchone()[0]=="LAUNCHED"
 q.execute("select count(*)from RRL_STOCK_OPERATION where OPERATION_ID='WAVE.DEFER169:401.UNCOMMITTED'");assert q.fetchone()[0]==0
'''+s[end:]
s=s.replace('native late rollback restores wave/operation','native401 late rollback restores wave/operation; legacy committed402 wrapper result preserved')
print(json.dumps({str(p.relative_to(r)):s}))
