"""Owned full-pallet stock through a nested HU, using existing preparation and writers."""
import json
import os
import subprocess
import sys
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4
import live_topup_common_pool as qa
import live_scoped_full_pallet as scoped
import live_stock_acceptance as receiving

OUT = qa.ROOT / 'runtime/test-evidence/tradecase/2026-10-23/T06/nested-shipping'
FILE = OUT / 'nested-shipping.json'
s = json.loads(FILE.read_text(encoding='utf-8')) if FILE.exists() else dict(tag='NS23.' + uuid4().hex[:9], requests={}, results={})
qa.FILE = FILE
qa.OUT = OUT
qa.s = s


def prepare():
    scoped.OUT = OUT
    scoped.FILE = OUT / 'scoped-full-pallet.json'
    scoped.s = json.loads(scoped.FILE.read_text(encoding='utf-8')) if scoped.FILE.exists() else dict(history=[])
    scoped.prep.OUT = OUT
    if 'session_id' not in scoped.s:
        # Check the generated legacy warehouse identity before the reused setup can write it.
        while True:
            identity = uuid4()
            warehouse = 210000000 + int(identity.hex[:6], 16)
            if warehouse != 225837931 and qa.query('select count(*)from RRL_WARES where ID=:w', w=warehouse) == [(0,)]:
                break
        with patch.object(receiving, 'uuid4', return_value=identity):
            scoped.initialize()
    else:
        scoped.prep.FILE = OUT / 'scoped-full-preparation.json'
        scoped.prep.s = json.loads(scoped.prep.FILE.read_text(encoding='utf-8'))
    s['warehouse'] = scoped.s['warehouse_id']
    s['fixture'] = scoped.prep.s['fixture']
    qa.save()
    if 'bound' not in scoped.s:
        scoped.move()
    if not s.get('actor_closed'):
        scoped.cleanup()
        s['actor_closed'] = True
        qa.save()


def snapshot(identifier):
    return qa.expect(200, qa.http('GET', '/api/warehouse-hus/composition?identifier=' + identifier))


def pack():
    stock = s['fixture']['pallet']
    current = snapshot(stock)
    assert current['physical_unit_count'] == 10
    s['physical_stock_before_pack'] = current
    qa.save()
    containers = [s['tag'] + '.' + kind for kind in ['PALLET', 'BOX']]
    for uid, kind in zip(containers, ['PALLET', 'BOX']):
        qa.step('create_' + kind, '/api/warehouse-hus/create', dict(operation_id=uid + '.create', identifier=uid,
            cell=current['cell'], warehouse=s['warehouse'], container_type=kind, tare_weight_kg='0.1', scan_container=uid, scan_cell=current['cell']))
    for key, parent, child in [('inner', containers[1], stock), ('outer', containers[0], containers[1])]:
        if key not in s['requests']:
            p, c = snapshot(parent), snapshot(child)
            s['requests'][key] = dict(path='/api/warehouse-hus/attach', method='POST', status=200, qa=False,
                body=dict(operation_id=s['tag'] + '.' + key, identifier=parent, child_uid=child,
                    expected_version=p['nodes'][0]['version'], expected_child_version=c['nodes'][0]['version'],
                    scan_container=parent, scan_child=child))
            qa.save()
        r = s['requests'][key]
        qa.step(key, r['path'], r['body'])
    root = snapshot(containers[0])
    assert root['physical_unit_count'] == 10 and len(root['nodes']) == 3
    s.update(root=containers[0], packed=root, status='PACKED_SHIPPING_PENDING')
    qa.save()


def prepare_transport():
    from decimal import Decimal
    import oracledb
    from app.oracle_gateway import OracleGateway
    from app.modules.fulfillment.infrastructure.store_source_scope import source_transaction
    from app.modules.fulfillment.infrastructure.legacy_preparation import LegacyPreparation

    f = s['fixture']
    picked = json.loads((OUT / 'scoped-full-pallet.json').read_text(encoding='utf-8'))
    preparation = json.loads((OUT / 'scoped-full-preparation.json').read_text(encoding='utf-8'))
    w = s['warehouse']
    st = 'FP.' + str(w)
    if not s.get('legacy_logistics'):
        with qa.oracle_connection() as conn:
            cur = conn.cursor()
            cur.callproc('RRL_STOCK_CONFIG_API.begin_change', ['admin', 'warehouse_settings_edit'])
            try:
                cur.execute('select CELL,COUNT_SHT_IN_KOR,BRUTTO_WEIGHT_OF_KOR,DIMKOR_X,DIMKOR_Y,DIMKOR_Z from RRL_ARTICULS where ACTICUL=:a', a=f['article'])
                s['sku_logistics_before'] = cur.fetchone()
                qa.save()
                cur.execute('update RRL_ARTICULS set CELL=:c,COUNT_SHT_IN_KOR=10,BRUTTO_WEIGHT_OF_KOR=10,DIMKOR_X=0.4,DIMKOR_Y=0.3,DIMKOR_Z=0.2 where ACTICUL=:a', c=f['pick'], a=f['article'])
                assert cur.rowcount == 1
                conn.commit()
            finally:
                cur.callproc('RRL_STOCK_CONFIG_API.end_change')
        s['legacy_logistics'] = 'Synthetic owned SKU declaration, not industrial dimensions'
        qa.save()
    if not s.get('legacy_order'):
        gateway = OracleGateway()
        with source_transaction(gateway, 'Owned nested shipping demand metadata', 'admin', 'customer_order_import', warehouse=w) as cur:
            cur.execute('select ID from RRL_ORDERS where ORD_NUMBER=:n and WARE_ID=:w', n=st, w=w)
            existing = cur.fetchall()
            assert len(existing) <= 1
            if existing:
                legacy = existing[0][0]
            else:
                day = datetime.now() + timedelta(days=1)
                legacy = cur.callfunc('ORDERS.CREATE_ORDER', oracledb.DB_TYPE_NUMBER, [st, day, w, 'Owned nested shipping fixture', '1', day, 'admin'])
                LegacyPreparation(gateway)._legacy_rows(cur, legacy, w, {f['article']: (Decimal(10), 'EA')})
            cur.execute('update RRL_SBORKA_PALLETS set ORIGINAL_ORDER_NUMBER=:n,ORIGINAL_ST_NUMBER=:n where ID=:p', n=st, p=picked['shipment_id'])
        s['legacy_order'] = int(legacy)
        qa.save()
    path = OUT / 'transport.json'
    if not path.exists():
        data = dict(warehouse_id=w, case_id=picked['shipment_id'], order_id=preparation['native_order'],
            article=f['article'], st_number=st, st_pallet=picked['shipment_identifier'], carrier=f['pallet'],
            quantity=10, expected_remaining=0, expected_hard=0, shipment_date=(datetime.now() + timedelta(days=1)).date().isoformat(),
            demand_order_id='FP21.' + str(w) + '.ORDER', planned_departure_at=(datetime.now() + timedelta(days=1)).astimezone().isoformat(),
            vehicle_number='NS23V' + str(w), dock='NS23D' + str(w), http=[])
        path.write_text(json.dumps(data, indent=2), encoding='utf-8')
    env = dict(os.environ, TRADECASE_TRANSPORT_FIXTURE=str(path))
    process = subprocess.run([sys.executable, 'tests/tradecase/prepare_transport_task.py'], cwd=qa.ROOT, env=env,
        capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=60)
    (OUT / 'prepare-transport-task.txt').write_text(process.stdout + process.stderr, encoding='utf-8')
    assert process.returncode == 0, process.stderr[-1600:]
    s['transport'] = json.loads(path.read_text(encoding='utf-8'))
    s['status'] = 'PACKED_TRANSPORT_PREPARED'
    qa.save()


def load():
    t = json.loads((OUT / 'transport.json').read_text(encoding='utf-8'))
    f = s['fixture']
    if 'profile' not in s['results']:
        p = qa.expect(200, qa.http('GET', f"/api/admin/transport/vehicles/{t['vehicle_id']}/profile"))
        qa.step('profile', '/api/admin/transport/vehicle-profiles', dict(operation_id=s['tag'] + '.profile', vehicle_id=t['vehicle_id'],
            expected_source_hash=p['base_hash'], expected_version=p['version'], vehicle_size_class='QA_VAN',
            cargo_length_mm=3000, cargo_width_mm=2400, cargo_height_mm=2400, outer_height_mm=3000, outer_length_mm=6000,
            floor_variants=[dict(code='QA_TWO_EURO', limits=[dict(pallet_type_id=1, max_places=2)])],
            reason='Owned nested shipment synthetic geometry', evidence_reference='SYNTHETIC_NOT_ROAD_VEHICLE'))
    if 'floor' not in s['results']:
        containers = [s['tag'] + '.' + kind for kind in ['PALLET', 'BOX']]
        for key, parent, child in [('outer_floor_detach', containers[0], containers[1]), ('inner_floor_detach', containers[1], f['pallet'])]:
            p, c = snapshot(parent), snapshot(child)
            qa.step(key, '/api/warehouse-hus/detach', dict(operation_id=s['tag'] + '.' + key, identifier=parent, child_uid=child,
                expected_version=p['nodes'][0]['version'], expected_child_version=c['nodes'][0]['version'],
                scan_container=parent, scan_child=child, reason='Declare owned physical floor type before repacking'))
        p = qa.expect(200, qa.http('GET', '/api/inventory/pallet-floor-types?identifier=' + f['pallet']))
        qa.step('floor', '/api/inventory/pallet-floor-types', dict(operation_id=s['tag'] + '.floor', identifier=f['pallet'],
            pallet_type_id=1, expected_version=p['version'], scan_pallet=f['pallet'], scan_cell=p['cell'], evidence_reference='OWN_QA_PALLET_TYPE_NOT_HARDWARE'))
    for key, parent, child in [('inner_floor_repack', s['tag'] + '.BOX', f['pallet']), ('outer_floor_repack', s['root'], s['tag'] + '.BOX')]:
        p, c = snapshot(parent), snapshot(child)
        qa.step(key, '/api/warehouse-hus/attach', dict(operation_id=s['tag'] + '.' + key, identifier=parent, child_uid=child,
            expected_version=p['nodes'][0]['version'], expected_child_version=c['nodes'][0]['version'], scan_container=parent, scan_child=child))
    if 'qc' not in s['results']:
        current = qa.expect(200, qa.http('GET', '/api/outgoing-quality/' + t['st_pallet']))
        prep = json.loads((OUT / 'scoped-full-preparation.json').read_text(encoding='utf-8'))
        qa.step('qc', '/api/outgoing-quality/' + t['st_pallet'] + '/scan', dict(operation_id=s['tag'] + '.qc',
            expected_composition_signature=current['composition_signature'], error_count=0, scans=prep['receipt_proof']['codes']))
    qa.step('tare_count', '/api/inventory/tare/count', dict(operation_id=s['tag'] + '.tare.count', owner_ware_id=s['warehouse'],
        pallet_type_id=1, condition='GOOD', observed_quantity='1', expected_version=0,
        reason='Synthetic owned pallet count for nested loading proof', decision_reference='TEST_NOT_PHYSICAL_TARE_SURVEY'))
    qa.step('tare_book', '/api/inventory/tare/book', dict(operation_id=s['tag'] + '.tare.book', place_kind='HU', place_id=s['root'],
        expected_warehouse_id=s['warehouse'], pallet_type_id=1))
    before = qa.step('composition_before_load', '/api/tradecase/order-compositions/report',
        dict(warehouse_id=s['warehouse'], order_id='FP21.' + str(s['warehouse']) + '.ORDER'))
    assert before['units'] == before['codes'] == 10
    key = 'load_with_tare'
    if key not in s['requests']:
        root = snapshot(s['root'])
        version = root['nodes'][0]['version']
        boxes = [dict(box_uid=n['uid'], scan_box=n['uid'], content_version=n['version'], origin='MANUAL_CONFIRMED',
            gross_weight_kg='10.1', measurement_ref='SYNTHETIC_TYPED_BOX_WEIGHT') for n in root['nodes'] if n['kind'] == 'CONTAINER' and n['type'] == 'BOX']
        s['requests'][key] = dict(path='/api/transport/loading/confirm', method='POST', qa=False, status=200,
            body=dict(operation_id=s['tag'] + '.load.tare_ready', identifier=s['root'], expected_version=version,
                scan_container=s['root'], scan_cell=root['cell'], transport_task_id=t['transport_task_id'],
                scan_vehicle=t['vehicle_number'], scan_dock=t['dock'], physical_boxes=boxes,
                measurements=dict(origin='MANUAL_CONFIRMED', content_version=version, gross_weight_kg='10.2', width_m='1.2', depth_m='0.8', height_m='1.5')))
        qa.save()
    req = s['requests'][key]
    qa.step(key, req['path'], req['body'])
    assert qa.expect(200, qa.http('POST', req['path'], req['body'])) == s['results'][key]
    assert qa.query('select nvl(sum(r.REMAIN),0),nvl(sum(r.HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w', w=s['warehouse']) == [(0, 0)]
    after = qa.step('composition_after_load', '/api/tradecase/order-compositions/report',
        dict(warehouse_id=s['warehouse'], order_id='FP21.' + str(s['warehouse']) + '.ORDER'))
    assert after['composition_no'] == before['composition_no'] and after['signature'] == before['signature']
    s['status'] = 'LOADED_DEPARTURE_PENDING'
    s.pop('error', None)
    qa.save()


def tare_handover():
    t = json.loads((OUT / 'transport.json').read_text(encoding='utf-8'))
    if 'actor' not in s:
        s.update(actor='ND23' + uuid4().hex[:9], password=secrets.token_hex(24))
        qa.save()
    if not s.get('driver_created'):
        with qa.oracle_connection() as conn:
            cur = conn.cursor()
            cur.execute('select count(*)from RUSERS where ID=:a', a=s['actor'])
            if not cur.fetchone()[0]:
                cur.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'Own nested tare driver',:a,:w,0,1)", a=s['actor'], p=s['password'], w=s['warehouse'])
                for right in ['tare_accept', 'tare_offer', 'driver_return_accept']:
                    cur.execute('insert into RIGHTS(USER_GROUP,RIGHT1)values(:a,:r)', a=s['actor'], r=right)
                conn.commit()
        s['driver_created'] = True
        qa.save()
    qa.step('driver_binding', '/api/transport/driver-bindings/' + str(t['driver_id']), dict(user_id=s['actor'], active=True, expected_version=0), method='PUT')
    qa.step('tare_offer', '/api/inventory/tare/offer', dict(operation_id=s['tag'] + '.tare.offer', task_id=t['transport_task_id'],
        owner_ware_id=s['warehouse'], pallet_type_id=1, condition='GOOD', from_kind='WAREHOUSE', from_id=str(s['warehouse']),
        to_kind='VEHICLE', to_id=str(t['vehicle_id']), quantity='1', scan_vehicle=t['vehicle_number'], booking_operation_ids=[s['tag'] + '.tare.book']))
    qa.step('tare_accept', '/api/inventory/tare/accept', dict(operation_id=s['tag'] + '.tare.accept', offer_operation_id=s['tag'] + '.tare.offer',
        accepted_quantity='1', scan_vehicle=t['vehicle_number']), qa=True)
    s['status'] = 'LOADED_TARE_ACCEPTED_DEPARTURE_PENDING'
    s.pop('error', None)
    qa.save()


def depart():
    path = OUT / 'transport.json'
    t = json.loads(path.read_text(encoding='utf-8'))
    t['load_body'] = s['requests']['load_with_tare']['body']
    t['loaded'] = s['results']['load_with_tare']
    path.write_text(json.dumps(t, indent=2), encoding='utf-8')
    card = s['results']['composition_after_load']
    for system, sender in [('SAP', 'TC03.SAP'), ('SKM', 'TC03.SKM')]:
        qa.step('composition_ack_' + system, '/api/tradecase/order-compositions/acknowledgments', dict(schema_version=1,
            warehouse_id=s['warehouse'], order_id='FP21.' + str(s['warehouse']) + '.ORDER', system_code=system, sender_id=sender,
            event_id=s['tag'] + '.ack.' + system, composition_no=card['composition_no'], signature=card['signature'],
            outcome='ACCEPTED', occurred_at=datetime.now(timezone.utc).isoformat()))
    env = dict(os.environ, TRADECASE_TRANSPORT_FIXTURE=str(path))
    process = subprocess.run([sys.executable, 'tests/tradecase/live_transport_documents.py'], cwd=qa.ROOT, env=env,
        capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=60)
    (OUT / 'transport-documents.txt').write_text(process.stdout + process.stderr, encoding='utf-8')
    assert process.returncode == 0, process.stderr[-1600:]
    s['transport'] = json.loads(path.read_text(encoding='utf-8'))
    historical = snapshot(s['root'])
    assert historical['physical_unit_count'] == 10 and historical['historical_composition']
    assert len(historical['nodes']) == 3 and historical['top_place_count'] == 1
    s['historical_tree'] = historical
    s['status'] = 'DEPARTED_TARE_RETURN_PENDING'
    s.pop('error', None)
    qa.save()


def finish():
    t = json.loads((OUT / 'transport.json').read_text(encoding='utf-8'))
    qa.step('tare_return_offer', '/api/inventory/tare/offer', dict(operation_id=s['tag'] + '.tare.return.offer', task_id=t['transport_task_id'],
        owner_ware_id=s['warehouse'], pallet_type_id=1, condition='GOOD', from_kind='VEHICLE', from_id=str(t['vehicle_id']),
        to_kind='WAREHOUSE', to_id=str(s['warehouse']), quantity='1', scan_vehicle=t['vehicle_number']), qa=True)
    qa.step('tare_return_accept', '/api/inventory/tare/accept', dict(operation_id=s['tag'] + '.tare.return.accept',
        offer_operation_id=s['tag'] + '.tare.return.offer', accepted_quantity='1', scan_vehicle=t['vehicle_number']))
    finish_wave()
    if 'tare_close' not in s['requests']:
        balances = qa.expect(200, qa.http('GET', f"/api/inventory/tare/warehouses/{s['warehouse']}/balances"))
        ware = [r for r in balances if r['custodian_kind'] == 'WAREHOUSE' and r['custodian_id'] == str(s['warehouse']) and r['pallet_type_id'] == 1 and r['condition_code'] == 'GOOD']
        assert len(ware) == 1 and ware[0]['quantity'] == '1', balances
        qa.step('tare_close', '/api/inventory/tare/count', dict(operation_id=s['tag'] + '.tare.close', owner_ware_id=s['warehouse'],
            pallet_type_id=1, condition='GOOD', observed_quantity='0', expected_version=ware[0]['balance_version'],
            reason='Close synthetic QA tare after real native return', decision_reference='TEST_NOT_PHYSICAL_TARE_SURVEY'))
    qa.step('driver_binding_close', '/api/transport/driver-bindings/' + str(t['driver_id']),
        dict(user_id=s['actor'], active=False, expected_version=1), method='PUT')
    with qa.oracle_connection() as conn:
        cur = conn.cursor()
        cur.execute('update RUSERS set DELETED=1 where ID=:a', a=s['actor'])
        cur.execute('delete from RIGHTS where USER_GROUP=:a', a=s['actor'])
        conn.commit()
    picked = json.loads((OUT / 'scoped-full-pallet.json').read_text(encoding='utf-8'))
    qa.step('qualification_close', f"/api/resources/{picked['resource_id']}/qualifications", dict(task_type='PICKING_MOVE', active=False), method='PUT')
    assert qa.query('select nvl(sum(r.REMAIN),0),nvl(sum(r.HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w', w=s['warehouse']) == [(0, 0)]
    assert qa.query('select sum(BASE_QTY)from RRL_EVENTS where OPERATION_ID=:o', o=s['requests']['load_with_tare']['body']['operation_id']) == [(-10,)]
    assert qa.query("select count(*)from RRL_STOCK_OPERATION where OPERATION_ID=:o and STATE='APPLIED'", o=s['requests']['load_with_tare']['body']['operation_id']) == [(1,)]
    assert qa.query("select count(*)from USER_OBJECTS where STATUS='INVALID'") == [(0,)]
    s['tare_after'] = qa.expect(200, qa.http('GET', f"/api/inventory/tare/warehouses/{s['warehouse']}/balances"))
    assert all(r['quantity'] == '0' for r in s['tare_after'])
    s['checks'] = ['Fresh received10 via native factory BOX; scoped reach-truck pick/bind', 'PALLET -> BOX -> STOCK,10 units counted once',
        'Explicit floor declaration and single held HU tare required; typed manual box/root measurements',
        'Native nested load and exact replay: one APPLIED, goods event total -10, warehouse0/H0',
        'Same order composition10 codes before/after load; separate late SAP/SKM accepts without stock write',
        'Two different tare participants; error document blocks departure, READY permits exact departure',
        'Historical3-node tree retained; tare returned by opposite participants; drivers retired, tare0, qualification off']
    s['status'] = 'PASS'
    s.pop('error', None)
    qa.save()


def finish_wave():
    prep = json.loads((OUT / 'scoped-full-preparation.json').read_text(encoding='utf-8'))
    path = '/api/picking/waves/' + str(prep['wave_id'])
    preview = qa.expect(200, qa.http('GET', path + '/execution'))
    assert preview['ready'] or preview['completed'], preview
    body = dict(operation_id=s['tag'] + '.wave.finish')
    result = qa.step('wave_finished', path + '/finish-execution', body)
    assert qa.expect(200, qa.http('POST', path + '/finish-execution', body)) == result
    assert qa.query('select STATUS from RRL_PICK_WAVE where PICK_WAVE_ID=:w', w=prep['wave_id']) == [('DONE',)]
    assert qa.query('select SYNC_STATUS from RRL_WAREHOUSE_TASK_SYNC where TASK_ID=:t', t=prep['task'][0]) == [('SYNCED',)]
    qa.save()


if __name__ == '__main__':
    s['previous_calls'] = s.get('calls', [])
    try:
        if s.get('status') == 'PASS':
            print('Closed; no commands sent')
        elif '--finish-wave' in sys.argv:
            finish_wave()
        elif '--finish' in sys.argv:
            finish()
        elif '--depart' in sys.argv:
            depart()
        elif '--tare' in sys.argv:
            tare_handover()
        elif '--load' in sys.argv:
            load()
        elif '--transport' in sys.argv:
            prepare_transport()
        elif not s.get('status'):
            prepare(); pack()
        else:
            print('Retained stage; no preparation repeated')
    except Exception as exc:
        s['error'] = str(exc)
        qa.save()
        raise
    finally:
        scoped.s.setdefault('history', []).extend(qa.CALLS)
        if scoped.prep.FILE.parent == OUT and 'fixture' in scoped.prep.s:
            scoped.prep.s.setdefault('history', []).extend(qa.CALLS)
            scoped.prep.save()
        if scoped.FILE.parent == OUT:
            scoped.save()
        qa.save()
    print(s.get('status'))
