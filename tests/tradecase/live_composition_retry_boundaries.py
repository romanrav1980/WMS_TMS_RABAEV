"""Retain SKM while retrying SAP; do not strand a still-pending other answer."""
from datetime import datetime, timezone
import json
from uuid import uuid4
import live_composition_switch as sw

qa = sw.qa
qa.FILE = qa.OUT / 'composition-retry-boundaries.json'
qa.s = json.loads(qa.FILE.read_text(encoding='utf-8')) if qa.FILE.exists() else dict(tag='CB23.' + uuid4().hex[:9], requests={}, results={})
s = qa.s
sw.s = s


def ack(key, card, system, outcome='ACCEPTED'):
    body = sw.acknowledgment(key, card, system)
    body['outcome'] = outcome
    if outcome == 'REJECTED':
        body['reason'] = 'Synthetic refusal; no external provider'
    return qa.step(key, sw.shared.ACK, body)


def retry(key, card, target, status=200):
    return qa.step(key, sw.shared.REPORT, dict(sw.BODY, retry_system=target, retry_of=card['composition_no']), status=status)


def run():
    if 'site' not in s:
        s.update(site=qa.expect(200, qa.http('GET', sw.BASE + '/site')), at=datetime.now(timezone.utc).isoformat(),
            slow_marker=qa.query('select nvl(max(LOG_ID),0)from RRL_SQL_SLOW_LOG')[0][0])
        qa.save()
    changed = sw.configure('switch', s['site']['version'], s['tag'] + '.SKM')
    first = qa.step('report', sw.shared.REPORT, sw.BODY)
    assert first['sap_status'] == first['skm_status'] == 'WAITING'
    ack('skm_refused', first, 'SKM', 'REJECTED')
    retry('other_pending', first, 'SKM', 409)
    assert qa.query('select max(COMPOSITION_NO)from RRL_TRADE_ORDER_COMPOSITION where WARE_ID=:w and ORDER_ID=:o', w=sw.W, o=sw.ORDER) == [(first['composition_no'],)]
    ack('sap_accepted', first, 'SAP')
    second = retry('retry_skm', first, 'SKM')
    assert second['sap_status'] == 'ACCEPTED' and second['skm_status'] == 'WAITING'
    assert ack('skm_accepted', second, 'SKM')['status'] == 'CONFIRMED'
    sw.configure('restore', changed['version'], s['site']['active_skm'])
    third = qa.step('restored_report', sw.shared.REPORT, sw.BODY)
    ack('restored_skm', third, 'SKM')
    ack('sap_refused', third, 'SAP', 'REJECTED')
    fourth = retry('retry_sap', third, 'SAP')
    assert fourth['sap_status'] == 'WAITING' and fourth['skm_status'] == 'ACCEPTED'
    rows = qa.query('select COMPOSITION_NO,SKM_EVENT_ID,PAYLOAD_JSON from RRL_TRADE_ORDER_COMPOSITION where WARE_ID=:w and ORDER_ID=:o and COMPOSITION_NO in(:a,:b)order by COMPOSITION_NO', w=sw.W, o=sw.ORDER, a=third['composition_no'], b=fourth['composition_no'])
    assert rows[0][1] == rows[1][1] == s['tag'] + '.restored_skm'
    payload = rows[1][2] if isinstance(rows[1][2], dict) else json.loads(rows[1][2])
    assert payload['target_system'] == 'SAP' and payload['retry_of'] == third['composition_no']
    assert ack('final_sap', fourth, 'SAP')['status'] == 'CONFIRMED'
    assert retry('sap_retry_replay', third, 'SAP')['composition_no'] == fourth['composition_no']
    current = qa.expect(200, qa.http('GET', sw.BASE + '/site'))
    assert all(current[k] == s['site'][k] for k in ['source_id', 'active_skm', 'planning_source', 'enabled'])
    assert qa.query('select nvl(sum(r.REMAIN),0),nvl(sum(r.HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w', w=sw.W) == [(0, 0)]
    assert qa.query("select count(*)from USER_OBJECTS where STATUS='INVALID'") == [(0,)]
    s['checks'] = ['Retry blocked while other system waits; no new snapshot', 'After pending SAP accepted, SKM retry succeeds',
        'SAP retry retains exact accepted SKM event and targets only SAP', 'Both directions confirmed; exact retry stable; settings restored; stock0/H0; INVALID0']
    s['slow_sql'] = qa.query('select LOG_ID,ELAPSED_MS,API_PATH,SQL_TEXT from RRL_SQL_SLOW_LOG where LOG_ID>:m order by ELAPSED_MS desc fetch first 15 rows only', m=s['slow_marker'])
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
