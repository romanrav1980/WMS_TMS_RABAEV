"""Real API/Oracle proof of tare/pick serialization on an owned ten-EA fixture."""
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import sys
from threading import Barrier

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT / 'tests/tradecase'), str(ROOT)]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
os.environ.setdefault('TRADECASE_ADMIN_USER', 'admin')
os.environ.setdefault('TRADECASE_ADMIN_PASSWORD', 'admin123')
import live_factory_case as case
from live_document_acceptance import http, expect, CALLS
from tools.mcp.tms_mcp_server import oracle_connection

OUT = ROOT / 'runtime/test-evidence/tradecase/2026-10-22/T11'
FILE = OUT / 'manual-tare-pick-race.json'
old = json.loads((ROOT / 'runtime/test-evidence/tradecase/2026-10-21/T06/factory-case.json').read_text())
case.OUT, case.FILE = OUT, FILE
case.w = 219023232
case.base = f'/api/tradecase/warehouses/{case.w}'
case.tag = 'MTP22.219023232'
case.s = json.loads(FILE.read_text()) if FILE.exists() else dict(
    warehouse_id=case.w, article=old['article'], pick=old['pick'], face=old['face'],
    cpt_policy=old['cpt_policy'], pallet_type_id=33, history=[], checks=[])
s = case.s


def query(sql, **binds):
    with oracle_connection() as conn:
        cur = conn.cursor()
        cur.execute(sql, binds)
        return [tuple(value.read() if hasattr(value, 'read') else value for value in row) for row in cur.fetchall()]


def prepare():
    case.verify_fixture()
    if 'before' not in s:
        s['before'] = query('select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE) from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w', w=case.w)
        assert s['before'] == [(10, 0)], s['before']
        s['slow_marker'] = query('select nvl(max(LOG_ID),0) from RRL_SQL_SLOW_LOG')[0][0]
        case.save()
    case.prepare()
    base = f"/api/case-pick/tasks/{s['case']}"
    if 'type_body' not in s:
        current = expect(200, http('GET', base + '/pallet-type'))
        assert current['can_change_empty_type']
        s['type_body'] = dict(operation_id=case.tag + '.type', pallet_type_id=33,
            expected_version=current['version'], scan_container=current['sscc'], reason='Isolated tare and pick serialization proof')
        case.save()
    case.step('type_set', base + '/pallet-type', s['type_body'])
    settings_path = f'/api/receiving/warehouses/{case.w}/settings'
    if 'settings_for_label' not in s:
        settings = expect(200, http('GET', settings_path))
        fields = ['company_prefix','extension_digit','coordinate_unit_m','reachtruck_mps','lift_mps',
                  'placement_metric','hu_cell_height_unit','outgoing_qc_mode','outgoing_qc_independent','outgoing_qc_sample_percent','defer_wait_cell']
        s['settings_before'] = {key:settings[key] for key in fields if key in settings}
        case.save()
        # Synthetic prefix is restricted to this isolated QA warehouse, then restored.
        case.step('settings_for_label', settings_path, dict(s['settings_before'],company_prefix='09999999',extension_digit=0), 'PUT')
    if 'tare_count' not in s:
        balances = expect(200, http('GET', f'/api/inventory/tare/warehouses/{case.w}/balances'))
        balance = next((b for b in balances if b['pallet_type_id'] == 33 and b['custodian_kind'] == 'WAREHOUSE' and b['condition_code'] == 'GOOD'), None)
        s['tare_before'] = int(balance['quantity']) if balance else 0
        case.save()
        case.step('tare_count', '/api/inventory/tare/count', dict(operation_id=case.tag+'.tare.count',
            owner_ware_id=case.w, pallet_type_id=33, condition='GOOD', observed_quantity=str(s['tare_before']+1),
            expected_version=balance['balance_version'] if balance else 0,
            reason='Additional synthetic empty carton for isolated proof', decision_reference='TEST_NOT_HARDWARE:'+case.tag))
    actor, password, base, resource, session = case.start()
    if 'label_body' not in s:
        sscc, version = query('select SSCC,CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t', t=s['case'])[0]
        s['label_body'] = dict(operation_id=case.tag+'.label', scan_container=sscc, expected_content_version=version)
        case.save()
    label = case.step('label', base+'/sscc-label', s['label_body'], actor=actor, password=password)
    case.step('label_confirmed', base+'/sscc-label/confirm', dict(scan=label['sscc']), actor=actor, password=password)
    path = f"/api/inventory/warehouse-scales/tasks/{s['case']}/manual-empty-tare"
    if 'tare_body' not in s:
        s['tare_body'] = dict(operation_id=case.tag+'.tare.first', expected_content_version=label['content_version'],
            scan_container=label['sscc'], tare_weight_kg='0.1', measurement_ref='SYNTHETIC_NOT_HARDWARE:'+case.tag)
        case.save()
    case.step('tare_first', path, s['tare_body'], actor=actor, password=password)
    return actor, password, base, resource, session, path


def run():
    actor, password, base, resource, session, path = prepare()
    if 'pick_body' not in s:
        scans = query("select c.SYSTEM_CODE,c.RAW_CODE from RRL_WMS_RECEIPT_UNIT u join RRL_WMS_RECEIPT_CODE c on c.UID_PALLET=u.UID_PALLET and c.UNIT_ID=u.UNIT_ID join RRL_STOCK_RESERVATION r on r.RESERVATION_ID=u.HARD_RESERVATION_ID where r.SOURCE_DOC_TYPE='PICK_WAVE' and r.SOURCE_LINE_ID=:p and r.STATUS in('ACTIVE','ALLOCATED','PICKING') order by u.UNIT_ID", p=s['pick_task'])
        scans = [dict(system_code=system, profile_code='TOBACCO', code=raw.read() if hasattr(raw,'read') else raw) for system, raw in scans]
        assert len(scans) == 2
        s['pick_body'] = dict(operation_id=case.tag+'.pick', fact_qty='2', scan_cell=s['pick'], scan_product=s['article'],
            scan_container=s['label']['sscc'], resource_id=resource, resource_session_id=session, unit_scans=scans)
        s['remeasure_body'] = dict(s['tare_body'], operation_id=case.tag+'.tare.race', tare_weight_kg='0.2')
        case.save()
    if 'race' not in s:
        barrier = Barrier(2)
        def request(item):
            barrier.wait(timeout=10)
            return http('POST', item[0], item[1], actor, password)
        with ThreadPoolExecutor(max_workers=2) as pool:
            replies = list(pool.map(request, [(base+f"/lines/{s['line']}/confirm",s['pick_body']), (path,s['remeasure_body'])]))
        s['race'] = replies
        case.save()
    picked, measured = s['race']
    s['picked'] = expect(200, picked)
    assert measured[0] in (200,409), measured
    current = expect(200, http('GET',base+'/sscc-label',actor=actor,password=password))
    expected_tare = '0.2' if measured[0] == 200 else '0.1'
    assert current['manual_empty_tare']['tare_weight_kg'] == expected_tare, current
    s['effective_tare'] = expected_tare
    assert expect(200,http('POST',base+f"/lines/{s['line']}/confirm",s['pick_body'],actor,password)) == s['picked']
    denied = expect(409,http('POST',path,dict(s['tare_body'],operation_id=case.tag+'.tare.after.pick'),actor,password))
    s['checks'].append(dict(test='pick and remeasure serialize; filled carton rejects new measurement',race=s['race'],after_pick=denied))
    case.save()
    # Close under the same warehouse actor. The final QC is a separate authorized control.
    if 'close_body' not in s:
        s['close_body'] = dict(operation_id=case.tag+'.close',expected_content_version=query('select CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t',t=s['case'])[0][0])
        case.save()
    case.step('closed',base+'/close-current',s['close_body'],actor=actor,password=password)
    # Final QC needs an existing shipment binding. Use the owned waiting carton
    # only for rejected commands; do not bind or change its route/composition.
    qc = '/api/outgoing-quality/099999990000026027'
    protected_before=query('select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE) from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=220793322')
    assert protected_before == [(7,5)], protected_before
    quality = expect(200,http('GET',qc))
    assert quality['case_task_id']==1169 and quality['ready'] is True, quality
    s['qc_before']=quality
    wrong = dict(operation_id=case.tag+'.qc.wrong.tare', expected_composition_signature=quality['composition_signature'],
        quality_kind='WEIGHT', gross_weight='1.3', wood_weight='0.3', measurement_origin='MANUAL_CONFIRMED')
    response = expect(409,http('POST',qc+'/weight',wrong))
    assert 'QC_MANUAL_TARE_MISMATCH' in str(response), response
    assert query("select count(*) from RRL_STOCK_OPERATION where OPERATION_ID=:o and STATE='APPLIED'",o=wrong['operation_id']) == [(0,)]
    s['checks'].append(dict(test='mismatched final tare rejected without applied command',response=response))
    invalid=dict(wrong,operation_id=case.tag+'.qc.gross.below.tare',gross_weight='0.1')
    rejected=expect(409,http('POST',qc+'/weight',invalid))
    assert 'QC_MANUAL_GROSS_TARE_INVALID' in str(rejected),rejected
    assert query("select count(*) from RRL_STOCK_OPERATION where OPERATION_ID=:o and STATE='APPLIED'",o=invalid['operation_id']) == [(0,)]
    assert expect(200,http('GET',qc))==quality
    assert query('select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE) from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=220793322') == protected_before
    s['checks'].append(dict(test='gross below tare rejected; prior QC/route/quantity unchanged',response=rejected))
    case.save()
    # Existing normal return restores the original quantity; it also retires the own actor.
    case.execute(return_after=True)
    case.step('book_released','/api/inventory/tare/book-cancel',dict(operation_id=case.tag+'.book.cancel',booking_operation_id=s['tare_book']['operation_id']))
    if 'tare_restored' not in s:
        balances=expect(200,http('GET',f'/api/inventory/tare/warehouses/{case.w}/balances'))
        balance=next(b for b in balances if b['pallet_type_id']==33 and b['custodian_kind']=='WAREHOUSE' and b['condition_code']=='GOOD')
        case.step('tare_restored','/api/inventory/tare/count',dict(operation_id=case.tag+'.tare.restore',owner_ware_id=case.w,
            pallet_type_id=33,condition='GOOD',observed_quantity=str(s['tare_before']),expected_version=balance['balance_version'],
            reason='Restore synthetic carton count after test',decision_reference='TEST_FIXTURE_RESTORE:'+case.tag))
    s['slow_sql']=query('select LOG_ID,ELAPSED_MS,OPERATION_KIND from RRL_SQL_SLOW_LOG where LOG_ID>:n order by LOG_ID fetch first 30 rows only',n=s['slow_marker'])
    case.step('settings_restored',f'/api/receiving/warehouses/{case.w}/settings',s['settings_before'],'PUT')
    case.step('wave_finished',f"/api/picking/waves/{s['wave']}/finish-execution",dict(operation_id=case.tag+'.wave.finish',
        disposition='RETURNED_TO_PLANNING',reason='Return isolated tare proof goods and preserve original demand'))
    if 'error' in s:
        s.setdefault('prior_attempt_errors',[]).append(s.pop('error'))
    s['status']='PASS'
    case.save()


if __name__ == '__main__':
    if s.get('status')=='PASS' and 'wave_finished' in s:
        print(json.dumps(dict(status='PASS',cached_evidence=str(FILE))))
        raise SystemExit(0)
    try:
        run()
    except Exception as exc:
        s['status']='FAIL'
        s['error']=str(exc)
        raise
    finally:
        s['history'] += CALLS
        case.save()
    print(json.dumps(dict(status=s['status'],case_id=s['case'],checks=len(s['checks']),evidence=str(FILE))))
