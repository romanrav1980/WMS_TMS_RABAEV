"""Read/replay persisted actual OPC reconciliation provenance; every test mutation rolls back."""
import sys,json
from pathlib import Path
from time import perf_counter
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'api/wms_api_server')]
from opc_scale_evidence_native_smoke import native,rejected,text
from app.db import oracle_connection
from app.modules.integrations.contracts_scale_evidence import AssemblyReconciliationEvidence
with oracle_connection() as con:
 c=con.cursor();c.execute("select to_clob(SOURCE_JSON),RECORDED_BY,EVIDENCE_SHA256 from RRL_OPC_SCALE_EVIDENCE where CAPTURE_KIND='WAREHOUSE_ASSEMBLY_RECON' and CAPTURE_DEVICE='ASM15.CASE1032'");row=c.fetchone();assert row
 wire=text(row[0]);actor=row[1];body=json.loads(wire)
 assert AssemblyReconciliationEvidence.model_validate(body).digest()==row[2]
 c.execute('select DELETED from RUSERS where ID=:a',a=actor);deleted=c.fetchone()[0]
 c.execute('select count(*) from RRL_OPC_SCALE_EVIDENCE');before=c.fetchone()[0];con.rollback()
 try:
  if deleted:
   rejected(lambda:native(c,'archive',[wire,actor]),'OPC_EVIDENCE_CURRENT_SENDER_REQUIRED')
  c.execute('update RUSERS set DELETED=0 where ID=:a',a=actor)
  t=perf_counter();first=native(c,'describe',['WAREHOUSE_ASSEMBLY_RECON',body['device_id'],body['capture_id'],actor]);ms=round((perf_counter()-t)*1000,3)
  assert first['binding']=='MATCHED' and first['protocol_version']=='1.2' and first['stock_posted'] is False
  assert native(c,'archive',[wire,actor])==first
  for key in ('session_id','step_id','reconciliation_id','tare_capture_key'):
   wrong=json.loads(wire);wrong['zero_reference'][key]='D'*64 if key=='tare_capture_key' else 'TEST.WRONG.REFERENCE'
   changed=AssemblyReconciliationEvidence.model_validate(wrong).canonical_bytes().decode()
   rejected(lambda:native(c,'archive',[changed,actor]),'OPC_EVIDENCE_PAYLOAD_CONFLICT')
  rejected(lambda:native(c,'describe',['WAREHOUSE_ASSEMBLY_RECON',body['device_id'],body['capture_id'],'admin']),'OPC_EVIDENCE_DEVICE_SENDER_REQUIRED')
 finally:con.rollback()
 c.execute('select DELETED from RUSERS where ID=:a',a=actor);assert c.fetchone()[0]==deleted
 c.execute('select count(*) from RRL_OPC_SCALE_EVIDENCE');assert c.fetchone()[0]==before
 c.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA='FULL.QA:d9a5c53b54' and CELL='QGd9a5c53b54'");assert c.fetchone()==(20,20)
 c.execute("select count(*) from USER_OBJECTS where STATUS='INVALID'");assert c.fetchone()[0]==0
 con.rollback()
r=dict(status='PASS',actual_encrypted_opc_record=True,physical_hardware=False,binding='MATCHED',exact_replay=True,changed_existing_reference='PAYLOAD_CONFLICT',reference_fields=4,retired_sender_denied=bool(deleted),foreign_sender_denied=True,temporary_undelete_rolled_back=True,evidence_count_unchanged=True,source_P=20,source_H=20,read_ms=ms,sql_decision='PK identity lookup retained; no index needed for bounded replay/read')
(ROOT/'reports/retailcase/2026-10-15/assembly-scale/reconciliation-evidence-native.json').write_text(json.dumps(r,indent=2),encoding='utf-8');print(json.dumps(r))
