"""Actual partial SUPPLY intake: isolated metadata, immutable events and process recovery; no goods receipts."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import secrets
import subprocess
import sys
from urllib.request import urlopen
from uuid import uuid4

sys.path[:0] = [str(Path(__file__).resolve().parent), str(Path(__file__).resolve().parents[2] / 'api/wms_api_server')]
import live_topup_common_pool as qa

qa.OUT = qa.ROOT / 'runtime/test-evidence/tradecase/2026-10-23/T02'
qa.FILE = qa.OUT / 'supply-parts-live.json'
qa.s = json.loads(qa.FILE.read_text(encoding='utf-8')) if qa.FILE.exists() else dict(
    tag='SP23.' + uuid4().hex[:9], warehouse_id=qa.W, requests={}, results={}, checks=[])
qa.TAG = qa.s['tag']; s = qa.s
PART = '/api/tradecase/supply-parts'
DELIVER = qa.BASE + '/supply-transfers/deliver'


def prepare():
    with urlopen('http://127.0.0.1:8088/openapi.json') as response:
        schema = json.load(response)
    assert '/api/tradecase/warehouses/{warehouse_id}/supply-transfers/deliver' in schema['paths'], 'Restart READY API before running'
    assert 'header' in schema['components']['schemas']['TradeSupplyPartsEnd']['required']
    if 'header' not in s:
        assert qa.stock() == [(250, 0)]
        raw = qa.query("select BODY_JSON from RRL_TRADE_DOCUMENT where WARE_ID=:w and ENTITY_TYPE='SUPPLY'and STATUS='ACCEPTED'order by EXTERNAL_ID fetch first 1 row only", w=qa.W)[0][0]
        header = json.loads(raw) if isinstance(raw, str) else raw
        header.pop('codes'); header['supplier_batch'] = 'TEST_PARTS_NOT_ERP.' + qa.TAG
        s.update(header=header, at=datetime.now(timezone.utc).isoformat(), actor='PS' + uuid4().hex[:12], password=secrets.token_hex(20),
            slow_marker=qa.query('select nvl(max(LOG_ID),0)from RRL_SQL_SLOW_LOG')[0][0], before=qa.stock()); qa.save()
    if 'identity' not in s:
        with qa.oracle_connection() as conn:
            q = conn.cursor(); q.execute('select count(*)from RUSERS where ID=:a', a=s['actor'])
            if not q.fetchone()[0]:
                q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'Owned parts proof','QA_PARTS_ONLY',:w,0,1)", a=s['actor'], p=s['password'], w=qa.W)
                q.execute("insert into RRL_ACCESS_ROLE(ROLE_ID,TITLE,ACTIVE,VERSION_NO)values(:a,'Owned parts proof',1,1)", a=s['actor'])
                for right in ['tradecase_import', 'tradecase_view']:
                    q.execute('insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION)values(:a,:r)', a=s['actor'], r=right)
                q.execute("insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO)values(:a,:a,:a,'WAREHOUSE',:w,'CURRENT',systimestamp-interval '1'minute,systimestamp+interval '2'hour,'admin','Own parts proof',1)", a=s['actor'], w=str(qa.W)); conn.commit()
        s['identity'] = True; qa.save()
    qa.step('owner', qa.BASE + '/stock/owner-grants', dict(operation_id=qa.TAG + '.owner', expected_version=0, username=s['actor'],
        owner_id='SNS', can_view=True, can_operate=True, reason='Own metadata parts acceptance'), method='PUT')


def bodies(key, version=1, document=None, codes=None):
    document = document or qa.TAG + '.DOC.' + key
    codes = codes or ['010460000000000121' + qa.TAG.replace('.', '') + key + str(i) for i in range(3)]
    header = dict(s['header'], pallet_identifier=qa.TAG + '.PAL.' + key)
    base = dict(schema_version=1, source_id='TC03.SAP', warehouse_id=qa.W, document_id=document, version=version,
        transfer_id=qa.TAG + '.' + key, part_count=2, occurred_at=s['at'], header=header)
    mid = len(codes) - 1
    p1 = dict(base, event_id=qa.TAG + '.' + key + '.P1', part_no=1, codes=[dict(code=c) for c in codes[:mid]])
    p2 = dict(base, event_id=qa.TAG + '.' + key + '.P2', part_no=2, codes=[dict(code=c) for c in codes[mid:]])
    end = dict(base, event_id=qa.TAG + '.' + key + '.END', total_codes=len(codes), codes_sha256=hashlib.sha256('\n'.join(codes).encode()).hexdigest())
    return p1, p2, end


def send(key, body, ending=False, status=200):
    return qa.step(key, PART + ('/end' if ending else ''), body, qa=True, status=status)


def canonical_count(body):
    from app.modules.integrations.contracts_supply_parts import assembled_event_id
    event = assembled_event_id(body['source_id'], qa.W, body['transfer_id'])
    return qa.query('select count(*)from RRL_TRADE_MESSAGE where WARE_ID=:w and SOURCE_ID=:s and EVENT_ID=:e', w=qa.W, s=body['source_id'], e=event)[0][0]


def assert_document(body):
    rows = qa.query("select VERSION_NO,BODY_JSON from RRL_TRADE_DOCUMENT where WARE_ID=:w and ENTITY_TYPE='SUPPLY'and EXTERNAL_ID=:d", w=qa.W, d=body['document_id'])
    assert len(rows) == 1 and rows[0][0] == body['version'], rows
    assert canonical_count(body) == 1


def ordered():
    if s.get('ordered_complete'):
        return
    p1, p2, end = bodies('ORDERED')
    first = send('end_first', end, True)
    assert first['status'] == 'OPEN' and first['missing_parts'] == [1, 2] and first['received_codes'] == 0
    if 'end_first_document_count' not in s:
        s['end_first_document_count'] = qa.query("select count(*)from RRL_TRADE_DOCUMENT where WARE_ID=:w and ENTITY_TYPE='SUPPLY'and EXTERNAL_ID=:d", w=qa.W, d=p1['document_id'])[0][0]; qa.save()
    assert s['end_first_document_count'] == 0
    second = send('part2', p2); assert second['missing_parts'] == [1]
    assert send('part2_replay', p2)['replayed']
    bad = dict(p2, codes=[dict(code='010460000000000121DIFFERENTVALUE')])
    send('part2_changed', bad, status=409)
    send('part2_alias', dict(p2, event_id=qa.TAG + '.ALIAS'), status=409)
    send('part_end_event_collision', dict(p1, event_id=end['event_id']), status=409)
    send('end_part_event_collision', dict(end, transfer_id=qa.TAG + '.COLLISION', event_id=p2['event_id']), True, 409)
    send('end_reuse_other_transfer', dict(end, transfer_id=qa.TAG + '.COLLISION'), True, 409)
    assert send('end_replay', end, True)['replayed']
    send('end_header_conflict', dict(end, header=dict(end['header'], supplier_batch='OTHER_BATCH')), True, 409)
    result = send('part1', p1); assert result['status'] == 'DELIVERED', result
    if 'v2_part1' not in s['results']:
        assert_document(p1)
    assert send('part1_replay', p1)['status'] == 'DELIVERED'
    send('linebreak_rejected', dict(p1, event_id=qa.TAG + '.LF', transfer_id=qa.TAG + '.LF', codes=[dict(code=p1['codes'][0]['code'] + '\n' + p2['codes'][0]['code'])]), status=422)
    a, b, e = bodies('V2', version=2, document=p1['document_id'])
    send('v2_part2', b); send('v2_end', e, True); assert send('v2_part1', a)['status'] == 'DELIVERED'
    send('late_old_new_event', dict(p1, event_id=qa.TAG + '.OLD.NEW', transfer_id=qa.TAG + '.OLD.NEW'), status=409)
    assert send('historical_replay', p1)['status'] == 'DELIVERED'
    assert_document(a)
    s['checks'].append('END before all parts persisted; missing list, stable retry, conflicts and event namespace; corrected v2 survives late v1')
    s['ordered_body'] = p1; s['ordered_complete'] = True; qa.save()


def race():
    if s.get('race_complete'):
        return
    a, b, e = bodies('RACE')
    send('race_part2', b)
    if 'race_results' not in s:
        s['race_requests'] = [a, e]; qa.save()
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda item: qa.http('POST', item[0], item[1], s['actor'], s['password']), [(PART, a), (PART + '/end', e)]))
        s['race_results'] = results; qa.save()
        assert all(r[0] == 200 for r in results), results
    assert_document(a)
    assert qa.query('select STATUS from RRL_TRADE_SUPPLY_TRANSFER where WARE_ID=:w and SOURCE_ID=:s and TRANSFER_ID=:t', w=qa.W, s=a['source_id'], t=a['transfer_id']) == [('DELIVERED',)]
    s['checks'].append('Concurrent last part and END committed one canonical intake event')
    s['race_complete'] = True; qa.save()


def recovery(key, after):
    a, b, e = bodies(key)
    if key + '_delivered' in s['results']:
        assert_document(a)
        return
    send(key + '_part2', b); send(key + '_end', e, True)
    marker = key + '_child'
    if marker not in s:
        s[key + '_body'] = a; qa.save()
        script = "import sys,os;sys.path[:0]=['tests/tradecase','api/wms_api_server'];import live_supply_parts as t;from app.oracle_gateway import OracleGateway;from app.modules.integrations.infrastructure.supply_parts import OracleSupplyParts,OracleTradecaseDocuments;from app.modules.integrations.contracts_supply_parts import TradeSupplyPart;original=OracleTradecaseDocuments.receive\ndef crash(self,body,actor):\n " + ("original(self,body,actor);" if after else "") + "os._exit(" + str(97 if after else 96) + ")\nOracleTradecaseDocuments.receive=crash\nOracleSupplyParts(OracleGateway()).put_part(TradeSupplyPart.model_validate(t.s[" + repr(key + '_body') + "]),t.s['actor'])"
        process = subprocess.run([sys.executable, '-c', script], cwd=qa.ROOT, capture_output=True, text=True, timeout=40)
        s[marker] = dict(exit_code=process.returncode, stdout=process.stdout, stderr=process.stderr); qa.save()
        assert process.returncode == (97 if after else 96), s[marker]
    assert canonical_count(a) == (1 if after else 0)
    assert qa.query('select STATUS from RRL_TRADE_SUPPLY_TRANSFER where WARE_ID=:w and SOURCE_ID=:s and TRANSFER_ID=:t', w=qa.W, s=a['source_id'], t=a['transfer_id']) == [('COMPLETE',)]
    delivered = qa.step(key + '_delivered', DELIVER, dict(source_id=a['source_id'], transfer_id=a['transfer_id']), qa=True)
    assert delivered['status'] == 'DELIVERED'; assert_document(a)
    s['checks'].append('Adapter process exits' + (' after real canonical commit' if after else ' before canonical intake') + '; HTTP recovery keeps one canonical event')


def finish():
    body = s['ordered_body']
    send('wrong_source', dict(body, event_id=qa.TAG + '.WRONG.SRC', source_id='NOT_CONFIGURED', transfer_id=qa.TAG + '.WRONG.SRC'), status=409)
    send('wrong_warehouse', dict(body, event_id=qa.TAG + '.WRONG.WARE', warehouse_id=219023232, transfer_id=qa.TAG + '.WRONG.WARE'), status=403)
    qa.step('owner_revoked', qa.BASE + '/stock/owner-grants', dict(operation_id=qa.TAG + '.owner.revoke', expected_version=1,
        username=s['actor'], owner_id='SNS', can_view=False, can_operate=False, reason='Revoke own metadata sender'), method='PUT')
    send('owner_replay_denied', body, status=403)
    listing = qa.step('hidden_list', qa.BASE + '/supply-transfers', method='GET', qa=True)
    assert qa.TAG not in json.dumps(listing), listing
    with qa.oracle_connection() as conn:
        q = conn.cursor(); q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp,VERSION_NO=VERSION_NO+1 where ASSIGNMENT_ID=:a and REVOKED_AT is null', a=s['actor'])
        q.execute('update RUSERS set DELETED=1 where ID=:a', a=s['actor']); conn.commit()
    assert qa.stock() == [(250, 0)] and qa.query("select count(*)from USER_OBJECTS where STATUS='INVALID'") == [(0,)]
    s['slow_sql'] = qa.query('select LOG_ID,ELAPSED_MS,API_PATH,SQL_TEXT from RRL_SQL_SLOW_LOG where LOG_ID>:m order by ELAPSED_MS desc fetch first 25 rows only', m=s['slow_marker'])
    s['status'] = 'PASS'; s.pop('error', None); qa.save()


if __name__ == '__main__':
    s['previous_calls'] = s.get('calls', [])
    try:
        if s.get('status') != 'PASS':
            prepare(); ordered(); race(); recovery('BEFORE', False); recovery('AFTER', True); finish()
        else:
            print('Closed; no commands sent')
    except Exception as exc:
        s['error'] = str(exc); qa.save(); raise
    finally:
        qa.save()
    print(s.get('status'))
