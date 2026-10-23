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
    s.setdefault('expedition', 'ALE' + qa.TAG[-9:])
    s.setdefault('dock', 'ALD' + qa.TAG[-9:]); qa.save()
    if 'locations' not in s:
        with qa.oracle_connection() as conn:
            q = conn.cursor(); q.callproc('RRL_STOCK_CONFIG_API.begin_change', ['admin', 'warehouse_settings_edit'])
            try:
                q.execute('select WARE_ID from RRL_CELLS where CELL=:c', c=s['expedition']); old = q.fetchone()
                if old:
                    assert old == (qa.W,)
                else:
                    q.execute('insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT)values(:c,:w,10,10,0,0,1,0,0)', c=s['expedition'], w=qa.W)
                    q.execute("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:c),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD", c=s['expedition'])
                q.execute('select WARE_ID from RRL_TT_DOCK where DOCK=:d', d=s['dock']); old = q.fetchone()
                if old:
                    assert old == (qa.W,)
                else:
                    q.execute('insert into RRL_TT_DOCK(DOCK,WARE_ID,ORD,COUNT_OF_PALLETS,DOCK_IS_BLOCKED)values(:d,:w,1,10,0)', d=s['dock'], w=qa.W)
                conn.commit()
            finally:
                q.callproc('RRL_STOCK_CONFIG_API.end_change')
        s['locations'] = True; qa.save()
    qa.step('expedition_policy', qa.BASE + '/stock/cells/' + s['expedition'], dict(operation_id=qa.TAG + '.expedition',
        expected_version=0, zone_kind='EXPEDITION', reason='Own isolated partial-loading proof'), method='PUT')
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
            scanned_to_cell=s['expedition'], expected_content_version=version))
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


def load_one():
    vehicle = 10125
    if 'vehicle_before' not in s:
        s['vehicle_before'] = qa.expect(200, qa.http('GET', f'/api/admin/transport/vehicles/{vehicle}/profile'))
        s['weight_before'] = qa.expect(200, qa.http('GET', f'/api/sku-quality-weight/{qa.W}/{qa.ARTICLE}')); qa.save()
    before = s['vehicle_before']; p = before['profile']
    qa.step('vehicle_profile', '/api/admin/transport/vehicle-profiles', dict(operation_id=qa.TAG + '.vehicle', vehicle_id=vehicle,
        expected_source_hash=before['base_hash'], expected_version=before['version'], vehicle_size_class=p['vehicle_size_class'],
        cargo_length_mm=p['cargo_length_mm'], cargo_width_mm=p['cargo_width_mm'], cargo_height_mm=p['cargo_height_mm'],
        outer_height_mm=p['outer_height_mm'], outer_length_mm=p['outer_length_mm'],
        floor_variants=p['floor_capacity']['variants'] + [dict(code='QA_AFTER_LOAD_BOXES', limits=[dict(pallet_type_id=33, max_places=2)])],
        reason='Synthetic two-carton partial-load proof', evidence_reference='TEST_NOT_HARDWARE:' + qa.TAG))
    qa.step('weight_policy', f'/api/sku-quality-weight/{qa.W}/{qa.ARTICLE}', dict(expected_version=s['weight_before']['version'],
        base_uom='EA', base_weight_kg='1', box_weight_kg='10'), method='PUT')
    for i in range(2):
        own = configure_case(i); carrier = own['label']['sscc']; path = '/api/outgoing-quality/' + carrier
        if 'scan_qc' not in own:
            current = qa.expect(200, qa.http('GET', path))
            case.step('scan_qc', path + '/scan', dict(operation_id=case.tag + '.scanqc', expected_composition_signature=current['composition_signature'],
                error_count=0, scans=own['pick_body']['unit_scans']))
        if 'weight_qc' not in own:
            current = qa.expect(200, qa.http('GET', path))
            case.step('weight_qc', path + '/weight', dict(operation_id=case.tag + '.weightqc', expected_composition_signature=current['composition_signature'],
                quality_kind='WEIGHT', gross_weight='20.1', wood_weight='0.1', measurement_origin='MANUAL_CONFIRMED'))
        assert qa.expect(200, qa.http('GET', path))['ready']
    if 'next_departure' not in s:
        s['next_departure'] = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(); qa.save()
    qa.send('trip_v3', 'TRIP', qa.TAG, dict(s['requests']['trip_v2']['body']['payload'], planned_departure_at=s['next_departure']), 3)
    task = qa.step('native_trip', '/api/admin/transport/tasks', dict(transtype='10', shipment_date=s['next_departure'][:10]))['task_id']
    s['native_task'] = task; qa.save()
    qa.step('native_configured', f'/api/admin/transport/tasks/{task}', dict(transport='TP22.089ddb36', dock=s['dock'],
        shipment_time=s['next_departure'][11:16], primechanie='Owned synthetic after-load proof; no real dispatch'), method='PATCH')
    qa.step('native_assigned', f'/api/admin/transport/tasks/{task}/sts', dict(st_numbers=['AL' + qa.TAG[-9:] + str(i) for i in range(2)]))
    qa.step('trade_bound', qa.TRIP + '/binding', dict(operation_id=qa.TAG + '.trip.bind', native_task_id=task,
        expected_trip_version=3, expected_binding_version=0))
    own = configure_case(0); carrier = own['label']['sscc']
    if 'loaded' not in s['requests']:
        preview = qa.expect(200, qa.http('GET', '/api/transport/loading/bulk-box-preview?identifier=' + carrier))
        assert preview['source_kind'] == 'SINGLE', preview
        s['load_preview'] = preview; qa.save()
        version = preview['snapshot']['nodes'][0]['version']
        body = dict(operation_id=qa.TAG + '.load', source_kind='SINGLE', identifier=preview['identifier'], expected_version=version,
            expected_composition_signature=preview['composition_signature'], scan_container=carrier, scan_cell=preview['snapshot']['cell'],
            transport_task_id=task, scan_vehicle='TP22.089ddb36', scan_dock=s['dock'], measurements=dict(origin='MANUAL_CONFIRMED',
                content_version=version, gross_weight_kg='20.1', width_m='0.4', depth_m='0.5', height_m='0.5'))
    else:
        body = s['requests']['loaded']['body']
    loaded = qa.step('loaded', '/api/transport/loading/confirm-bulk-box', body)
    assert qa.expect(200, qa.http('POST', '/api/transport/loading/confirm-bulk-box', body)) == loaded
    assert qa.query("select STATUS from RRL_TT_HU_LOAD_FACT where TT_ID=:t order by LOAD_OPERATION_ID", t=task) == [('LOADED',)]
    s['status'] = 'PARTIALLY_LOADED'; qa.save()


def prove_topup():
    if 'load_need_time' not in s:
        s['load_need_time'] = datetime.now(timezone.utc).isoformat(); qa.save()
    now = datetime.fromisoformat(s['load_need_time'])
    qa.send('load_need', 'NEED', qa.TAG + '.LOAD_NEED', dict(recipient_id='C1', sku_id='A', recipient_version=2, sku_version=1,
        snapshot_at=s['load_need_time'], period_from=s['load_need_time'], period_until=(now + timedelta(days=2)).isoformat(),
        uom='BOX', forecast_quantity='8', target_quantity='0', available_quantity='0', received_in_available=True,
        supplies=[dict(supply_id=qa.TAG + '.MAIN_SUPPLY', version=1, quantity='4', uom='BOX', status='PLANNED',
            confirmed=True, current_trip=True, expected_at=s['next_departure'])]))
    preview = qa.step('topup_preview', qa.TRIP + '/topup-preview', dict(need_ids=[qa.TAG + '.LOAD_NEED'], max_age_minutes=1440), qa=True)
    saved = qa.step('topup_saved', qa.TRIP + '/topup-proposals', dict(operation_id=qa.TAG + '.topup.save',
        need_ids=[qa.TAG + '.LOAD_NEED'], max_age_minutes=1440), qa=True)
    proposal = saved['proposals'][0]
    assert proposal['approved_boxes'] == 2, saved
    assert proposal['calculation']['limited_by'] == 'CAPACITY'
    s['proposal'] = proposal['proposal_id']; qa.save()
    confirmed = qa.step('topup_confirmed', qa.TRIP + f"/topup-proposals/{s['proposal']}/confirm",
        dict(operation_id=qa.TAG + '.topup.confirm', expected_version=proposal['version']), qa=True)
    request = s['requests']['topup_confirmed']
    assert qa.expect(200, qa.http('POST', request['path'], request['body'], s['actor'], s['password'])) == confirmed
    s['stock_after_confirm'] = qa.stock()
    assert s['stock_after_confirm'] == [(230, 40)], s['stock_after_confirm']
    s['checks'].append('Actual one of two cartons loaded: main40 counted once; capacity admits2 of4BOX, HARD20 confirmed/replayed without new hold')
    qa.step('topup_released', qa.TRIP + f"/topup-proposals/{s['proposal']}/release",
        dict(operation_id=qa.TAG + '.topup.release', expected_version=confirmed['version']), qa=True)
    saved2 = qa.step('before_unload_saved', qa.TRIP + '/topup-proposals', dict(operation_id=qa.TAG + '.before.unload',
        need_ids=[qa.TAG + '.LOAD_NEED'], max_age_minutes=1440), qa=True)
    proposal2 = saved2['proposals'][0]; s['proposal2'] = proposal2; qa.save()
    body = s['requests']['loaded']['body']
    qa.step('unloaded', '/api/transport/loading/unload', dict(operation_id=qa.TAG + '.unload', load_operation_id=body['operation_id'],
        expected_version=body['expected_version'], scan_container=body['scan_container'], scan_cell=body['scan_cell'],
        scan_vehicle=body['scan_vehicle'], scan_dock=body['scan_dock'], reason='Actual removal invalidates prior top-up basis'))
    rejected = qa.step('stale_confirm', qa.TRIP + f"/topup-proposals/{proposal2['proposal_id']}/confirm",
        dict(operation_id=qa.TAG + '.stale.confirm', expected_version=proposal2['version']), qa=True, status=409)
    assert 'STALE' in str(rejected) or 'CHANGED' in str(rejected), rejected
    qa.step('stale_rejected', qa.TRIP + f"/topup-proposals/{proposal2['proposal_id']}/decision",
        dict(operation_id=qa.TAG + '.reject.stale', expected_version=proposal2['version'], action='REJECT'), qa=True)
    assert qa.stock() == [(250, 40)]
    s['checks'].append('Actual UNLOAD makes saved calculation stale; stale confirm produces no new reserve; own proposals released/rejected')
    s['status'] = 'AFTER_LOAD_PASS_CLEANUP_REQUIRED'; qa.save()


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


def cleanup_full():
    assert qa.query("select count(*)from RRL_TT_HU_LOAD_FACT where TT_ID=:t and STATUS in('LOADED','DEPARTED')", t=s['native_task']) == [(0,)]
    qa.step('native_cancelled', f"/api/admin/transport/tasks/{s['native_task']}/cancel")
    for i in range(2):
        own = configure_case(i); key = 'case' + str(i)
        sscc, version = qa.query('select SSCC,CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t', t=own['case'])[0]
        destinations = dict(qa.query('select lot.LOT_UID,l.CELL_CODE from RRL_CASE_CARRIER_LOT lot join RRL_CASE_PICK_LINE l on l.CASE_PICK_LINE_ID=lot.CASE_PICK_LINE_ID where lot.CASE_PICK_TASK_ID=:t', t=own['case']))
        qa.step(key + '_returned', f"/api/case-pick/tasks/{own['case']}/return-carrier", dict(operation_id=qa.TAG + '.' + key + '.return',
            scan_container=sscc, expected_content_version=version, destinations=destinations))
        qa.step(key + '_logout', f"/api/resources/sessions/{own['session']['id']}/logout", dict(reason='End owned partial-load proof'))
        qa.step(key + '_owner_retired', qa.BASE + '/stock/owner-grants', dict(operation_id=qa.TAG + '.' + key + '.owner.retire',
            expected_version=1, username=own['actor'], owner_id='SNS', can_view=False, can_operate=False, reason='End owned partial-load proof'), method='PUT')
        qa.step(key + '_qualification_off', f"/api/resources/{own['resource']['id']}/qualifications", dict(task_type='CASE_PICK', active=False), method='PUT')
        qa.step(key + '_book_cancelled', '/api/inventory/tare/book-cancel', dict(operation_id=qa.TAG + '.' + key + '.book.cancel',
            booking_operation_id=own['tare_book']['operation_id']))
        qa.step(key + '_finished', f"/api/picking/waves/{own['wave']}/finish-execution", dict(operation_id=qa.TAG + '.' + key + '.finish',
            disposition='RETURNED_TO_PLANNING', reason='Actual picked goods returned; no departure'))
        with qa.oracle_connection() as conn:
            q = conn.cursor(); q.execute("update RUSERS set DELETED=1 where ID=:a and USER_GROUP='TC03QA'", a=own['actor'])
            q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:a and REVOKED_AT is null', a=own['actor']); conn.commit()
    assert qa.stock() == [(250, 0)]
    grain = qa.query('select r.UID_POLETA,r.CELL,r.REMAIN from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w and r.REMAIN>0 order by r.UID_POLETA,r.CELL', w=qa.W)
    if 'restore_targets' not in s:
        returned = [uid for uid, _, _ in grain if uid != '690000000445629982']
        assert len(returned) == 2 and len(grain) == 3
        s['restore_targets'] = dict(zip(returned, ['ALS' + qa.TAG[-9:] + str(i) for i in range(2)]))
        s['restore_targets']['690000000445629982'] = 'T3S089ddb36'; qa.save()
    for target in s['restore_targets'].values():
        if target == 'T3S089ddb36':
            continue
        with qa.oracle_connection() as conn:
            q = conn.cursor(); q.callproc('RRL_STOCK_CONFIG_API.begin_change', ['admin', 'warehouse_settings_edit'])
            try:
                q.execute('select WARE_ID from RRL_CELLS where CELL=:c', c=target); old = q.fetchone()
                if old:
                    assert old == (qa.W,)
                else:
                    q.execute('insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT)values(:c,:w,11,11,0,0,0,0,0)', c=target, w=qa.W)
                    q.execute("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:c),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD", c=target)
                conn.commit()
            finally:
                q.callproc('RRL_STOCK_CONFIG_API.end_change')
        qa.step('storage_policy_' + target, qa.BASE + '/stock/cells/' + target, dict(operation_id=qa.TAG + '.' + target,
            expected_version=0, zone_kind='STORAGE', reason='Store returned own CASE lots without merging identities'), method='PUT')
    for uid, cell, qty in grain:
        target = s['restore_targets'][uid]
        if cell == target:
            continue
        chosen = {}
        for key, system, raw, profiles in qa.query("select u.PHYSICAL_UNIT_KEY,c.SYSTEM_CODE,c.RAW_CODE,c.PROFILES_JSON from RRL_WMS_RECEIPT_UNIT u join RRL_WMS_RECEIPT_CODE c on c.UID_PALLET=u.UID_PALLET and c.UNIT_ID=u.UNIT_ID where u.CURRENT_UID=:u and u.CURRENT_CELL=:c and u.STOCK_STATUS='AVAILABLE'order by u.PHYSICAL_UNIT_KEY,c.SYSTEM_CODE", u=uid, c=cell):
            profiles = json.loads(profiles) if isinstance(profiles, str) else profiles
            chosen.setdefault(key, dict(system_code=system, profile_code=profiles[0]['profile'], code=raw))
        assert len(chosen) == qty, (uid, qty, len(chosen))
        qa.step('restore_storage_' + uid, qa.BASE + '/stock/sort', dict(operation_id=qa.TAG + '.storage.' + str(len(s['requests'])),
            source_pallet=uid, source_cell=cell, target_cell=target, scans=list(chosen.values())))
    qa.send('trip_cancelled', 'TRIP', qa.TAG, dict(s['requests']['trip_v3']['body']['payload'], cancelled=True), 4)
    for key, suffix in [('primary_doc', '.MAIN'), ('second_doc', '.SECOND')]:
        qa.send('cancel_after_trip_' + key, 'ORDER', qa.TAG + suffix, dict(s['requests'][key]['body']['payload'], cancelled=True), 2)
    qa.step('pool_cleaned', qa.POOL + '/allocate', dict(operation_id=qa.TAG + '.pool.cleaned'))
    policy = qa.expect(200, qa.http('GET', qa.POLICY)); before = s['policy_before']
    qa.step('policy_restored', qa.POLICY, dict(expected_version=policy['policy_version'], stock_class=before['stock_class'],
        ship_from_stock=before['ship_from_stock'], pick_step=before['pick_step']), method='PUT')
    qa.step('settings_restored', f'/api/receiving/warehouses/{qa.W}/settings', s['settings_before'], method='PUT')
    balances = qa.expect(200, qa.http('GET', f'/api/inventory/tare/warehouses/{qa.W}/balances'))
    balance = next(b for b in balances if b['pallet_type_id'] == 33 and b['custodian_kind'] == 'WAREHOUSE' and b['condition_code'] == 'GOOD')
    qa.step('tare_restored', '/api/inventory/tare/count', dict(operation_id=qa.TAG + '.tare.restore', owner_ware_id=qa.W,
        pallet_type_id=33, condition='GOOD', observed_quantity=str(s['tare_before']['quantity']), expected_version=balance['balance_version'],
        reason='Restore prior unbooked synthetic carton balance', decision_reference='TEST_RESTORE:' + qa.TAG))
    current = qa.expect(200, qa.http('GET', f'/api/sku-quality-weight/{qa.W}/{qa.ARTICLE}')); before = s['weight_before']
    qa.step('weight_restored', f'/api/sku-quality-weight/{qa.W}/{qa.ARTICLE}', dict(expected_version=current['version'],
        base_uom=before['base_uom'] or 'EA', base_weight_kg=before['base_weight_kg'], box_weight_kg=before['box_weight_kg']), method='PUT')
    current = qa.expect(200, qa.http('GET', '/api/admin/transport/vehicles/10125/profile')); p = s['vehicle_before']['profile']
    qa.step('vehicle_restored', '/api/admin/transport/vehicle-profiles', dict(operation_id=qa.TAG + '.vehicle.restore', vehicle_id=10125,
        expected_source_hash=current['base_hash'], expected_version=current['version'], vehicle_size_class=p['vehicle_size_class'],
        cargo_length_mm=p['cargo_length_mm'], cargo_width_mm=p['cargo_width_mm'], cargo_height_mm=p['cargo_height_mm'],
        outer_height_mm=p['outer_height_mm'], outer_length_mm=p['outer_length_mm'], floor_variants=p['floor_capacity']['variants'],
        reason='Restore prior synthetic vehicle profile after unloading', evidence_reference='TEST_RESTORE:' + qa.TAG))
    qa.step('owner_retired', qa.BASE + '/stock/owner-grants', dict(operation_id=qa.TAG + '.owner.retire', expected_version=1,
        username=s['actor'], owner_id='SNS', can_view=False, can_operate=False, reason='End own top-up proof'), method='PUT')
    with qa.oracle_connection() as conn:
        q = conn.cursor(); q.execute("update RUSERS set DELETED=1 where ID=:a and USER_GROUP='QA_ONLY'", a=s['actor'])
        q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:a and REVOKED_AT is null', a=s['actor']); conn.commit()
    assert qa.stock() == [(250, 0)]
    assert qa.query("select count(*)from USER_OBJECTS where STATUS='INVALID'") == [(0,)]
    original = json.loads((qa.ROOT / 'runtime/test-evidence/tradecase/2026-10-23/T11/paper-wave-state.json').read_text(encoding='utf-8'))['before_units']
    current = qa.query('select a.PHYSICAL_UNIT_KEY,u.CURRENT_UID,u.CURRENT_CELL,u.STOCK_STATUS,u.HARD_RESERVATION_ID,a.OWNER_ID,a.MRC,a.EXPIRY_DATE,a.MARK_STATE from RRL_TRADE_STOCK_ATTR a join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=a.PHYSICAL_UNIT_KEY where a.CAPTURE_WARE_ID=:w order by a.PHYSICAL_UNIT_KEY', w=qa.W)
    assert len(current) == 250 and all(r[2] in s['restore_targets'].values() and r[3] == 'AVAILABLE' and r[4] is None for r in current)
    attributes = lambda rows: [[r[i] for i in (0, 5, 6, 7, 8)] for r in rows]
    assert json.loads(json.dumps(attributes(current), default=str)) == attributes(original)
    s['restored_stock_grain'] = qa.query('select r.UID_POLETA,r.CELL,r.REMAIN,r.HARD_RESERVED_BASE from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w and r.REMAIN>0 order by r.UID_POLETA,r.CELL', w=qa.W)
    s['slow_sql'] = qa.query('select LOG_ID,ELAPSED_MS,API_PATH,SQL_TEXT from RRL_SQL_SLOW_LOG where LOG_ID>:n order by ELAPSED_MS desc fetch first 30 rows only', n=s['slow_marker'])
    s['status'] = 'PASS'; s.pop('error', None); qa.save()


if __name__ == '__main__':
    s['previous_calls'] = s.get('calls', [])
    try:
        if s.get('status', '').endswith('CLOSED') or s.get('status') == 'PASS':
            print('Closed; no commands sent')
        elif sys.argv[-1] == 'pick':
            pick_cases()
        elif sys.argv[-1] == 'load':
            load_one()
        elif sys.argv[-1] == 'prove':
            prove_topup()
        elif sys.argv[-1] == 'cleanup':
            cleanup_full()
        elif sys.argv[-1] == 'cleanup-empty':
            cleanup_empty()
        else:
            prepare()
    except Exception as exc:
        s['error'] = str(exc); qa.save(); raise
    finally:
        qa.save()
    print(json.dumps(dict(status=s.get('status'), cases=[s.get('case0'), s.get('case1')]), default=str))
