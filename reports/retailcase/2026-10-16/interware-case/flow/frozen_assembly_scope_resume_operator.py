"""Resume exact setup after known OBJECT_NOT_FOUND, without recreating resources."""
from pathlib import Path
import sys,json
from datetime import datetime,timedelta,timezone
sys.path.insert(0,str(Path(__file__).parent))
import assembly_scope_fixture as f
from app.modules.inventory.infrastructure.case_labels import CaseLabels
from app.modules.inventory.contracts_case_labels import CaseSsccLabelRequest
from app.modules.resources.infrastructure.case_resource_commands import CaseResourceCommands
from app.modules.resources.contracts_case_resource import CaseResourceCommand
x=json.loads((f.BASE/'fixture.json').read_text());g=f.OracleGateway()
out=f.BASE/'operator-setup.json';report=json.loads(out.read_text())
assert report['flat_revoked']['deleted']==1 and x['resource_session_id']>0
assert not g.fetch_all('select ASSIGNMENT_ID from RRL_ACCESS_ASSIGNMENT where ASSIGNMENT_ID=:a',{'a':x['assignment']})
def save():out.write_text(json.dumps(report,indent=2,default=str),encoding='utf-8');f.save(x)
f.acl(g,x,'OBJECT_SAVE',dict(kind='WAREHOUSE',object_id=str(x['warehouse_id']),title=f.NOTE,active=True,expected_version=0),'WARE.OBJECT')
now=datetime.now(timezone.utc)
f.acl(g,x,'ASSIGN',dict(assignment_id=x['assignment'],username=x['actor'],role_id=x['role'],scope_kind='WAREHOUSE',scope_id=str(x['warehouse_id']),valid_from=(now-timedelta(minutes=1)).isoformat(),valid_until=(now+timedelta(hours=6)).isoformat(),expected_version=0,reason=f.NOTE),'ASSIGN.AFTER.OBJECT')
source=(Path(__file__).parent/'assembly_scope_setup_operator.py').read_text(encoding='utf-8')
tail=source.split("t=x['case_before'];",1)[1]
exec(compile("t=x['case_before'];"+tail,'<reviewed remainder setup>','exec'))
