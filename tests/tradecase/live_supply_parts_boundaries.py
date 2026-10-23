"""Mismatch, size bound, END-only recovery and existing deferred intake; metadata only, no stock receipts."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parent))
import live_supply_parts as sp

qa = sp.qa
previous = json.loads(qa.FILE.read_text(encoding='utf-8'))
qa.FILE = qa.OUT / 'supply-parts-boundaries.json'
s = json.loads(qa.FILE.read_text(encoding='utf-8')) if qa.FILE.exists() else dict(
    tag='PB23.' + uuid4().hex[:9], warehouse_id=qa.W, header=previous['header'], at=datetime.now(timezone.utc).isoformat(),
    requests={}, results={}, checks=[], provider='CONTROLLED_INTERNAL_SENDER_NOT_REAL_SAP')
qa.s = sp.s = s; qa.TAG = s['tag']


def send(key, body, ending=False, status=200):
    return qa.step(key, sp.PART + ('/end' if ending else ''), body, status=status)


def absent(doc):
    assert qa.query("select count(*)from RRL_TRADE_DOCUMENT where WARE_ID=:w and ENTITY_TYPE='SUPPLY'and EXTERNAL_ID=:d", w=qa.W, d=doc) == [(0,)]


def run():
    if 'slow_marker' not in s:
        assert qa.stock() == [(250, 0)]
        s['slow_marker'] = qa.query('select nvl(max(LOG_ID),0)from RRL_SQL_SLOW_LOG')[0][0]; qa.save()
    a, b, end = sp.bodies('END_ONLY')
    result = send('end_only', end, True)
    assert result['status'] == 'OPEN' and result['missing_parts'] == [1, 2]
    assert qa.query('select count(*)from RRL_TRADE_SUPPLY_PART where WARE_ID=:w and SOURCE_ID=:s and TRANSFER_ID=:t', w=qa.W, s=end['source_id'], t=end['transfer_id']) == [(0,)]
    if 'rollback_history' not in s:
        os.environ['PARTS_HISTORY_CONN'] = 'User Id=' + os.environ['WMS_ORACLE_USER'] + ';Password=' + os.environ['WMS_ORACLE_PASSWORD'] + ';Data Source=' + os.environ['WMS_ORACLE_DSN']
        process = subprocess.run(['dotnet', 'run', '--project', 'tools/oracle_apply/OracleApply.csproj', '--', 'PARTS_HISTORY_CONN',
            str(qa.ROOT / 'db/migrations/2026-10-23_trade_supply_parts/rollback.sql'), '--stop-on-error'], cwd=qa.ROOT,
            capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=50)
        log = (process.stdout + process.stderr).replace(os.environ['WMS_ORACLE_PASSWORD'], '[REDACTED]')
        (qa.OUT / 'supply-parts-history-rollback-refused.txt').write_text(log, encoding='utf-8')
        s['rollback_history'] = dict(exit_code=process.returncode, reason='SUPPLY_PART_HISTORY_PRESENT' in log); qa.save()
        assert process.returncode != 0 and s['rollback_history']['reason']
    send('end_only_part2', b); assert send('end_only_part1', a)['status'] == 'DELIVERED'
    sp.assert_document(a)
    for key, change, reason in [('TOTAL', {'total_codes': 4}, 'TOTAL_MISMATCH'), ('HASH', {'codes_sha256': '0' * 64}, 'CODES_HASH_MISMATCH')]:
        a, b, end = sp.bodies(key)
        send(key + '_part1', a); send(key + '_part2', b)
        result = send(key + '_end', dict(end, **change), True)
        assert result['status'] == 'MISMATCH' and result['status_reason'].startswith(reason), result
        absent(a['document_id'])
    codes = ['010460000000000121' + str(i).zfill(8) + 'X' * 375 for i in range(3000)]
    a, b, end = sp.bodies('BIG', codes=codes)
    a['codes'] = [dict(code=c) for c in codes[:1500]]; b['codes'] = [dict(code=c) for c in codes[1500:]]
    assert len(json.dumps(a).encode()) < 1024 * 1024 and len(json.dumps(b).encode()) < 1024 * 1024
    send('big_part1', a); send('big_part2', b)
    result = send('big_end', end, True)
    assert result['status'] == 'DELIVERY_REJECTED' and result['status_reason'] == 'SUPPLY_ASSEMBLED_TOO_LARGE', result
    assert send('big_replay', b)['status'] == 'DELIVERY_REJECTED'
    absent(a['document_id']); assert sp.canonical_count(a) == 0
    a, b, end = sp.bodies('WAITING')
    for body in (a, b, end):
        body['header']['sku_id'] = qa.TAG + '.SKU'
    send('waiting_part1', a); send('waiting_end', end, True)
    handed = send('waiting_part2', b)
    assert handed['status'] == 'DELIVERED' and handed['delivery']['status'] == 'WAITING', handed
    absent(a['document_id'])
    from app.modules.integrations.contracts_supply_parts import assembled_event_id
    event = assembled_event_id(a['source_id'], qa.W, a['transfer_id'])
    s['waiting_event'] = event; s['waiting_document'] = a['document_id']; qa.save()
    raw = qa.query("select BODY_JSON from RRL_TRADE_DOCUMENT where WARE_ID=:w and ENTITY_TYPE='SKU'and EXTERNAL_ID='A'", w=qa.W)[0][0]
    sku = json.loads(raw) if isinstance(raw, str) else raw
    qa.send('missing_sku_arrived', 'SKU', qa.TAG + '.SKU', sku)
    qa.step('waiting_retried', qa.BASE + '/messages/' + event + '/retry', {})
    sp.assert_document(a)
    qa.send('own_sku_deactivated', 'SKU', qa.TAG + '.SKU', dict(sku, active=False), 2)
    assert qa.stock() == [(250, 0)] and qa.query("select count(*)from USER_OBJECTS where STATUS='INVALID'") == [(0,)]
    s['checks'] = ['END-only transfer retained; history rollback refused without dropping objects',
        'Total/hash mismatch never created SUPPLY', 'Two bounded parts assembled over1MB: durable rejection, no intake event',
        'Full composition handed to deferred intake while SKU missing; existing retry accepted it after master arrived, no goods received']
    s['slow_sql'] = qa.query('select LOG_ID,ELAPSED_MS,API_PATH,SQL_TEXT from RRL_SQL_SLOW_LOG where LOG_ID>:m order by ELAPSED_MS desc fetch first 20 rows only', m=s['slow_marker'])
    s['status'] = 'PASS'; s.pop('error', None); qa.save()


if __name__ == '__main__':
    s['previous_calls'] = s.get('calls', [])
    try:
        if s.get('status') != 'PASS':
            run()
        else:
            print('Closed; no commands sent')
    except Exception as exc:
        s['error'] = str(exc); qa.save(); raise
    finally:
        qa.save()
    print(s.get('status'))
