"""Resumable common-pool acceptance on existing stock; no physical receipts."""
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import secrets
import sys
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT / 'tests/tradecase'), str(ROOT)]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
os.environ.setdefault('TRADECASE_ADMIN_USER', 'admin')
os.environ.setdefault('TRADECASE_ADMIN_PASSWORD', 'admin123')
from live_document_acceptance import http, expect, CALLS
from tools.mcp.tms_mcp_server import oracle_connection

OUT = ROOT / 'runtime/test-evidence/tradecase/2026-10-23/T08'
FILE = OUT / 'common-pool-live.json'
s = json.loads(FILE.read_text(encoding='utf-8')) if FILE.exists() else dict(
    tag='PC23.' + uuid4().hex[:9], warehouse_id=210564699, requests={}, results={}, checks=[])
W = s['warehouse_id']
TAG = s['tag']
ARTICLE = 'TC03089DDB36'
BASE = f'/api/tradecase/warehouses/{W}'
TRIP = BASE + '/trips/' + TAG
POOL = f'/api/inventory/soft-pools/{W}/{ARTICLE}'
POLICY = f'/api/sku-allocation/{W}/{ARTICLE}'


def save():
    OUT.mkdir(parents=True, exist_ok=True)
    s['calls'] = s.get('previous_calls', []) + CALLS
    FILE.write_text(json.dumps(s, indent=2, default=str), encoding='utf-8')


def query(sql, **binds):
    with oracle_connection() as conn:
        q = conn.cursor()
        q.execute(sql, binds)
        return [tuple(x.read() if hasattr(x, 'read') else x for x in row) for row in q.fetchall()]


def stock():
    return query('select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE) from RRL_REMAINS r '
                 'join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w', w=W)


def step(key, path, body=None, method='POST', status=200, qa=False):
    if key not in s['requests']:
        s['requests'][key] = dict(path=path, body=body, method=method, status=status, qa=qa)
        save()
    if key not in s['results']:
        r = s['requests'][key]
        args = (s['actor'], s['password']) if r['qa'] else ()
        s['results'][key] = expect(r['status'], http(r['method'], r['path'], r['body'], *args))
        save()
    return s['results'][key]


def send(key, kind, identifier, body, version=1):
    return step(key, '/api/tradecase/messages', dict(schema_version=1, event_id=TAG + '.' + key,
        source_id='TC03.SAP', warehouse_id=W, document_id=identifier, version=version,
        occurred_at=datetime.now(timezone.utc).isoformat(), payload=dict(body, entity_type=kind)))


def native_order(key, external, quantity):
    if key not in s:
        with oracle_connection() as conn:
            q = conn.cursor()
            q.callproc('RRL_STOCK_METADATA_TX.begin_change', ['admin', 'warehouse_settings_edit'])
            try:
                q.execute('select CUSTOMER_ORDER_ID from RRL_CUSTOMER_ORDER where ORDER_NO=:n', n=external)
                existing = q.fetchone()
                if existing:
                    native = existing[0]
                    q.execute('select CUSTOMER_ORDER_ROW_ID from RRL_CUSTOMER_ORDER_ROW where CUSTOMER_ORDER_ID=:o', o=native)
                    row = q.fetchone()[0]
                else:
                    q.execute('select RRL_CUSTOMER_ORDER_SQ.nextval,RRL_CUSTOMER_ORDER_ROW_SQ.nextval from dual')
                    native, row = q.fetchone()
                    q.execute("insert into RRL_CUSTOMER_ORDER(CUSTOMER_ORDER_ID,ORDER_NO,CUSTOMER_ID,WARE_ID,SHIPMENT_DATE,STATUS,SOURCE_SYSTEM,CREATED_BY) values(:o,:n,770,:w,to_date(:d,'YYYY-MM-DD'),'OPEN','QA_TRADECASE_ONLY','admin')",
                              o=native, n=external, w=W, d=s['departure'][:10])
                    q.execute("insert into RRL_CUSTOMER_ORDER_ROW(CUSTOMER_ORDER_ROW_ID,CUSTOMER_ORDER_ID,LINE_NO,ARTICUL,PRODUCT_NAME,UNIT_CODE,ORDER_QTY,WARE_ID,STATUS,CREATED_BY) values(:r,:o,1,:a,'Owned pool adoption proof','EA',:qty,:w,'OPEN','admin')",
                              r=row, o=native, a=ARTICLE, qty=quantity, w=W)
                    conn.commit()
                s[key] = dict(order=native, row=row)
                save()
            finally:
                q.callproc('RRL_STOCK_METADATA_TX.end_change')
    n = s[key]
    step(key + '_binding', BASE + '/orders/' + external + '/binding', dict(operation_id=TAG + '.' + key + '.bind',
        expected_order_version=1, customer_order_id=n['order'], lines=[dict(line_id='1', customer_order_row_id=n['row'])]))
    return n


def setup():
    if 'before' not in s:
        assert stock() == [(250, 0)]
        assert query('select NAME from RRL_WARES where ID=:w', w=W) == [('TRADECASE QA 089ddb36',)]
        s['before'] = stock()
        s['policy_before'] = expect(200, http('GET', POLICY))
        s['departure'] = (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()
        s['slow_marker'] = query('select nvl(max(LOG_ID),0) from RRL_SQL_SLOW_LOG')[0][0]
        s.update(actor='PC' + uuid4().hex[:12], password=secrets.token_hex(20))
        save()
    if not s.get('actor_created'):
        with oracle_connection() as conn:
            q = conn.cursor()
            q.execute('select count(*) from RUSERS where ID=:a', a=s['actor'])
            if not q.fetchone()[0]:
                q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED) values(:a,:p,'Owned pool proof','QA_ONLY',:w,0)", a=s['actor'], p=s['password'], w=W)
                q.execute("insert into RRL_ACCESS_ROLE(ROLE_ID,TITLE,ACTIVE,VERSION_NO) values(:a,'Owned pool proof',1,1)", a=s['actor'])
                for right in ['tradecase_view', 'tradecase_topup_approve', 'tradecase_topup_result']:
                    q.execute('insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION) values(:a,:r)', a=s['actor'], r=right)
                q.execute("insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO) values(:a,:a,:a,'WAREHOUSE',:w,'CURRENT',systimestamp-interval '1' minute,systimestamp+interval '12' hour,'admin','Owned pool acceptance',1)", a=s['actor'], w=str(W))
                conn.commit()
        s['actor_created'] = True
        save()
    step('owner_grant', BASE + '/stock/owner-grants', dict(operation_id=TAG + '.owner', expected_version=0,
        username=s['actor'], owner_id='SNS', can_view=True, can_operate=True, reason='Owned pool acceptance'), method='PUT')
    p = s['policy_before']
    step('policy_pool', POLICY, dict(expected_version=p['policy_version'], stock_class=p['stock_class'],
        ship_from_stock=True, pick_step=p['pick_step']), method='PUT')
    line = dict(line_id='1', sku_id='A', source_owner_id='SNS', target_owner_id='SNS', mrc='200', quantity='20', uom='EA', min_osg_days=0)
    send('primary_doc', 'ORDER', TAG + '.MAIN', dict(order_kind='OUTBOUND', recipient_id='C1', planned_ship_at=s['departure'], lines=[line]))
    native_order('primary_native', TAG + '.MAIN', 20)
    s['trip_body'] = dict(vehicle_id='TP22.089ddb36', planning_source='SAP', planned_departure_at=s['departure'],
        capacity_kg='8000', capacity_m3='0.6', orders=[dict(order_id=TAG + '.MAIN', line_id='1', quantity='20')])
    save()
    send('trip_doc', 'TRIP', TAG, s['trip_body'])
    now = datetime.now(timezone.utc)
    send('need_doc', 'NEED', TAG + '.NEED', dict(recipient_id='C1', sku_id='A', recipient_version=2, sku_version=1,
        snapshot_at=now.isoformat(), period_from=now.isoformat(), period_until=(now + timedelta(days=1)).isoformat(),
        uom='BOX', forecast_quantity='6', target_quantity='0', available_quantity='0', received_in_available=True,
        supplies=[dict(supply_id=TAG + '.SUPPLY', version=1, quantity='2', uom='BOX', status='PLANNED',
                       confirmed=True, current_trip=True, expected_at=s['departure'])]))


def run():
    if s.get('status') in ('PASS', 'ADOPTION_PASS_PRIMARY_POOL_OPEN'):
        print('Already PASS; no commands sent')
        return
    if s.get('status') == 'TRANSFER_PASS_CLEANUP_REQUIRED' or 'wave_cancelled' in s['results']:
        cleanup()
        return
    setup()
    saved = step('saved', TRIP + '/topup-proposals', dict(operation_id=TAG + '.save', need_ids=[TAG + '.NEED'], max_age_minutes=1440), qa=True)
    proposal = saved['proposals'][0]
    assert proposal['approved_boxes'] == 4, proposal
    pid = proposal['proposal_id']
    s['proposal_id'] = pid
    save()
    confirmed = step('confirmed', TRIP + f'/topup-proposals/{pid}/confirm', dict(operation_id=TAG + '.confirm', expected_version=proposal['version']), qa=True)
    assert stock() == [(250, 40)]
    if 'held_units' not in s:
        s['held_units'] = query('select u.PHYSICAL_UNIT_KEY,u.HARD_RESERVATION_ID from RRL_WMS_RECEIPT_UNIT u join RRL_TRADE_TOPUP_HOLD h on h.RESERVATION_ID=u.HARD_RESERVATION_ID where h.PROPOSAL_ID=:p order by u.PHYSICAL_UNIT_KEY', p=pid)
        assert len(s['held_units']) == 40
        save()
    step('sap_reply', TRIP + f'/topup-proposals/{pid}/sap-reply', dict(operation_id=TAG + '.sap', expected_version=confirmed['version'],
        source_id='TC03.SAP', event_id=TAG + '.SAP', outcome='ACCEPTED', sap_order_id=TAG + '.EXTRA'), qa=True)
    send('extra_doc', 'ORDER', TAG + '.EXTRA', dict(order_kind='TOPUP', parent_trip_id=TAG, recipient_id='C1', planned_ship_at=s['departure'],
        lines=[dict(line_id='1', sku_id='A', source_owner_id='SNS', target_owner_id='SNS', mrc='200', quantity='40', uom='EA', min_osg_days=0)]))
    n = native_order('extra_native', TAG + '.EXTRA', 40)
    if 'trip_updated' not in s['results']:
        assert query('select RRL_TRADE_TOPUP_ADOPT.line_proposal(:r) from dual', r=n['row']) == [(-1,)]
        step('missing_trip', '/api/picking/plans', dict(operation_id=TAG + '.missing.trip', customer_order_id=n['order']), status=409)
    send('trip_updated', 'TRIP', TAG, dict(s['trip_body'], orders=s['trip_body']['orders'] + [dict(order_id=TAG + '.EXTRA', line_id='1', quantity='40')]), 2)
    if 'launched' not in s['results']:
        assert query('select RRL_TRADE_TOPUP_ADOPT.line_proposal(:r) from dual', r=n['row']) == [(pid,)]
    preview = step('pool_preview', POOL, method='GET')
    rows = {int(x['line_id']): x for x in preview['orders']}
    assert rows[n['row']]['quantity'] == '0', preview
    assert rows[s['primary_native']['row']]['quantity'] == '20', preview
    allocated = step('pool_allocated', POOL + '/allocate', dict(operation_id=TAG + '.pool'))
    assert stock() == [(250, 40)]
    assert query("select nvl(sum(BASE_QTY),0) from RRL_STOCK_RESERVATION where POOL_WARE_ID=:w and SOURCE_LINE_ID=:r and RESERVATION_KIND='SOFT' and STATUS in('ACTIVE','ALLOCATED')", w=W, r=n['row']) == [(0,)]
    s['checks'].append('Primary demand20; own top-up pool demand0; HARD remains40. Primary allocation is ZERO: trade stock requires order binding in generic eligibility')
    s['primary_pool_gap'] = dict(reason='TRADE_ORDER_BINDING_REQUIRED', allocated_quantity=allocated['allocated_quantity'],
        decision='Do not weaken trade stock guard; owner/MRC-aware pool eligibility remains open')
    plan = step('plan', '/api/picking/plans', dict(operation_id=TAG + '.plan', customer_order_id=n['order']))['pick_plan_id']
    s['plan'] = plan
    wave = step('wave', '/api/picking/waves', dict(wave_code=TAG, wave_name=TAG, ware_id=W,
        planned_start_at=datetime.now(timezone.utc).isoformat(), planned_finish_at=(datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()))['pick_wave_id']
    s['wave'] = wave
    save()
    wp = f'/api/picking/waves/{wave}'
    step('added', wp + '/plans', dict(pick_plan_id=plan))
    step('calculated', wp + '/calculate', {})
    launched = step('launched', wp + '/launch', dict(operation_id=TAG + '.launch'))
    assert expect(200, http('POST', wp + '/launch', s['requests']['launched']['body'])) == launched
    after = query('select u.PHYSICAL_UNIT_KEY,u.HARD_RESERVATION_ID from RRL_WMS_RECEIPT_UNIT u join RRL_TRADE_TOPUP_ADOPTION a on a.RESERVATION_ID=u.HARD_RESERVATION_ID where a.PROPOSAL_ID=:p order by u.PHYSICAL_UNIT_KEY', p=pid)
    assert [list(x) for x in after] == [list(x) for x in s['held_units']]
    assert stock() == [(250, 40)]
    s['checks'].append('Actual wave adopted same forty unit keys and HARD ids; exact launch replay unchanged')
    s['status'] = 'TRANSFER_PASS_CLEANUP_REQUIRED'
    save()
    cleanup()


def cleanup():
    pid = s['proposal_id']
    wp = f"/api/picking/waves/{s['wave']}"
    step('wave_cancelled', wp + '/cancel', dict(operation_id=TAG + '.cancel.wave', reason='End owned common-pool adoption proof without physical movements'))
    assert stock() == [(250, 0)]
    for task, carrier, version in query("select c.CASE_PICK_TASK_ID,c.SSCC,c.CONTENT_VERSION from RRL_PICK_TASK t join RRL_CASE_PICK_TASK c on c.CASE_PICK_TASK_ID=t.CASE_PICK_TASK_ID where t.PICK_PLAN_ID=:p and c.STATUS<>'CANCELLED'", p=s['plan']):
        assert query('select count(*) from RRL_CASE_CARRIER_LOT where CASE_PICK_TASK_ID=:t', t=task) == [(0,)]
        step('empty_' + str(task), f'/api/case-pick/tasks/{task}/return-carrier', dict(operation_id=TAG + '.empty.' + str(task),
            scan_container=carrier, expected_content_version=version, destinations={}, allow_empty=True, reason='Cancel empty own acceptance carrier'))
    v = query('select VERSION_NO from RRL_TRADE_TOPUP_PROPOSAL where PROPOSAL_ID=:p', p=pid)[0][0]
    step('proposal_released', TRIP + f'/topup-proposals/{pid}/release', dict(operation_id=TAG + '.release', expected_version=v), qa=True)
    r = s['requests']['proposal_released']
    if 'owner_retired' not in s['results']:
        replay = expect(200, http('POST', r['path'], r['body'], s['actor'], s['password']))
        assert replay['status'] == 'CANCELLED'
    send('trip_cancelled_valid', 'TRIP', TAG, dict(s['trip_body'], cancelled=True), 3)
    for key, kind in [('MAIN', 'primary_doc'), ('EXTRA', 'extra_doc')]:
        body = s['requests'][kind]['body']['payload']
        send('cancel_' + key, 'ORDER', TAG + '.' + key, dict(body, cancelled=True), 2)
    step('pool_final', POOL + '/allocate', dict(operation_id=TAG + '.pool.final'))
    p = s['policy_before']
    v = expect(200, http('GET', POLICY))['policy_version']
    step('policy_restored', POLICY, dict(expected_version=v, stock_class=p['stock_class'],
        ship_from_stock=p['ship_from_stock'], pick_step=p['pick_step']), method='PUT')
    step('owner_retired', BASE + '/stock/owner-grants', dict(operation_id=TAG + '.owner.retire', expected_version=1,
        username=s['actor'], owner_id='SNS', can_view=False, can_operate=False, reason='End owned acceptance'), method='PUT')
    step('replay_owner_denied', r['path'], r['body'], qa=True, status=403)
    with oracle_connection() as conn:
        q = conn.cursor()
        q.execute('update RUSERS set DELETED=1 where ID=:a', a=s['actor'])
        q.execute("update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp,VERSION_NO=VERSION_NO+1 where ASSIGNMENT_ID=:a and REVOKED_AT is null", a=s['actor'])
        conn.commit()
    assert stock() == [(250, 0)]
    assert query("select STATUS from RRL_TRADE_TOPUP_HOLD where PROPOSAL_ID=:p", p=pid) == [('RELEASED',)]
    s['slow_sql'] = query('select LOG_ID,ELAPSED_MS,OPERATION_KIND from RRL_SQL_SLOW_LOG where LOG_ID>:n order by LOG_ID fetch first 40 rows only', n=s['slow_marker'])
    s['checks'].append('Wave and empty carrier cancelled, proposal reconciled; replay allowed then denied after owner revoke; policy restored, actor retired, stock250/H0')
    s['status'] = 'ADOPTION_PASS_PRIMARY_POOL_OPEN'
    s.pop('error', None)
    s.pop('error_type', None)
    save()


if __name__ == '__main__':
    s['previous_calls'] = s.get('calls', [])
    try:
        run()
    except Exception as exc:
        s.update(status='FAIL', error_type=type(exc).__name__, error=str(exc))
        raise
    finally:
        save()
