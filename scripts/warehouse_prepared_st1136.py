"""Root-approved TEST metadata ST/row/fulfillment only, rollback proof then one commit."""
import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import sys
import oracledb
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'api/wms_api_server')]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
from app.modules.platform.public import stock_configuration_transaction
UID='TEST.WHREQ15.PREPARED'
ARTICLE='REUSE.QA:cdbf4c0962'
NOTE='TEST_NOT_HARDWARE_CASE1136_PREPARED_METADATA_ONLY'
OUT=ROOT/'reports/retailcase/2026-10-15/warehouse-weigh-request/prepared-st1136.json'


class RollbackProof(Exception):pass


def baseline(g):
    return dict(stock=g.fetch_all("select UID_POLETA,CELL,REMAIN,HARD_RESERVED_BASE,STOCK_VERSION from RRL_REMAINS where UID_POLETA='REUSE.RETURN:e6c16d0bbd' order by CELL"),
        case=g.fetch_all('select STATUS,SSCC,CONTENT_VERSION,PICKED_QTY,LEGACY_SBORKA_PALLET_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=1136'))


def identities(g):
    return dict(st=g.fetch_all('select ID,PALLET_UID,ST_NUMBER,WARE_ID,CONDITION from RRL_SBORKA_PALLETS where PALLET_UID=:id or ST_NUMBER=:id',{'id':UID}),
        rows=g.fetch_all('select ID,PALLET_UID,ARTICUL,EI,QUANTITY from RRL_SBORKA_PALLET_ROWS where PALLET_UID=:id',{'id':UID}),
        fulfillment=g.fetch_all('select FULFILLMENT_ID,CUSTOMER_ORDER_ID,LEGACY_SBORKA_PALLET_ID,PALLET_UID,STATUS,FACT_QTY from RRL_CUSTOMER_ORDER_FULFILLMENT where PALLET_UID=:id',{'id':UID}))


def stage(g,rollback=False):
    # Inline the existing CONFIG transaction so the rollback occurs before its __exit__ commit.
    with stock_configuration_transaction(g,NOTE,'admin','warehouse_settings_edit')as c:
        c.execute('lock table RRL_SBORKA_PALLETS in share row exclusive mode wait 3')
        c.execute('select count(*)from RRL_SBORKA_PALLETS where PALLET_UID=:id or ST_NUMBER=:id',id=UID);assert c.fetchone()[0]==0
        c.execute('select count(*)from RRL_CUSTOMER_ORDER_FULFILLMENT where CUSTOMER_ORDER_ID=2146');assert c.fetchone()[0]==0
        st=int(c.callfunc('RRL_SBORKA_PALLETS_ADD2',oracledb.DB_TYPE_NUMBER,[UID,NOTE,1,UID,'1',datetime.now(),None,'admin',13583852]))
        c.execute('update RRL_SBORKA_PALLETS set CONDITION=0,ORIGINAL_ORDER_NUMBER=:pallet_identifier,ORIGINAL_ST_NUMBER=:pallet_identifier where ID=:id and PALLET_UID=:pallet_identifier',pallet_identifier=UID,id=st);assert c.rowcount==1
        row=int(c.callfunc('RRL_SBORKA_PALLET_ROWS_ADD4',oracledb.DB_TYPE_NUMBER,[UID,ARTICLE,'TEST CASE1136 1EA',None,'EA',None,None,None,None,1,0,None,None,13583852,None]))
        c.execute("""insert into RRL_CUSTOMER_ORDER_FULFILLMENT(FULFILLMENT_ID,CUSTOMER_ORDER_ID,LEGACY_SBORKA_PALLET_ID,PALLET_UID,ADDRESS_TEXT,STATUS,FACT_QTY,FACT_WEIGHT,SOURCE_SYSTEM,CREATED_AT,CREATED_BY)
            values(RRL_CUSTOMER_ORDER_FULF_SQ.nextval,2146,:st,:pallet_identifier,:note,'PLANNED',0,0,'TEST_WHREQ15',sysdate,'admin')""",st=st,pallet_identifier=UID,note=NOTE)
        c.execute('select FULFILLMENT_ID from RRL_CUSTOMER_ORDER_FULFILLMENT where PALLET_UID=:pallet_identifier',pallet_identifier=UID);fid=int(c.fetchone()[0])
        c.execute('select count(*)from RRL_SBORKA_PALLET_ROWS where ID=:id and PALLET_UID=:pallet_identifier and ARTICUL=:article and EI=\'EA\'and QUANTITY=1',id=row,pallet_identifier=UID,article=ARTICLE);assert c.fetchone()[0]==1
        c.execute("select REMAIN,HARD_RESERVED_BASE,STOCK_VERSION from RRL_REMAINS where UID_POLETA='REUSE.RETURN:e6c16d0bbd'and CELL='QIPcdbf4c0962'");assert c.fetchone()==(24,1,10)
        c.execute('select STATUS,CONTENT_VERSION,PICKED_QTY,LEGACY_SBORKA_PALLET_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=1136');assert c.fetchone()==('IN_PROGRESS',2,0,None)
        result=dict(st_id=st,row_id=row,fulfillment_id=fid)
        if rollback:raise RollbackProof(json.dumps(result))
        return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--execute-metadata',action='store_true');args=parser.parse_args()
    if not args.execute_metadata:print('PREPARED_ONLY: metadata execution requires root approval');return
    g=OracleGateway()
    before=baseline(g);assert identities(g)==dict(st=[],rows=[],fulfillment=[])
    sources=g.fetch_all("select NAME,LINE,TEXT from USER_SOURCE where TYPE='FUNCTION'and NAME in('RRL_SBORKA_PALLETS_ADD2','RRL_SBORKA_PALLET_ROWS_ADD4')order by NAME,LINE")
    assert len(sources)==205
    native=''.join(r['text']for r in sources)
    assert not re.search(r'\b(COMMIT|AUTONOMOUS_TRANSACTION)\b',native,re.I)
    assert not re.search(r'\b(RRL_REMAINS|RRL_STOCK_RESERVATION|RRL_STOCK_POSTING_API)\b',native,re.I)
    marker=g.fetch_all('select nvl(max(LOG_ID),0)N from RRL_SQL_SLOW_LOG')[0]['n']
    try:stage(g,True);raise AssertionError('Trial did not roll back')
    except RollbackProof as trial:trial_ids=json.loads(str(trial))
    assert identities(g)==dict(st=[],rows=[],fulfillment=[])and baseline(g)==before
    committed=stage(g)
    assert baseline(g)==before
    after=identities(g)
    assert len(after['st'])==len(after['rows'])==len(after['fulfillment'])==1
    assert after['rows'][0]['quantity']==1 and after['rows'][0]['ei']=='EA'and after['fulfillment'][0]['status']=='PLANNED'and after['fulfillment'][0]['fact_qty']==0
    report=dict(status='PASS',identity=UID,trial_ids=trial_ids,committed_ids=committed,caller_rollback_all_three_absent=True,sequence_gaps_expected=True,
        before=before,after=baseline(g),metadata=after,stock_changed=False,case_bound=False,physical_hardware=False,
        native_function_source_sha256=hashlib.sha256(native.encode()).hexdigest().upper(),native_function_lines=len(sources),native_function_commit=False,
        prior_trial_error='ORA-01745 reserved :uid smoke bind; CONFIG rollback and identities/source reverified before corrected trial',row_DOCID=None,unmeasured_logistics_fields=None,source_system='TEST_WHREQ15',
        cleanup='Canonical CASE_CARRIER_RETURN resets current fulfillment PLANNED/0 and unbinds CASE; TEST ST/row/fulfillment history retained, no business journal deletion.',
        slow_sql=g.fetch_all('select *from(select LOG_ID,ELAPSED_MS,SQL_TEXT from RRL_SQL_SLOW_LOG where LOG_ID>:marker order by ELAPSED_MS desc)where rownum<=10',{'marker':marker}))
    OUT.write_text(json.dumps(report,indent=2,default=str),encoding='utf-8')
    print(json.dumps(dict(status='PASS',identity=UID,ids=committed,stock_changed=False,case_bound=False)))


if __name__=='__main__':main()

