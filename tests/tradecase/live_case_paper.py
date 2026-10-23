"""Paper-version proof on existing marked QA stock; fresh CASE, no new goods receipt."""
import json
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests/tradecase'),str(ROOT)]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
os.environ.setdefault('TRADECASE_ADMIN_USER','admin')
os.environ.setdefault('TRADECASE_ADMIN_PASSWORD','admin123')
import manual_tare_pick_race as fixture
from live_document_acceptance import http, expect, CALLS
from tools.mcp.tms_mcp_server import oracle_connection

OUT=ROOT/'runtime/test-evidence/tradecase/2026-10-23/T11'
FILE=OUT/'case-paper-live-one.json'
case=fixture.case
old=json.loads((ROOT/'runtime/test-evidence/tradecase/2026-10-21/T06/factory-case.json').read_text())
case.OUT=fixture.OUT=OUT;case.FILE=fixture.FILE=FILE
case.tag='CP23B.219023232';case.w=219023232;case.base=f'/api/tradecase/warehouses/{case.w}'
case.s=fixture.s=json.loads(FILE.read_text()) if FILE.exists() else dict(
    warehouse_id=case.w,article=old['article'],pick=old['pick'],face=old['face'],
    cpt_policy=old['cpt_policy'],pallet_type_id=33,quantity=1,history=[],checks=[])
s=case.s

def save(): case.save()

def query(sql,**binds):
    with oracle_connection() as connection:
        q=connection.cursor();q.execute(sql,binds)
        return [tuple(x.read() if hasattr(x,'read') else x for x in row) for row in q]

def own(method,path,body=None):
    password=query('select PASS from RUSERS where ID=:a',a=s['actor'])[0][0]
    return http(method,path,body,s['actor'],password)

def step(name,path,body=None,method='POST',status=200):
    s.setdefault('paper_requests',{})
    if name not in s['paper_requests']:
        s['paper_requests'][name]=dict(path=path,body=body,method=method,status=status);save()
    if name not in s:
        req=s['paper_requests'][name]
        s[name]=expect(req['status'],own(req['method'],req['path'],req['body']));save()
    return s[name]

def prepare():
    if s.get('status')=='PASS': return
    actor,password,base,resource,session,_=fixture.prepare()
    s['paper_actor']=actor;s['paper_resource']=resource;s['paper_session']=session
    rows=query("select c.SYSTEM_CODE,c.RAW_CODE from RRL_WMS_RECEIPT_UNIT u join RRL_WMS_RECEIPT_CODE c "
        "on c.UID_PALLET=u.UID_PALLET and c.UNIT_ID=u.UNIT_ID join RRL_STOCK_RESERVATION r "
        "on r.RESERVATION_ID=u.HARD_RESERVATION_ID where r.SOURCE_DOC_TYPE='PICK_WAVE'and r.SOURCE_LINE_ID=:p "
        "and r.STATUS in('ACTIVE','ALLOCATED','PICKING')order by u.UNIT_ID",p=s['pick_task'])
    if 'paper_scans'not in s:
        assert len(rows)==1,rows
        s['paper_scans']=[dict(system_code=system,profile_code='TOBACCO',code=raw)for system,raw in rows]
    s['status']='PREPARED';save()

def execute():
    if s.get('status')=='PASS': print('Already PASS; no new CASE/receipts');return
    base=f"/api/case-pick/tasks/{s['case']}"; path=base+f"/lines/{s['line']}/confirm"
    first=step('paper_first',base+'/paper',method='GET');line=next(v for v in first['lines']if v['line_id']==s['line'])
    body=dict(operation_id=case.tag+'.paper.first',fact_qty='1',scan_cell=s['pick'],scan_product=s['article'],
        scan_container=s['label']['sscc'],resource_id=s['paper_resource'],resource_session_id=s['paper_session'],
        unit_scans=s['paper_scans'][:1],expected_case_signature=line['signature'])
    step('paper_wrong',path,dict(body,operation_id=case.tag+'.paper.wrong',expected_case_signature='0'*64),status=409)
    picked=step('paper_picked_first',path,body)
    assert expect(200,own('POST',path,s['paper_requests']['paper_picked_first']['body']))==picked
    step('paper_old_after_first',base+f"/paper?line={s['line']}&expected_signature={line['signature']}",method='GET',status=409)
    # The original code is already in the carrier; scan resolution rejects it before native execution.
    if 'paper_stale_second'in s.get('paper_requests',{}):
        req=s['paper_requests']['paper_stale_second']
        if req['status']==409:
            req['prior_expected_status']=409;req['status']=422;save()
    step('paper_stale_second',path,dict(body,operation_id=case.tag+'.paper.stale.second'),status=422)
    current=step('paper_after_first',base+'/paper',method='GET');fresh=next(v for v in current['lines']if v['line_id']==s['line'])
    assert fresh['signature']!=line['signature']
    assert expect(200,own('POST',path,s['paper_requests']['paper_picked_first']['body']))==picked
    step('paper_conflict',path,dict(body,fact_qty='2'),status=409)
    assert query("select count(*)from RRL_STOCK_OPERATION where OPERATION_ID in(:a,:b)",
        a=case.tag+'.paper.wrong',b=case.tag+'.paper.stale.second')==[(0,)]
    assert query('select PICKED_QTY from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=:l',l=s['line'])==[(1,)]
    s['pick_body']=s['paper_requests']['paper_picked_first']['body'];s['picked']=picked
    s['checks'].append('Marked native1 uses paper signature; old paper rejected, original receipt replays after line completion')
    save()
    # Existing return owner preserves stock/marks and retires only the fresh actor.
    case.execute(return_after=True)
    case.step('book_released','/api/inventory/tare/book-cancel',dict(operation_id=case.tag+'.book.cancel',booking_operation_id=s['tare_book']['operation_id']))
    if 'tare_restored'not in s:
        balances=expect(200,http('GET',f'/api/inventory/tare/warehouses/{case.w}/balances'))
        balance=next(b for b in balances if b['pallet_type_id']==33 and b['custodian_kind']=='WAREHOUSE'and b['condition_code']=='GOOD')
        case.step('tare_restored','/api/inventory/tare/count',dict(operation_id=case.tag+'.tare.restore',owner_ware_id=case.w,
            pallet_type_id=33,condition='GOOD',observed_quantity=str(s['tare_before']),expected_version=balance['balance_version'],
            reason='Restore own synthetic paper test carton count',decision_reference='TEST_FIXTURE_RESTORE:'+case.tag))
    case.step('settings_restored',f'/api/receiving/warehouses/{case.w}/settings',s['settings_before'],'PUT')
    case.step('wave_finished',f"/api/picking/waves/{s['wave']}/finish-execution",dict(operation_id=case.tag+'.wave.finish',
        disposition='RETURNED_TO_PLANNING',reason='Return own paper-version proof goods; preserve source demand'))
    s['slow_sql']=query('select LOG_ID,ELAPSED_MS,OPERATION_KIND from RRL_SQL_SLOW_LOG where LOG_ID>:n order by LOG_ID fetch first 40 rows only',n=s['slow_marker'])
    s['status']='PASS';save()

if __name__=='__main__':
    try:
        prepare() if '--prepare'in sys.argv else execute()
        print(json.dumps(dict(status=s.get('status'),case=s.get('case'),wave=s.get('wave'))))
    except Exception as exc:s.update(error=str(exc),status='FAIL');raise
    finally:
        if s.get('status')=='PASS'and 'error'in s:
            s.setdefault('prior_attempt_errors',[]).append(s.pop('error'))
        s['history']+=CALLS;save()
