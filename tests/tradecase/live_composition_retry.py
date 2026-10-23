"""Retry a rejected SKM result without resending the accepted SAP result."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import secrets
from uuid import uuid4
import live_composition_ack as shared

qa = shared.qa
qa.FILE = qa.OUT / 'composition-retry-live.json'
qa.s = json.loads(qa.FILE.read_text(encoding='utf-8')) if qa.FILE.exists() else dict(tag='CR23.' + uuid4().hex[:9], requests={}, results={})
s = qa.s


def grant(key, version, enabled):
    return qa.step(key, qa.BASE + '/stock/owner-grants', dict(operation_id=s['tag'] + '.' + key, expected_version=version,
        username=s['actor'], owner_id='SNS', can_view=enabled, can_operate=enabled, reason='Own targeted retry proof'), method='PUT')


def prepare():
    if 'actor' not in s:
        rows = qa.query("select COMPOSITION_NO,SAP_STATUS,SKM_STATUS,SAP_EVENT_ID,SIGNATURE from RRL_TRADE_ORDER_COMPOSITION where WARE_ID=:w and ORDER_ID=:o and STATE='CURRENT'", w=qa.W, o=shared.ORDER)
        assert len(rows) == 1 and rows[0][:3] == (1, 'ACCEPTED', 'REJECTED'), rows
        s.update(original=rows[0], actor='CR' + uuid4().hex[:12], password=secrets.token_hex(20), at=datetime.now(timezone.utc).isoformat(),
            slow_marker=qa.query('select nvl(max(LOG_ID),0)from RRL_SQL_SLOW_LOG')[0][0])
        qa.save()
    if not s.get('actor_created'):
        with qa.oracle_connection() as conn:
            q = conn.cursor()
            q.execute('select count(*)from RUSERS where ID=:a', a=s['actor'])
            if not q.fetchone()[0]:
                q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'Own retry proof',:a,:w,0,1)", a=s['actor'], p=s['password'], w=qa.W)
                for permission in ['tradecase_order_bind', 'tradecase_import', 'tradecase_view']:
                    q.execute('insert into RIGHTS(USER_GROUP,RIGHT1)values(:a,:p)', a=s['actor'], p=permission)
                conn.commit()
        s['actor_created'] = True
        qa.save()
    grant('owner', 0, True)


def run():
    prepare()
    body = dict(warehouse_id=qa.W, order_id=shared.ORDER, retry_system='SKM', retry_of=1)
    qa.step('accepted_side_forbidden', shared.REPORT, dict(body, retry_system='SAP'), qa=True, status=409)
    qa.step('missing_parent', shared.REPORT, dict(warehouse_id=qa.W, order_id=shared.ORDER, retry_system='SKM'), qa=True, status=422)
    qa.step('foreign_warehouse', shared.REPORT, dict(body, warehouse_id=219023232), qa=True, status=403)
    if 'race' not in s:
        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(lambda _: qa.http('POST', shared.REPORT, body, s['actor'], s['password']), range(2)))
        s['race'] = outcomes
        qa.save()
    assert all(r[0] == 200 for r in s['race']), s['race']
    card = s['race'][0][1]
    assert card['composition_no'] == s['race'][1][1]['composition_no'] == 2
    assert card['sap_status'] == 'ACCEPTED' and card['skm_status'] == 'WAITING' and card['signature'] == s['original'][4]
    rows = qa.query('select SAP_EVENT_ID,PAYLOAD_JSON from RRL_TRADE_ORDER_COMPOSITION where WARE_ID=:w and ORDER_ID=:o and COMPOSITION_NO=2', w=qa.W, o=shared.ORDER)
    assert rows[0][0] == s['original'][3]
    payload = rows[0][1] if isinstance(rows[0][1], dict) else json.loads(rows[0][1])
    assert payload['retry_system'] == payload['target_system'] == 'SKM' and payload['retry_of'] == 1
    base = dict(schema_version=1, warehouse_id=qa.W, sender_id='TC03.SKM', system_code='SKM', order_id=shared.ORDER,
        signature=card['signature'], outcome='REJECTED', reason='Synthetic second refusal for exact-attempt replay proof', occurred_at=s['at'])
    qa.step('old_reply', shared.ACK, dict(base, composition_no=1, event_id=s['tag'] + '.old'), qa=True, status=409)
    rejected = qa.step('second_refusal', shared.ACK, dict(base, composition_no=2, event_id=s['tag'] + '.refused'), qa=True)
    assert rejected['sap_status'] == 'ACCEPTED' and rejected['skm_status'] == 'REJECTED'
    again = qa.step('same_retry_after_second_refusal', shared.REPORT, body, qa=True)
    assert again['composition_no'] == 2 and again['replayed']
    assert qa.query('select count(*),count(distinct OUTBOX_ID)from RRL_TRADE_ORDER_COMPOSITION where WARE_ID=:w and ORDER_ID=:o', w=qa.W, o=shared.ORDER) == [(2, 2)]
    grant('owner_revoke', 1, False)
    qa.step('revoked_retry_receipt', shared.REPORT, body, qa=True, status=403)
    grant('owner_restore', 2, True)
    assert qa.step('restored_retry_receipt', shared.REPORT, body, qa=True)['composition_no'] == 2
    grant('owner_retire', 3, False)
    with qa.oracle_connection() as conn:
        q = conn.cursor()
        q.execute('update RUSERS set DELETED=1 where ID=:a', a=s['actor'])
        q.execute('delete from RIGHTS where USER_GROUP=:a', a=s['actor'])
        conn.commit()
    assert qa.stock() == [(0, 0)]
    assert qa.query("select count(*)from USER_OBJECTS where STATUS='INVALID'") == [(0,)]
    s['slow_sql'] = qa.query('select LOG_ID,ELAPSED_MS,API_PATH,SQL_TEXT from RRL_SQL_SLOW_LOG where LOG_ID>:m order by ELAPSED_MS desc fetch first 15 rows only', m=s['slow_marker'])
    s['checks'] = ['Only rejected SKM retried; accepted SAP event retained', 'Concurrent identical retry commits one new snapshot/outbox',
        'Old reply rejected; same original retry after next refusal returns existing attempt2, no attempt3',
        'Current owner rights protect retry receipt; actor retired, stock0/H0, INVALID0']
    s['status'] = 'PASS_RETRY_UI_PENDING'
    s.pop('error', None)
    qa.save()


if __name__ == '__main__':
    s['previous_calls'] = s.get('calls', [])
    try:
        if not s.get('status'):
            run()
        else:
            print('Closed; no commands sent')
    except Exception as exc:
        s['error'] = str(exc)
        qa.save()
        raise
    finally:
        qa.save()
    print(s.get('status'))
