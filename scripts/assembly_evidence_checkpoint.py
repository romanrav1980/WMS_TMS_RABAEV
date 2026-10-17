"""Checkpoint exact live source before additive assembly evidence migration."""
import hashlib,json,re,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'api/wms_api_server')]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
g=OracleGateway()
f=ROOT/'db/migrations/2026-10-15_assembly_evidence_binding'
assert not (f/'checkpoint.json').exists(),'Do not overwrite before image'
identity=g.fetch_all("select USER SCHEMA_NAME,sys_context('USERENV','SERVICE_NAME') SERVICE_NAME from dual")[0]
assert identity['schema_name']=='RABAEV' and identity['service_name'].lower()=='orcl',identity
assert g.fetch_all("select count(*) N from USER_OBJECTS where STATUS='INVALID'")[0]['n']==0
live=''.join(r['text'] for r in g.fetch_all("select TEXT from USER_SOURCE where NAME='RRL_OPC_EVIDENCE_API' and TYPE='PACKAGE BODY' order by LINE"))
def norm(v):
    return re.sub(r'^create\s+or\s+replace\s+','',v.replace('\r','').strip(),flags=re.I).rstrip('/').strip()
assert norm(live)==norm((ROOT/'db/migrations/2026-10-15_opc_scale_evidence/body.sql').read_text(encoding='utf-8')),'Live source drift'
assert g.fetch_all("select count(*) N from USER_TABLES where TABLE_NAME in('RRL_ASSEMBLY_SESSION','RRL_ASSEMBLY_STEP','RRL_ASSEMBLY_CAPTURE')")[0]['n']==3
(f/'before_body.sql').write_text('create or replace '+live.rstrip()+'\n/\n',encoding='utf-8')
manifest=dict(migration_id='2026-10-15-assembly-evidence-binding',captured_at=datetime.now(timezone.utc).isoformat(),identity=identity,invalid_before=0,before_exact=True,status='PREPARED',recovery='Quiesced writers and zero assembly evidence required for rollback; preserve history',sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(f.glob('*.sql'))})
(f/'checkpoint.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps(dict(status='PREPARED',before_exact=True,invalid_before=0)))

