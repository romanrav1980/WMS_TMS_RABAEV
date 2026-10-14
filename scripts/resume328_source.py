exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.inventory.infrastructure.fullpal_shipment import FullPalletShipment
from app.modules.fulfillment.infrastructure.execution_progress import OrderExecution
from datetime import datetime,timedelta,timezone
from uuid import uuid4
import httpx
progress=json.loads(Path("tmp/source328_progress.json").read_text(encoding="utf-8"))
globals().update(progress);ware=progress["warehouse"];gtin=progress["barcode"];units=[]
cfg=s;admin_api=httpx.Client(auth=("admin","admin123"),timeout=35);base="http://127.0.0.1:8088"
with oracledb.connect(user=cfg.oracle_user,password=cfg.oracle_password,dsn=cfg.oracle_dsn)as conn:
    q=conn.cursor()
    q.execute("select p.PICK_TASK_ID,p.PICK_PLAN_ID,p.PICK_PLAN_LINE_ID,p.CUSTOMER_ID from RRL_WAREHOUSE_TASK t join RRL_PICK_WAVE_TASK w on w.PICK_WAVE_TASK_ID=t.SOURCE_TASK_ID join RRL_PICK_TASK p on p.PICK_TASK_ID=w.PICK_TASK_ID where t.TASK_ID=:task_id",task_id=task)
    pt,plan,pl,customer=q.fetchone()
    q.execute("select FULFILLMENT_ID from RRL_CUSTOMER_ORDER_FULFILLMENT where CUSTOMER_ORDER_ID=:order_id",order_id=order);ff=q.fetchone()[0]
    q.execute("select TRANSTYPE,VODITEL_ID from RRL_TRANSPORT_TASK where ID=:trip_id",trip_id=trip);trtype,driver=q.fetchone()
    q.execute("select count(*)from RRL_PALLETS where UID_PALLET=:lot_id",lot_id=lot)
    assert q.fetchone()==(0,),"Birth already performed; resume later stage without recreating"
    conn.rollback()
    def meta(sql, **b):
        if ':ware' in sql:
            b['ware'] = ware
        q.callproc('RRL_STOCK_CONFIG_API.begin_change', ['admin', 'warehouse_settings_edit'])
        try:
            q.execute(sql, b)
            conn.commit()
        except BaseException:
            conn.rollback()
            raise
        finally:
            q.callproc('RRL_STOCK_CONFIG_API.end_change')

    def seq(name):
        q.execute('select ' + name + '.nextval from dual')
        return int(q.fetchone()[0])

    def post(kind, body, source, op=None):
        command = {'contract_version': 2, 'operation_id': op or 'FULL.QA:' + uuid4().hex, 'command_type': kind, 'actor': 'admin', 'source': source, 'lines': [], 'units': [], 'metadata': body}
        inp, out = (q.var(oracledb.DB_TYPE_CLOB), q.var(oracledb.DB_TYPE_CLOB))
        inp.setvalue(0, json.dumps(command))
        try:
            q.callproc('RRL_STOCK_POSTING_API.prepare_command', [json.dumps(command), 'admin', out, None])
            if out.getvalue() is None:
                q.callproc('RRL_STOCK_POSTING_API.execute_prepared', [out])
            result = out.getvalue()
            conn.commit()
            return json.loads(result.read() if hasattr(result, 'read') else result)
        except BaseException:
            conn.rollback()
            raise
        finally:
            q.callproc('RRL_STOCK_POSTING_API.reset_connection')

    def api(method, path, body=None, status=200):
        r = admin_api.request(method, base + path, json=body)
        assert r.status_code == status, (r.status_code, r.text[:2200])
        return r.json()
    born = api('POST', '/api/inventory/stock-posting/inventory/lots', {'operation_id': 'IW328.BIRTH:' + tag, 'revision_id': revision, 'uid': lot, 'cell': src, 'article': article, 'quantity': '3', 'expiry_date': '2030-01-01', 'price': '0', 'reason': 'Own328 exact physical marked units'})
    post('RESERVATION_CREATE', {'uid_pallet': lot, 'cell': src, 'articul': article, 'qty': '3', 'unit_code': 'EA', 'ware_id': ware, 'reservation_kind': 'HARD', 'reservation_scope': 'PALLET', 'reservation_domain': 'PICKING', 'source_doc_type': 'PICK_WAVE', 'source_doc_id': wave, 'source_line_id': pt, 'customer_order_id': order, 'customer_id': customer, 'pick_plan_id': plan, 'pick_plan_line_id': pl}, {'type': 'PICK_WAVE', 'id': wave})
    post('WAVE_PICK_RELEASE', {}, {'wave_id': wave})
    before = OrderExecution(OracleGateway()).get(order)
    assert before['lines'][0]['picked_quantity'] == '0'
    completed = post('TASK_COMPLETE', {'fact_qty': '3', 'scanned_pallet': lot, 'scanned_from_cell': src, 'scanned_to_cell': dst}, {'task_id': task})
    preview = FullPalletShipment(OracleGateway()).preview(task)
    assert preview['pallet_identifier'] == lot and preview['quantity'] == '3'
    body = {'shipment_identifier': st_uid, 'scanned_pallet': lot, 'expected_stock_version': int(preview['stock_version'])}
    op = 'FULL.BIND:' + tag
    bound = post('PICK_PALLET_BIND_SHIPMENT', body, {'task_id': task}, op)
    assert post('PICK_PALLET_BIND_SHIPMENT', body, {'task_id': task}, op) == bound
    q.execute('select STATUS,FACT_QTY,FACT_UOM,PICKED_WAREHOUSE_TASK_ID,PICKED_PALLET_UID from RRL_CUSTOMER_ORDER_FULFILLMENT where FULFILLMENT_ID=:id', id=ff)
    assert q.fetchone() == ('PICKED', 3, 'EA', task, lot)
    assert OrderExecution(OracleGateway()).get(order)['lines'][0]['picked_quantity'] == '3'
    post('INTERNAL_MOVE', {'uid': lot, 'source_cell': dst, 'target_cell': shipcell, 'quantity': '0', 'unit': 'EA'}, {})
    from app.transport_composition import build_transport_loading
    loading = build_transport_loading()
    preview = loading.preview_single(st_uid)
    assert preview['root'] == lot and preview['snapshot']['nodes'][0]['kind'] == 'STOCK'
    from app.modules.inventory.infrastructure.outgoing_quality import OutgoingQuality
    qc = OutgoingQuality(OracleGateway())
    quality = qc.status(st_uid, 'admin')
    scans = [code for unit in units for code in unit['codes']]
    api('POST', '/api/outgoing-quality/' + st_uid + '/scan', {'operation_id': 'IW328.QC:' + tag, 'expected_composition_signature': quality['composition_signature'], 'error_count': 0, 'scans': scans})
    assert qc.status(st_uid, 'admin')['ready']
    loading_context = {'transport_task_id': trip, 'scan_vehicle': 'QL' + tag, 'scan_dock': dock, 'measurements': {'origin': 'MANUAL_CONFIRMED', 'content_version': preview['expected_version'], 'gross_weight_kg': '10', 'width_m': '1', 'depth_m': '1', 'height_m': '1.5'}}
    ship_body = {'expected_version': preview['expected_version'], 'expected_composition_signature': preview['composition_signature'], 'scan_container': lot, 'scan_cell': shipcell, 'loading_context': loading_context}
    shipop = 'IW328.LOAD:' + tag
    shipped = loading.load_single(shipop, st_uid, ship_body, 'admin')
    assert loading.load_single(shipop, st_uid, ship_body, 'admin') == shipped and shipped['physical_places'] == 1
    q.execute('select TT_ID,ROOT_UID,VEHICLE_ID,VEHICLE_NUMBER,DOCK,STATUS from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:op', op=shipop)
    assert q.fetchone() == (trip, lot, vehicle, 'QL' + tag, dock, 'LOADED')
    departed = loading.depart('IW328.DEPART:' + tag, trip, 'admin')
    q.execute('select STATUS from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:p', p=shipop)
    assert q.fetchone()[0] == 'DEPARTED'
    q.execute("select count(*),sum(BASE_QTY)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:u and STOCK_STATUS='ISSUED'and HARD_RESERVATION_ID is null", u=lot)
    assert q.fetchone() == (0, None)
    target = ware + 50000000
    inbound = 'QI328' + tag
    outbound = 'QO328' + tag
    meta("insert into RRL_WARES(ID,NAME,PREFIX)values(:w,:n,'QI')", w=target, n='Own328 target ' + tag)
    for dc in [inbound, outbound]:
        meta('insert into RRL_TT_DOCK(DOCK,WARE_ID,DOCK_IS_BLOCKED)values(:d,:w,0)', d=dc, w=target)
    target_trip = seq('RRL_TRANSPORT_TASK_SQ')
    meta("insert into RRL_TRANSPORT_TASK(ID,TRANSPORT,TRANSTYPE,CONDITION,SHIPMENT_DATE,VODITEL_ID,DOCK,DELETED)values(:id,:plate,:typ,'Спланирован',trunc(sysdate),:driver,:dock,0)", id=target_trip, plate='QL' + tag, typ=trtype, driver=driver, dock=outbound)
    now = datetime.now(timezone.utc)
    plan_body = {'operation_id': 'IW328.PLAN:' + tag, 'source_load_operation_id': shipop, 'target_warehouse_id': target, 'target_trip_id': target_trip, 'inbound_dock': inbound, 'arrival_due': (now + timedelta(hours=1)).isoformat(), 'ready_due': (now + timedelta(hours=2)).isoformat(), 'reason': 'Own328 exact marked source preserves original units', 'decision_reference': 'IW328:' + tag}
    planned = api('POST', '/api/inventory/interwarehouse/plan', plan_body)
    assert not planned['unit_capture_required'] and planned['physical_unit_count'] == 0 and (planned['regulatory_ack_verified'] is False) and (not planned['stock_changed']), planned
    assert api('POST', '/api/inventory/interwarehouse/plan', plan_body) == planned
    api('POST', '/api/inventory/interwarehouse/plan', {**plan_body, 'operation_id': 'IW328.SECOND:' + tag}, status=409)
    q.execute('select count(*)from RRL_EVENTS where OPERATION_ID=:p', p=plan_body['operation_id'])
    assert q.fetchone()[0] == 0
    q.execute('select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA=:u', u=lot)
    assert q.fetchone() == (0, 0)
    q.execute('select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=6667491')
    assert q.fetchone() == (20, 20)
    context = {'tag': tag, 'article': article, 'lot': lot, 'warehouse': ware, 'target_warehouse': target, 'source_load': shipop, 'plan_operation_id': plan_body['operation_id'], 'source_trip': trip, 'target_trip': target_trip, 'inbound': inbound, 'outbound': outbound, 'barcode': gtin, 'source_quantity': '3'}
    Path('tmp/context328.json').write_text(json.dumps(context, indent=2), encoding='utf-8')
    print('SOURCE328 original ordinaryFULLPAL born3/picked3/singleload/depart P0 ->frozeninterwareplan3, no physicalunit registry/protected20-20')
