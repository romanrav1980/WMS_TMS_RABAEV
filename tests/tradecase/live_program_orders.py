"""Revision-27 stock: 700 A + 400 B boxes, ten marked units per independent place.

Own warehouse only. Inventory is received and moved through HTTP, never inserted.
Master data and external acknowledgments are synthetic; this is not ERP acceptance.
Resume the same state after interruption; do not reopen a closed fixture.
"""
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).parent))
import live_topup_physical_660 as q

q.OUT = q.ROOT / 'runtime/test-evidence/tradecase/2026-10-27/T08/program-orders'
resumed_state = q.OUT / 'state.resumed.json'
state_name = os.environ.get('TRADECASE_PROGRAM_STATE', resumed_state.name if resumed_state.exists() else 'state.json')
assert Path(state_name).name == state_name, 'State filename must stay inside the fixture directory'
assert not (resumed_state.exists() and state_name == 'state.json'), 'The recovered state supersedes the old checkpoint'
q.STATE = q.OUT / state_name
if q.STATE.exists():
    q.s.update(json.loads(q.STATE.read_text(encoding='utf-8')))
s = q.s


def setup():
    if 'fixture' not in s:
        if 'planned' not in s:
            uid, warehouse = q.plan_fixture()
            s['planned'] = dict(uid=uid, warehouse=warehouse)
            q.save()
        original = q.live_stock_acceptance.uuid4
        q.live_stock_acceptance.uuid4 = lambda: type('Tag', (), dict(hex=s['planned']['uid']))()
        try:
            f = q.setup()
        finally:
            q.live_stock_acceptance.uuid4 = original
        assert f['warehouse_id'] == s['planned']['warehouse']
        s['fixture'] = {k: v for k, v in f.items() if k != 'password'}
        q.save()
    f = s['fixture']
    s.setdefault('day', (datetime.now(ZoneInfo('Europe/Moscow')).date()+timedelta(days=1)).isoformat())
    s.setdefault('expiry', (datetime.now(ZoneInfo('Europe/Moscow')).date()+timedelta(days=90)).isoformat())
    s.setdefault('skus', dict(A=dict(article=f['article'], gtin=f['gtin'], mrc='200', boxes=700),
                              B=dict(article=f['article']+'B', gtin=q.ean('292'+f['gtin'][3:13]), mrc='220', boxes=400)))
    q.save()
    if 'article_b' not in s:
        b = s['skus']['B']
        doc = ET.Element('ARTMAS10'); idoc = ET.SubElement(doc, 'IDOC')
        q.fields(ET.SubElement(idoc, 'EDI_DC40'), dict(MESTYP='ARTMAS', IDOCTYP='ARTMAS10', DOCNUM=str(int(s['planned']['uid'][:8], 16)+2000000000000000), SNDPRN='TC03.QA.SAP', CREDAT='20261027', CRETIM='060000'))
        for segment, values in [('E1BPE1MATHEAD', {}), ('E1BPE1MARART', dict(BASE_UOM='EA', EAN_UPC=b['gtin'])),
                                ('E1BPE1MAKTRT', dict(LANGU_ISO='EN', MATL_DESC='TRADECASE program B')),
                                ('E1BPE1MARMRT', dict(ALT_UNIT='EA', NUMERATOR=1, DENOMINATR=1, EAN_UPC=b['gtin'])),
                                ('E1BPE1MARMRT', dict(ALT_UNIT='BOX', NUMERATOR=10, DENOMINATR=1, EAN_UPC=q.ean('293'+b['gtin'][3:13])))]:
            q.fields(ET.SubElement(idoc, segment), dict(MATERIAL=b['article'], **values))
        s['article_b'] = q.xml_call('/api/integrations/sap/artmas', doc, 202); q.save()
    if 'configured' not in s:
        with q.oracle_connection() as conn:
            cur = conn.cursor(); cur.callproc('RRL_STOCK_CONFIG_API.begin_change', ['admin', 'warehouse_settings_edit'])
            try:
                for sku in s['skus'].values():
                    cur.execute('update RRL_ARTICULS set TYPE_W=0,COUNT_SHT_IN_KOR=10,BRUTTO_WEIGHT_OF_KOR=10,DIMKOR_X=0.4,DIMKOR_Y=0.5,DIMKOR_Z=0.5,NORMA_UKLADKI=1,COUNT_IN_ROW=1,ROWS_IN_PAL=1 where ACTICUL=:a', a=sku['article'])
                    assert cur.rowcount == 1
                cur.execute("insert into RRL_RECEIPT_SKU_RULE(WARE_ID,ARTICUL,PICK_CELL,MIN_SHELF_DAYS,ALLOW_PICK_BATCH_MIX,SOURCE_PICK_MODE)values(:w,:a,:p,0,0,'AFTER_PUTAWAY')", w=f['warehouse_id'], a=s['skus']['B']['article'], p=f['pick'])
                cells = [f['storage']+str(i).zfill(4) for i in range(1, 1101)]
                cur.executemany('insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT)values(:1,:2,0,0,0,0,0,0,0)', [(c, f['warehouse_id']) for c in cells])
                for cell in cells:
                    cur.execute("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:c),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD", c=cell)
                conn.commit()
            finally:
                cur.callproc('RRL_STOCK_CONFIG_API.end_change')
            cur.execute("update RUSERS set DELETED=1 where ID=:a and USER_GROUP='TC03QA'", a=f['actor'])
            cur.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:r', r=f['role']); conn.commit()
        s['configured'] = True; q.save()
    b = s['skus']['B']
    q.step('b.policy', 'PUT', '/api/finished-goods/skus/'+b['article']+'/receiving-policy', dict(expected_version=0, marking_required=True, serialized_weight_boxes=False, profiles=[dict(system_code='CRPT', profile_code='TOBACCO', profile_version='TC03', scan_mode='UNIT')]))


def receive():
    f = s['fixture']; w = f['warehouse_id']; base = f'/api/tradecase/warehouses/{w}'
    q.step('site', 'PUT', base+'/site', dict(operation_id=q.tag()+'.site', expected_version=0, source_id='TC03.SAP', active_skm='TC03.SKM', planning_source='SAP', enabled=True, reason='Revision27 owned 1100 BOX stock'))
    q.send('owner', 'OWNER', 'SNS', dict(title='SNS'))
    for name, sku in s['skus'].items():
        q.send('sku.'+name, 'SKU', name, dict(title='Program '+name, wms_article_id=sku['article'], units_per_box=10, permitted_mrc=[sku['mrc']]))
    for cell, zone in ((f['receive'], 'RECEIVE'), (f['storage'], 'STORAGE'), (f['pick'], 'PICK')):
        body = dict(operation_id=q.tag()+'.zone.'+cell, expected_version=0, zone_kind=zone, reason='Owned program fixture')
        if zone == 'PICK': body['owner_id'] = 'SNS'
        q.step('zone.'+cell, 'PUT', base+'/stock/cells/'+cell, body)
    if 'supply' not in s:
        doc = ET.Element('WarehouseSupplyOrder', version='1')
        q.fields(doc, dict(Sender='TC03.QA.SAP', MessageId=q.tag()+'.supply', OrderNumber='PO'+f['tag'], Revision=1, WarehouseId=w, ReceiveCell=f['receive'], Supplier='Synthetic program supplier'))
        lines = ET.SubElement(doc, 'Lines')
        for i, sku in enumerate(s['skus'].values(), 1):
            line = ET.SubElement(lines, 'Line'); q.fields(line, dict(LineNumber=str(i), Material=sku['article']))
            ET.SubElement(line, 'Quantity', unit='EA').text = str(sku['boxes']*10)
        s['supply'] = q.xml_call('/api/integrations/sap/supply-orders', doc, 202); q.save()
    for i in range(1, 1101):
        key = str(i).zfill(4)
        if s.get('pallets', {}).get(key, {}).get('valid'): continue
        name = 'A' if i <= 700 else 'B'; sku = s['skus'][name]
        cell = f['storage']+key
        q.step('zone.'+key, 'PUT', base+'/stock/cells/'+cell, dict(operation_id=q.tag()+'.zone.'+key, expected_version=0, zone_kind='STORAGE', reason='One physical BOX per place'))
        pallet = 'PO27.'+str(w)+'.'+key
        # TOBACCO identifies a unit by GTIN + seven serial characters.
        codes = [sku['gtin']+f['tag'][:1]+key+str(n).zfill(2) for n in range(1, 11)]
        receipt = q.step('receipt.v2.'+key, 'POST', f"/api/receiving/supply-orders/{s['supply']['order_id']}/pallets", dict(operation_id=q.tag()+'.receipt.v2.'+key, line_number='1' if name=='A' else '2', pallet_identifier=pallet, quantity='10', supplier_batch='PO27', expiry_date=s['expiry'], gross_weight='10', units=[dict(unit_id=str(n), quantity='1', codes=[dict(system_code='CRPT', profile_code='TOBACCO', code=c)]) for n, c in enumerate(codes, 1)]), status=201)
        q.send('supply.'+key, 'SUPPLY', 'S'+key, dict(wms_article_id=sku['article'], sap_order_id=s['supply']['order_id'], sap_line_id='1' if name=='A' else '2', sku_id=name, owner_id='SNS', mrc=sku['mrc'], pallet_identifier=pallet, supplier_batch='PO27', expiry_date=s['expiry'], composition_source='SAP', codes=[dict(system_code='CRPT', profile_code='TOBACCO', code=c) for c in codes]))
        q.step('bind.'+key, 'POST', base+'/stock/bind', dict(operation_id=q.tag()+'.bind.'+key, supply_id='S'+key, expected_supply_version=1, scanned_pallet=pallet))
        target = q.db('select TO_CELL from RRL_WAREHOUSE_TASK where TASK_ID=:t', t=receipt['task_id'])[0][0]
        q.step('putaway.'+key, 'POST', f"/api/receiving/putaway/{receipt['task_id']}/complete", dict(scanned_pallet=pallet, scanned_from_cell=f['receive'], scanned_to_cell=target))
        items = [dict(physical_unit_key=k, expected_attribute_version=v, verdict='VALID') for k, v in q.db('select a.PHYSICAL_UNIT_KEY,a.VERSION_NO from RRL_TRADE_STOCK_ATTR a join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=a.PHYSICAL_UNIT_KEY where u.UID_PALLET=:p', p=pallet)]
        assert len(items) == 10
        q.step('valid.'+key, 'POST', base+'/stock/mark-confirmations', dict(operation_id=q.tag()+'.valid.'+key, skm_id='TC03.SKM', external_event_id=q.tag()+'.valid.'+key, expected_site_version=1, occurred_at=datetime.now(timezone.utc).isoformat(), items=items))
        s.setdefault('pallets', {})[key] = dict(pallet=pallet, cell=target, sku=name, valid=True); q.save()
        if i % 25 == 0: print('Received', i, 'of 1100 BOX', flush=True)
    assert q.stock() == (11000, 0, 1100), q.stock()
    s['phase'] = 'RECEIVED'; q.save()


def orders():
    assert s.get('phase') == 'RECEIVED', s.get('phase')
    f = s['fixture']; base = f"/api/tradecase/warehouses/{f['warehouse_id']}"
    q.step('expedition', 'PUT', base+'/stock/cells/'+f['receive'], dict(operation_id=q.tag()+'.expedition', expected_version=1, zone_kind='EXPEDITION', reason='Original three-order staging'))
    s.setdefault('orders', {})
    for number, title, sku, boxes, osg in [('101', 'Hub', 'A', 200, 70), ('102', 'Branch', 'A', 150, 50), ('103', 'Store', 'B', 250, 50)]:
        customer = q.step('customer.'+number, 'POST', '/api/customers', dict(customer_code=q.tag()+'.'+number, customer_name='Program '+title, customer_type='LEGAL_ENTITY'))['customer_id']
        q.send('recipient.'+number, 'RECIPIENT', 'C'+number, dict(title=title, wms_customer_id=customer, target_owner_id='SNS', permitted_source_owners=['SNS'], buyout_mode='BEFORE_PICK', min_osg_days=osg, lead_time_days=0, allow_broken_box=False, allow_partial_ship=True, topup_enabled=False, topup_horizon_days=3 if number=='103' else None))
        q.send('order.'+number, 'ORDER', number, dict(recipient_id='C'+number, planned_ship_at=s['day']+'T12:00:00+03:00', lines=[dict(line_id='1', sku_id=sku, source_owner_id='SNS', target_owner_id='SNS', mrc=s['skus'][sku]['mrc'], quantity=str(boxes), uom='BOX', min_osg_days=osg)]))
        native = q.native_order('order_'+number, boxes, article=s['skus'][sku]['article'], customer=customer,uom='BOX')
        repair_unbound_fixture_uom(number,native,boxes)
        q.step('binding.'+number, 'POST', base+'/orders/'+number+'/binding', dict(operation_id=q.tag()+'.bind.'+number, expected_order_version=1, customer_order_id=native['order'], lines=[dict(line_id='1', customer_order_row_id=native['row'])]))
        plan = q.step('plan.'+number, 'POST', '/api/picking/plans', dict(operation_id=q.tag()+'.plan.'+number, customer_order_id=native['order']))['pick_plan_id']
        s['orders'][number] = dict(native, customer=customer, sku=sku, boxes=boxes, plan=plan); q.save()
    wid = q.step('main.wave', 'POST', '/api/picking/waves', dict(wave_code=q.tag()+'.main', wave_name='Program three main orders', ware_id=f['warehouse_id'], planned_start_at=s['day']+'T08:00:00+03:00', planned_finish_at=s['day']+'T10:00:00+03:00'))['pick_wave_id']
    route = f'/api/picking/waves/{wid}'
    for number, order in s['orders'].items():
        q.step('main.add.'+number, 'POST', route+'/plans', dict(pick_plan_id=order['plan']))
    q.step('main.calculate', 'POST', route+'/calculate', {})
    q.step('main.launch', 'POST', route+'/launch', dict(operation_id=q.tag()+'.main.launch'))
    q.step('main.staging', 'POST', route+'/staging/release', dict(to_cell=f['receive']))
    q.step('main.release', 'POST', route+'/release-picking', dict(operation_id=q.tag()+'.main.release'))
    tasks = q.db("select TASK_ID,UID_PALLET,FROM_CELL,TO_CELL,QTY from RRL_WAREHOUSE_TASK where TASK_SOURCE='WAVE' and SOURCE_DOC_ID=:w and TASK_TYPE='PICKING_MOVE' order by TASK_ID", w=wid)
    assert len(tasks) == 600 and sum(t[4] for t in tasks) == 6000, (len(tasks), sum(t[4] for t in tasks))
    assert q.stock() == (11000, 6000, 1100), q.stock()
    s.update(main_wave=wid, main_tasks=tasks, phase='MAIN_WAVE'); q.save()


def repair_unbound_fixture_uom(number,native,boxes):
    """Correct only this fixture's earlier EA demand, before any binding or plan exists."""
    key='native.box.uom.'+number
    if key in s:return
    with q.oracle_connection() as conn:
        cur=conn.cursor()
        cur.execute("select r.UNIT_CODE,r.ORDER_QTY,o.WARE_ID,o.SOURCE_SYSTEM from RRL_CUSTOMER_ORDER_ROW r "
            "join RRL_CUSTOMER_ORDER o on o.CUSTOMER_ORDER_ID=r.CUSTOMER_ORDER_ID where r.CUSTOMER_ORDER_ROW_ID=:r",r=native['row'])
        unit,qty,ware,source=cur.fetchone()
        assert (ware,source)==(s['fixture']['warehouse_id'],'QA_TRADECASE_ONLY')
        if (unit,qty)!=('BOX',boxes):
            assert (unit,qty)==('EA',boxes*10)
            cur.execute('select count(*) from RRL_PICK_PLAN where CUSTOMER_ORDER_ID=:o',o=native['order']);assert cur.fetchone()==(0,)
            cur.execute('select count(*) from RRL_TRADE_ORDER_LINE where CUSTOMER_ORDER_ROW_ID=:r',r=native['row']);assert cur.fetchone()==(0,)
            cur.callproc('RRL_STOCK_METADATA_TX.begin_change',['admin','warehouse_settings_edit'])
            try:
                cur.execute("update RRL_CUSTOMER_ORDER_ROW set UNIT_CODE='BOX',ORDER_QTY=:b where CUSTOMER_ORDER_ROW_ID=:r and UNIT_CODE='EA' and ORDER_QTY=:q",
                    b=boxes,r=native['row'],q=boxes*10)
                assert cur.rowcount==1;conn.commit()
            finally:cur.callproc('RRL_STOCK_METADATA_TX.end_change')
    s[key]=dict(uom='BOX',quantity=boxes);q.save()


def proposals():
    assert s.get('phase') == 'MAIN_WAVE', s.get('phase')
    f = s['fixture']; base = f"/api/tradecase/warehouses/{f['warehouse_id']}"
    s['box_type'] = q.step('box.type', 'POST', '/api/case-pick/pallet-types', dict(pallet_type_code='PO27_'+f['tag'], pallet_type_name='Program independent BOX', load_unit_class='BOX', default_volume_m3='0.1', default_weight_kg='0', length_mm=500, width_mm=400, height_mm=500))['pallet_type_id']
    plate = 'PO27V'+str(f['warehouse_id'])
    vehicle = q.step('vehicle', 'POST', '/api/admin/transport/vehicles', dict(num_plat=plate, transtype_id='10', max_weight_kg=8000, max_pallets=660, sobstvennyy=True), status=201)['id']
    if 'vehicle.profile' not in s.get('steps', {}):
        profile = q.expect(200, q.http('GET', f'/api/admin/transport/vehicles/{vehicle}/profile'))
        q.step('vehicle.profile', 'POST', '/api/admin/transport/vehicle-profiles', dict(operation_id=q.tag()+'.vehicle.profile', vehicle_id=vehicle, expected_source_hash=profile['base_hash'], expected_version=profile['version'], vehicle_size_class='QA_PROGRAM', cargo_length_mm=13200, cargo_width_mm=2500, cargo_height_mm=2000, outer_height_mm=3000, outer_length_mm=14000, floor_variants=[dict(code='BOX660', limits=[dict(pallet_type_id=s['box_type'], max_places=660)])], reason='Program box-mode 66m3 vehicle', evidence_reference='TEST_NOT_HARDWARE'))
    trip = dict(vehicle_id=plate, planning_source='SAP', planned_departure_at=s['day']+'T12:00:00+03:00', capacity_kg='8000', capacity_m3='66', orders=[dict(order_id=number, line_id='1', quantity=str(o['boxes'])) for number, o in s['orders'].items()])
    q.send('trip', 'TRIP', 'T1', trip)
    now = datetime.now(timezone.utc)
    forecast=dict(recipient_id='C103', sku_id='A', recipient_version=1, sku_version=1, forecast_kind='MOVEMENT', snapshot_at=now.isoformat(), period_from=s['day']+'T00:00:00+03:00', period_until=s['day']+'T23:59:59+03:00', uom='BOX', forecast_quantity='80', target_quantity='0', available_quantity='0', received_in_available=True, supplies=[])
    q.send('need', 'NEED', 'N1', forecast)
    route = base+'/trips/T1'
    denied('disabled.preview',route+'/topup-preview',dict(need_ids=['N1'],max_age_minutes=1440),'TOPUP_RECIPIENT_DISABLED')
    recipient=dict(s['steps']['msg_recipient.103']['body']['payload']);recipient.pop('entity_type')
    recipient['topup_enabled']=True
    q.send('recipient.enabled','RECIPIENT','C103',recipient,version=2)
    denied('stale.preview',route+'/topup-preview',dict(need_ids=['N1'],max_age_minutes=1440),'NEED_MASTER_VERSION_CHANGED')
    forecast['recipient_version']=2
    q.send('need.enabled','NEED','N1',forecast,version=2)
    q.send('need.consumption','NEED','N.CONSUMPTION',dict(forecast,forecast_kind='CONSUMPTION'))
    denied('consumption.preview',route+'/topup-preview',dict(need_ids=['N.CONSUMPTION'],max_age_minutes=1440),'TOPUP_MOVEMENT_FORECAST_REQUIRED')
    end=(datetime.fromisoformat(forecast['period_from'])+timedelta(days=4)).isoformat()
    q.send('need.long','NEED','N.LONG',dict(forecast,period_until=end))
    denied('horizon.preview',route+'/topup-preview',dict(need_ids=['N.LONG'],max_age_minutes=1440),'TOPUP_RECIPIENT_HORIZON_EXCEEDED')
    preview = q.step('topup.preview', 'POST', route+'/topup-preview', dict(need_ids=['N1'], max_age_minutes=1440))
    item = preview['items'][0]
    assert (item['proposed_boxes'], item['uncovered_boxes'], item['sender_stock_boxes']) == (60, '20', 350), item
    saved = q.step('topup.save', 'POST', route+'/topup-proposals', dict(operation_id=q.tag()+'.topup.save', need_ids=['N1'], max_age_minutes=1440))
    proposal = saved['proposals'][0]
    assert proposal['approved_boxes'] == 60, proposal
    q.send('recipient.disabled.before.confirm','RECIPIENT','C103',dict(recipient,topup_enabled=False),version=3)
    denied('disabled.confirm',route+f"/topup-proposals/{proposal['proposal_id']}/confirm",dict(operation_id=q.tag()+'.disabled.confirm',expected_version=proposal['version']),'TOPUP_RECIPIENT_DISABLED')
    if 'topup.confirm' not in s['steps']:
        assert q.stock()==(11000,6000,1100), q.stock()
    q.send('recipient.reenabled','RECIPIENT','C103',recipient,version=4)
    forecast['recipient_version']=4
    q.send('need.reenabled','NEED','N1',forecast,version=3)
    saved=q.step('topup.save.current','POST',route+'/topup-proposals',dict(operation_id=q.tag()+'.topup.save.current',need_ids=['N1'],max_age_minutes=1440))
    proposal=saved['proposals'][0]
    confirmed = q.step('topup.confirm', 'POST', route+f"/topup-proposals/{proposal['proposal_id']}/confirm", dict(operation_id=q.tag()+'.topup.confirm', expected_version=proposal['version']))
    replay = q.expect(200, q.http('POST', route+f"/topup-proposals/{proposal['proposal_id']}/confirm", s['steps']['topup.confirm']['body']))
    assert replay == confirmed
    assert q.stock() == (11000, 6600, 1100), q.stock()
    s.update(proposal=confirmed, trip=trip, vehicle=vehicle, phase='TOPUP_HELD'); q.save()


def denied(key,path,body,code):
    result=q.step(key,'POST',path,body,status=409)
    assert result['detail']['code'].startswith(code),result


def topup_order():
    assert s.get('phase')=='TOPUP_HELD',s.get('phase')
    f=s['fixture'];base=f"/api/tradecase/warehouses/{f['warehouse_id']}";pid=s['proposal']['proposal_id']
    if 'held_units'not in s:
        s['held_units']=q.db('select u.PHYSICAL_UNIT_KEY,u.HARD_RESERVATION_ID from RRL_WMS_RECEIPT_UNIT u join RRL_TRADE_TOPUP_HOLD h on h.RESERVATION_ID=u.HARD_RESERVATION_ID where h.PROPOSAL_ID=:p order by u.PHYSICAL_UNIT_KEY',p=pid);q.save()
    assert len(s['held_units'])==600
    q.step('topup.sap','POST',base+f'/trips/T1/topup-proposals/{pid}/sap-reply',dict(operation_id=q.tag()+'.topup.sap',expected_version=s['proposal']['version'],source_id='TC03.SAP',event_id=q.tag()+'.sap104',outcome='ACCEPTED',sap_order_id='104'))
    q.send('topup.order','ORDER','104',dict(order_kind='TOPUP',parent_trip_id='T1',recipient_id='C103',planned_ship_at=s['day']+'T12:00:00+03:00',lines=[dict(line_id='1',sku_id='A',source_owner_id='SNS',target_owner_id='SNS',mrc='200',quantity='60',uom='BOX',min_osg_days=50)]))
    order=q.native_order('order_104',60,article=s['skus']['A']['article'],customer=s['orders']['103']['customer'],uom='BOX')
    q.step('binding.104','POST',base+'/orders/104/binding',dict(operation_id=q.tag()+'.bind.104',expected_order_version=1,customer_order_id=order['order'],lines=[dict(line_id='1',customer_order_row_id=order['row'])]))
    q.send('trip.topup','TRIP','T1',dict(s['trip'],orders=s['trip']['orders']+[dict(order_id='104',line_id='1',quantity='60')]),version=2)
    tasks=q.wave('topup104',order['order'])
    assert len(tasks)==60 and sum(t[4]for t in tasks)==600
    adopted=q.db('select u.PHYSICAL_UNIT_KEY,u.HARD_RESERVATION_ID from RRL_WMS_RECEIPT_UNIT u join RRL_TRADE_TOPUP_ADOPTION a on a.RESERVATION_ID=u.HARD_RESERVATION_ID where a.PROPOSAL_ID=:p order by u.PHYSICAL_UNIT_KEY',p=pid)
    assert [list(x)for x in adopted]==[list(x)for x in s['held_units']],'The same holds must reach picking'
    assert q.stock()==(11000,6600,1100),q.stock()
    s['orders']['104']=dict(order,customer=s['orders']['103']['customer'],sku='A',boxes=60)
    s.update(topup_wave=s['topup104_wave_id'],topup_tasks=tasks,phase='TOPUP_WAVE');q.save()


def pick():
    """Move each independent box through its own task and bind it to its original order."""
    from full_pallet_fixture import prepare_shipment
    assert s.get('phase') in ('TOPUP_WAVE', 'PICKING'), s.get('phase')
    f=s['fixture'];s['phase']='PICKING';q.save()
    tasks=q.db("select t.TASK_ID,t.UID_PALLET,t.FROM_CELL,t.TO_CELL,t.QTY,p.CUSTOMER_ORDER_ID "
        "from RRL_WAREHOUSE_TASK t join RRL_PICK_WAVE_TASK wt on wt.PICK_WAVE_TASK_ID=t.SOURCE_TASK_ID and wt.PICK_WAVE_ID=t.SOURCE_DOC_ID "
        "join RRL_PICK_TASK p on p.PICK_TASK_ID=wt.PICK_TASK_ID "
        "where t.TASK_SOURCE='WAVE' and t.SOURCE_DOC_ID in(:a,:b) and t.TASK_TYPE='PICKING_MOVE' order by t.TASK_ID",
        a=s['main_wave'],b=s['topup_wave'])
    assert len(tasks)==660 and sum(t[4] for t in tasks)==6600, (len(tasks),sum(t[4] for t in tasks))
    orders={v['order']:(k,v) for k,v in s['orders'].items()}
    for tid,pallet,src,dst,qty,native in tasks:
        number,order=orders[native];key=str(tid)
        assert qty==10
        suffix=s.get('pick_retry_suffix',{}).get(key,'')
        body=dict(operation_id=q.tag()+'.move.'+key+suffix,scanned_pallet=pallet,scanned_from_cell=src,scanned_to_cell=dst,fact_qty=str(qty))
        moved=q.step('move.'+key+suffix,'POST',f'/api/warehouse-tasks/{tid}/complete',body)
        if suffix:
            assert q.step('move.compat.replay.'+key,'POST',f'/api/warehouse-tasks/{tid}/complete',body)==moved
        if 'move_replay' not in s:
            assert q.expect(200,q.http('POST',f'/api/warehouse-tasks/{tid}/complete',body))==moved
            s['move_replay']=tid;q.save()
        ships=s.setdefault('shipments',{})
        if key not in ships:
            fixture=dict(f,article=s['skus'][order['sku']]['article'])
            st='P'+str(f['warehouse_id'])+number
            assert len(st)<=15, 'Legacy shipment document key length'
            ships[key]=dict(prepare_shipment(dict(fixture=fixture,native_order=native,shipment_identifier='PO27.ST.'+key,
                shipment_quantity=qty,st_number=st)),order_number=number,pallet=pallet,cell=dst,st_number=st)
            q.save()
        path=f'/api/warehouse-tasks/{tid}/full-pallet-shipment'
        if 'bind.ship.'+key not in s['steps']:
            current=q.expect(200,q.http('GET',path))
            q.step('bind.ship.'+key,'POST',path,dict(operation_id=q.tag()+'.ship.'+key,
                shipment_identifier=ships[key]['shipment_identifier'],scanned_pallet=current['pallet_identifier'],
                expected_stock_version=current['stock_version']))
        if len([k for k in s['steps'] if k.startswith('bind.ship.')])%25==0:
            print('Picked',sum(k.startswith('bind.ship.') for k in s['steps']),'of 660 BOX',flush=True)
    fulfillment=q.db("select f.CUSTOMER_ORDER_ID,f.STATUS,count(*),sum(f.FACT_QTY) from RRL_CUSTOMER_ORDER_FULFILLMENT f "
        "join RRL_CUSTOMER_ORDER o on o.CUSTOMER_ORDER_ID=f.CUSTOMER_ORDER_ID where o.WARE_ID=:w "
        "group by f.CUSTOMER_ORDER_ID,f.STATUS order by f.CUSTOMER_ORDER_ID",w=f['warehouse_id'])
    assert sorted(fulfillment)==sorted((o['order'],'PICKED',o['boxes'],o['boxes']*10) for o in s['orders'].values()),fulfillment
    assert q.stock()==(11000,6600,1100),q.stock()
    s.update(fulfillment=fulfillment,phase='PICKED');q.save()


def prepare_pick_retry():
    """Record a fresh logical attempt only after the known rejected task and its repaired context are read back."""
    assert s.get('phase')=='PICKING'
    f=s['fixture'];assert f['warehouse_id']==210069361
    resolved=q.db("select RRL_TRADE_RECIPIENT_VERSION(:w,'C103',1) from dual",w=f['warehouse_id'])
    assert resolved==[(4,)],resolved
    key='4109';old=s['steps']['move.'+key]
    assert 'result'not in old
    assert q.db('select STATE from RRL_STOCK_OPERATION where OPERATION_ID=:o',o=old['body']['operation_id'])==[]
    assert q.db('select STATUS,FACT_QTY from RRL_WAREHOUSE_TASK where TASK_ID=:t',t=int(key))==[('PLANNED',None)]
    suffix='.recipient.compat'
    assert s.setdefault('pick_retry_suffix',{}).get(key,suffix)==suffix
    s['pick_retry_suffix'][key]=suffix
    s['pick_retry_evidence']=dict(task_id=int(key),old_operation_id=old['body']['operation_id'],old_operation_rows=0,
        task_status='PLANNED',resolved_recipient_version=4,reason='Known rejection before effect; preserve original request and use a fresh attempt after repair')
    q.save()


def transport():
    assert s.get('phase')=='PICKED',s.get('phase')
    f=s['fixture'];base='/api/admin/transport';dock='PO27D'+str(f['warehouse_id'])
    with q.oracle_connection() as conn:
        cur=conn.cursor();cur.execute('select count(*) from RRL_TT_DOCK where DOCK=:d',d=dock)
        if cur.fetchone()==(0,):
            cur.callproc('RRL_STOCK_CONFIG_API.begin_change',['admin','warehouse_settings_edit'])
            try:
                cur.execute('insert into RRL_TT_DOCK(DOCK,WARE_ID,ORD,COUNT_OF_PALLETS,DOCK_IS_BLOCKED)values(:d,:w,1,660,0)',d=dock,w=f['warehouse_id']);conn.commit()
            finally:cur.callproc('RRL_STOCK_CONFIG_API.end_change')
    driver=q.step('transport.driver','POST',base+'/drivers',dict(name='Program QA '+f['tag'],license_number='TEST_NOT_ROAD_'+f['tag']),status=201)['id']
    task=q.step('transport.create','POST',base+'/tasks',dict(transtype='10',shipment_date=s['day']))['task_id']
    plate='PO27V'+str(f['warehouse_id'])
    q.step('transport.configure','PATCH',base+'/tasks/'+str(task),dict(transport=plate,voditel_id=driver,dock=dock,shipment_time='12:00',primechanie='Owned program BOX test, not real dispatch'))
    sts=sorted(set(x['st_number'] for x in s['shipments'].values()))
    assert len(sts)==4,sts
    q.step('transport.assign','POST',base+'/tasks/'+str(task)+'/sts',dict(st_numbers=sts))
    s.update(transport=dict(transport_task_id=task,vehicle_number=plate,vehicle_id=s['vehicle'],dock=dock,driver_id=driver),phase='TRANSPORT_READY');q.save()


def load():
    """Scan and load independent boxes using the actual BOX type and confirmed box measurements."""
    assert s.get('phase') in ('TRANSPORT_READY','LOADING'),s.get('phase')
    s['phase']='LOADING';q.save();t=s['transport'];f=s['fixture']
    physical={p['pallet']:(key,p['sku']) for key,p in s['pallets'].items()}
    for key,ship in sorted(s['shipments'].items(),key=lambda x:int(x[0])):
        ident=ship['shipment_identifier'];pallet=ship['pallet']
        if 'floor.'+key not in s['steps']:
            current=q.expect(200,q.http('GET','/api/inventory/pallet-floor-types?identifier='+pallet))
            q.step('floor.'+key,'POST','/api/inventory/pallet-floor-types',dict(operation_id=q.tag()+'.floor.'+key,
                identifier=pallet,pallet_type_id=s['box_type'],expected_version=current['version'],scan_pallet=pallet,
                scan_cell=current['cell'],evidence_reference='OWN_SYNTHETIC_BOX_NOT_HARDWARE'))
        if 'qc.'+key not in s['steps']:
            n,sku=physical[pallet]
            codes=[dict(system_code='CRPT',profile_code='TOBACCO',code=s['skus'][sku]['gtin']+f['tag'][:1]+n+str(i).zfill(2)) for i in range(1,11)]
            current=q.expect(200,q.http('GET','/api/outgoing-quality/'+ident))
            q.step('qc.'+key,'POST','/api/outgoing-quality/'+ident+'/scan',dict(operation_id=q.tag()+'.qc.'+key,
                expected_composition_signature=current['composition_signature'],error_count=0,scans=codes))
        if key not in s.setdefault('load_bodies',{}):
            current=q.expect(200,q.http('GET','/api/transport/loading/single-preview?shipment_identifier='+ident))
            s['load_bodies'][key]=dict(operation_id=q.tag()+'.load.'+key,identifier=ident,expected_version=current['expected_version'],
                expected_composition_signature=current['composition_signature'],scan_container=pallet,scan_cell=current['snapshot']['cell'],
                transport_task_id=t['transport_task_id'],scan_vehicle=t['vehicle_number'],scan_dock=t['dock'],
                measurements=dict(origin='MANUAL_CONFIRMED',content_version=current['expected_version'],gross_weight_kg='10',width_m='0.4',depth_m='0.5',height_m='0.5'))
            q.save()
        body=s['load_bodies'][key]
        result=q.step('load.'+key,'POST','/api/transport/loading/confirm-single',body)
        if 'load_replay'not in s:
            assert q.expect(200,q.http('POST','/api/transport/loading/confirm-single',body))==result
            s['load_replay']=key;q.save()
        count=sum(k.startswith('load.') for k in s['steps'])
        if count%25==0:print('Loaded',count,'of 660 BOX',flush=True)
    facts=q.db("select count(*),sum(GROSS_WEIGHT_KG),sum(BOUNDING_VOLUME_M3) from RRL_TT_HU_LOAD_FACT where TT_ID=:t and STATUS='LOADED'",t=t['transport_task_id'])
    assert facts==[(660,6600,66)],facts
    assert q.stock()==(4400,0,440),q.stock()
    s.update(load_facts=facts,phase='LOADED');q.save()


def main():
    os.environ['TRADECASE_ADMIN_USER'] = 'admin'
    os.environ.setdefault('TRADECASE_ADMIN_PASSWORD', 'admin123')
    assert s.get('phase') != 'CLOSED', 'Never reopen a closed fixture'
    try:
        setup()
        stage = sys.argv[1] if len(sys.argv)>1 else 'receive'
        original_http = q.http
        def budget_http(method, path, body=None, *args, **kwargs):
            if method == 'POST' and path.endswith(('/launch', '/release-picking')): kwargs['timeout'] = 100
            return original_http(method, path, body, *args, **kwargs)
        q.http = budget_http
        globals()[stage]()
        if s.get('error'):s.setdefault('previous_errors',[]).append(s.pop('error'));q.save()
    except Exception as error:
        s['error'] = str(error); q.save(); raise
    finally:
        q.OUT.mkdir(parents=True, exist_ok=True)
        archive = 'http-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f')+'.json'
        (q.OUT/archive).write_text(json.dumps(q.CALLS, default=str), encoding='utf-8')
        s.setdefault('http_archives', []).append(archive); q.save()
    print(json.dumps(dict(phase=s.get('phase'), warehouse=s['fixture']['warehouse_id'])))


if __name__ == '__main__':
    main()
