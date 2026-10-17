"""Live HTTP negative close boundary: unfinished isolated CASE cannot close."""
import json,sys
from pathlib import Path
import requests
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'api/wms_api_server')]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
g=OracleGateway();fixture=json.loads((ROOT/'reports/retailcase/2026-10-15/assembly-scale/native-acceptance.json').read_text(encoding='utf-8'));actor=fixture['fixture']['operator']
secret=g.fetch_all('select PASS from RUSERS where ID=:a',dict(a=actor))[0]['pass']
op='ASM15.CLOSE.NEGATIVE1031'
before=g.fetch_all('select count(*) N from RRL_CASE_PICK_EVENT where OFFLINE_EVENT_ID=:op',dict(op=op))[0]['n']
assert before==0
s=requests.Session();s.auth=(actor,secret);base='http://127.0.0.1:8088/api/inventory/assembly-scale'
a=s.get(base+'/sessions/ASM15.S1031',timeout=20);assert a.status_code==200,a.status_code
body=dict(operation_id=op,expected_content_version=a.json()['content_version'])
r=s.post(base+'/sessions/ASM15.S1031/close',json=body,timeout=20)
assert r.status_code==409 and r.json()['detail']=='CASE_OPEN_LINES_REMAIN',(r.status_code,r.text)
spoof=s.post(base+'/sessions/ASM15.S1031/close',json={**body,'actor':'admin'},timeout=20);assert spoof.status_code==422
foreign=requests.post(base+'/sessions/ASM15.S1031/close',json=body,auth=('admin','admin123'),timeout=20);assert foreign.status_code==403,(foreign.status_code,foreign.text)
assert g.fetch_all('select count(*) N from RRL_CASE_PICK_EVENT where OFFLINE_EVENT_ID=:op',dict(op=op))[0]['n']==0
stock=g.fetch_all("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA='FULL.QA:d9a5c53b54' and CELL='QGd9a5c53b54'")[0];assert stock==dict(remain=20,hard_reserved_base=20)
report=dict(status='PASS',checks=['ordinary_terminal_identity_reaches_existing_owner','open_lines_native_owner_refusal','browser_actor_forbidden','other_actor_denied','no_close_event','P20H20_unchanged'],business_stock_committed=False)
(ROOT/'reports/retailcase/2026-10-15/assembly-scale/close-http-negative.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))
