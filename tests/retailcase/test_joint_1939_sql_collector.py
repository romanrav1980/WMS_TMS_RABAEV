"""Offline collector evidence boundaries; never connect Oracle."""
import importlib.util
import json
from pathlib import Path

PATH=Path(__file__).resolve().parents[2]/'scripts/joint_1939_sql_review.py'
SPEC=importlib.util.spec_from_file_location('joint_sql_collector',PATH)
collector=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(collector)


def test_local_phase_correlation_never_exports_body_or_native_pair(tmp_path,monkeypatch):
    monkeypatch.setattr(collector,'ROOT',tmp_path)
    path=tmp_path/'audit.jsonl'
    rows=[dict(phase='STARTED',request_id='r1',method='GET',path='/api/case-pick/tasks/1139/resource-context',
               request_body='SECRET',request_headers_json='PASSWORD',logged_at='2026-10-15T18:00:00+00:00'),
          dict(phase='FINISHED',request_id='r1',api_call_id=69201,response_status=200,duration_ms=62,
               response_body='SECRET',logged_at='2026-10-15T18:00:01+00:00'),
          dict(phase='FINISHED',api_call_id=99999,duration_ms=1,logged_at='2026-10-15T18:00:02+00:00'),
          dict(phase='STARTED',request_id='old',method='GET',path='/api/case-pick/tasks/1139',logged_at='2026-10-15T16:00:00+00:00')]
    path.write_text('\n'.join(json.dumps(r)for r in rows),encoding='utf-8')
    result=collector.local_audit(path,'2026-10-15T17:45:00+00:00')
    assert len(result['rows'])==1
    row=result['rows'][0]
    assert(row['request_id'],row['api_call_id'],row['method'],row['duration_ms'])==('r1',69201,'GET',62)
    assert 'SECRET'not in json.dumps(result)and 'PASSWORD'not in json.dumps(result)
    assert 'native' in result['scope']
