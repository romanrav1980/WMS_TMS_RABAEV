"""Measure real CASE request stages in an isolated process; never record bind values."""
from contextlib import contextmanager
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
from time import perf_counter
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'api/wms_api_server'), str(ROOT)]
from fastapi.testclient import TestClient
from app import oracle_gateway
from app.main import app
from app.modules.resources.infrastructure import timeline_queries

OUT = ROOT / 'runtime/test-evidence/tradecase/2026-10-22/T12/case-request-stages.json'
events = []
original_lease = oracle_gateway.oracle_connection
original_log = oracle_gateway.OracleGateway._log_slow_sql
original_rows = timeline_queries.read_rows


def measured_rows(cursor, sql, params, limit=2000):
    began = perf_counter()
    try:
        result = original_rows(cursor, sql, params, limit)
    finally:
        events[-1].setdefault('timeline_queries', []).append(dict(
            sql_sha256=sha256(sql.encode()).hexdigest(), ms=round((perf_counter()-began)*1000, 3)))
    events[-1]['timeline_queries'][-1]['rows'] = len(result)
    return result


@contextmanager
def measured_lease():
    began = perf_counter()
    lease = original_lease()
    connection = lease.__enter__()
    acquired = perf_counter()
    event = dict(acquire_ms=round((acquired - began) * 1000, 3))
    events.append(event)
    try:
        yield connection
    finally:
        released = perf_counter()
        lease.__exit__(*sys.exc_info())
        event.update(body_ms=round((released-acquired)*1000, 3),
                     cleanup_ms=round((perf_counter()-released)*1000, 3))


def measured_log(self, connection, sql, params, started, row_count, error_text, operation_kind):
    elapsed = (perf_counter() - started) * 1000
    # Store stage names only, never SQL bind values, credentials or audit payloads.
    label = ('AUTH' if 'from RUSERS' in sql else
             'AUDIT_START' if 'RRL_API_AUDIT_API.start_call' in sql else
             'AUDIT_FINISH' if 'RRL_API_AUDIT_API.finish_call' in sql else
             'CASE_QUEUE' if sql == 'Current CASE queue READ ONLY snapshot' else
             'QC_STATUS' if sql == 'Current warehouse QC status access' else operation_kind)
    began = perf_counter()
    original_log(self, connection, sql, params, started, row_count, error_text, operation_kind)
    events[-1].update(stage=label, sql_ms=round(elapsed, 3),
                      slow_log_ms=round((perf_counter()-began)*1000, 3), failed=bool(error_text))


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--path',default='/api/case-pick/tasks?scope=all&limit=200')
    parser.add_argument('--out',type=Path,default=OUT)
    args=parser.parse_args()
    report = dict(status='FAIL', transport='in-process ASGI with real Oracle and audit middleware',
                  startup='No lifespan workers; new process and new Oracle pool', physical_writes=0, samples=[])
    try:
        # No lifespan context: do not start unrelated background workers.
        with patch.object(oracle_gateway, 'oracle_connection', measured_lease), patch.object(
            oracle_gateway.OracleGateway, '_log_slow_sql', measured_log), patch.object(timeline_queries, 'read_rows', measured_rows):
            client = TestClient(app)
            expected = None
            for i in range(6):
                events.clear()
                began = perf_counter()
                response = client.get(args.path, auth=('admin', 'admin123'))
                elapsed = (perf_counter()-began)*1000
                assert response.status_code == 200, response.status_code
                payload = response.json()
                if args.path.startswith('/api/resources/timeline?'):
                    report['excluded_volatile_fields'] = ['observed_at','sources[*].observed_at']
                    payload = {key:value for key,value in payload.items() if key != 'observed_at'}
                    payload['sources'] = [{key:value for key,value in source.items() if key != 'observed_at'} for source in payload['sources']]
                digest = sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()
                if expected is None: expected = digest
                assert digest == expected, 'Response changed beyond declared volatile fields'
                report['samples'].append(dict(round=i, total_ms=round(elapsed, 3), rows=len(response.json())if isinstance(response.json(),list)else None,
                    sha=digest, request_id=response.headers.get('x-wms-request-id'), leases=list(events)))
            report['status'] = 'PASS'
    except Exception as exc:
        report['error'] = str(exc)
        raise
    finally:
        args.out.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report))
