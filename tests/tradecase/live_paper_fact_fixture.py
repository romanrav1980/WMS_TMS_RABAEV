"""Own empty-HU fixture for the actual paper-fact screen; no goods receipt or stock restoration."""
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / 'scripts'), str(ROOT / 'tests/tradecase')]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from tools.mcp.tms_mcp_server import oracle_connection
from live_document_acceptance import http, expect, CALLS
os.environ['TRADECASE_ADMIN_USER'] = 'admin'
os.environ['TRADECASE_ADMIN_PASSWORD'] = 'admin123'
FILE = ROOT / 'runtime/test-evidence/tradecase/2026-10-23/T11/paper-fact-ui-state.json'
state = json.loads(FILE.read_text(encoding='utf-8')) if FILE.exists() else {
    'tag': 'PH23.68eb5dba.factui', 'hu': 'PH23.68eb5dba.HU',
    'source': 'PH23.68eb5dba.A', 'target': 'PH23.68eb5dba.B', 'requests': {}, 'results': {}}

def save():
    FILE.write_text(json.dumps(state, indent=2, default=str), encoding='utf-8')

def query(sql, **binds):
    with oracle_connection() as connection:
        q = connection.cursor(); q.execute(sql, binds); return q.fetchall()

def balances():
    return query('select c.WARE_ID,nvl(sum(r.REMAIN),0),nvl(sum(r.HARD_RESERVED_BASE),0) '
                 'from RRL_CELLS c left join RRL_REMAINS r on r.CELL=c.CELL '
                 'where c.WARE_ID in (210564699,215266197,219023232,220793322,212476763) '
                 'group by c.WARE_ID order by c.WARE_ID')

def step(name, method, path, body=None):
    if name not in state['requests']:
        state['requests'][name] = dict(method=method, path=path, body=body); save()
    if name not in state['results']:
        r = state['requests'][name]
        state['results'][name] = expect(200, http(r['method'], r['path'], r['body'])); save()
    return state['results'][name]

def plan(prefix, source, target):
    version = query('select HU_CONTENT_VERSION from RRL_PALLETS where UID_PALLET=:u', u=state['hu'])[0][0]
    result = step(prefix + '.plan', 'POST', '/api/warehouse-hus/plan-move', dict(
        operation_id=state['tag']+'.'+prefix+'.plan', identifier=state['hu'], target_cell=target,
        expected_version=version, scan_container=state['hu'], scanned_from_cell=source, scanned_to_cell=target))
    task = result['task_id']; path = f'/api/warehouse-tasks/{task}'
    step(prefix+'.assign', 'POST', path+'/assign', dict(assigned_to='admin'))
    step(prefix+'.start', 'POST', path+'/start', {})
    paper = step(prefix+'.paper', 'GET', path+'/paper')
    return task, paper

def run():
    assert query("select user,sys_context('USERENV','SERVICE_NAME')from dual") == [('RABAEV', 'orcl')]
    if sys.argv[1] == 'prepare':
        if 'before' not in state:
            assert query('select HU_CURRENT_CELL from RRL_PALLETS where UID_PALLET=:u', u=state['hu']) == [(state['source'],)]
            assert query('select count(*)from RRL_WAREHOUSE_TASK where UID_PALLET=:u and STATUS not in(\'DONE\',\'CANCELLED\')', u=state['hu']) == [(0,)]
            state['before'] = balances()
            state['slow_marker'] = query('select nvl(max(LOG_ID),0)from RRL_SQL_SLOW_LOG')[0][0]; save()
        task, paper = plan('out', state['source'], state['target'])
        state.update(task=task, paper=paper); save()
    elif sys.argv[1] == 'restore':
        task = state['task']
        assert query('select STATUS,FACT_QTY from RRL_WAREHOUSE_TASK where TASK_ID=:t', t=task) == [('DONE', 1)]
        assert query('select count(*)from RRL_WAREHOUSE_TASK_STOCK_MOVE where TASK_ID=:t', t=task) == [(0,)]
        back, paper = plan('back', state['target'], state['source'])
        step('back.complete', 'POST', f'/api/warehouse-tasks/{back}/complete', dict(
            operation_id=state['tag']+'.back.complete', expected_task_signature=paper['task']['task_signature'],
            fact_qty='1', scanned_pallet=state['hu'], scanned_from_cell=state['target'], scanned_to_cell=state['source']))
        assert query('select HU_CURRENT_CELL from RRL_PALLETS where UID_PALLET=:u', u=state['hu']) == [(state['source'],)]
        assert query('select count(*)from RRL_WAREHOUSE_TASK where UID_PALLET=:u and STATUS not in(\'DONE\',\'CANCELLED\')', u=state['hu']) == [(0,)]
        state['after'] = balances()
        assert [list(r) for r in state['after']] == state['before']
        state['slow_sql'] = query('select LOG_ID,ELAPSED_MS,SQL_TEXT from RRL_SQL_SLOW_LOG where LOG_ID>:m order by LOG_ID', m=state['slow_marker'])
        state['status'] = 'PASS'; save()
    else:
        raise ValueError('prepare or restore required')
    state['http_calls'] = state.get('http_calls', []) + CALLS; save()
    print(json.dumps(dict(task=state.get('task'), status=state.get('status', 'PREPARED'))))

if __name__ == '__main__': run()
