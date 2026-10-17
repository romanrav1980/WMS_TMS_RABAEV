"""Explicitly released phase-fenced client of the existing TEST1136 OPC server.

BEFORE is metadata only. AFTER may cause native auto-consented StockPosting;
root must authorize it separately and --allow-stock-commit is mandatory.
This client never creates consent, steps, placed commands or fixture weights.
"""
import argparse
import asyncio
import hashlib
import json
from pathlib import Path
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
from warehouse_task_scoped_complete_smoke import OracleGateway
from api.wms_api_server.app.modules.integrations.infrastructure.scale_opc_profile import OpcScaleProfile
from api.wms_api_server.app.modules.integrations.infrastructure.scale_opc_client import Opc40200Client
from api.wms_api_server.app.modules.integrations.infrastructure.scale_device_lease import SqliteScaleDeviceLease
from api.wms_api_server.app.modules.integrations.infrastructure.scale_bundle_journal import SqliteScaleBundleJournal
from api.wms_api_server.app.modules.integrations.infrastructure.scale_outbox import SqliteScaleOutbox
from api.wms_api_server.app.modules.integrations.infrastructure.assembly_scale_http import HttpAssemblyScaleGateway
from api.wms_api_server.app.modules.integrations.application.assembly_opc_capture import OpcAssemblyCapture
from api.wms_api_server.app.modules.integrations.application.assembly_scale_gateway import AssemblyScaleWorker
from api.wms_api_server.app.modules.integrations.application.scale_evidence_delivery import deliver_evidence
RUNTIME=ROOT/'runtime/assembly-opc-native1136'


def snapshot(g):
    return dict(stock=g.fetch_all("select UID_POLETA,CELL,REMAIN,HARD_RESERVED_BASE,STOCK_VERSION from RRL_REMAINS where UID_POLETA='REUSE.RETURN:e6c16d0bbd'order by CELL"),
        case=g.fetch_all('select STATUS,CONTENT_VERSION,PICKED_QTY,LEGACY_SBORKA_PALLET_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=1136'))


async def run(args):
    if args.phase=='AFTER'and not args.allow_stock_commit:raise ValueError('AFTER requires separate root quantity authorization')
    profile=OpcScaleProfile.load(ROOT/'runtime/warehouse-opc-native1136/commissioned-test-profile.json')
    assert profile.data['device_id']=='WHREQ15.SCALE'
    secret=json.loads((ROOT/'runtime/warehouse-weigh-qa-secrets.json').read_text(encoding='utf-8-sig'))['WHREQ15.GW']
    if isinstance(secret,dict):secret=secret['password']
    api=HttpAssemblyScaleGateway('http://127.0.0.1:8088','WHREQ15.GW',secret,allow_loopback_http=True)
    g=OracleGateway();before=snapshot(g)
    queue=await asyncio.to_thread(api.requests,profile.data['device_id'])
    assert len(queue)==1,queue
    request=queue[0]
    assert request['session_id']=='WHREQ15.ASM.S1136'and request['case_task_id']==1136 and request['phase']==args.phase,request
    assert request['scan_container']=='090000000000008014'
    operation=request['operation_id']
    RUNTIME.mkdir(parents=True,exist_ok=True)
    box=SqliteScaleOutbox(RUNTIME/'captures.sqlite');rawbox=SqliteScaleOutbox(RUNTIME/'raw.sqlite',max_packet_bytes=131072)
    bundle=SqliteScaleBundleJournal(RUNTIME/'bundles.sqlite')
    if not args.allow_stock_commit:
        assert all(json.loads(body)['phase']!='AFTER'for body in box.bodies()),'Pending/history AFTER requires explicit stock review'
    worker=AssemblyScaleWorker(api,box,profile.data['device_id'],time.time)
    bundle.reconcile(box,rawbox)
    await asyncio.to_thread(worker.cycle)
    await asyncio.to_thread(deliver_evidence,api.post_evidence,rawbox,time.time())
    assert box.pending_count()==0 and rawbox.pending_count()==0,'Drain original exact archives before new measurement'
    reader=Opc40200Client(profile)
    capture=OpcAssemblyCapture(reader,SqliteScaleDeviceLease(ROOT/'runtime/opc-device-leases.sqlite'),profile.data,profile.digest,bundle)
    marker=g.fetch_all('select nvl(max(LOG_ID),0)N from RRL_SQL_SLOW_LOG')[0]['n']
    await reader.connect()
    try:body,raw=await capture.capture(request)
    finally:await reader.disconnect()
    assert json.loads(body)['phase']==args.phase
    bundle.reconcile(box,rawbox)
    archived=await asyncio.to_thread(worker.cycle)
    evidence=await asyncio.to_thread(deliver_evidence,api.post_evidence,rawbox,time.time())
    assert archived['status']=='CAPTURE_ARCHIVED'and evidence==dict(status='EVIDENCE_ARCHIVED',binding='MATCHED'),(archived,evidence)
    step=g.fetch_all('select STATE,OPERATION_ID,SOURCE_VERSION,FACT_QTY from RRL_ASSEMBLY_STEP where STEP_ID=:step_id',{'step_id':request['step_id']})[0]
    after=snapshot(g)
    usage=g.fetch_all('select count(*)N from RRL_ASSEMBLY_STEP_USE where STEP_ID=:step_id',{'step_id':request['step_id']})[0]['n']
    operations=g.fetch_all('select OPERATION_ID,COMMAND_TYPE,STATE from RRL_STOCK_OPERATION where OPERATION_ID=:operation',{'operation':operation})
    if args.phase=='BEFORE':
        assert step['state']=='ARMED'and usage==0 and operations==[]and after==before
    else:
        assert step['state']=='APPLIED'and usage==1 and len(operations)==1 and operations[0]['state']=='APPLIED'
        assert sum(r['remain']for r in after['stock'])==23 and sum(r['hard_reserved_base']for r in after['stock'])==0
        assert after['case'][0]['picked_qty']==1
        assert g.fetch_all('select count(*)N from RRL_STOCK_OP_CLOCK where OPERATION_ID=:operation',{'operation':operation})[0]['n']==1
    report=dict(status='PASS',phase=args.phase,request=request,capture=archived,evidence=evidence,step=step,operation=operations,step_use_count=usage,
        source_before=before,source_after=after,physical_hardware=False,local_encrypted_opc=True,stock_committed=args.phase=='AFTER',
        body_sha256=hashlib.sha256(body).hexdigest().upper(),raw_sha256=hashlib.sha256(raw).hexdigest().upper(),
        measured_at=json.loads(body)['measured_at'],weight_kg=json.loads(body)['samples'][-1]['weight_kg'],
        slow_sql=g.fetch_all('select *from(select LOG_ID,ELAPSED_MS,SQL_TEXT from RRL_SQL_SLOW_LOG where LOG_ID>:marker order by ELAPSED_MS desc)where rownum<=10',{'marker':marker}))
    out=ROOT/f'reports/retailcase/2026-10-15/assembly-scale/opc1136-{args.phase.lower()}.json'
    out.write_text(json.dumps(report,indent=2,default=str),encoding='utf-8')
    print(json.dumps(dict(status='PASS',phase=args.phase,step_state=step['state'],stock_committed=report['stock_committed'],physical_hardware=False)))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--phase',choices=['BEFORE','AFTER'],default='BEFORE')
    parser.add_argument('--execute-phase',action='store_true');parser.add_argument('--allow-stock-commit',action='store_true')
    args=parser.parse_args()
    if not args.execute_phase:print('PREPARED_ONLY: wait for root phase release');return
    asyncio.run(run(args))


if __name__=='__main__':main()
