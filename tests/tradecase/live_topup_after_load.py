"""Resumable partial-loading proof on retained marked stock; no goods receipts."""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sys
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parent))
import live_topup_common_pool as qa
import live_factory_case as case
from full_pallet_fixture import prepare_shipment

qa.FILE = qa.OUT / 'after-load-live.json'
qa.s = json.loads(qa.FILE.read_text(encoding='utf-8')) if qa.FILE.exists() else dict(
    tag='AL23.' + uuid4().hex[:9], warehouse_id=qa.W, requests={}, results={}, checks=[])
qa.TAG = qa.s['tag']; qa.TRIP = qa.BASE + '/trips/' + qa.TAG
s = qa.s


def configure_case(i):
    key = 'case' + str(i)
    case.OUT = qa.OUT
    case.FILE = qa.OUT / ('after-load-case-' + str(i) + '.json')
    case.w = qa.W; case.base = qa.BASE; case.tag = qa.TAG + '.' + key
    case.s = json.loads(case.FILE.read_text(encoding='utf-8')) if case.FILE.exists() else dict(
        s[key], warehouse_id=qa.W, article=qa.ARTICLE, pick='T3P089ddb36', quantity=20,
        pallet_type_id=33, history=[], tare_count=s['results']['tare_count'])
    if qa.query('select count(*)from RRL_TRADE_CELL_POLICY where CELL=:c', c='CPT_' + str(qa.W)) == [(1,)]:
        case.s.setdefault('cpt_policy', {'read_existing': True})
    case.save()
    return case.s


def pick_cases():
    if 'settings_before' not in s:
        settings = qa.expect(200, qa.http('GET', f'/api/receiving/warehouses/{qa.W}/settings'))
        fields = ['company_prefix', 'extension_digit', 'coordinate_unit_m', 'reachtruck_mps', 'lift_mps',
                  'placement_metric', 'hu_cell_height_unit', 'outgoing_qc_mode', 'outgoing_qc_independent',
                  'outgoing_qc_sample_percent', 'defer_wait_cell']
        s['settings_before'] = {k: settings[k] for k in fields if k in settings}
        balances = qa.expect(200, qa.http('GET', f'/api/inventory/tare/warehouses/{qa.W}/balances'))
        before = next((b for b in balances if b['pallet_type_id'] == 33 and b['custodian_kind'] == 'WAREHOUSE' and b['condition_code'] == 'GOOD'), None)
        s['tare_before'] = before or {'quantity': '0', 'balance_version': 0}; qa.save()
    qa.step('settings', f'/api/receiving/warehouses/{qa.W}/settings', dict(s['settings_before'], company_prefix='09999999', extension_digit=0), method='PUT')
    before = s['tare_before']
    qa.step('tare_count', '/api/inventory/tare/count', dict(operation_id=qa.TAG + '.tare.count', owner_ware_id=qa.W,
        pallet_type_id=33, condition='GOOD', observed_quantity=str(int(before['quantity']) + 2), expected_version=before['balance_version'],
        reason='Two synthetic cartons for partial-load proof', decision_reference='TEST_NOT_HARDWARE:' + qa.TAG))
    for i in range(2):
        own = configure_case(i); path = f"/api/case-pick/tasks/{own['case']}"
        if 'type' not in own:
            current = qa.expect(200, qa.http('GET', path + '/pallet-type'))
            case.step('type', path + '/pallet-type', dict(operation_id=case.tag + '.type', pallet_type_id=33,
                expected_version=current['version'], scan_container=current['sscc'], reason='Own manual-weighed carton'))
        actor, password, _, _, _ = case.start()
        if 'label' not in own:
            carrier, version = qa.query('select SSCC,CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t', t=own['case'])[0]
            case.step('label', path + '/sscc-label', dict(operation_id=case.tag + '.label', scan_container=carrier,
                expected_content_version=version), actor=actor, password=password)
        label = own['label']
        case.step('label_confirmed', path + '/sscc-label/confirm', dict(scan=label['sscc']), actor=actor, password=password)
        case.step('empty_tare', f"/api/inventory/warehouse-scales/tasks/{own['case']}/manual-empty-tare",
            dict(operation_id=case.tag + '.tare', expected_content_version=label['content_version'], scan_container=label['sscc'],
                 tare_weight_kg='0.1', measurement_ref='SYNTHETIC_NOT_HARDWARE:' + case.tag), actor=actor, password=password)
        case.execute(return_after=False)
        if 'shipment' not in own:
            own['shipment'] = prepare_shipment(dict(fixture=dict(warehouse_id=qa.W, article=qa.ARTICLE, tag='089ddb36'),
                native_order=own['native']['order'], shipment_identifier=case.tag + '.ST', shipment_quantity=20, st_number='AL' + qa.TAG[-9:] + str(i)))
            case.save()
        version = qa.query('select CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t', t=own['case'])[0][0]
        case.step('moved', path + '/move-carrier', dict(operation_id=case.tag + '.move', scan_container=label['sscc'],
            scanned_to_cell='T3E089ddb36', expected_content_version=version))
        version = qa.query('select CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t', t=own['case'])[0][0]
        case.step('bound', path + '/bind-shipment', dict(pallet_identifier=own['shipment']['shipment_identifier'],
            scan_container=label['sscc'], expected_content_version=version))
    assert qa.stock() == [(250, 40)]
    s['status'] = 'CASES_PICKED_BOUND'; qa.save()


def prepare():
    qa.setup()
    qa.send('second_doc', 'ORDER', qa.TAG + '.SECOND', dict(order_kind='OUTBOUND', recipient_id='C1', planned_ship_at=s['departure'],
        lines=[dict(line_id='1', sku_id='A', source_owner_id='SNS', target_owner_id='SNS', mrc='200', quantity='20', uom='EA', min_osg_days=0)]))
    second = qa.native_order('second_native', qa.TAG + '.SECOND', 20)
    qa.send('trip_v2', 'TRIP', qa.TAG, dict(s['trip_body'], orders=s['trip_body']['orders'] + [dict(order_id=qa.TAG + '.SECOND', line_id='1', quantity='20')]), 2)
    qa.step('pool', qa.POOL + '/allocate', dict(operation_id=qa.TAG + '.pool'))
    for i, native in enumerate((s['primary_native'], second)):
        key = 'case' + str(i)
        plan = qa.step(key + '_plan', '/api/picking/plans', dict(operation_id=qa.TAG + '.' + key + '.plan', customer_order_id=native['order']))['pick_plan_id']
        wave = qa.step(key + '_wave', '/api/picking/waves', dict(wave_code=qa.TAG + '.' + key, wave_name='Owned after-load proof', ware_id=qa.W,
            planned_start_at=datetime.now(timezone.utc).isoformat(), planned_finish_at=s['departure']))['pick_wave_id']
        path = f'/api/picking/waves/{wave}'
        qa.step(key + '_added', path + '/plans', dict(pick_plan_id=plan))
        qa.step(key + '_calculated', path + '/calculate', {})
        qa.step(key + '_launched', path + '/launch', dict(operation_id=qa.TAG + '.' + key + '.launch'))
        for tid, uid, src, dst, quantity in qa.query("select TASK_ID,UID_PALLET,FROM_CELL,TO_CELL,QTY from RRL_WAREHOUSE_TASK where SOURCE_DOC_TYPE='PICK_WAVE'and SOURCE_DOC_ID=:w and TASK_TYPE='REPLENISHMENT'and STATUS<>'CANCELLED'", w=wave):
            qa.step(key + '_repl_' + str(tid), f'/api/warehouse-tasks/{tid}/complete', dict(operation_id=qa.TAG + '.repl.' + str(tid),
                scanned_pallet=uid, scanned_from_cell=src, scanned_to_cell=dst, fact_qty=str(quantity)))
        qa.step(key + '_released', path + '/release-picking', dict(operation_id=qa.TAG + '.' + key + '.release'))
        rows = qa.query('select CASE_PICK_TASK_ID,CASE_PICK_LINE_ID,PICK_TASK_ID from RRL_CASE_PICK_LINE where PICK_WAVE_ID=:w', w=wave)
        assert len(rows) == 1, rows
        s[key] = dict(plan=plan, wave=wave, native=native, case=rows[0][0], line=rows[0][1], pick_task=rows[0][2])
        qa.save()
    assert qa.stock() == [(250, 40)]
    s['status'] = 'WAVES_READY'; qa.save()


def cleanup_empty():
    """Only before picking/loading. Refuse to erase evidence or cancel a populated carrier."""
    for i in range(2):
        key = 'case' + str(i)
        if key not in s:
            continue
        own = s[key]
        assert qa.query('select count(*)from RRL_CASE_CARRIER_LOT where CASE_PICK_TASK_ID=:t', t=own['case']) == [(0,)]
        qa.step(key + '_cancel', f"/api/picking/waves/{own['wave']}/cancel", dict(operation_id=qa.TAG + '.' + key + '.cancel', reason='Cancel own empty after-load preparation'))
        sscc, version, status = qa.query('select SSCC,CONTENT_VERSION,STATUS from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t', t=own['case'])[0]
        if status != 'CANCELLED':
            qa.step(key + '_empty', f"/api/case-pick/tasks/{own['case']}/return-carrier", dict(operation_id=qa.TAG + '.' + key + '.empty',
                scan_container=sscc, expected_content_version=version, destinations={}, allow_empty=True, reason='Cancel own empty carrier'))
    for key, suffix in [('primary_doc', '.MAIN'), ('second_doc', '.SECOND')]:
        if key in s['results']:
            qa.send('cancel_' + key, 'ORDER', qa.TAG + suffix, dict(s['requests'][key]['body']['payload'], cancelled=True), 2)
    if 'trip_v2' in s['results']:
        qa.send('trip_cancelled', 'TRIP', qa.TAG, dict(s['requests']['trip_v2']['body']['payload'], cancelled=True), 3)
    qa.step('pool_cleaned', qa.POOL + '/allocate', dict(operation_id=qa.TAG + '.pool.cleaned'))
    policy = qa.expect(200, qa.http('GET', qa.POLICY)); before = s['policy_before']
    qa.step('policy_restored', qa.POLICY, dict(expected_version=policy['policy_version'], stock_class=before['stock_class'],
        ship_from_stock=before['ship_from_stock'], pick_step=before['pick_step']), method='PUT')
    assert qa.stock() == [(250, 0)]
    s['status'] = 'EMPTY_PREPARATION_CLOSED'; qa.save()


if __name__ == '__main__':
    s['previous_calls'] = s.get('calls', [])
    try:
        if s.get('status', '').endswith('CLOSED') or s.get('status') == 'PASS':
            print('Closed; no commands sent')
        elif sys.argv[-1] == 'pick':
            pick_cases()
        elif sys.argv[-1] == 'cleanup-empty':
            cleanup_empty()
        else:
            prepare()
    except Exception as exc:
        s['error'] = str(exc); qa.save(); raise
    finally:
        qa.save()
    print(json.dumps(dict(status=s.get('status'), cases=[s.get('case0'), s.get('case1')]), default=str))
