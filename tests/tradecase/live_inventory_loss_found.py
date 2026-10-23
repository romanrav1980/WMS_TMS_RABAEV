"""Prepare an owned revision for live loss/found acceptance; no count until native release."""
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlencode
from uuid import uuid4
import live_inventory_equal_count as equal

qa = equal.qa
qa.FILE = qa.OUT / 'inventory-loss-found-live.json'
qa.s = json.loads(qa.FILE.read_text(encoding='utf-8')) if qa.FILE.exists() else dict(
    tag='IF23.' + uuid4().hex[:9], requests={}, results={})
s = qa.s
equal.s = s


def prepare():
    assert not s.get('status'), 'Do not reopen a closed revision or reactivate its actor'
    equal.prepare()
    assert qa.stock() == [(250, 0)]
    s['baseline_attributes'] = qa.query('''select a.PHYSICAL_UNIT_KEY,a.OWNER_ID,a.SKU_ID,a.MRC,a.EXPIRY_DATE,
        u.CURRENT_UID,u.CURRENT_CELL,u.STOCK_STATUS,u.BASE_QTY,u.UNIT_VERSION
        from RRL_TRADE_STOCK_ATTR a join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=a.PHYSICAL_UNIT_KEY
        where a.CAPTURE_WARE_ID=:w order by a.PHYSICAL_UNIT_KEY''', w=qa.W)
    assert len(s['baseline_attributes']) == 250
    s['baseline_code_hashes'] = qa.query('''select c.SYSTEM_CODE,c.CODE_HASH,u.PHYSICAL_UNIT_KEY
        from RRL_WMS_RECEIPT_CODE c join RRL_WMS_RECEIPT_UNIT u on u.UID_PALLET=c.UID_PALLET and u.UNIT_ID=c.UNIT_ID
        join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY
        where a.CAPTURE_WARE_ID=:w order by u.PHYSICAL_UNIT_KEY,c.SYSTEM_CODE,c.CODE_HASH''', w=qa.W)
    assert len(s['baseline_code_hashes']) == 250
    lots = [x for x in s['body']['counts'] if x['quantity'] == '20']
    assert len(lots) == 2
    s['selected_lot'] = lots[0]
    s['selected_key'] = lots[0]['unit_keys'][0]
    s['planned_checks'] = [
        'Raw scans of present units: one missing code, exact replay and changed body conflict',
        'Same physical code found: original key, owner/MRC/expiry/code identity preserved',
        'Lose/find the same unit again: distinct loss occurrence, one restoration each',
        'Entire 20-unit lot lost: current owner operate denial even when remaining quantity is zero',
        'Restoration cannot create a duplicate unit or recover a shipped/no-loss code',
        'Restore baseline250/H0, close revision and retire actor/rights/grants',
    ]
    s['stage'] = 'PREPARED_NO_COUNT_WAITING_NATIVE_RELEASE'
    qa.save()
    print(json.dumps(dict(stage=s['stage'],revision=s['revision'],warehouse=qa.W,quantity=250)))


def baseline_denials():
    assert s.get('stage') == 'PREPARED_NO_COUNT_WAITING_NATIVE_RELEASE'
    if 'uncaptured_positive_body' not in s:
        row = dict(s['selected_lot'], quantity='21')
        s['uncaptured_positive_body'] = dict(operation_id=s['tag'] + '.uncaptured.positive',
            revision_id=s['revision'], reason='Reject uncaptured marked inventory increase', counts=[row])
        qa.save()
    value = qa.step('uncaptured_positive', equal.PATH + '/counts', s['uncaptured_positive_body'], qa=True, status=409)
    assert 'MARKED_INVENTORY_INCREASE_REQUIRES_CAPTURED_UNITS' in json.dumps(value), value
    assert qa.stock() == [(250, 0)]
    current = qa.query('''select a.PHYSICAL_UNIT_KEY,a.OWNER_ID,a.SKU_ID,a.MRC,a.EXPIRY_DATE,
        u.CURRENT_UID,u.CURRENT_CELL,u.STOCK_STATUS,u.BASE_QTY,u.UNIT_VERSION
        from RRL_TRADE_STOCK_ATTR a join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=a.PHYSICAL_UNIT_KEY
        where a.CAPTURE_WARE_ID=:w order by a.PHYSICAL_UNIT_KEY''', w=qa.W)
    # Saved JSON stringifies dates; normalize before comparing the native baseline.
    assert json.loads(json.dumps(current, default=str)) == json.loads(json.dumps(s['baseline_attributes'], default=str))
    assert qa.query("select count(*)from USER_OBJECTS where STATUS='INVALID'") == [(0,)]
    s['baseline_denial_verified'] = True
    qa.save()
    print('PASS uncaptured positive rejected;250/H0 and all unit attributes/versions unchanged')


def observed(key, present):
    if key not in s['requests']:
        lot=s['selected_lot']
        rows=qa.expect(200,qa.http('GET',equal.PATH+'/'+str(s['revision'])+'/lots?'+urlencode(dict(cell=lot['cell'])),
                                  actor=s['actor'],password=s['password']))['lots']
        current=next(r for r in rows if r['uid']==lot['uid'])
        codes=qa.query('''select u.PHYSICAL_UNIT_KEY,c.SYSTEM_CODE,c.RAW_CODE
            from RRL_WMS_RECEIPT_UNIT u join RRL_WMS_RECEIPT_CODE c on c.UID_PALLET=u.UID_PALLET and c.UNIT_ID=u.UNIT_ID
            where u.CURRENT_UID=:p_uid order by u.PHYSICAL_UNIT_KEY''',p_uid=lot['uid'])
        assert len(codes)==20 and len({r[0]for r in codes})==20
        scans=[dict(system_code=system,profile_code='TOBACCO',code=raw)for unit,system,raw in codes if unit in present]
        assert len(scans)==len(present)
        row={k:current[k]for k in ['uid','cell','article','unit']}
        row.update(quantity=str(len(present)),expected_stock_version=current['stock_version'],scans=scans)
        body=dict(operation_id=s['tag']+'.'+key,revision_id=s['revision'],reason='Own physical loss/found acceptance',counts=[row])
        s['requests'][key]=dict(path=equal.PATH+'/counts',body=body,method='POST',status=200,qa=True)
        qa.save()
    return s['requests'][key]['body']


def count(key,present):
    body=observed(key,present)
    return qa.step(key,equal.PATH+'/counts',body,qa=True)


def owner(key,version,operate):
    return qa.step(key,qa.BASE+'/stock/owner-grants',dict(operation_id=s['tag']+'.'+key,expected_version=version,
        username=s['actor'],owner_id='SNS',can_view=True,can_operate=operate,reason='Current inventory restoration authority'),method='PUT')


def execute():
    assert qa.query("select STATUS from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-23-inventory-found-units'")==[('APPLIED',)], 'Apply/review/empty rollback proof must precede any loss'
    assert s.get('baseline_denial_verified') and not s.get('status')
    all_keys=set(s['selected_lot']['unit_keys']); present=all_keys-{s['selected_key']}
    count('loss_one',present)
    assert qa.step('loss_one_replay',equal.PATH+'/counts',s['requests']['loss_one']['body'],qa=True)['operation_id']==s['requests']['loss_one']['body']['operation_id']
    if 'restore_race' not in s:
        body=observed('restore_one',all_keys)
        bodies=[body,dict(body,operation_id=body['operation_id']+'.racer')]
        s['restore_race_bodies']=bodies;qa.save()
        with ThreadPoolExecutor(max_workers=2)as pool:
            replies=list(pool.map(lambda b:qa.http('POST',equal.PATH+'/counts',b,s['actor'],s['password']),bodies))
        s['restore_race']=replies;qa.save()
    assert sorted(r[0]for r in s['restore_race'])==[200,409],s['restore_race']
    winner=next(i for i,r in enumerate(s['restore_race'])if r[0]==200)
    qa.step('restore_one_replay',equal.PATH+'/counts',s['restore_race_bodies'][winner],qa=True)
    count('loss_again',present);count('found_again',all_keys)
    count('whole_lot_lost',set())
    if 'whole_lot_at_zero' not in s:
        assert qa.stock()==[(230,0)]
        s['whole_lot_at_zero']=True;qa.save()
    restored_body=observed('whole_lot_found',all_keys)
    owner('owner_view_only',1,False)
    if 'revoked_loss_replay' not in s:
        s['revoked_loss_replay']=qa.http('POST',equal.PATH+'/counts',s['requests']['whole_lot_lost']['body'],s['actor'],s['password']);qa.save()
    qa.step('zero_owner_restore_denied',equal.PATH+'/counts',restored_body,qa=True,status=403)
    owner('owner_operate_restore',2,True)
    qa.step('whole_lot_found',equal.PATH+'/counts',restored_body,qa=True)
    qa.step('whole_lot_found_replay',equal.PATH+'/counts',restored_body,qa=True)
    assert qa.stock()==[(250,0)]
    current=qa.query('''select a.PHYSICAL_UNIT_KEY,a.OWNER_ID,a.SKU_ID,a.MRC,a.EXPIRY_DATE,
        u.CURRENT_UID,u.CURRENT_CELL,u.STOCK_STATUS,u.BASE_QTY,u.UNIT_VERSION
        from RRL_TRADE_STOCK_ATTR a join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=a.PHYSICAL_UNIT_KEY
        where a.CAPTURE_WARE_ID=:w order by a.PHYSICAL_UNIT_KEY''',w=qa.W)
    normalize=lambda rows:json.loads(json.dumps([r[:-1]for r in rows],default=str))
    assert normalize(current)==normalize(s['baseline_attributes'])
    s['unit_versions_after']=current
    s['loss_history']=qa.query('''select l.PHYSICAL_UNIT_KEY,l.LOSS_OPERATION_ID,f.FOUND_OPERATION_ID
        from RRL_INVENTORY_LOSS_UNIT l left join RRL_INVENTORY_FOUND_UNIT f
        on f.PHYSICAL_UNIT_KEY=l.PHYSICAL_UNIT_KEY and f.LOSS_OPERATION_ID=l.LOSS_OPERATION_ID
        where l.REVISION_ID=:r order by l.PHYSICAL_UNIT_KEY,l.LOSS_OPERATION_ID''',r=s['revision'])
    assert len(s['loss_history'])==22 and all(r[2]for r in s['loss_history'])
    assert len([r for r in s['loss_history']if r[0]==s['selected_key']])==3
    assert qa.query("select count(*)from USER_OBJECTS where STATUS='INVALID'")==[(0,)]
    s['stage']='PHYSICAL_RESTORED_PENDING_SHIPPED_NEGATIVE_AND_CLEANUP'
    qa.save()
    print(json.dumps(dict(stage=s['stage'],cached_loss_replay_status=s['revoked_loss_replay'][0],quantity=250)))


def shipped_denial(key):
    """A new metadata revision cannot turn the retained shipped stock into a find."""
    w=222385707;uid='690000000707411744'
    assert qa.query('select NAME from RRL_WARES where ID=:w',w=w)==[('TRADECASE QA bcfdabb6',)]
    before=qa.query('''select PHYSICAL_UNIT_KEY,CURRENT_UID,CURRENT_CELL,STOCK_STATUS,UNIT_VERSION
        from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:p_uid order by PHYSICAL_UNIT_KEY''',p_uid=uid)
    assert len(before)==10 and all(r[3]=='ISSUED'for r in before)
    if key not in s:
        s[key]=dict(revision=qa.expect(200,qa.http('POST',equal.PATH+'/revisions',dict(warehouse_id=w)))['revision_id'])
        qa.save()
    entry=s[key]
    assert not entry.get('closed'), 'Never replay a closed revision as physical validation'
    try:
        cell=before[0][2];assert all(r[2]==cell for r in before)
        stock=qa.query('select REMAIN,HARD_RESERVED_BASE,STOCK_VERSION from RRL_REMAINS where UID_POLETA=:p_uid and CELL=:c',p_uid=uid,c=cell)
        assert len(stock)==1 and stock[0][:2]==(0,0)
        article=qa.query('select ARTICUL from RRL_PALLETS where UID_PALLET=:p_uid',p_uid=uid)[0][0]
        codes=qa.query('''select c.SYSTEM_CODE,c.RAW_CODE from RRL_WMS_RECEIPT_UNIT u
            join RRL_WMS_RECEIPT_CODE c on c.UID_PALLET=u.UID_PALLET and c.UNIT_ID=u.UNIT_ID
            where u.CURRENT_UID=:p_uid order by u.PHYSICAL_UNIT_KEY''',p_uid=uid)
        assert len(codes)==10
        body=dict(operation_id=s['tag']+'.'+key,revision_id=entry['revision'],reason='Do not restore shipped stock as inventory found',
            counts=[dict(uid=uid,cell=cell,article=article,unit='EA',quantity='10',expected_stock_version=stock[0][2],
                         scans=[dict(system_code=system,profile_code='TOBACCO',code=raw)for system,raw in codes])])
        entry['result']=qa.http('POST',equal.PATH+'/counts',body);qa.save()
        assert entry['result'][0]==422,entry['result']
        assert qa.query('''select PHYSICAL_UNIT_KEY,CURRENT_UID,CURRENT_CELL,STOCK_STATUS,UNIT_VERSION
            from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:p_uid order by PHYSICAL_UNIT_KEY''',p_uid=uid)==before
        assert qa.query("select count(*)from RRL_STOCK_OPERATION where OPERATION_ID=:o and STATE='APPLIED'",o=body['operation_id'])==[(0,)]
        entry['status']='PASS_NO_RESTORATION'
    finally:
        with qa.oracle_connection()as conn:
            cur=conn.cursor();result=cur.var(int)
            cur.execute('begin :v:=REVIZION.close_revision(:r);end;',v=result,r=entry['revision'])
            assert result.getvalue()==1;conn.commit()
        entry['closed']=True;qa.save()
    print(json.dumps(dict(test=key,status=entry['status'],revision_closed=entry['revision'])))


def guard_acceptance():
    assert qa.query("select STATUS from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-23-inventory-current-owner'")==[('APPLIED',)]
    assert s['stage']=='PHYSICAL_RESTORED_PENDING_SHIPPED_NEGATIVE_AND_CLEANUP'
    all_keys=set(s['selected_lot']['unit_keys'])
    count('guard_loss',set())
    body=observed('guard_found',all_keys)
    owner('guard_view_only',3,False)
    qa.step('guard_denied_loss_replay',equal.PATH+'/counts',s['requests']['guard_loss']['body'],qa=True,status=403)
    qa.step('guard_denied_found',equal.PATH+'/counts',body,qa=True,status=403)
    owner('guard_operate_restored',4,True)
    qa.step('guard_found',equal.PATH+'/counts',body,qa=True)
    qa.step('guard_found_replay',equal.PATH+'/counts',body,qa=True)
    assert qa.stock()==[(250,0)]
    s['cached_owner_guard_verified']=True
    qa.save()
    shipped_denial('shipped_after_apply')
    if 'uncaptured_after_body'not in s:
        observed('uncaptured_after',all_keys)
        row=dict(s['requests']['uncaptured_after']['body']['counts'][0],quantity='21',unit_keys=sorted(all_keys))
        row.pop('scans')
        s['uncaptured_after_body']=dict(operation_id=s['tag']+'.uncaptured.after',revision_id=s['revision'],
            reason='Preserve rejection of uncaptured marked increase after apply',counts=[row]);qa.save()
    denied=qa.step('uncaptured_after_denied',equal.PATH+'/counts',s['uncaptured_after_body'],qa=True,status=409)
    assert 'MARKED_INVENTORY_INCREASE_REQUIRES_CAPTURED_UNITS'in json.dumps(denied)
    assert qa.stock()==[(250,0)]
    s['stage']='ALL_QUANTITIES_RESTORED_PENDING_CLEANUP'
    qa.save()
    print(s['stage'])


def cleanup():
    assert s['stage']=='ALL_QUANTITIES_RESTORED_PENDING_CLEANUP'
    assert qa.stock()==[(250,0)]
    current=qa.query('''select a.PHYSICAL_UNIT_KEY,a.OWNER_ID,a.SKU_ID,a.MRC,a.EXPIRY_DATE,
        u.CURRENT_UID,u.CURRENT_CELL,u.STOCK_STATUS,u.BASE_QTY,u.UNIT_VERSION
        from RRL_TRADE_STOCK_ATTR a join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=a.PHYSICAL_UNIT_KEY
        where a.CAPTURE_WARE_ID=:w order by a.PHYSICAL_UNIT_KEY''',w=qa.W)
    normalize=lambda rows:json.loads(json.dumps([r[:-1]for r in rows],default=str))
    assert normalize(current)==normalize(s['baseline_attributes'])
    s['unit_versions_after']=current
    qa.step('final_owner_retire',qa.BASE+'/stock/owner-grants',dict(operation_id=s['tag']+'.owner.retire',expected_version=5,
        username=s['actor'],owner_id='SNS',can_view=False,can_operate=False,reason='Finish owned inventory loss/found acceptance'),method='PUT')
    with qa.oracle_connection()as conn:
        cur=conn.cursor();result=cur.var(int)
        cur.execute('select USER_ID,WARE_ID,CONDITION from RRL_REVIZION where ID=:r',r=s['revision'])
        actor,ware,condition=cur.fetchone();assert (actor,ware)==(s['actor'],qa.W)
        if condition!=2:
            cur.execute('begin :v:=REVIZION.close_revision(:r);end;',v=result,r=s['revision'])
            assert result.getvalue()==1
        cur.execute('update RUSERS set DELETED=1 where ID=:a',a=s['actor'])
        cur.execute('delete from RIGHTS where USER_GROUP=:a',a=s['actor']);conn.commit()
    s['loss_history']=qa.query('''select l.PHYSICAL_UNIT_KEY,l.LOSS_OPERATION_ID,f.FOUND_OPERATION_ID
        from RRL_INVENTORY_LOSS_UNIT l left join RRL_INVENTORY_FOUND_UNIT f
        on f.PHYSICAL_UNIT_KEY=l.PHYSICAL_UNIT_KEY and f.LOSS_OPERATION_ID=l.LOSS_OPERATION_ID
        where l.REVISION_ID=:r order by l.PHYSICAL_UNIT_KEY,l.LOSS_OPERATION_ID''',r=s['revision'])
    assert len(s['loss_history'])==42 and all(r[2]for r in s['loss_history'])
    from collections import Counter
    occurrences=Counter(r[0]for r in s['loss_history'])
    baseline_versions={r[0]:r[-1]for r in s['baseline_attributes']}
    assert all(r[-1]==baseline_versions[r[0]]+2*occurrences[r[0]]for r in current)
    codes=qa.query('''select c.SYSTEM_CODE,c.CODE_HASH,u.PHYSICAL_UNIT_KEY
        from RRL_WMS_RECEIPT_CODE c join RRL_WMS_RECEIPT_UNIT u on u.UID_PALLET=c.UID_PALLET and c.UNIT_ID=u.UNIT_ID
        join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY
        where a.CAPTURE_WARE_ID=:w order by u.PHYSICAL_UNIT_KEY,c.SYSTEM_CODE,c.CODE_HASH''',w=qa.W)
    assert [list(r)for r in codes]==s['baseline_code_hashes']
    assert qa.query("select count(*)from USER_OBJECTS where STATUS='INVALID'")==[(0,)]
    s['slow_sql']=qa.query('''select LOG_ID,ELAPSED_MS,API_PATH from RRL_SQL_SLOW_LOG
        where LOG_ID>:m and API_PATH like '/api/inventory/%' order by ELAPSED_MS desc fetch first 20 rows only''',m=s['slow_marker'])
    s['status']='PASS';s['stage']='CLOSED';s.pop('error',None);qa.save()
    print(json.dumps(dict(status=s['status'],revision=s['revision'],quantity=250,closed_loss_occurrences=42)))


if __name__ == '__main__':
    s['previous_calls'] = s.get('calls', [])
    assert sys.argv[1:] in [['--prepare'], ['--baseline'], ['--execute'], ['--shipped-baseline'], ['--guard'], ['--cleanup']]
    try:
        if s.get('status')=='PASS':
            print('Closed; no commands sent')
        elif '--guard' in sys.argv:
            guard_acceptance()
        elif '--cleanup' in sys.argv:
            cleanup()
        elif '--shipped-baseline' in sys.argv:
            shipped_denial('shipped_before_apply')
        elif '--execute' in sys.argv:
            execute()
        elif '--baseline' in sys.argv:
            baseline_denials()
        elif s.get('stage') == 'PREPARED_NO_COUNT_WAITING_NATIVE_RELEASE':
            print('Already prepared; no commands sent')
        else:
            prepare()
    except Exception as exc:
        s['error'] = str(exc); qa.save(); raise
