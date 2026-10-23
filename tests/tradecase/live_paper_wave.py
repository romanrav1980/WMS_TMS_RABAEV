"""Paper completion of a real wave's replenishment; reuse existing 250EA without receiving goods."""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sys
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parent))
import live_topup_common_pool as qa

qa.OUT = qa.ROOT / 'runtime/test-evidence/tradecase/2026-10-23/T11'
qa.FILE = qa.OUT / 'paper-wave-state.json'
qa.s = json.loads(qa.FILE.read_text(encoding='utf-8')) if qa.FILE.exists() else dict(
    tag='PW23.' + uuid4().hex[:9], warehouse_id=210564699, requests={}, results={}, checks=[],
    hu='690000000445629982', source='T3S089ddb36', target='T3P089ddb36', fact_qty='250')
qa.TAG = qa.s['tag']
s = qa.s


def units():
    return qa.query("select u.PHYSICAL_UNIT_KEY,u.CURRENT_UID,u.CURRENT_CELL,u.STOCK_STATUS,u.HARD_RESERVATION_ID,a.OWNER_ID,a.MRC,a.EXPIRY_DATE,a.MARK_STATE from RRL_WMS_RECEIPT_UNIT u join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY where u.CURRENT_UID=:u and u.STOCK_STATUS<>'ISSUED'order by u.PHYSICAL_UNIT_KEY", u=s['hu'])


def prepare():
    if 'before' not in s:
        assert qa.stock() == [(250, 0)]
        assert qa.query('select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c', u=s['hu'], c=s['source']) == [(250, 0)]
        s.update(before=qa.stock(), before_units=units(), slow_marker=qa.query('select nvl(max(LOG_ID),0)from RRL_SQL_SLOW_LOG')[0][0],
                 departure=(datetime.now(timezone.utc) + timedelta(days=1)).isoformat())
        assert len(s['before_units']) == 250
        qa.save()
    qa.send('order_doc', 'ORDER', qa.TAG + '.ORDER', dict(order_kind='OUTBOUND', recipient_id='C1', planned_ship_at=s['departure'],
        lines=[dict(line_id='1', sku_id='A', source_owner_id='SNS', target_owner_id='SNS', mrc='200', quantity='10', uom='EA', min_osg_days=0)]))
    n = qa.native_order('native', qa.TAG + '.ORDER', 10)
    s['plan'] = qa.step('plan', '/api/picking/plans', dict(operation_id=qa.TAG + '.plan', customer_order_id=n['order']))['pick_plan_id']
    s['wave'] = qa.step('wave', '/api/picking/waves', dict(wave_code=qa.TAG, wave_name='Owned paper replenishment proof', ware_id=qa.W,
        planned_start_at=datetime.now(timezone.utc).isoformat(), planned_finish_at=s['departure']))['pick_wave_id']
    qa.save()
    path = f"/api/picking/waves/{s['wave']}"
    qa.step('add', path + '/plans', dict(pick_plan_id=s['plan']))
    qa.step('calculate', path + '/calculate', {})
    qa.step('launch', path + '/launch', dict(operation_id=qa.TAG + '.launch'))
    tasks = qa.query("select TASK_ID,UID_PALLET,FROM_CELL,TO_CELL,QTY,QTY_MODE from RRL_WAREHOUSE_TASK where SOURCE_DOC_TYPE='PICK_WAVE'and SOURCE_DOC_ID=:w and TASK_TYPE='REPLENISHMENT'and STATUS<>'CANCELLED'", w=s['wave'])
    assert len(tasks) == 1, tasks
    task, uid, source, target, qty, mode = tasks[0]
    assert (uid, source, target, qty, mode) == (s['hu'], s['source'], s['target'], 250, 'PALLET'), tasks
    s['task'] = task; qa.save()
    path = f'/api/warehouse-tasks/{task}'
    qa.step('assign', path + '/assign', dict(assigned_to='admin'))
    qa.step('start', path + '/start', {})
    s['paper'] = qa.step('paper', path + '/paper', method='GET')
    s['status'] = 'PREPARED'; qa.save()


def restore():
    assert qa.query('select STATUS,FACT_QTY from RRL_WAREHOUSE_TASK where TASK_ID=:t', t=s['task']) == [('DONE', 250)]
    assert qa.query('select sum(BASE_QTY)from RRL_WAREHOUSE_TASK_STOCK_MOVE where TASK_ID=:t', t=s['task']) == [(250,)]
    moved = units()
    assert len(moved) == 250 and all(x[2] == s['target'] for x in moved)
    s['moved_units'] = moved; qa.save()
    cases = qa.query("select CASE_PICK_TASK_ID,SSCC,CONTENT_VERSION from RRL_CASE_PICK_TASK where PICK_WAVE_ID=:w and STATUS<>'CANCELLED'", w=s['wave'])
    for task, sscc, version in cases:
        assert qa.query('select count(*)from RRL_CASE_CARRIER_LOT where CASE_PICK_TASK_ID=:t', t=task) == [(0,)]
        qa.step('cancel_empty_' + str(task), f'/api/case-pick/tasks/{task}/return-carrier', dict(operation_id=qa.TAG + '.empty.' + str(task),
            scan_container=sscc, expected_content_version=version, destinations={}, allow_empty=True, reason='End owned unpicked paper replenishment proof'))
    qa.step('finish', f"/api/picking/waves/{s['wave']}/finish-execution", dict(operation_id=qa.TAG + '.finish',
        disposition='RETURNED_TO_PLANNING', reason='Empty cases cancelled; return the unpicked demand without shipping'))
    assert qa.stock() == [(250, 0)]
    if 'scans' not in s:
        codes = qa.query("select u.PHYSICAL_UNIT_KEY,c.SYSTEM_CODE,c.RAW_CODE,c.PROFILES_JSON from RRL_WMS_RECEIPT_UNIT u join RRL_WMS_RECEIPT_CODE c on c.UID_PALLET=u.UID_PALLET and c.UNIT_ID=u.UNIT_ID where u.CURRENT_UID=:u and u.CURRENT_CELL=:cell and u.STOCK_STATUS='AVAILABLE'order by u.PHYSICAL_UNIT_KEY,c.SYSTEM_CODE", u=s['hu'], cell=s['target'])
        chosen = {}
        for key, system, code, profiles in codes:
            profiles = json.loads(profiles) if isinstance(profiles, str) else profiles
            chosen.setdefault(key, dict(system_code=system, profile_code=profiles[0]['profile'], code=code))
        assert len(chosen) == 250
        s['scans'] = list(chosen.values()); qa.save()
    qa.step('stock_restored', '/api/tradecase/warehouses/210564699/stock/sort', dict(operation_id=qa.TAG + '.restore',
        source_pallet=s['hu'], source_cell=s['target'], target_cell=s['source'], scans=s['scans']))
    body = s['requests']['order_doc']['body']['payload']
    qa.send('order_cancelled', 'ORDER', qa.TAG + '.ORDER', dict(body, cancelled=True), 2)
    assert qa.stock() == [(250, 0)]
    now = [list(x) for x in units()]
    # JSON serialization converts dates to strings; compare the same retained representation.
    assert json.loads(json.dumps(now, default=str)) == s['before_units']
    assert qa.query("select count(*)from USER_OBJECTS where STATUS='INVALID'") == [(0,)]
    s['slow_sql'] = qa.query('select LOG_ID,ELAPSED_MS,API_PATH,SQL_TEXT from RRL_SQL_SLOW_LOG where LOG_ID>:m order by ELAPSED_MS desc fetch first 25 rows only', m=s['slow_marker'])
    s['status'] = 'PASS'; s.pop('error', None); qa.save()


if __name__ == '__main__':
    s['previous_calls'] = s.get('calls', [])
    try:
        if s.get('status') != 'PASS':
            prepare() if sys.argv[1] == 'prepare' else restore()
        else:
            print('Already PASS; no commands sent')
    except Exception as exc:
        s['error'] = str(exc); qa.save(); raise
    finally:
        qa.save()
    print(json.dumps(dict(status=s['status'], task=s.get('task'), wave=s.get('wave'))))
