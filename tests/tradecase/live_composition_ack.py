"""Live business receipts on the closed FP21 fixture; no physical stock commands."""
from datetime import datetime, timezone
import json
from pathlib import Path
import secrets
import sys
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parent))
import live_topup_common_pool as qa

qa.OUT = qa.ROOT / 'runtime/test-evidence/tradecase/2026-10-23/T02'
qa.FILE = qa.OUT / 'composition-ack-live.json'
qa.s = json.loads(qa.FILE.read_text(encoding='utf-8')) if qa.FILE.exists() else dict(
    tag='CA23.' + uuid4().hex[:9], requests={}, results={}, checks=[])
s = qa.s
qa.W = 221164919
qa.BASE = f'/api/tradecase/warehouses/{qa.W}'
ORDER = 'FP21.221164919.ORDER'
REPORT = '/api/tradecase/order-compositions/report'
ACK = '/api/tradecase/order-compositions/acknowledgments'


def prepare():
    if 'before' not in s:
        assert qa.query('select NAME from RRL_WARES where ID=:w', w=qa.W)[0][0].startswith('TRADECASE QA')
        assert qa.stock() == [(0, 0)]
        assert qa.query('select count(*)from RRL_TRADE_ORDER_COMPOSITION where WARE_ID=:w', w=qa.W) == [(0,)]
        s.update(before=qa.stock(), actor='CA' + uuid4().hex[:12], password=secrets.token_hex(20),
                 at=datetime.now(timezone.utc).isoformat(), slow_marker=qa.query('select nvl(max(LOG_ID),0)from RRL_SQL_SLOW_LOG')[0][0])
        qa.save()
    if not s.get('actor_created'):
        with qa.oracle_connection() as conn:
            q = conn.cursor()
            q.execute('select count(*)from RUSERS where ID=:a', a=s['actor'])
            if not q.fetchone()[0]:
                q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'Own composition proof','QA_COMP_ONLY',:w,0,1)", a=s['actor'], p=s['password'], w=qa.W)
                q.execute("insert into RRL_ACCESS_ROLE(ROLE_ID,TITLE,ACTIVE,VERSION_NO)values(:a,'Own composition proof',1,1)", a=s['actor'])
                for right in ['tradecase_view', 'tradecase_import', 'tradecase_order_bind']:
                    q.execute('insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION)values(:a,:r)', a=s['actor'], r=right)
                q.execute("insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO)values(:a,:a,:a,'WAREHOUSE',:w,'CURRENT',systimestamp-interval '1'minute,systimestamp+interval '2'hour,'admin','Own composition proof',1)", a=s['actor'], w=str(qa.W))
                conn.commit()
        s['actor_created'] = True
        qa.save()
    grant('owner', 0, True)


def grant(key, version, enabled):
    return qa.step(key, qa.BASE + '/stock/owner-grants', dict(operation_id=s['tag'] + '.' + key,
        expected_version=version, username=s['actor'], owner_id='SNS', can_view=enabled, can_operate=enabled,
        reason='Own composition metadata acceptance'), method='PUT')


def ack(key, system, outcome='ACCEPTED', **changes):
    card = s['results']['report']
    body = dict(schema_version=1, warehouse_id=qa.W, system_code=system,
        sender_id='TC03.' + system, event_id=s['tag'] + '.' + key, order_id=ORDER,
        composition_no=card['composition_no'], signature=card['signature'], outcome=outcome, occurred_at=s['at'])
    if outcome == 'REJECTED':
        body['reason'] = 'Synthetic business refusal; no external provider called'
    body.update(changes)
    return body


def run():
    prepare()
    body = dict(warehouse_id=qa.W, order_id=ORDER)
    card = qa.step('report', REPORT, body, qa=True)
    assert card['units'] == 10 and card['codes'] == 10 and card['assembly_closed']
    assert card['sap_status'] == card['skm_status'] == 'WAITING', card
    replay = qa.step('report_replay', REPORT, body, qa=True)
    assert replay['composition_no'] == card['composition_no'] and replay['signature'] == card['signature']
    assert qa.query('select count(*)from RRL_TRADE_ORDER_COMPOSITION where WARE_ID=:w', w=qa.W) == [(1,)]
    qa.step('wrong_warehouse', REPORT, dict(body, warehouse_id=219023232), qa=True, status=403)
    qa.step('wrong_signature', ACK, ack('bad_sig', 'SAP', signature='0'*64), qa=True, status=409)
    qa.step('wrong_sender', ACK, ack('bad_sender', 'SAP', sender_id='UNASSIGNED'), qa=True, status=409)
    sap = ack('sap', 'SAP')
    accepted = qa.step('sap', ACK, sap, qa=True)
    assert accepted['sap_status'] == 'ACCEPTED' and accepted['skm_status'] == 'WAITING' and not accepted['stock_changed']
    assert qa.step('sap_replay', ACK, sap, qa=True)['business_replayed']
    qa.step('sap_changed_event', ACK, dict(sap, outcome='REJECTED', reason='changed same event'), qa=True, status=409)
    refused = qa.step('skm_rejected', ACK, ack('skm_no', 'SKM', 'REJECTED'), qa=True)
    assert refused['sap_status'] == 'ACCEPTED' and refused['skm_status'] == 'REJECTED' and refused['status'] == 'REJECTED'
    qa.step('final_ack_immutable', ACK, ack('skm_yes_new', 'SKM'), qa=True, status=409)
    grant('owner_revoke', 1, False)
    qa.step('revoked_report', REPORT, body, qa=True, status=403)
    qa.step('revoked_replay', ACK, sap, qa=True, status=403)
    hidden = qa.step('hidden', qa.BASE + '/order-compositions', method='GET', qa=True)
    assert ORDER not in json.dumps(hidden)
    grant('owner_restore', 2, True)
    assert qa.step('restored_replay', ACK, sap, qa=True)['business_replayed']
    listed = qa.step('list', qa.BASE + '/order-compositions', method='GET', qa=True)
    assert any(x['order_id'] == ORDER and x['sap_status'] == 'ACCEPTED' and x['skm_status'] == 'REJECTED' for x in listed['items'])
    grant('owner_retire', 3, False)
    with qa.oracle_connection() as conn:
        q = conn.cursor()
        q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp,VERSION_NO=VERSION_NO+1 where ASSIGNMENT_ID=:a and REVOKED_AT is null', a=s['actor'])
        q.execute('update RUSERS set DELETED=1 where ID=:a', a=s['actor'])
        conn.commit()
    assert qa.stock() == [(0, 0)]
    assert qa.query("select count(*)from USER_OBJECTS where STATUS='INVALID'") == [(0,)]
    s['slow_sql'] = qa.query('select LOG_ID,ELAPSED_MS,API_PATH,SQL_TEXT from RRL_SQL_SLOW_LOG where LOG_ID>:m order by ELAPSED_MS desc fetch first 15 rows only', m=s['slow_marker'])
    s['checks'] = ['Full-pallet 10 units / 10 codes; stable snapshot retry', 'Independent SAP accepted / SKM rejected',
        'Changed event, wrong signature/sender and foreign warehouse denied', 'Current owner rights guard cached receipt; hidden orders filtered',
        'Actor retired; stock 0/H0 and INVALID0; no physical commands']
    s['status'] = 'PASS_BASIC_RETRY_PENDING'
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

