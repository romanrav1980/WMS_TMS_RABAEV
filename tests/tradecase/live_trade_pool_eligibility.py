"""Actual trade pool, wave consumption and shortage on existing marked stock."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sys
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parent))
import live_topup_common_pool as qa

qa.FILE = qa.OUT / 'trade-pool-live.json'
qa.s = json.loads(qa.FILE.read_text(encoding='utf-8')) if qa.FILE.exists() else dict(
    tag='PE23.' + uuid4().hex[:9], warehouse_id=qa.W, requests={}, results={}, checks=[])
qa.TAG = qa.s['tag']; qa.TRIP = qa.BASE + '/trips/' + qa.TAG
s = qa.s


def prepare():
    if 'before' not in s:
        assert qa.stock() == [(250, 0)]
        s.update(before=qa.stock(), departure=(datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
                 policy_before=qa.expect(200, qa.http('GET', qa.POLICY)),
                 slow_marker=qa.query('select nvl(max(LOG_ID),0)from RRL_SQL_SLOW_LOG')[0][0])
        s['before_units'] = qa.query("select u.PHYSICAL_UNIT_KEY,u.CURRENT_UID,u.CURRENT_CELL,u.STOCK_STATUS,u.HARD_RESERVATION_ID,a.OWNER_ID,a.MRC,a.EXPIRY_DATE,a.MARK_STATE from RRL_WMS_RECEIPT_UNIT u join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY where u.CURRENT_UID='690000000445629982'and u.STOCK_STATUS<>'ISSUED'order by u.PHYSICAL_UNIT_KEY")
        assert len(s['before_units']) == 250
        qa.save()
    p = s['policy_before']
    qa.step('policy_on', qa.POLICY, dict(expected_version=p['policy_version'], stock_class=p['stock_class'],
        ship_from_stock=True, pick_step=p['pick_step']), method='PUT')


def order(key, quantity, min_osg_days=0):
    external = qa.TAG + '.' + key
    qa.send('doc_' + key, 'ORDER', external, dict(order_kind='OUTBOUND', recipient_id='C1', planned_ship_at=s['departure'],
        lines=[dict(line_id='1', sku_id='A', source_owner_id='SNS', target_owner_id='SNS', mrc='200',
                    quantity=str(quantity), uom='EA', min_osg_days=min_osg_days)]))
    return qa.native_order('native_' + key, external, quantity)


def run():
    prepare()
    main = order('MAIN', 20)
    preview = qa.step('preview', qa.POOL, method='GET')
    assert preview['allocations'][str(main['row'])] == '20', preview
    allocated = qa.step('allocated', qa.POOL + '/allocate', dict(operation_id=qa.TAG + '.allocate'))
    assert allocated['allocated_quantity'] == '20', allocated
    assert qa.expect(200, qa.http('POST', qa.POOL + '/allocate', s['requests']['allocated']['body'])) == allocated
    s['plan'] = qa.step('plan', '/api/picking/plans', dict(operation_id=qa.TAG + '.plan', customer_order_id=main['order']))['pick_plan_id']
    s['wave'] = qa.step('wave', '/api/picking/waves', dict(wave_code=qa.TAG, wave_name='Owned trade pool proof', ware_id=qa.W,
        planned_start_at=datetime.now(timezone.utc).isoformat(), planned_finish_at=s['departure']))['pick_wave_id']; qa.save()
    path = f"/api/picking/waves/{s['wave']}"
    qa.step('added', path + '/plans', dict(pick_plan_id=s['plan']))
    qa.step('calculated', path + '/calculate', {})
    launched = qa.step('launched', path + '/launch', dict(operation_id=qa.TAG + '.launch'))
    assert qa.expect(200, qa.http('POST', path + '/launch', s['requests']['launched']['body'])) == launched
    assert qa.stock() == [(250, 20)]
    assert qa.query("select QTY,STATUS from RRL_STOCK_RESERVATION where POOL_WARE_ID=:w and SOURCE_LINE_ID=:r and RESERVATION_KIND='SOFT'order by RESERVATION_ID", w=qa.W, r=main['row']) == [(0, 'CONSUMED')]
    other = order('SHORT', 300)
    incompatible = order('OSG', 10, 3650)
    current = qa.step('after_hard', qa.POOL, method='GET')
    assert current['available_quantity'] == '230', current
    assert current['allocations'][str(main['row'])] == '0'
    assert current['allocations'][str(other['row'])] == '230'
    assert current['allocations'][str(incompatible['row'])] == '0'
    blocked = next(x for x in current['orders'] if x['line_id'] == incompatible['row'])
    assert blocked['pool_reason'] == 'TRADE_ORDER_OSG_NOT_MET', blocked
    qa.step('short_allocated', qa.POOL + '/allocate', dict(operation_id=qa.TAG + '.short'))
    if 'concurrency' not in s:
        bodies = [dict(operation_id=qa.TAG + '.parallel.' + str(i)) for i in range(2)]
        s['parallel_requests'] = bodies; qa.save()
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda body: qa.http('POST', qa.POOL + '/allocate', body), bodies))
        s['concurrency'] = results; qa.save()
        assert all(x[0] == 200 for x in results), results
    assert qa.stock() == [(250, 20)]
    assert qa.query("select sum(QTY)from RRL_STOCK_RESERVATION where POOL_WARE_ID=:w and ARTICUL=:a and RESERVATION_KIND='SOFT'and STATUS in('ACTIVE','ALLOCATED')", w=qa.W, a=qa.ARTICLE) == [(230,)]
    s['checks'].append('20 consumed once at launch; 230 shared from remaining stock; incompatible expiry0; concurrent recalculations did not duplicate shares')
    s['status'] = 'BUSINESS_PASS_CLEANUP_REQUIRED'; qa.save()
    cleanup()


def cleanup():
    qa.step('wave_cancelled', f"/api/picking/waves/{s['wave']}/cancel", dict(operation_id=qa.TAG + '.cancel', reason='End owned common-pool proof without stock movement'))
    for task, sscc, version in qa.query("select CASE_PICK_TASK_ID,SSCC,CONTENT_VERSION from RRL_CASE_PICK_TASK where PICK_WAVE_ID=:w and STATUS<>'CANCELLED'", w=s['wave']):
        assert qa.query('select count(*)from RRL_CASE_CARRIER_LOT where CASE_PICK_TASK_ID=:t', t=task) == [(0,)]
        qa.step('empty_' + str(task), f'/api/case-pick/tasks/{task}/return-carrier', dict(operation_id=qa.TAG + '.empty.' + str(task),
            scan_container=sscc, expected_content_version=version, destinations={}, allow_empty=True, reason='Cancel own empty carrier'))
    for key in ('MAIN', 'SHORT', 'OSG'):
        if 'doc_' + key in s['results']:
            body = s['requests']['doc_' + key]['body']['payload']
            qa.send('cancel_' + key, 'ORDER', qa.TAG + '.' + key, dict(body, cancelled=True), 2)
    qa.step('pool_final', qa.POOL + '/allocate', dict(operation_id=qa.TAG + '.final'))
    p = s['policy_before']; version = qa.expect(200, qa.http('GET', qa.POLICY))['policy_version']
    qa.step('policy_restored', qa.POLICY, dict(expected_version=version, stock_class=p['stock_class'],
        ship_from_stock=p['ship_from_stock'], pick_step=p['pick_step']), method='PUT')
    assert qa.stock() == [(250, 0)]
    now = qa.query("select u.PHYSICAL_UNIT_KEY,u.CURRENT_UID,u.CURRENT_CELL,u.STOCK_STATUS,u.HARD_RESERVATION_ID,a.OWNER_ID,a.MRC,a.EXPIRY_DATE,a.MARK_STATE from RRL_WMS_RECEIPT_UNIT u join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY where u.CURRENT_UID='690000000445629982'and u.STOCK_STATUS<>'ISSUED'order by u.PHYSICAL_UNIT_KEY")
    assert json.loads(json.dumps(now, default=str)) == s['before_units']
    assert qa.query("select count(*)from USER_OBJECTS where STATUS='INVALID'") == [(0,)]
    s['slow_sql'] = qa.query('select LOG_ID,ELAPSED_MS,API_PATH,SQL_TEXT from RRL_SQL_SLOW_LOG where LOG_ID>:m order by ELAPSED_MS desc fetch first 25 rows only', m=s['slow_marker'])
    s['status'] = 'PASS_ADMIN_SCOPE_PENDING'; s.pop('error', None); qa.save()


if __name__ == '__main__':
    s['previous_calls'] = s.get('calls', [])
    try:
        if s.get('status') == 'PASS_ADMIN_SCOPE_PENDING':
            print('Already closed; no commands sent')
        elif sys.argv[-1] == 'cleanup' or s.get('status') == 'BUSINESS_PASS_CLEANUP_REQUIRED':
            cleanup()
        else:
            run()
    except Exception as exc:
        s['error'] = str(exc); qa.save(); raise
    finally:
        qa.save()
    print(json.dumps(dict(status=s.get('status'), wave=s.get('wave'))))
