"""Actual full-pallet move -> existing ST binding -> pinned shipment; clean only own P/H through root."""
import json, sys
from pathlib import Path
from uuid import uuid4
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'api/wms_api_server'))
from app.config import get_settings
from app.oracle_gateway import OracleGateway
from app.modules.inventory.infrastructure.fullpal_shipment import FullPalletShipment
from app.modules.fulfillment.infrastructure.execution_progress import OrderExecution
cfg = get_settings()
if Path('tmp/context347.json').exists():
    raise SystemExit('SOURCE347 already retained; use case347_partial.py without recreating')
tag = uuid4().hex[:10]
lot = 'FULL.QA:' + tag
other = lot + 'O'
src = 'QF' + tag
dst = 'QG' + tag
st_uid = 'FULL.ST:' + tag
with oracledb.connect(user=cfg.oracle_user, password=cfg.oracle_password, dsn=cfg.oracle_dsn) as conn:
    conn.call_timeout = 15000
    q = conn.cursor()

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
    q.execute("select user,sys_context('USERENV','SERVICE_NAME') from dual")
    assert q.fetchone() == ('RABAEV', 'orcl')
    q.execute("select ARTICUL from RRL_PALLETS where UID_PALLET='DS-BASE-B1'")
    article = q.fetchone()[0]
    old_article = article
    article = 'QIW347' + tag.upper()
    barcode_prefix = '046' + str(int(tag, 16) % 10000000000).zfill(10)
    gtin = barcode_prefix + str((10 - sum((int(n) * (3 if i % 2 == 0 else 1) for i, n in enumerate(reversed(barcode_prefix)))) % 10) % 10)
    meta('declare x RRL_ARTICULS%rowtype;begin select *into x from RRL_ARTICULS where ACTICUL=:old;x.ACTICUL:=:a;x.BARCODE_SHT:=:bc;insert into RRL_ARTICULS values x;end;', old=old_article, a=article, bc=gtin)
    meta("insert into RRL_STOCK_UOM_CONVERSION(ARTICUL,INPUT_UOM,BASE_UOM,POLICY_VERSION,NUMERATOR,DENOMINATOR,BASE_SCALE,PROVENANCE)select :a,INPUT_UOM,BASE_UOM,POLICY_VERSION,NUMERATOR,DENOMINATOR,BASE_SCALE,'Own347 marked fullpal'from RRL_STOCK_UOM_CONVERSION where ARTICUL=:old", a=article, old=old_article)
    meta("insert into RRL_SKU_RECEIPT_POLICY(ARTICUL,POLICY_VERSION,MARKING_REQUIRED,UPDATED_BY)values(:a,1,0,'admin')", a=article)
    meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('SKU',:a),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD", a=article)
    import httpx
    from datetime import datetime, timedelta, timezone
    admin_api = httpx.Client(auth=('admin', 'admin123'), timeout=35)
    base = 'http://127.0.0.1:8088'

    def api(method, path, body=None, status=200):
        r = admin_api.request(method, base + path, json=body)
        assert r.status_code == status, (r.status_code, r.text[:2200])
        return r.json()
    units = []
    q.execute('select min(CUSTOMER_ID) from RRL_CUSTOMER')
    customer = q.fetchone()[0]
    ware = 100000 + int(tag[:6], 16)
    shipcell = 'QH' + tag
    top = 'HU.FULL:' + tag
    box = 'HU.FULL.BOX:' + tag
    meta('insert into RRL_WARES(ID,NAME,PREFIX) values(:ware,:n,:p)', n='Own FULLPAL HU ' + tag, p='Q' + tag[:2])
    meta("insert into RRL_RECEIPT_WARE_SETTINGS(WARE_ID,OUTGOING_QC_MODE,OUTGOING_QC_INDEPENDENT) values(:ware,'NONE',0)")
    for cell in (src, dst, shipcell):
        meta('insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT) values(:c,:ware,0,0,0,0,0,0,0)', c=cell)
        meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID) select RRL_STOCK_LOCK_API.resource_key('CELL',:c),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD", c=cell)
    revision = int(q.callfunc('REVIZION.create_revizion', oracledb.DB_TYPE_NUMBER, [ware, 'admin']))
    conn.commit()
    order, row, plan, pl, pt, wave, wt, task, st, ff = [seq(n) for n in ('RRL_CUSTOMER_ORDER_SQ', 'RRL_CUSTOMER_ORDER_ROW_SQ', 'RRL_PICK_PLAN_SQ', 'RRL_PICK_PLAN_LINE_SQ', 'RRL_PICK_TASK_SQ', 'RRL_PICK_WAVE_SQ', 'RRL_PICK_WAVE_TASK_SQ', 'RRL_WAREHOUSE_TASK_SQ', 'RRL_SBORKA_PALLETS_SQ', 'RRL_CUSTOMER_ORDER_FULF_SQ')]
    meta('insert into RRL_CUSTOMER_ORDER(CUSTOMER_ORDER_ID,ORDER_NO,CUSTOMER_ID,WARE_ID) values(:id,:no,:c,:ware)', id=order, no=lot, c=customer)
    meta("insert into RRL_CUSTOMER_ORDER_ROW(CUSTOMER_ORDER_ROW_ID,CUSTOMER_ORDER_ID,LINE_NO,ARTICUL,ORDER_QTY,UNIT_CODE) values(:id,:o,1,:a,3,'EA')", id=row, o=order, a=article)
    meta("insert into RRL_PICK_PLAN(PICK_PLAN_ID,CUSTOMER_ORDER_ID,CUSTOMER_ID,WARE_ID,STATUS) values(:id,:o,:c,:ware,'RELEASED')", id=plan, o=order, c=customer)
    meta("insert into RRL_PICK_PLAN_LINE(PICK_PLAN_LINE_ID,PICK_PLAN_ID,CUSTOMER_ORDER_ROW_ID,ARTICUL,REQUESTED_QTY,PLANNED_QTY,STATUS) values(:id,:p,:r,:a,3,3,'PLANNED_FULL')", id=pl, p=plan, r=row, a=article)
    meta("insert into RRL_PICK_TASK(PICK_TASK_ID,PICK_PLAN_ID,PICK_PLAN_LINE_ID,CUSTOMER_ORDER_ID,CUSTOMER_ID,TASK_TYPE,STATUS,ARTICUL,PALLET_UID,SOURCE_CELL_CODE,TARGET_CELL_CODE,QTY) values(:id,:p,:pl,:o,:c,'FULL_PALLET','NEW',:a,:u,:src,:dst,3)", id=pt, p=plan, pl=pl, o=order, c=customer, a=article, u=lot, src=src, dst=dst)
    meta("insert into RRL_PICK_WAVE(PICK_WAVE_ID,WAVE_CODE,WARE_ID,STATUS,CREATED_BY) values(:id,:code,:ware,'LAUNCHED','admin')", id=wave, code=lot)
    meta("insert into RRL_PICK_WAVE_TASK(PICK_WAVE_TASK_ID,PICK_WAVE_ID,PICK_TASK_ID,TASK_TYPE,STATUS,ARTICUL,PALLET_UID,QTY,SOURCE_CELL_CODE,TARGET_CELL_CODE) values(:id,:w,:p,'FULL_PALLET','NEW',:a,:u,3,:src,:dst)", id=wt, w=wave, p=pt, a=article, u=lot, src=src, dst=dst)
    meta("insert into RRL_WAREHOUSE_TASK(TASK_ID,TASK_TYPE,TASK_SOURCE,SOURCE_TASK_ID,SOURCE_DOC_TYPE,SOURCE_DOC_ID,UID_PALLET,FROM_CELL,TO_CELL,FROM_WARE_ID,TO_WARE_ID,QTY,UNIT_CODE,QTY_MODE,STATUS,ASSIGNED_TO,CREATED_BY) values(:id,'PICKING_MOVE','WAVE',:wt,'PICK_WAVE',:w,:u,:src,:dst,:ware,:ware,3,'EA','PALLET','ASSIGNED','admin','admin')", id=task, wt=wt, w=wave, u=lot, src=src, dst=dst)
    meta("insert into RRL_SBORKA_PALLETS(ID,PALLET_UID,ST_NUMBER,WARE_ID,CONDITION,ADDR) values(:id,:u,:u,:ware,0,'Own full-pallet ST')", id=st, u=st_uid)
    meta("insert into RRL_SBORKA_PALLET_ROWS(ID,PALLET_UID,ARTICUL,EI,QUANTITY) values(RRL_SBORKA_PALLET_ROWS_SQ.nextval,:u,:a,'BOX',0.125)", u=st_uid, a=article)
    meta("insert into RRL_CUSTOMER_ORDER_FULFILLMENT(FULFILLMENT_ID,CUSTOMER_ORDER_ID,LEGACY_SBORKA_PALLET_ID,PALLET_UID,STATUS,FACT_QTY) values(:id,:o,:st,:u,'PLANNED',0)", id=ff, o=order, st=st, u=st_uid)
    q.execute("select TRANSPORTTYPE from RRL_TRANSPORT_TYPE where TRANSPORTTYPE='15'")
    trtype = q.fetchone()[0]
    driver = seq('RRL_TR_VODITEL_SQ')
    meta("insert into RRL_TR_VODITEL(ID,F,I,O,DELETED)values(:id,'Own347','Driver',:tag,0)", id=driver, tag=tag)
    vehicle = int(q.callfunc('RRL_TR_VEHICLE_ADD', oracledb.DB_TYPE_NUMBER, ['QL' + tag, trtype, 100, 1, 0, None]))
    conn.commit()
    trip = seq('RRL_TRANSPORT_TASK_SQ')
    dock = 'QD' + tag
    pending_st = seq('RRL_SBORKA_PALLETS_SQ')
    meta('insert into RRL_TT_DOCK(DOCK,WARE_ID,DOCK_IS_BLOCKED) values(:dock,:ware,0)', dock=dock)
    meta("insert into RRL_TRANSPORT_TASK(ID,TRANSPORT,TRANSTYPE,CONDITION,SHIPMENT_DATE,VODITEL_ID,DOCK,DELETED) values(:id,:plate,:typ,'Спланирован',trunc(sysdate),:driver,:dock,0)", id=trip, plate='QL' + tag, typ=trtype, driver=driver, dock=dock)
    meta('update RRL_TR_VEHICLE set WORKING_NOW=1,BLOCKED=0,DELETED=0 where ID=:id', id=vehicle)
    meta('update RRL_SBORKA_PALLETS set TRANSTASK_ID=:tt where ID=:id', tt=trip, id=st)
    try:
        Path("tmp/source347_progress.json").write_text(json.dumps({"tag":tag,"article":article,"lot":lot,"warehouse":ware,"src":src,"dst":dst,"shipcell":shipcell,"task":task,"st":st,"st_uid":st_uid,"order":order,"wave":wave,"revision":revision,"trip":trip,"vehicle":vehicle,"dock":dock,"barcode":gtin},indent=2),encoding="utf-8")
        born = api('POST', '/api/inventory/stock-posting/inventory/lots', {'operation_id': 'IW347.BIRTH:' + tag, 'revision_id': revision, 'uid': lot, 'cell': src, 'article': article, 'quantity': '3', 'expiry_date': '2030-01-01', 'price': '0', 'reason': 'Own347 exact physical marked units'})
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
        api('POST', '/api/outgoing-quality/' + st_uid + '/scan', {'operation_id': 'IW347.QC:' + tag, 'expected_composition_signature': quality['composition_signature'], 'error_count': 0, 'scans': scans})
        assert qc.status(st_uid, 'admin')['ready']
        loading_context = {'transport_task_id': trip, 'scan_vehicle': 'QL' + tag, 'scan_dock': dock, 'measurements': {'origin': 'MANUAL_CONFIRMED', 'content_version': preview['expected_version'], 'gross_weight_kg': '10', 'width_m': '1', 'depth_m': '1', 'height_m': '1.5'}}
        ship_body = {'expected_version': preview['expected_version'], 'expected_composition_signature': preview['composition_signature'], 'scan_container': lot, 'scan_cell': shipcell, 'loading_context': loading_context}
        shipop = 'IW347.LOAD:' + tag
        shipped = loading.load_single(shipop, st_uid, ship_body, 'admin')
        assert loading.load_single(shipop, st_uid, ship_body, 'admin') == shipped and shipped['physical_places'] == 1
        q.execute('select TT_ID,ROOT_UID,VEHICLE_ID,VEHICLE_NUMBER,DOCK,STATUS from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:op', op=shipop)
        assert q.fetchone() == (trip, lot, vehicle, 'QL' + tag, dock, 'LOADED')
        departed = loading.depart('IW347.DEPART:' + tag, trip, 'admin')
        q.execute('select STATUS from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:p', p=shipop)
        assert q.fetchone()[0] == 'DEPARTED'
        q.execute("select count(*),sum(BASE_QTY)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:u and STOCK_STATUS='ISSUED'and HARD_RESERVATION_ID is null", u=lot)
        assert q.fetchone() == (0, None)
        common=json.loads(Path('tmp/context346.json').read_text(encoding='utf-8'))
        target=common['target_warehouse'];inbound=common['inbound'];outbound=common['outbound'];target_trip=common['target_trip']
        now = datetime.now(timezone.utc)
        plan_body = {'operation_id': 'IW347.PLAN:' + tag, 'source_load_operation_id': shipop, 'target_warehouse_id': target, 'target_trip_id': target_trip, 'inbound_dock': inbound, 'arrival_due': (now + timedelta(hours=1)).isoformat(), 'ready_due': (now + timedelta(hours=2)).isoformat(), 'reason': 'Own347 exact marked source preserves original units', 'decision_reference': 'IW347:' + tag}
        planned = api('POST', '/api/inventory/interwarehouse/plan', plan_body)
        assert not planned.get('unit_capture_required',False) and planned.get('physical_unit_count',0) == 0 and (planned.get('regulatory_ack_verified',False) is False) and (not planned['stock_changed']), planned
        assert api('POST', '/api/inventory/interwarehouse/plan', plan_body) == planned
        api('POST', '/api/inventory/interwarehouse/plan', {**plan_body, 'operation_id': 'IW347.SECOND:' + tag}, status=409)
        q.execute('select count(*)from RRL_EVENTS where OPERATION_ID=:p', p=plan_body['operation_id'])
        assert q.fetchone()[0] == 0
        q.execute('select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA=:u', u=lot)
        assert q.fetchone() == (0, 0)
        q.execute('select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=6667491')
        assert q.fetchone() == (20, 20)
        context = {'tag': tag, 'article': article, 'lot': lot, 'warehouse': ware, 'target_warehouse': target, 'source_load': shipop, 'plan_operation_id': plan_body['operation_id'], 'source_trip': trip, 'target_trip': target_trip, 'inbound': inbound, 'outbound': outbound, 'barcode': gtin, 'source_quantity': '3'}
        Path('tmp/context347.json').write_text(json.dumps(context, indent=2), encoding='utf-8')
        print('SOURCE347 original ordinaryFULLPAL born3/picked3/singleload/depart P0 ->frozeninterwareplan3, no physicalunit registry/protected20-20')
    finally:
        conn.rollback()
        q.callproc('RRL_STOCK_POSTING_API.reset_connection')
