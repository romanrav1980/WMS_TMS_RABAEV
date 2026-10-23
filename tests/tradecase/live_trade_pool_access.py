"""Current role, owner and legacy rights protect live pool preview and saved receipts."""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import secrets
import sys
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parent))
import live_topup_common_pool as qa

qa.FILE = qa.OUT / 'trade-pool-access-live.json'
qa.s = json.loads(qa.FILE.read_text(encoding='utf-8')) if qa.FILE.exists() else dict(
    tag='PA23.' + uuid4().hex[:9], warehouse_id=qa.W, requests={}, results={}, checks=[])
qa.TAG = qa.s['tag']; s = qa.s


def grant(key, user, version, view, operate):
    return qa.step(key, qa.BASE + '/stock/owner-grants', dict(operation_id=qa.TAG + '.' + key, expected_version=version,
        username=user, owner_id='SNS', can_view=view, can_operate=operate, reason='Own pool scope and receipt proof'), method='PUT')


def prepare():
    if 'before' not in s:
        assert qa.stock() == [(250, 0)]
        s.update(before=qa.stock(), policy_before=qa.expect(200, qa.http('GET', qa.POLICY)),
            departure=(datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
            actor='PA' + uuid4().hex[:12], password=secrets.token_hex(20),
            legacy='PL' + uuid4().hex[:12], legacy_password=secrets.token_hex(20),
            slow_marker=qa.query('select nvl(max(LOG_ID),0)from RRL_SQL_SLOW_LOG')[0][0]); qa.save()
    if 'identities' not in s:
        with qa.oracle_connection() as conn:
            q = conn.cursor()
            for user, password, group in [(s['actor'], s['password'], 'QA_POOL_ONLY'), (s['legacy'], s['legacy_password'], s['legacy'])]:
                q.execute('select count(*)from RUSERS where ID=:a', a=user)
                if not q.fetchone()[0]:
                    q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'Owned pool proof',:g,:w,0,1)", a=user, p=password, g=group, w=qa.W)
            q.execute('select count(*)from RRL_ACCESS_ROLE where ROLE_ID=:a', a=s['actor'])
            if not q.fetchone()[0]:
                q.execute("insert into RRL_ACCESS_ROLE(ROLE_ID,TITLE,ACTIVE,VERSION_NO)values(:a,'Owned pool proof',1,1)", a=s['actor'])
                for permission in ['stock_reservation_view', 'stock_reservation_edit']:
                    q.execute('insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION)values(:a,:p)', a=s['actor'], p=permission)
                q.execute("insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO)values(:a,:a,:a,'WAREHOUSE',:w,'CURRENT',systimestamp-interval '1'minute,systimestamp+interval '2'hour,'admin','Own pool proof',1)", a=s['actor'], w=str(qa.W))
            for permission in ['stock_reservation_view', 'stock_reservation_edit']:
                q.execute('select count(*)from RIGHTS where USER_GROUP=:g and RIGHT1=:p', g=s['legacy'], p=permission)
                if not q.fetchone()[0]:
                    q.execute('insert into RIGHTS(USER_GROUP,RIGHT1)values(:g,:p)', g=s['legacy'], p=permission)
            conn.commit()
        s['identities'] = True; qa.save()
    grant('role_owner', s['actor'], 0, True, True)
    grant('legacy_owner', s['legacy'], 0, True, True)
    before = s['policy_before']
    qa.step('policy_on', qa.POLICY, dict(expected_version=before['policy_version'], stock_class=before['stock_class'],
        ship_from_stock=True, pick_step=before['pick_step']), method='PUT')
    qa.send('order', 'ORDER', qa.TAG + '.ORDER', dict(order_kind='OUTBOUND', recipient_id='C1', planned_ship_at=s['departure'],
        lines=[dict(line_id='1', sku_id='A', source_owner_id='SNS', target_owner_id='SNS', mrc='200', quantity='20', uom='EA', min_osg_days=0)]))
    qa.native_order('native', qa.TAG + '.ORDER', 20)


def run():
    prepare()
    preview = qa.step('role_preview', qa.POOL, method='GET', qa=True)
    assert preview['complete'] and preview['allocations'][str(s['native']['row'])] == '20', preview
    assert float(preview['available_quantity']) >= 20
    allocated = qa.step('role_allocated', qa.POOL + '/allocate', dict(operation_id=qa.TAG + '.role.allocate'), qa=True)
    assert allocated['allocated_quantity'] == '20' and qa.stock() == [(250, 0)], allocated
    qa.step('foreign_preview', f'/api/inventory/soft-pools/219023232/{qa.ARTICLE}', method='GET', qa=True, status=403)
    qa.step('foreign_write', f'/api/inventory/soft-pools/219023232/{qa.ARTICLE}/allocate', dict(operation_id=qa.TAG + '.foreign'), qa=True, status=403)
    grant('role_operate_revoked', s['actor'], 1, True, False)
    original = s['requests']['role_allocated']
    qa.step('owner_replay_denied', original['path'], original['body'], qa=True, status=403)
    grant('role_operate_restored', s['actor'], 2, True, True)
    assert qa.step('role_replay_restored', original['path'], original['body'], qa=True) == allocated
    grant('role_hidden', s['actor'], 3, False, False)
    hidden = qa.step('hidden_preview', qa.POOL, method='GET', qa=True)
    assert hidden['complete'] is False and hidden['available_quantity'] is None
    assert str(s['native']['row']) not in hidden['allocations'] and not hidden['classes'], hidden
    if 'legacy_proof' not in s:
        read = qa.expect(200, qa.http('GET', qa.POOL, actor=s['legacy'], password=s['legacy_password']))
        result = qa.expect(200, qa.http('POST', qa.POOL + '/allocate', dict(operation_id=qa.TAG + '.legacy.allocate'), s['legacy'], s['legacy_password']))
        assert read['complete'] and result['allocated_quantity'] == '20'
        s['legacy_proof'] = dict(preview=read, result=result); qa.save()
    if 'assignment_revoked' not in s:
        with qa.oracle_connection() as conn:
            q = conn.cursor(); q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp,VERSION_NO=VERSION_NO+1 where ASSIGNMENT_ID=:a and REVOKED_AT is null', a=s['actor'])
            conn.commit()
        s['assignment_revoked'] = True; qa.save()
    qa.step('scope_preview_denied', qa.POOL, method='GET', qa=True, status=403)
    qa.step('scope_replay_denied', original['path'], original['body'], qa=True, status=403)
    if 'legacy_edit_revoked' not in s:
        with qa.oracle_connection() as conn:
            q = conn.cursor(); q.execute("delete from RIGHTS where USER_GROUP=:g and RIGHT1='stock_reservation_edit'", g=s['legacy']); conn.commit()
        s['legacy_edit_revoked'] = True; qa.save()
    qa.expect(403, qa.http('POST', qa.POOL + '/allocate', dict(operation_id=qa.TAG + '.legacy.allocate'), s['legacy'], s['legacy_password']))
    s['checks'].append('Scoped role and legacy group each allocate20; foreign warehouse403; recorded receipt owner403 then identical after restore; hidden preview incomplete/null; assignment and legacy edit revoke deny replay')
    s['status'] = 'ACCESS_PASS_CLEANUP_REQUIRED'; qa.save()
    cleanup()


def cleanup():
    qa.send('order_cancelled', 'ORDER', qa.TAG + '.ORDER', dict(s['requests']['order']['body']['payload'], cancelled=True), 2)
    qa.step('pool_cleaned', qa.POOL + '/allocate', dict(operation_id=qa.TAG + '.clean'))
    now = qa.expect(200, qa.http('GET', qa.POLICY)); before = s['policy_before']
    qa.step('policy_restored', qa.POLICY, dict(expected_version=now['policy_version'], stock_class=before['stock_class'],
        ship_from_stock=before['ship_from_stock'], pick_step=before['pick_step']), method='PUT')
    grant('legacy_owner_retired', s['legacy'], 1, False, False)
    with qa.oracle_connection() as conn:
        q = conn.cursor(); q.execute('update RUSERS set DELETED=1 where ID in(:a,:l)', a=s['actor'], l=s['legacy'])
        q.execute('delete from RIGHTS where USER_GROUP=:g', g=s['legacy']); conn.commit()
    assert qa.stock() == [(250, 0)]
    assert qa.query("select nvl(sum(QTY),0)from RRL_STOCK_RESERVATION where POOL_WARE_ID=:w and ARTICUL=:a and RESERVATION_KIND='SOFT'and STATUS in('ACTIVE','ALLOCATED')", w=qa.W, a=qa.ARTICLE) == [(0,)]
    assert qa.query("select count(*)from USER_OBJECTS where STATUS='INVALID'") == [(0,)]
    s['slow_sql'] = qa.query('select LOG_ID,ELAPSED_MS,API_PATH,SQL_TEXT from RRL_SQL_SLOW_LOG where LOG_ID>:m order by ELAPSED_MS desc fetch first 20 rows only', m=s['slow_marker'])
    s['status'] = 'PASS'; s.pop('error', None); qa.save()


if __name__ == '__main__':
    s['previous_calls'] = s.get('calls', [])
    try:
        if s.get('status') == 'PASS':
            print('Already PASS; no commands sent')
        elif sys.argv[-1] == 'cleanup' or s.get('status') == 'ACCESS_PASS_CLEANUP_REQUIRED':
            cleanup()
        else:
            run()
    except Exception as exc:
        s['error'] = str(exc); qa.save(); raise
    finally:
        qa.save()
    print(s.get('status'))
