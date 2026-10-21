"""Read the retained full-pallet task under three Oracle session zones; no DML."""
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import re
import sys
from time import perf_counter
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / 'api/wms_api_server'), str(Path(__file__).parent)]
from app.modules.resources.infrastructure.timeline_queries import task_rows
from tools.mcp.tms_mcp_server import oracle_connection
from live_document_acceptance import http, expect, CALLS

OUT = ROOT / 'runtime/test-evidence/tradecase/2026-10-21/T06'
report = dict(status='FAIL', checks=[])


class InferredCursor:
    """Reproduce the previous driver inference using a fresh cursor for each call."""
    def __init__(self, cursor): self.cursor = cursor
    def setinputsizes(self, **_): pass
    def __getattr__(self, name): return getattr(self.cursor, name)


if __name__ == '__main__':
    os.environ['TRADECASE_ADMIN_USER'] = 'admin'
    os.environ['TRADECASE_ADMIN_PASSWORD'] = re.search(r'PASS=(\S+?)[`,)\s]', (ROOT/'AGENTS.md').read_text(encoding='utf-8'))[1]
    try:
        with oracle_connection() as conn:
            q = conn.cursor()
            q.execute("select to_char(STARTED_AT_INSTANT at time zone 'UTC','YYYY-MM-DD\"T\"HH24:MI:SS.FF6TZH:TZM') from RRL_WAREHOUSE_TASK where TASK_ID=1221")
            instant = datetime.fromisoformat(q.fetchone()[0])
            start, finish = instant-timedelta(minutes=30), instant+timedelta(minutes=30)
            params = dict(ware=220639789, actor='admin', start_at=start, finish_at=finish)
            for zone in ['+00:00', '+03:00', '-04:00']:
                q.execute("alter session set time_zone='" + zone + "'")
                row = dict(session_zone=zone)
                for typed in [False, True]:
                    with conn.cursor() as cursor:
                        began = perf_counter()
                        values = task_rows(cursor if typed else InferredCursor(cursor), params)
                        row['typed' if typed else 'inferred'] = dict(task_ids=[x['task_id'] for x in values], elapsed_ms=round((perf_counter()-began)*1000, 3))
                assert 1221 in row['typed']['task_ids'], row
                report['checks'].append(row)
            assert 1221 in report['checks'][0]['inferred']['task_ids']
            assert all(1221 not in x['inferred']['task_ids'] for x in report['checks'][1:])
        for offset in [timezone.utc, timezone(timedelta(hours=3)), timezone(timedelta(hours=-4))]:
            query = urlencode(dict(warehouse_id=220639789, start_at=start.astimezone(offset).isoformat(), finish_at=finish.astimezone(offset).isoformat()))
            value = expect(200, http('GET', '/api/resources/timeline?'+query))
            assert any(x['source_id'] == 1221 for x in value['events'] if x['kind'] == 'WAREHOUSE_TASK')
            assert dict(event_id='WAREHOUSE_TASK:1221', resource_id='EQUIPMENT:32') in value['assignments']
        report.update(status='PASS', anchor=instant.isoformat(), physical_writes=0)
    except Exception as exc:
        report['error'] = str(exc)
        raise
    finally:
        report['http'] = CALLS
        (OUT/'fullpal-timeline-timezones.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k != 'http'}))
