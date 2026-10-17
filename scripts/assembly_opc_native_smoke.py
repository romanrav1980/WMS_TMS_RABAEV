"""Actual encrypted localhost OPC -> live WMS HTTP/native TEST1032 discrepancy.

Owner-authorized fixed fixture only. Never sends an admitted AFTER stock command.
"""
import asyncio
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
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


def load_fixture_server():
    spec=importlib.util.spec_from_file_location('opc_test_fixture',ROOT/'tests/retailcase/test_scale_opc_client.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.opc_fixture


def main():
    fixture=json.loads((ROOT/'reports/retailcase/2026-10-15/assembly-scale/opc-fixture.json').read_text(encoding='utf-8-sig'))
    expected=fixture['gateway_request'];assert expected['device_id']=='ASM15.CASE1032'and expected['phase']=='BEFORE'
    secrets=json.loads((ROOT/'runtime/assembly-qa-secrets.json').read_text(encoding='utf-8-sig'))
    password=secrets['ASM15.GW1032']
    if isinstance(password,dict):password=password['password']
    api=HttpAssemblyScaleGateway('http://127.0.0.1:8088','ASM15.GW1032',password,allow_loopback_http=True)
    g=OracleGateway();before=snapshot(g,{})
    marker=g.fetch_all('select nvl(max(LOG_ID),0) N from RRL_SQL_SLOW_LOG')[0]['n']
    assert g.fetch_all('select count(*) N from RRL_STOCK_OPERATION where OPERATION_ID=:op',{'op':'ASM15.PICK1032'})[0]['n']==0
    runtime=ROOT/'runtime/assembly-opc-native1032';runtime.mkdir(parents=True,exist_ok=True)
    bundle=SqliteScaleBundleJournal(runtime/'bundles.sqlite');box=SqliteScaleOutbox(runtime/'captures.sqlite');rawbox=SqliteScaleOutbox(runtime/'raw.sqlite',max_packet_bytes=131072)
    bundle.reconcile(box,rawbox)
    requests=api.requests(expected['device_id']);assert len(requests)==1 and requests[0]==expected,requests
    results=[]
    async def scenario():
        async with load_fixture_server()(runtime)as(profile,state):
            data=dict(profile.data);data.update(device_id=expected['device_id'],station_id=fixture['session']['post_cell'])
            passport=runtime/'commissioned-test-profile.json';passport.write_text(json.dumps(data,sort_keys=True,indent=2),encoding='utf-8')
            actual=OpcScaleProfile.load(passport);reader=Opc40200Client(actual)
            lease=SqliteScaleDeviceLease(runtime/'device-lease.sqlite')
            capture=OpcAssemblyCapture(reader,lease,actual.data,actual.digest,bundle)
            worker=AssemblyScaleWorker(api,box,expected['device_id'],time.time)
            await reader.connect()
            try:
                for phase,weight in [('BEFORE',.5),('AFTER',3.5)]:
                    request=(await asyncio.to_thread(api.requests,expected['device_id']))[0]
                    assert request['phase']==phase,request
                    state.update(gross=weight,zero=False)
                    body,raw=await capture.capture(request)
                    assert float(json.loads(body)['samples'][-1]['weight_kg'])==weight
                    bundle.reconcile(box,rawbox)
                    result=await asyncio.to_thread(worker.cycle,body)
                    assert result['status']=='CAPTURE_ARCHIVED',result
                    rawresult=await asyncio.to_thread(deliver_evidence,api.post_evidence,rawbox,time.time())
                    assert rawresult['status']=='EVIDENCE_ARCHIVED',rawresult
                    results.append(dict(phase=phase,weight_kg=str(weight),capture_id=request['capture_id'],capture_body_sha256=hashlib.sha256(body).hexdigest().upper(),raw_body_sha256=hashlib.sha256(raw).hexdigest().upper(),capture=result,evidence=rawresult))
                    target='ARMED'if phase=='BEFORE'else'DISCREPANCY'
                    assert g.fetch_all('select STATE from RRL_ASSEMBLY_STEP where STEP_ID=:id',{'id':expected['step_id']})==[{'state':target}]
            finally:await reader.disconnect()
    asyncio.run(scenario())
    assert snapshot(g,{})==before
    assert g.fetch_all('select STATE from RRL_ASSEMBLY_SESSION where SESSION_ID=:id',{'id':expected['session_id']})==[{'state':'BLOCKED'}]
    assert g.fetch_all('select count(*) N from RRL_ASSEMBLY_STEP_USE where STEP_ID=:id',{'id':expected['step_id']})[0]['n']==0
    assert g.fetch_all('select count(*) N from RRL_STOCK_OPERATION where OPERATION_ID=:op',{'op':'ASM15.PICK1032'})[0]['n']==0
    assert g.fetch_all('select count(*) N from USER_OBJECTS where STATUS=\'INVALID\'')[0]['n']==0
    assert box.claim(time.time())is None and rawbox.claim(time.time())is None
    report=dict(status='PASS',results=results,stock_unchanged=True,stock_operation_created=False,step_use_created=False,session_state='BLOCKED',step_state='DISCREPANCY',native_mutations='TEST_CAPTURE_AND_RAW_ARCHIVES_ONLY',physical_hardware=False,local_encrypted_opc=True,immutable_test_history_retained=True,
      slow_sql=g.fetch_all('select *from(select LOG_ID,ELAPSED_MS,SQL_TEXT from RRL_SQL_SLOW_LOG where LOG_ID>:marker order by ELAPSED_MS desc)where rownum<=10',{'marker':marker}))
    out=ROOT/'reports/retailcase/2026-10-15/assembly-scale/opc-native-http-report.json';out.write_text(json.dumps(report,indent=2,default=str),encoding='utf-8')
    print(json.dumps(report,default=str))
if __name__=='__main__':main()
