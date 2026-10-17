"""Explicit owner-approved TEST reconciliation OPC -> actual HTTP/native proof.

Does not create operator/controller consent and refuses non-RECONCILE queues.
"""
import argparse
import asyncio
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
from assembly_opc_native_smoke import load_fixture_server
from warehouse_task_scoped_complete_smoke import OracleGateway,snapshot
from api.wms_api_server.app.modules.integrations.infrastructure.scale_opc_profile import OpcScaleProfile
from api.wms_api_server.app.modules.integrations.infrastructure.scale_opc_client import Opc40200Client
from api.wms_api_server.app.modules.integrations.infrastructure.scale_device_lease import SqliteScaleDeviceLease
from api.wms_api_server.app.modules.integrations.infrastructure.scale_bundle_journal import SqliteScaleBundleJournal
from api.wms_api_server.app.modules.integrations.infrastructure.scale_outbox import SqliteScaleOutbox
from api.wms_api_server.app.modules.integrations.infrastructure.assembly_scale_http import HttpAssemblyScaleGateway
from api.wms_api_server.app.modules.integrations.application.assembly_opc_capture import OpcAssemblyCapture
from api.wms_api_server.app.modules.integrations.application.assembly_scale_gateway import AssemblyScaleWorker
from api.wms_api_server.app.modules.integrations.application.scale_evidence_delivery import deliver_evidence


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--reconciliation-id',required=True)
    parser.add_argument('--test-gross-kg',required=True)
    args=parser.parse_args();g=OracleGateway();device='ASM15.CASE1032';sender='ASM15.GW1032'
    requested=Decimal(args.test_gross_kg);assert requested.is_finite()and requested>0
    password=json.loads((ROOT/'runtime/assembly-qa-secrets.json').read_text(encoding='utf-8-sig'))[sender]
    if isinstance(password,dict):password=password['password']
    api=HttpAssemblyScaleGateway('http://127.0.0.1:8088',sender,password,allow_loopback_http=True)
    items=api.requests(device);assert len(items)==1 and items[0]['phase']=='RECONCILE'and items[0]['reconciliation_id']==args.reconciliation_id,items
    request=items[0]
    # The only allowed live fixture path restores its prior accepted baseline, not a stock delta.
    assert requested==Decimal(request['expected_before_kg'])
    before=snapshot(g,{})
    marker=g.fetch_all('select nvl(max(LOG_ID),0) N from RRL_SQL_SLOW_LOG')[0]['n']
    assert g.fetch_all('select STATE from RRL_ASM_RECONCILIATION where RECONCILIATION_ID=:id',{'id':args.reconciliation_id})==[{'state':'AUTHORIZED'}]
    current=g.fetch_all('select LAST_WEIGHT_KG,LAST_CONTENT_VERSION from RRL_ASSEMBLY_SESSION where SESSION_ID=:id',{'id':request['session_id']})
    runtime=ROOT/'runtime/assembly-opc-reconciliation1032';runtime.mkdir(parents=True,exist_ok=True)
    bundle=SqliteScaleBundleJournal(runtime/'bundles.sqlite');box=SqliteScaleOutbox(runtime/'captures.sqlite');rawbox=SqliteScaleOutbox(runtime/'raw.sqlite',max_packet_bytes=131072)
    bundle.reconcile(box,rawbox)
    results={}
    async def scenario():
        async with load_fixture_server()(runtime)as(profile,state):
            data=dict(profile.data);data.update(device_id=device,station_id='TEST_RECON1032')
            passport=runtime/'commissioned-test-profile.json';passport.write_text(json.dumps(data,sort_keys=True,indent=2),encoding='utf-8')
            actual=OpcScaleProfile.load(passport);reader=Opc40200Client(actual)
            capture=OpcAssemblyCapture(reader,SqliteScaleDeviceLease(runtime/'lease.sqlite'),actual.data,actual.digest,bundle)
            worker=AssemblyScaleWorker(api,box,device,time.time)
            state.update(gross=float(requested),zero=False);await reader.connect()
            try:
                body,raw=await capture.capture(request)
                bundle.reconcile(box,rawbox)
                result=await asyncio.to_thread(worker.cycle,body)
                assert result['status']=='CAPTURE_ARCHIVED'and result['stock_outcome']=='NO_STOCK_EFFECT_RECONCILIATION',result
                evidence=await asyncio.to_thread(deliver_evidence,api.post_evidence,rawbox,time.time())
                assert evidence=={'status':'EVIDENCE_ARCHIVED','binding':'MATCHED'},evidence
                results.update(capture=result,evidence=evidence,source_sha256=hashlib.sha256(body).hexdigest().upper(),evidence_sha256=hashlib.sha256(raw).hexdigest().upper(),capture_id=request['capture_id'])
            finally:await reader.disconnect()
    asyncio.run(scenario())
    assert snapshot(g,{})==before
    assert g.fetch_all('select LAST_WEIGHT_KG,LAST_CONTENT_VERSION from RRL_ASSEMBLY_SESSION where SESSION_ID=:id',{'id':request['session_id']})==current
    assert g.fetch_all('select STATE from RRL_ASSEMBLY_SESSION where SESSION_ID=:id',{'id':request['session_id']})==[{'state':'OPEN'}]
    assert g.fetch_all('select STATE from RRL_ASSEMBLY_STEP where STEP_ID=:id',{'id':request['step_id']})==[{'state':'CANCELLED'}]
    assert g.fetch_all('select STATE from RRL_ASM_RECONCILIATION where RECONCILIATION_ID=:id',{'id':args.reconciliation_id})==[{'state':'COMPLETED'}]
    assert g.fetch_all('select count(*) N from RRL_ASSEMBLY_STEP_USE where STEP_ID=:id',{'id':request['step_id']})[0]['n']==0
    assert g.fetch_all('select count(*) N from RRL_STOCK_OPERATION where OPERATION_ID=:op',{'op':'ASM15.PICK1032'})[0]['n']==0
    report=dict(status='PASS',reconciliation_id=args.reconciliation_id,results=results,stock_changed=False,accepted_baseline_unchanged=True,content_version_unchanged=True,step='CANCELLED',session='OPEN',physical_hardware=False,immutable_test_history_retained=True,
        slow_sql=g.fetch_all('select *from(select LOG_ID,ELAPSED_MS,SQL_TEXT from RRL_SQL_SLOW_LOG where LOG_ID>:marker order by ELAPSED_MS desc)where rownum<=10',{'marker':marker}))
    path=ROOT/'reports/retailcase/2026-10-15/assembly-scale/opc-reconciliation-http-report.json';path.write_text(json.dumps(report,indent=2,default=str),encoding='utf-8');print(json.dumps(report,default=str))
if __name__=='__main__':main()
