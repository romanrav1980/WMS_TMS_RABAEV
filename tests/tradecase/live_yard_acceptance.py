"""Native yard lifecycle on synthetic metadata; rollback all fixtures and visits."""
import hashlib
import json
from pathlib import Path
import sys
import time
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT), str(ROOT / 'api/wms_api_server')]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from tools.mcp.tms_mcp_server import oracle_connection
import oracledb

W = 220793322
TAG = 'YD22.' + uuid4().hex[:10]
OUT = ROOT / 'runtime/test-evidence/tradecase/2026-10-22/T10' / (TAG + '.json')
report = dict(status='FAIL', fixture='Synthetic metadata, real native commands, entire transaction rolled back', checks=[], commands=[])


def run():
    with oracle_connection() as c:
        q = c.cursor()
        q.execute("select user,sys_context('USERENV','SERVICE_NAME')from dual")
        assert q.fetchone() == ('RABAEV', 'orcl')
        q.execute('select NAME from RRL_WARES where ID=:w', w=W)
        assert q.fetchone()[0].startswith('TRADECASE QA ')

        def stocks():
            q.execute('select c.WARE_ID,sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID in(210564699,215266197,219023232,220793322)group by c.WARE_ID order by c.WARE_ID')
            return [list(r) for r in q]

        before = stocks()
        q.execute('select nvl(max(LOG_ID),0)from RRL_SQL_SLOW_LOG')
        slow_marker = q.fetchone()[0]
        def command(body, actor='admin', denied=None):
            request = q.var(oracledb.DB_TYPE_CLOB)
            request.setvalue(0, json.dumps(body, sort_keys=True, separators=(',', ':')))
            result = q.var(oracledb.DB_TYPE_CLOB)
            start = time.perf_counter()
            q.execute('savepoint yard_command')
            try:
                q.callproc('RRL_YARD_VISIT_API.command', [W, request, actor, result])
                value = result.getvalue()
                value = json.loads(value.read() if hasattr(value, 'read') else value)
            except oracledb.DatabaseError as exc:
                q.execute('rollback to yard_command')
                error = str(exc).split('\n')[0]
                report['commands'].append(dict(action=body['action'], error=error, elapsed_ms=round((time.perf_counter()-start)*1000, 2)))
                if denied and denied in error:
                    return
                raise
            assert denied is None, (denied, value)
            assert value['operation_id'] == body['operation_id']
            report['commands'].append(dict(action=body['action'], receipt=value, elapsed_ms=round((time.perf_counter()-start)*1000, 2)))
            return value

        def change(v, action, **kw):
            return command(dict(operation_id=TAG+'.'+str(len(report['commands'])), visit_id=v['visit_id'], expected_version=v['version'], action=action, **kw))

        try:
            # New synthetic source documents deliberately have no native ORDER_LINK.
            order = TAG+'.ORDER'
            for entity, external, body in [('ORDER', order, dict(lines=[dict(line_id='1', source_owner_id='SNS')])), *[
                ('TRIP', TAG+'.T'+str(i), dict(orders=[dict(order_id=order, line_id='1')])) for i in range(3)
            ]]:
                raw = json.dumps(body)
                q.execute("insert into RRL_TRADE_DOCUMENT(WARE_ID,ENTITY_TYPE,EXTERNAL_ID,SOURCE_ID,VERSION_NO,CONTENT_HASH,BODY_JSON,STATUS,CHANGED_BY)values(:w,:e,:id,'TC03.SAP',1,:hash,:body,'ACCEPTED','admin')", w=W, e=entity, id=external, hash=hashlib.sha256(raw.encode()).hexdigest(), body=raw)
            docks = ['B22D1161', 'N22DA1168']

            expect = dict(operation_id=TAG+'.expect', action='EXPECT', visit_kind='OUTBOUND', trip_id=TAG+'.T0')
            first = command(expect)
            assert command(expect)['replayed'] is True
            command(dict(expect, trip_id=TAG+'.T1'), denied='YARD_OPERATION_CONFLICT')
            report['checks'].append('Exact native replay and changed-body conflict')

            command(dict(operation_id=TAG+'.missing.binding', visit_id=first['visit_id'], expected_version=1, action='ARRIVE'), denied='YARD_TRIP_BINDING_REQUIRED')
            first = change(first, 'CANCEL', reason='Rollback fixture completion')
            # Existing owned QA trip provides the genuine guarded native binding.
            # Yard facts are rolled back; no transport/load/stock state is changed.
            second = command(dict(expect, operation_id=TAG+'.second', trip_id='R1.1168'))
            second = change(second, 'ARRIVE')
            second = change(second, 'ASSIGN_DOCK', dock=docks[0])
            second = change(second, 'REASSIGN_DOCK', dock=docks[1])
            second = change(second, 'START')
            second = change(second, 'FINISH')
            second = change(second, 'DEPART')
            report['checks'].append('Missing native binding denies arrival; owned native lifecycle, reassign and departure (rolled back, no physical yard claim)')
            q.execute("select to_char(systimestamp-interval '1'hour,'YYYY-MM-DD\"T\"HH24:MI:SSTZH:TZM'),to_char(systimestamp+interval '1'hour,'YYYY-MM-DD\"T\"HH24:MI:SSTZH:TZM')from dual")
            start, end = q.fetchone()
            history = q.callfunc('RRL_YARD_VISIT_API.history', oracledb.DB_TYPE_CLOB, [W, 'admin', start, end])
            history = json.loads(history.read())
            own = next(v for v in history['visits'] if v['visit_id']==second['visit_id'])
            assert [v['action'] for v in own['events']] == ['EXPECT','ARRIVE','ASSIGN_DOCK','REASSIGN_DOCK','START','FINISH','DEPART']
            assert own['events'][2]['dock']==docks[0] and own['events'][3]['dock']==docks[1]
            report['history'] = own
            q.execute('savepoint append_test')
            try:
                q.execute('update RRL_YARD_VISIT_EVENT set ACTOR=ACTOR where OPERATION_ID=:op', op=expect['operation_id'])
                raise AssertionError('event update was accepted')
            except oracledb.DatabaseError as exc:
                assert 'YARD_EVENT_APPEND_ONLY' in str(exc)
                q.execute('rollback to append_test')
            report['checks'].append('Closed visit remains in history with both dock assignments; immutable event update denied')
            assert stocks()==before
            report['stock'] = before
            q.execute("select count(*)from USER_OBJECTS where STATUS='INVALID'")
            assert q.fetchone()==(0,)
            report['status'] = 'PASS'
        finally:
            c.rollback()
            assert stocks()==before
            q.execute('select count(*)from RRL_YARD_VISIT_EVENT where OPERATION_ID like :tag', tag=TAG+'%')
            assert q.fetchone()==(0,)
            q.execute('select count(*)from RUSERS where ID=:a', a=TAG.replace('.', ''))
            assert q.fetchone()==(0,)
            report['rolled_back'] = True
            q.execute('select OPERATION_KIND,ELAPSED_MS from RRL_SQL_SLOW_LOG where LOG_ID>:m order by ELAPSED_MS desc fetch first 5 rows only', m=slow_marker)
            report['slow_sql'] = [list(r) for r in q]


if __name__=='__main__':
    try:
        run()
    finally:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(report, indent=2, default=str), encoding='utf-8')
    print(json.dumps(dict(status=report['status'], checks=len(report['checks']), evidence=str(OUT))))
