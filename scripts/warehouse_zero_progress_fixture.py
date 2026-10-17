"""Root-approved empty metadata fixture; explicit stage/cleanup, no picking or reservations."""
import json
import os
import sys
from pathlib import Path
from typing import Any
import oracledb
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'api/wms_api_server')]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
from app.services.picking_service import PickingService
from app.schemas import PickWaveCreateRequest
from app.modules.inventory.public import StockCommand,StockPosting
from app.modules.inventory.infrastructure.case_labels import CaseLabels
from app.modules.inventory.contracts_case_labels import CaseSsccLabelRequest
from app.modules.inventory.infrastructure.configuration import ReceiptConfiguration
from app.modules.inventory.infrastructure.metadata_transactions import receipt_task_metadata
from app.modules.platform.public import stock_configuration_transaction,read_oracle_json

WARE=13583852
CELL='QIPcdbf4c0962'
PREFIX='WHZERO15.AK06'
DEVICE='WHZERO15.AK06.SCALE'
REPORT=ROOT/'reports/retailcase/2026-10-15/warehouse-weigh-request/zero-fixture.json'
NOTE='SIMULATED_TEST_NOT_HARDWARE; empty root-approved ZERO UX fixture'


def save(data:dict[str,Any])->None:
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps(data,indent=2,default=str),encoding='utf-8')


def stock(g:OracleGateway)->list[dict[str,Any]]:
    return g.fetch_all("select UID_POLETA,CELL,REMAIN,HARD_RESERVED_BASE,STOCK_VERSION from RRL_REMAINS where UID_POLETA='REUSE.RETURN:e6c16d0bbd'order by CELL")


def cancel_command(data:dict[str,Any])->StockCommand:
    return StockCommand(PREFIX+'.CANCEL','WAVE_CANCEL','admin',(),dict(document_type='PICK_WAVE',document_id=data['wave']),
        metadata=dict(reason=NOTE,only_cancelled_replenishment=0,reservation_kind=None))


class RollbackTrial(Exception):
    pass


def cancel_preflight(g:OracleGateway,data:dict[str,Any])->None:
    before=stock(g);command=cancel_command(data)
    prior=g.fetch_all('select STATE from RRL_STOCK_OPERATION where OPERATION_ID=:id',{'id':command.operation_id})
    if prior:
        assert prior==[{'state':'APPLIED'}],'Uncertain original cancellation needs review'
        return
    try:
        with g.transaction('Empty QA wave canonical cancellation preflight rollback')as c:
            out=c.var(oracledb.DB_TYPE_CLOB)
            try:
                c.callproc('RRL_STOCK_POSTING_API.prepare_command',[command.canonical_json(),'admin',out])
                if out.getvalue()is None:c.callproc('RRL_STOCK_POSTING_API.execute_prepared',[out])
                data['cancel_preflight_result']=read_oracle_json(out.getvalue())
            finally:c.callproc('RRL_STOCK_POSTING_API.reset_connection')
            raise RollbackTrial()
    except RollbackTrial:
        pass
    assert stock(g)==before
    assert g.fetch_all('select OPERATION_ID from RRL_STOCK_OPERATION where OPERATION_ID=:id',{'id':command.operation_id})==[]
    data['canonical_cancel_preflight_rollback']=True;save(data)


def stage(g:OracleGateway)->None:
    assert os.environ.get('RUN_APPROVED_ZERO_METADATA_STAGE')=='1','Root-approved explicit stage required'
    assert not REPORT.exists(),'Resume original numeric IDs, never fork metadata fixture'
    data=dict(prefix=PREFIX,device=DEVICE,ware=WARE,cell=CELL,source_before=stock(g),state='STAGING',physical_hardware=False)
    data['wave']=PickingService(g).create_wave(PickWaveCreateRequest(wave_code=PREFIX,wave_name=NOTE,ware_id=WARE,created_by='admin'))
    save(data)
    with receipt_task_metadata(g,NOTE,'admin','case_pick_manage')as c:
        c.execute('select CUSTOMER_ID,CUSTOMER_STORE_MAP_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=1136')
        customer,mapping=c.fetchone()
        c.execute('select RRL_CUSTOMER_ORDER_SQ.nextval,RRL_CASE_PICK_TASK_SQ.nextval from dual')
        data['order'],data['case']=[int(value)for value in c.fetchone()]
        c.execute("insert into RRL_CUSTOMER_ORDER(CUSTOMER_ORDER_ID,ORDER_NO,CUSTOMER_ID,CUSTOMER_STORE_MAP_ID,WARE_ID,STATUS,SOURCE_SYSTEM)values(:id,:code,:customer,:mapping,:ware,'IMPORTED','QA_ZERO')",
            id=data['order'],code=PREFIX,customer=customer,mapping=mapping,ware=WARE)
        c.execute("""insert into RRL_CASE_PICK_TASK(CASE_PICK_TASK_ID,PICK_WAVE_ID,CUSTOMER_ORDER_ID,CUSTOMER_ID,CUSTOMER_STORE_MAP_ID,
            SSCC,PALLET_TYPE_ID,PALLET_NO,STATUS,WARE_ID,CREATED_BY)values(:id,:wave,:order_id,:customer,:mapping,:carrier,32,1,'NEW',:ware,'admin')""",
            id=data['case'],wave=data['wave'],order_id=data['order'],customer=customer,mapping=mapping,carrier='CPZERO'+str(data['case']),ware=WARE)
    save(data)
    cancel_preflight(g,data)
    configuration=ReceiptConfiguration(g);original=configuration.get(WARE);data['warehouse_settings_before']=original;save(data)
    try:
        configuration.save(WARE,{**original,'company_prefix':'900000','extension_digit':0},'admin')
        labels=CaseLabels(g)
        data['label']=labels.issue(data['case'],CaseSsccLabelRequest(operation_id=PREFIX+'.LABEL',scan_container='CPZERO'+str(data['case']),expected_content_version=0),'admin')
        data['label_confirmation']=labels.confirm(data['case'],data['label']['sscc'],'admin');save(data)
    finally:configuration.save(WARE,original,'admin')
    with stock_configuration_transaction(g,NOTE,'admin','warehouse_settings_edit')as c:
        c.execute("""insert into RRL_WH_SCALE_DEVICE(DEVICE_ID,WARE_ID,POST_CELL,SENDER_ID,POLICY_VERSION,ACTIVE_FLAG,DEVICE_MODE,
            MEASUREMENT_BASIS,CAPACITY_KG,RESOLUTION_KG,CALIBRATION_REF,CALIBRATED_UNTIL,CHANGED_BY)
            values(:id,:ware,:cell,'WHREQ15.GW',1,1,'TEST','GROSS',100,.001,'SIMULATED_TEST_NOT_HARDWARE',systimestamp+interval '1'day,'admin')""",
            id=DEVICE,ware=WARE,cell=CELL)
    assert stock(g)==data['source_before']
    for table,column in [('RRL_PICK_WAVE_ORDER','PICK_WAVE_ID'),('RRL_CASE_PICK_LINE','CASE_PICK_TASK_ID')]:
        identity=data['case']if table=='RRL_CASE_PICK_LINE'else data['wave']
        assert g.fetch_all('select count(*)N from '+table+' where '+column+'=:id',{'id':identity})[0]['n']==0,table
    for table in ('RRL_WAREHOUSE_TASK','RRL_STOCK_RESERVATION'):
        assert g.fetch_all('select count(*)N from '+table+" where SOURCE_DOC_TYPE='PICK_WAVE'and SOURCE_DOC_ID=:id",{'id':data['wave']})[0]['n']==0
    data.update(state='EMPTY_LABELLED_CASE_READY',stock_changed=False,qualified_operator_proof=False);save(data)
    print(json.dumps({key:data[key]for key in('state','wave','case','order','device')}))


def cleanup(g:OracleGateway)->None:
    data=json.loads(REPORT.read_text(encoding='utf-8-sig'));before=stock(g)
    cancel_preflight(g,data)
    data['cancel_result']=StockPosting().post(cancel_command(data));save(data)
    with receipt_task_metadata(g,NOTE,'admin','case_pick_manage')as c:
        c.execute("""update RRL_CASE_PICK_TASK t set STATUS='CANCELLED'where t.CASE_PICK_TASK_ID=:id and t.PICK_WAVE_ID=:wave
            and t.STATUS in('NEW','CANCELLED')and t.ASSIGNED_TO is null and nvl(t.PICKED_QTY,0)=0
            and exists(select 1 from RRL_PICK_WAVE w where w.PICK_WAVE_ID=t.PICK_WAVE_ID and w.STATUS='CANCELLED')
            and not exists(select 1 from RRL_CASE_PICK_LINE l where l.CASE_PICK_TASK_ID=t.CASE_PICK_TASK_ID)
            and not exists(select 1 from RRL_ASSEMBLY_SESSION s where s.CASE_PICK_TASK_ID=t.CASE_PICK_TASK_ID)
            and not exists(select 1 from RRL_CASE_CARRIER_LOT l where l.CASE_PICK_TASK_ID=t.CASE_PICK_TASK_ID)""",id=data['case'],wave=data['wave'])
        assert c.rowcount==1,'Synthetic empty CASE retirement guard refused; preserve state'
    with receipt_task_metadata(g,NOTE,'admin','case_pick_manage')as c:
        c.execute("update RRL_CUSTOMER_ORDER set STATUS='CANCELLED'where CUSTOMER_ORDER_ID=:id and SOURCE_SYSTEM='QA_ZERO'",id=data['order'])
    with stock_configuration_transaction(g,NOTE,'admin','warehouse_settings_edit')as c:
        c.execute('update RRL_WH_SCALE_DEVICE set ACTIVE_FLAG=0,POLICY_VERSION=POLICY_VERSION+1 where DEVICE_ID=:id and ACTIVE_FLAG=1',id=DEVICE)
    assert stock(g)==before
    data.update(state='CANONICALLY_CANCELLED_METADATA_RETIRED',source_after_cleanup=stock(g),immutable_history_preserved=True);save(data)
    print(data['state'])


if __name__=='__main__':
    {'stage':stage,'cleanup':cleanup}[sys.argv[1]](OracleGateway())
