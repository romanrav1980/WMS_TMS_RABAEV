"""Repeat interface checks against the saved pre-return context; all physical POSTs are intercepted."""
import os,sys,json,subprocess
from pathlib import Path
sys.path.insert(0,'.')
from tools.mcp.tms_mcp_server import oracle_connection
f=json.loads(Path('runtime/test-evidence/tradecase/2026-10-19/T11/return-ui-fixture.json').read_text())
with oracle_connection()as c:
 q=c.cursor();q.execute('select PASS from RUSERS where ID=:a and nvl(DELETED,0)=0',a=f['actor']);r=q.fetchone();assert r
 env=dict(os.environ,TRADECASE_UI_USER=f['actor'],TRADECASE_UI_PASSWORD=r[0],TRADECASE_RETURN_FIXTURE_ONLY='1')
raise SystemExit(subprocess.run(['node','tests/tradecase/return_ui_check.cjs'],env=env).returncode)
