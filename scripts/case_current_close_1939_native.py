"""Root-run only N1939 scoped CLOSE negative caller-rollback proof. No goods or close commit."""
import argparse
import json
import os
from pathlib import Path
import sys
from typing import Any
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/retailcase/2026-10-15/case-scoped-close/native-1939-negative.json'


def snapshot(g:Any)->dict[str,Any]:
    return dict(task=g.fetch_all('select STATUS,ASSIGNED_TO,CONTENT_VERSION,ASSIGNMENT_VERSION,PICKED_QTY,RESOURCE_SESSION_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=1139'),
        lines=g.fetch_all('select CASE_PICK_LINE_ID,STATUS,PLANNED_QTY,PICKED_QTY from RRL_CASE_PICK_LINE where CASE_PICK_TASK_ID=1139 order by CASE_PICK_LINE_ID'),
        stock=g.fetch_all('select UID_POLETA,CELL,REMAIN,HARD_RESERVED_BASE,STOCK_VERSION from RRL_REMAINS where UID_POLETA in(:p,:c)order by UID_POLETA,CELL',{'p':'REUSE.RETURN:e6c16d0bbd','c':'CASELOT:E8EAB9A962B9D19BA5AC8FCEE19D8021895BD0:1'}),
        events=g.fetch_all('select CASE_PICK_EVENT_ID,OFFLINE_EVENT_ID,EVENT_TYPE from RRL_CASE_PICK_EVENT where CASE_PICK_TASK_ID=1139 order by CASE_PICK_EVENT_ID'))


def run()->None:
    from stock_posting_environment import load_local_oracle_environment
    load_local_oracle_environment()
    from app.db import oracle_connection
    from app.oracle_gateway import OracleGateway
    from app.transaction_gateway import TransactionGateway
    from app.modules.inventory.infrastructure.case_current_close import CaseCurrentClose
    from app.modules.inventory.contracts_case_current_close import CaseCurrentCloseInput
    from fastapi import HTTPException
    gateway=OracleGateway();before=snapshot(gateway);task=before['task'][0]
    assert task['status']=='IN_PROGRESS'and task['assigned_to']=='N1939.OP'and task['picked_qty']==0 and task['resource_session_id']==59
    assert task['assignment_version']==2 and any(r['picked_qty']<r['planned_qty']for r in before['lines'])
    checks=[]
    for suffix,target,actor,version,status,marker in [
        ('VERSION',1139,'N1939.OP',task['content_version']+1,409,'CASE_CONTENT_VERSION_CHANGED'),
        ('OPENLINES',1139,'N1939.OP',task['content_version'],409,'CASE_OPEN_LINES_REMAIN'),
        ('FOREIGN',1138,'N1939.OP',0,403,'CASE_CLOSE_CURRENT_SCOPE_REQUIRED'),
        ('INACTIVE',1139,'N1939.NOT_A_USER',task['content_version'],403,'CASE_CLOSE_CURRENT_SCOPE_REQUIRED')]:
        with oracle_connection()as connection:
            cursor=connection.cursor()
            try:
                assert cursor.callfunc('DBMS_TRANSACTION.LOCAL_TRANSACTION_ID',str,[False])is None
                body=CaseCurrentCloseInput(operation_id='N1939.CLOSE.RB.'+suffix,expected_content_version=version)
                try:CaseCurrentClose(TransactionGateway(cursor)).close(target,body,actor)
                except HTTPException as error:
                    assert error.status_code==status and marker in str(error.detail),(error.status_code,error.detail)
                else:raise AssertionError('Unexpected CLOSE acceptance '+suffix)
            finally:
                connection.rollback();cursor.callproc('RRL_STOCK_LOCK_API.clear_plan')
        assert snapshot(gateway)==before
        assert not gateway.fetch_all("select OFFLINE_EVENT_ID from RRL_CASE_PICK_EVENT where OFFLINE_EVENT_ID like 'N1939.CLOSE.RB.%'")
        checks.append(dict(name=suffix,expected_marker=marker,rollback_exact=True))
    report=dict(status='PASS_NEGATIVE_CALLER_ROLLBACK_ONLY',checks=checks,before=before,after=snapshot(gateway),quantity_effect=False,close_commits=0,
        pending=['current-role revoke after native fences requires separate canonical committed ACL window','positive CLOSE requires physically admissible fulfilled CASE, cannot follow dirty Stock transaction','actual HTTP replay/positive lifecycle under root release'])
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(report,indent=2,default=str),encoding='utf-8')
    print(json.dumps(dict(status=report['status'],checks=len(checks),close_commits=0)))


def main()->None:
    parser=argparse.ArgumentParser();parser.add_argument('--execute-caller-rollback',action='store_true');args=parser.parse_args()
    if not args.execute_caller_rollback:
        print('PREPARED_ONLY: root-run negative scoped CLOSE; no positive close or quantity command');return
    assert os.environ.get('CASE_CLOSE_1939_ROOT_RELEASE')=='1'
    assert not OUT.exists(),'Retain original report; no blind rerun'
    sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'api/wms_api_server')]
    run()


if __name__=='__main__':main()
