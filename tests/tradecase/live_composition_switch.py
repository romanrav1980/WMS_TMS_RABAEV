"""Concurrent report and provider switching on owned, already-shipped FP21 metadata."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from uuid import uuid4
import live_composition_ack as shared

qa = shared.qa
qa.FILE = qa.OUT / 'composition-switch-live.json'
qa.s = json.loads(qa.FILE.read_text(encoding='utf-8')) if qa.FILE.exists() else dict(tag='CS23.' + uuid4().hex[:9], requests={}, results={})
s = qa.s
W = 220639789
BASE = f'/api/tradecase/warehouses/{W}'
ORDER = 'FP21.220639789.ORDER'
BODY = dict(warehouse_id=W, order_id=ORDER)


def acknowledgment(key, card, system, sender=None):
    return dict(schema_version=1, warehouse_id=W, system_code=system, sender_id=sender or card['source_id' if system == 'SAP' else 'skm_id'],
        event_id=s['tag'] + '.' + key, order_id=ORDER, composition_no=card['composition_no'], signature=card['signature'],
        outcome='ACCEPTED', occurred_at=s['at'])


def configure(key, version, skm):
    original = s['site']
    return qa.step(key, BASE + '/site', dict(operation_id=s['tag'] + '.' + key, expected_version=version,
        source_id=original['source_id'], active_skm=skm, planning_source=original['planning_source'],
        enabled=original['enabled'], reason='Owned provider switching metadata proof'), method='PUT')


def run():
    if 'site' not in s:
        assert qa.query('select NAME from RRL_WARES where ID=:w', w=W)[0][0].startswith('TRADECASE QA')
        assert qa.query('select count(*)from RRL_TRADE_ORDER_COMPOSITION where WARE_ID=:w', w=W) == [(0,)]
        s.update(site=qa.expect(200, qa.http('GET', BASE + '/site')), at=datetime.now(timezone.utc).isoformat(),
            slow_marker=qa.query('select nvl(max(LOG_ID),0)from RRL_SQL_SLOW_LOG')[0][0])
        qa.save()
    if 'race' not in s:
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: qa.http('POST', shared.REPORT, BODY), range(2)))
        s['race'] = results
        qa.save()
    assert all(r[0] == 200 for r in s['race']), s['race']
    first = s['race'][0][1]
    assert first['composition_no'] == s['race'][1][1]['composition_no'] == 1
    assert first['signature'] == s['race'][1][1]['signature']
    qa.step('first_sap', shared.ACK, acknowledgment('first_sap', first, 'SAP'))
    switched = configure('switch', s['site']['version'], s['tag'] + '.SKM')
    listing = qa.step('changed', BASE + '/order-compositions', method='GET')
    assert any(i['order_id'] == ORDER and i['status'] == 'CHANGED' and i['change_reason'] == 'SKM_CHANGED' for i in listing['items'])
    qa.step('old_skm_after_switch', shared.ACK, acknowledgment('old_skm', first, 'SKM'), status=409)
    second = qa.step('second_report', shared.REPORT, BODY)
    assert second['composition_no'] == 2 and second['signature'] == first['signature']
    qa.step('superseded_reply', shared.ACK, acknowledgment('late_sap', first, 'SAP'), status=409)
    accepted_skm = qa.step('second_skm', shared.ACK, acknowledgment('second_skm', second, 'SKM'))
    assert accepted_skm['skm_status'] == 'ACCEPTED' and accepted_skm['sap_status'] == 'WAITING'
    assert qa.step('second_sap', shared.ACK, acknowledgment('second_sap', second, 'SAP'))['status'] == 'CONFIRMED'
    configure('restore', switched['version'], s['site']['active_skm'])
    third = qa.step('third_report', shared.REPORT, BODY)
    assert third['composition_no'] == 3 and third['signature'] == first['signature']
    qa.step('third_skm', shared.ACK, acknowledgment('third_skm', third, 'SKM'))
    assert qa.step('third_sap', shared.ACK, acknowledgment('third_sap', third, 'SAP'))['status'] == 'CONFIRMED'
    assert qa.query('select count(*),count(distinct OUTBOX_ID)from RRL_TRADE_ORDER_COMPOSITION where WARE_ID=:w', w=W) == [(3, 3)]
    if not s.get('frozen_checked'):
        with qa.oracle_connection() as conn:
            q = conn.cursor()
            try:
                q.execute('update RRL_TRADE_ORDER_COMPOSITION set UNIT_COUNT=UNIT_COUNT+1 where WARE_ID=:w and COMPOSITION_NO=3', w=W)
            except Exception as exc:
                assert 'COMPOSITION_SNAPSHOT_FROZEN' in str(exc), exc
                s['frozen_error'] = str(exc)
            else:
                raise AssertionError('Frozen snapshot allowed modification')
            finally:
                conn.rollback()
        s['frozen_checked'] = True
        qa.save()
    current = qa.expect(200, qa.http('GET', BASE + '/site'))
    assert all(current[k] == s['site'][k] for k in ['source_id', 'active_skm', 'planning_source', 'enabled'])
    assert qa.query('select nvl(sum(r.REMAIN),0),nvl(sum(r.HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w', w=W) == [(0, 0)]
    assert qa.query("select count(*)from USER_OBJECTS where STATUS='INVALID'") == [(0,)]
    s['slow_sql'] = qa.query('select LOG_ID,ELAPSED_MS,API_PATH,SQL_TEXT from RRL_SQL_SLOW_LOG where LOG_ID>:m order by ELAPSED_MS desc fetch first 15 rows only', m=s['slow_marker'])
    s['checks'] = ['Two concurrent reports commit one snapshot/outbox', 'Current SKM switching invalidates waiting report and rejects old sender',
        'Superseded snapshot rejects fresh late reply', 'SKM before SAP independently reaches CONFIRMED',
        'Switch back queues distinct snapshot, never reuses old outbox', 'Frozen snapshot rejects direct metadata change; site restored; stock0/H0; INVALID0']
    s['status'] = 'PASS'
    s.pop('error', None)
    qa.save()


if __name__ == '__main__':
    s['previous_calls'] = s.get('calls', [])
    try:
        if s.get('status') != 'PASS':
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
