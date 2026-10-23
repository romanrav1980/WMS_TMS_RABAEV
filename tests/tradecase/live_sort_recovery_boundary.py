"""Read retained owned stock; reject a same-cell move without changing quantities."""
import json
import os
from pathlib import Path
from uuid import uuid4
import live_document_acceptance as qa
from tools.mcp.tms_mcp_server import oracle_connection

OUT = qa.ROOT / 'runtime/test-evidence/tradecase/2026-10-23/T06'
FILE = OUT / 'sort-recovery-boundary-live.json'
WARE = 219023232


def stock(cur):
    cur.execute('''select r.UID_POLETA,r.CELL,r.REMAIN,r.HARD_RESERVED_BASE,r.STOCK_VERSION
        from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL
        where c.WARE_ID=:w order by r.UID_POLETA,r.CELL''', w=WARE)
    return cur.fetchall()


def run():
    assert not FILE.exists(), 'Preserve the recorded result; do not rerun a closed probe'
    report = dict(status='FAIL', warehouse=WARE, quantitative_commands_expected=0)
    OUT.mkdir(parents=True, exist_ok=True)
    try:
        with oracle_connection() as c:
            q=c.cursor(); q.execute('set transaction read only')
            q.execute("select user,sys_context('USERENV','SERVICE_NAME')from dual")
            assert q.fetchone()==('RABAEV','orcl')
            q.execute('select NAME from RRL_WARES where ID=:w', w=WARE)
            assert q.fetchone()==('TRADECASE QA 89af0087',)
            before=stock(q); assert sum(r[2] for r in before)==10 and sum(r[3] for r in before)==0
            source=[r for r in before if r[2]==3]; assert len(source)==1
            uid,cell=source[0][:2]
            q.execute('''select u.PHYSICAL_UNIT_KEY,u.CURRENT_UID,u.CURRENT_CELL,u.STOCK_STATUS
                from RRL_WMS_RECEIPT_UNIT u join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY
                where a.CAPTURE_WARE_ID=:w order by u.PHYSICAL_UNIT_KEY''', w=WARE)
            units=q.fetchall(); assert len(units)==10
            q.execute('''select c.SYSTEM_CODE,c.RAW_CODE from RRL_WMS_RECEIPT_UNIT u
                join RRL_WMS_RECEIPT_CODE c on c.UID_PALLET=u.UID_PALLET and c.UNIT_ID=u.UNIT_ID
                where u.CURRENT_UID=:p_uid and u.STOCK_STATUS<>'ISSUED' order by u.PHYSICAL_UNIT_KEY fetch first 1 row only''', p_uid=uid)
            system,raw=q.fetchone(); code=raw.read() if hasattr(raw,'read') else raw
            q.execute("select PASS from RUSERS where ID='admin'")
            os.environ['TRADECASE_ADMIN_USER']='admin'; os.environ['TRADECASE_ADMIN_PASSWORD']=q.fetchone()[0]
            q.execute('select nvl(max(LOG_ID),0)from RRL_SQL_SLOW_LOG'); marker=q.fetchone()[0]
        body=dict(operation_id='SORT23.REJECT.'+uuid4().hex,source_pallet=uid,source_cell=cell,target_cell=cell,
                  scans=[dict(system_code=system,profile_code='TOBACCO',code=code)])
        result=qa.expect(409,qa.http('POST',f'/api/tradecase/warehouses/{WARE}/stock/sort',body))
        detail=result['detail']
        assert detail['operation_id']==body['operation_id'] and detail['code']=='STOCK_RULE_REJECTED',result
        assert detail['outcome_confirmed'] is True and detail['operation_id_conflict'] is False,result
        assert detail['retry_same_operation_id'] is False and detail['reason'],result
        with oracle_connection() as c:
            q=c.cursor(); q.execute('set transaction read only')
            assert stock(q)==before
            q.execute('''select u.PHYSICAL_UNIT_KEY,u.CURRENT_UID,u.CURRENT_CELL,u.STOCK_STATUS
                from RRL_WMS_RECEIPT_UNIT u join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY
                where a.CAPTURE_WARE_ID=:w order by u.PHYSICAL_UNIT_KEY''',w=WARE)
            assert q.fetchall()==units
            q.execute("select count(*)from RRL_STOCK_OPERATION where OPERATION_ID=:op and STATE='APPLIED'",op=body['operation_id'])
            assert q.fetchone()==(0,)
            q.execute("select count(*)from user_objects where STATUS='INVALID'"); assert q.fetchone()==(0,)
            q.execute('''select LOG_ID,API_PATH,ELAPSED_MS from RRL_SQL_SLOW_LOG
                where LOG_ID>:marker order by LOG_ID fetch first 20 rows only''',marker=marker)
            report['fresh_slow_sql']=q.fetchall()
        report.update(status='PASS',result=result,stock=before,units_unchanged=10,
            limitation='Actual native denial only; uncertain and post-commit connection errors are ASGI injected, not induced in Oracle.')
    finally:
        report['http']=qa.CALLS
        FILE.write_text(json.dumps(report,indent=2,default=str),encoding='utf-8')
    print(json.dumps(dict(status=report['status'],result=report['result'],http=len(qa.CALLS))))


if __name__=='__main__':
    run()
