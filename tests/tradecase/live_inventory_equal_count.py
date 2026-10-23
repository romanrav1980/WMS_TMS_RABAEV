"""Same-quantity marked inventory on the owned 250-unit fixture; no FOUND/LOST claim."""
import json
import secrets
from uuid import uuid4
from urllib.parse import urlencode
import live_topup_common_pool as qa

qa.OUT = qa.ROOT / 'runtime/test-evidence/tradecase/2026-10-23/T11'
qa.FILE = qa.OUT / 'inventory-equal-count.json'
qa.s = json.loads(qa.FILE.read_text(encoding='utf-8')) if qa.FILE.exists() else dict(tag='IC23.' + uuid4().hex[:9], requests={}, results={})
s = qa.s
PATH = '/api/inventory/stock-posting/inventory'


def prepare():
    if 'actor' not in s:
        assert qa.stock() == [(250, 0)]
        assert qa.query('select NAME from RRL_WARES where ID=:w', w=qa.W) == [('TRADECASE QA 089ddb36',)]
        s.update(actor='IC' + uuid4().hex[:12], password=secrets.token_hex(20), before=qa.stock(),
            slow_marker=qa.query('select nvl(max(LOG_ID),0)from RRL_SQL_SLOW_LOG')[0][0])
        qa.save()
    if not s.get('actor_created'):
        with qa.oracle_connection() as conn:
            q = conn.cursor()
            q.execute('select count(*)from RUSERS where ID=:a', a=s['actor'])
            if not q.fetchone()[0]:
                q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'Own inventory proof',:a,:w,0,1)", a=s['actor'], p=s['password'], w=qa.W)
                q.execute("insert into RIGHTS(USER_GROUP,RIGHT1)values(:a,'stock_inventory_count')", a=s['actor'])
                conn.commit()
        s['actor_created'] = True
        qa.save()
    qa.step('owner', qa.BASE + '/stock/owner-grants', dict(operation_id=s['tag'] + '.owner', expected_version=0,
        username=s['actor'], owner_id='SNS', can_view=True, can_operate=True, reason='Own marked inventory proof'), method='PUT')
    if 'revision' not in s:
        rows = qa.query('select ID from RRL_REVIZION where USER_ID=:a and WARE_ID=:w order by ID', a=s['actor'], w=qa.W)
        if rows:
            assert len(rows) == 1
            s['revision'] = rows[0][0]
        else:
            s['revision'] = qa.expect(200, qa.http('POST', PATH + '/revisions', dict(warehouse_id=qa.W), s['actor'], s['password']))['revision_id']
        qa.save()
    if 'body' not in s or 'before_units' not in s:
        counts = []
        for uid, cell in qa.query('select r.UID_POLETA,r.CELL from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w and r.REMAIN>0 order by r.CELL,r.UID_POLETA', w=qa.W):
            lots = qa.expect(200, qa.http('GET', PATH + '/' + str(s['revision']) + '/lots?' + urlencode(dict(cell=cell)), actor=s['actor'], password=s['password']))['lots']
            lot = next(x for x in lots if x['uid'] == uid)
            keys = [x[0] for x in qa.query('select PHYSICAL_UNIT_KEY from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:u order by PHYSICAL_UNIT_KEY', u=uid)]
            assert len(keys) == int(lot['physical_qty'])
            counts.append(dict(uid=uid, cell=cell, article=lot['article'], unit=lot['unit'], quantity=lot['physical_qty'],
                expected_stock_version=lot['stock_version'], unit_keys=keys))
        assert sum(int(x['quantity']) for x in counts) == 250
        s['body'] = dict(operation_id=s['tag'] + '.count', revision_id=s['revision'], reason='Same-quantity owned marked inventory proof', counts=counts)
        s['before_units'] = qa.query('select u.PHYSICAL_UNIT_KEY,u.CURRENT_UID,u.STOCK_STATUS from RRL_WMS_RECEIPT_UNIT u join RRL_CELLS c on c.CELL=u.CURRENT_CELL where c.WARE_ID=:w order by u.PHYSICAL_UNIT_KEY', w=qa.W)
        qa.save()


def run():
    prepare()
    result = qa.step('count', PATH + '/counts', s['body'], qa=True)
    assert result['operation_id'] == s['body']['operation_id']
    again = qa.step('replay', PATH + '/counts', s['body'], qa=True)
    assert again['operation_id'] == result['operation_id']
    assert qa.query('select count(*)from RRL_STOCK_OPERATION where OPERATION_ID=:o', o=s['body']['operation_id']) == [(1,)]
    qa.step('changed', PATH + '/counts', dict(s['body'], reason='Changed same operation'), qa=True, status=409)
    if not s.get('right_revoked'):
        with qa.oracle_connection() as conn:
            q = conn.cursor()
            q.execute("delete from RIGHTS where USER_GROUP=:a and RIGHT1='stock_inventory_count'", a=s['actor'])
            conn.commit()
        s['right_revoked'] = True
        qa.save()
    qa.step('revoked_replay', PATH + '/counts', s['body'], qa=True, status=403)
    if not s.get('revision_closed'):
        with qa.oracle_connection() as conn:
            q = conn.cursor()
            q.execute('select CONDITION from RRL_REVIZION where ID=:r and USER_ID=:a and WARE_ID=:w', r=s['revision'], a=s['actor'], w=qa.W)
            assert q.fetchone()[0] in (0, 1, 2)
            ret = q.var(int)
            q.execute('begin :v:=REVIZION.close_revision(:r);end;', v=ret, r=s['revision'])
            assert ret.getvalue() == 1
            conn.commit()
        s['revision_closed'] = True
        qa.save()
    qa.step('owner_retire', qa.BASE + '/stock/owner-grants', dict(operation_id=s['tag'] + '.owner.retire', expected_version=1,
        username=s['actor'], owner_id='SNS', can_view=False, can_operate=False, reason='End own inventory proof'), method='PUT')
    with qa.oracle_connection() as conn:
        q = conn.cursor()
        q.execute('update RUSERS set DELETED=1 where ID=:a', a=s['actor'])
        q.execute('delete from RIGHTS where USER_GROUP=:a', a=s['actor'])
        conn.commit()
    assert qa.stock() == [(250, 0)]
    after = qa.query('select u.PHYSICAL_UNIT_KEY,u.CURRENT_UID,u.STOCK_STATUS from RRL_WMS_RECEIPT_UNIT u join RRL_CELLS c on c.CELL=u.CURRENT_CELL where c.WARE_ID=:w order by u.PHYSICAL_UNIT_KEY', w=qa.W)
    assert [list(x)for x in after] == [list(x)for x in s['before_units']]
    assert qa.query("select count(*)from USER_OBJECTS where STATUS='INVALID'") == [(0,)]
    s['slow_sql'] = qa.query('select LOG_ID,ELAPSED_MS,API_PATH,SQL_TEXT from RRL_SQL_SLOW_LOG where LOG_ID>:m order by ELAPSED_MS desc fetch first 20 rows only', m=s['slow_marker'])
    s['status'] = 'PASS_EQUAL_COUNT_ONLY'
    s.pop('error', None)
    qa.save()


if __name__ == '__main__':
    s['previous_calls'] = s.get('calls', [])
    try:
        if not s.get('status'):
            run()
        else:
            print('Closed; no commands sent')
    except Exception as exc:
        s['error'] = str(exc)
        qa.save()
        raise
    finally:
        qa.save()
    print(s.get('status'))
