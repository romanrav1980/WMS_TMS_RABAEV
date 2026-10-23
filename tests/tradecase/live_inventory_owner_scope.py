"""Owner-view revocation on live inventory reads; observe write denial without quantity changes."""
import json
from uuid import uuid4
import live_inventory_equal_count as equal

qa = equal.qa
qa.FILE = qa.OUT / 'inventory-owner-scope-live.json'
qa.s = json.loads(qa.FILE.read_text(encoding='utf-8')) if qa.FILE.exists() else dict(tag='IV23.' + uuid4().hex[:9], requests={}, results={})
s = qa.s
equal.s = s


def grant(key, version, view, operate):
    return qa.step(key, qa.BASE + '/stock/owner-grants', dict(operation_id=s['tag'] + '.' + key, expected_version=version,
        username=s['actor'], owner_id='SNS', can_view=view, can_operate=operate, reason='Own inventory current owner scope'), method='PUT')


def run():
    equal.prepare()
    path = equal.PATH + '/' + str(s['revision']) + '/lots?cell=ALS303760e2f0'
    visible = qa.step('allowed', path, method='GET', qa=True)
    assert len(visible['lots']) == 1 and visible['lots'][0]['physical_qty'] == '20'
    grant('revoke_view', 1, False, False)
    denied = qa.step('denied', path, method='GET', qa=True, status=403)
    assert 'lots' not in denied
    grant('restore_view_only', 2, True, False)
    assert len(qa.step('view_only_read', path, method='GET', qa=True)['lots']) == 1
    if 'view_only_count' not in s:
        # Every submitted quantity equals the recorded physical stock; an incorrect grant cannot alter quantities.
        s['view_only_count'] = qa.http('POST', equal.PATH + '/counts', s['body'], s['actor'], s['password'])
        qa.save()
    grant('retire_owner', 3, False, False)
    with qa.oracle_connection() as conn:
        q = conn.cursor()
        result = q.var(int)
        q.execute('begin :v:=REVIZION.close_revision(:r);end;', v=result, r=s['revision'])
        assert result.getvalue() == 1
        q.execute('update RUSERS set DELETED=1 where ID=:a', a=s['actor'])
        q.execute('delete from RIGHTS where USER_GROUP=:a', a=s['actor'])
        conn.commit()
    assert qa.stock() == [(250, 0)]
    after = qa.query('select u.PHYSICAL_UNIT_KEY,u.CURRENT_UID,u.STOCK_STATUS from RRL_WMS_RECEIPT_UNIT u join RRL_CELLS c on c.CELL=u.CURRENT_CELL where c.WARE_ID=:w order by u.PHYSICAL_UNIT_KEY', w=qa.W)
    assert [list(x)for x in after] == [list(x)for x in s['before_units']]
    assert qa.query("select count(*)from USER_OBJECTS where STATUS='INVALID'") == [(0,)]
    s['slow_sql'] = qa.query('select LOG_ID,ELAPSED_MS,API_PATH,SQL_TEXT from RRL_SQL_SLOW_LOG where LOG_ID>:m order by ELAPSED_MS desc fetch first 15 rows only', m=s['slow_marker'])
    s['cleanup'] = 'Revision closed; actor/legacy rights removed; owner0/0;250/H0; all unit identities/current lots/statuses unchanged'
    s['status'] = 'PASS' if s['view_only_count'][0] == 403 else 'READ_PASS_COUNT_OWNER_GAP'
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
