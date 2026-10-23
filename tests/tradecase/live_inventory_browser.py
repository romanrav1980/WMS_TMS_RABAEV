"""One owned physical count through the served UI, then native restoration and cleanup."""
import json
import sys
from uuid import uuid4
import live_inventory_loss_found as case

qa=case.qa
qa.FILE=qa.OUT/'inventory-browser-live.json'
qa.s=json.loads(qa.FILE.read_text(encoding='utf-8'))if qa.FILE.exists()else dict(tag='IB23.'+uuid4().hex[:9],requests={},results={})
s=qa.s;case.s=s;case.equal.s=s


def prepare():
    case.prepare()
    with qa.oracle_connection()as conn:
        cur=conn.cursor()
        cur.execute("insert into RIGHTS(USER_GROUP,RIGHT1)select :a,'wms_admin_login'from dual where not exists(select 1 from RIGHTS where USER_GROUP=:a and RIGHT1='wms_admin_login')",a=s['actor'])
        conn.commit()
    s['browser_codes']=qa.query('''select u.PHYSICAL_UNIT_KEY,c.RAW_CODE from RRL_WMS_RECEIPT_UNIT u
        join RRL_WMS_RECEIPT_CODE c on c.UID_PALLET=u.UID_PALLET and c.UNIT_ID=u.UNIT_ID
        where u.CURRENT_UID=:p_uid order by u.PHYSICAL_UNIT_KEY''',p_uid=s['selected_lot']['uid'])
    assert len(s['browser_codes'])==20
    s['stage']='READY_FOR_REAL_BROWSER';qa.save()


def finish():
    report=json.loads((qa.OUT/'inventory-browser-ui.json').read_text(encoding='utf-8'))
    assert report['status']=='PASS' and len(report['posts'])==3
    body=report['posts'][0]
    assert report['posts']==[body,body,body]and body['revision_id']==s['revision']
    assert qa.stock()==[(249,0)]
    assert qa.query("select count(*)from RRL_STOCK_OPERATION where OPERATION_ID=:o and STATE='APPLIED'",o=body['operation_id'])==[(1,)]
    changed=qa.step('changed_original',case.equal.PATH+'/counts',dict(body,reason='Changed original browser count'),qa=True,status=409)
    assert 'OPERATION_CONTENT_CONFLICT'in json.dumps(changed)
    case.count('browser_found',set(s['selected_lot']['unit_keys']))
    assert qa.stock()==[(250,0)]
    attrs=qa.query('''select a.PHYSICAL_UNIT_KEY,a.OWNER_ID,a.SKU_ID,a.MRC,a.EXPIRY_DATE,
        u.CURRENT_UID,u.CURRENT_CELL,u.STOCK_STATUS,u.BASE_QTY,u.UNIT_VERSION
        from RRL_TRADE_STOCK_ATTR a join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=a.PHYSICAL_UNIT_KEY
        where a.CAPTURE_WARE_ID=:w order by a.PHYSICAL_UNIT_KEY''',w=qa.W)
    norm=lambda rows:json.loads(json.dumps([r[:-1]for r in rows],default=str))
    assert norm(attrs)==norm(s['baseline_attributes'])
    baseline={r[0]:r[-1]for r in s['baseline_attributes']}
    assert all(r[-1]==baseline[r[0]]+(2 if r[0]==s['selected_key']else 0)for r in attrs)
    version=qa.query('select VERSION_NO from RRL_TRADE_OWNER_GRANT where WARE_ID=:w and USERNAME=:a and OWNER_ID=\'SNS\'',w=qa.W,a=s['actor'])[0][0]
    qa.step('retire_owner',qa.BASE+'/stock/owner-grants',dict(operation_id=s['tag']+'.owner.retire',expected_version=version,
        username=s['actor'],owner_id='SNS',can_view=False,can_operate=False,reason='Finish physical browser count recovery'),method='PUT')
    with qa.oracle_connection()as conn:
        cur=conn.cursor();result=cur.var(int)
        cur.execute('begin :v:=REVIZION.close_revision(:r);end;',v=result,r=s['revision']);assert result.getvalue()==1
        cur.execute('update RUSERS set DELETED=1 where ID=:a',a=s['actor'])
        cur.execute('delete from RIGHTS where USER_GROUP=:a',a=s['actor']);conn.commit()
    assert qa.query("select count(*)from USER_OBJECTS where STATUS='INVALID'")==[(0,)]
    s.update(status='PASS',stage='CLOSED',browser_operation=body['operation_id'],attributes_preserved=250)
    s['slow_sql']=qa.query('''select LOG_ID,ELAPSED_MS,API_PATH from RRL_SQL_SLOW_LOG
        where LOG_ID>:m and API_PATH like '/api/inventory/%' order by ELAPSED_MS desc fetch first 20 rows only''',m=s['slow_marker'])
    qa.save();print(json.dumps(dict(status=s['status'],revision=s['revision'],quantity=250)))


if __name__=='__main__':
    s['previous_calls']=s.get('calls',[])
    try:
        if s.get('status')=='PASS':print('Closed; no commands sent')
        elif sys.argv[1:]==['--prepare']:
            assert s.get('stage')!='READY_FOR_REAL_BROWSER','Already prepared'
            prepare()
        elif sys.argv[1:]==['--finish']:finish()
        else:raise ValueError('Choose --prepare or --finish')
    except Exception as exc:s['error']=str(exc);qa.save();raise
