"""Real native assembly binding proof using persisted simulated captures; caller rollback."""
from copy import deepcopy
import json,sys
from pathlib import Path
from time import perf_counter
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'api/wms_api_server')]
from opc_scale_evidence_native_smoke import fixture_envelope,native,rejected
from app.db import oracle_connection
from app.modules.integrations.contracts_scale_evidence import AssemblyScaleEvidence
checks=[];timings=[]
with oracle_connection() as con:
 c=con.cursor()
 c.execute("select c.DEVICE_ID,c.CAPTURE_ID,c.SOURCE_SHA256,c.RECORDED_BY,c.SESSION_ID,c.STEP_ID,c.PHASE,s.TARE_CAPTURE_KEY from RRL_ASSEMBLY_CAPTURE c join RRL_ASSEMBLY_SESSION s on s.SESSION_ID=c.SESSION_ID where c.SESSION_ID='ASM15.S1031' order by c.PHASE")
 rows=c.fetchall();assert len(rows)==2
 c.execute('select count(*) from RRL_OPC_SCALE_EVIDENCE');before=c.fetchone()[0]
 con.rollback()
 try:
  for device,capture,sha,actor,session,step,phase,tare in rows:
   b=fixture_envelope();b.pop('zero_observation')
   b.update(protocol_version='1.1',capture_kind='WAREHOUSE_ASSEMBLY',device_id=device,capture_id=capture,capture_sha256=sha,station_id='TEST_NATIVE_BINDING_NOT_HARDWARE',zero_reference=dict(session_id=session,step_id=step,phase=phase,tare_capture_key=tare))
   for field,value in [('session_id','WRONG'),('step_id','WRONG'),('phase','BEFORE' if phase=='AFTER' else 'AFTER'),('tare_capture_key','D'*64)]:
    wrong=deepcopy(b);wrong['zero_reference'][field]=value
    rejected(lambda: native(c,'archive',[AssemblyScaleEvidence.model_validate(wrong).canonical_bytes().decode(),actor]),'OPC_ASSEMBLY_ZERO_REFERENCE_CONFLICT')
   wrong=deepcopy(b);wrong['capture_sha256']='D'*64
   rejected(lambda:native(c,'archive',[AssemblyScaleEvidence.model_validate(wrong).canonical_bytes().decode(),actor]),'OPC_EVIDENCE_CAPTURE_HASH_CONFLICT')
   wire=AssemblyScaleEvidence.model_validate(b).canonical_bytes().decode();t=perf_counter()
   first=native(c,'archive',[wire,actor]);timings.append(round((perf_counter()-t)*1000,3))
   assert first['binding']=='MATCHED' and first['protocol_version']=='1.1' and first['stock_posted'] is False
   assert first['evidence_sha256']==AssemblyScaleEvidence.model_validate(b).digest()
   assert native(c,'archive',[wire,actor])==first
   assert native(c,'describe',['WAREHOUSE_ASSEMBLY',device,capture,actor])==first
   wrong=deepcopy(b);wrong['profile_sha256']='E'*64
   rejected(lambda:native(c,'archive',[AssemblyScaleEvidence.model_validate(wrong).canonical_bytes().decode(),actor]),'OPC_EVIDENCE_PAYLOAD_CONFLICT')
   rejected(lambda:native(c,'describe',['WAREHOUSE_ASSEMBLY',device,capture,'admin']),'OPC_EVIDENCE_DEVICE_SENDER_REQUIRED')
   c.execute('update RUSERS set DELETED=1 where ID=:a',a=actor)
   rejected(lambda:native(c,'archive',[wire,actor]),'OPC_EVIDENCE_CURRENT_SENDER_REQUIRED')
   c.execute('update RUSERS set DELETED=0 where ID=:a',a=actor)
   checks.append(dict(phase=phase,matched=True,exact_replay=True,readback=True,bad_refs=4,wrong_hash=True,changed_body=True,foreign=True,revoked=True))
  for stmt in ('update RRL_OPC_SCALE_EVIDENCE set RECORDED_BY=RECORDED_BY','delete from RRL_OPC_SCALE_EVIDENCE'):
   rejected(lambda:c.execute(stmt),'OPC_EVIDENCE_APPEND_ONLY')
 finally:con.rollback()
 c.execute('select count(*) from RRL_OPC_SCALE_EVIDENCE');assert c.fetchone()[0]==before
 c.execute("select count(*) from USER_OBJECTS where STATUS='INVALID'");assert c.fetchone()[0]==0
 c.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA='FULL.QA:d9a5c53b54' and CELL='QGd9a5c53b54'");assert c.fetchone()==(20,20)
 con.rollback()
report=dict(status='PASS',checks=checks,archive_ms=timings,raw='SIMULATED_TEST_NOT_HARDWARE',business_stock_committed=False,evidence_count_restored=True,source_P=20,source_H=20,invalid=0,sql_decision='Indexed device/capture identities; no index needed for bounded archive; no physical wait in transaction')
(ROOT/'reports/retailcase/2026-10-15/assembly-scale/evidence-native.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
