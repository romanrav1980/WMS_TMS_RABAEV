"""Read-only native compile refusals; this does not prove a successful physical move."""
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / 'scripts')]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from tools.mcp.tms_mcp_server import oracle_connection

report = {'status': 'FAIL', 'checks': [], 'basis': 'Native compiler calls in READ ONLY; completed own task, no execution'}
with oracle_connection() as connection:
    cursor = connection.cursor()
    cursor.execute('set transaction read only')
    cursor.execute("select user,sys_context('USERENV','SERVICE_NAME')from dual")
    assert cursor.fetchone() == ('RABAEV', 'orcl')
    cursor.execute('select RRL_WAREHOUSE_TASK_ACCESS.task_signature(1231)from dual')
    signature = cursor.fetchone()[0]
    assert len(signature) == 64
    cursor.execute("select p.TASK_ID,p.CASE_TASK_ID,RRL_WAREHOUSE_TASK_ACCESS.task_signature(p.TASK_ID) from RRL_ST_DEFER_WAIT_PLAN p join RRL_WAREHOUSE_TASK t on t.TASK_ID=p.TASK_ID where p.CASE_TASK_ID is not null and t.ASSIGNED_TO='admin'and t.STATUS='DONE'order by p.TASK_ID fetch first 1 row only")
    case_physical, case_id, case_signature = cursor.fetchone()
    for package, command, source, metadata, expected in [
        ('RRL_STOCK_HU_TASK', 'HU_TASK_COMPLETE', {'task_id': 1231}, {'expected_task_signature': '0' * 64}, 'TASK_EXPECTED_SIGNATURE_CHANGED'),
        ('RRL_STOCK_HU_TASK', 'HU_TASK_COMPLETE', {'task_id': 1231}, {'expected_task_signature': signature}, 'HU_TASK_CONTRACT_OR_STATE_INVALID'),
        ('RRL_STOCK_HU_TASK', 'HU_TASK_COMPLETE', {'task_id': 1231}, {}, 'HU_TASK_CONTRACT_OR_STATE_INVALID'),
        ('RRL_STOCK_CASE_MOVE_CMD', 'CASE_CARRIER_MOVE', {'case_task_id': case_id}, {'physical_task_id': case_physical, 'expected_task_signature': '0' * 64}, 'TASK_EXPECTED_SIGNATURE_CHANGED'),
        ('RRL_STOCK_CASE_MOVE_CMD', 'CASE_CARRIER_MOVE', {'case_task_id': case_id}, {'expected_task_signature': case_signature}, 'PAPER_PHYSICAL_TASK_REQUIRED'),
        ('RRL_STOCK_CASE_MOVE_CMD', 'CASE_CARRIER_MOVE', {'case_task_id': case_id}, {'physical_task_id': case_physical, 'expected_task_signature': case_signature}, 'CASE_CARRIER_MOVE_SNAPSHOT_TARGET_REQUIRED'),
        ('RRL_STOCK_CASE_MOVE_CMD', 'CASE_CARRIER_MOVE', {'case_task_id': case_id}, {}, 'CASE_CARRIER_MOVE_SNAPSHOT_TARGET_REQUIRED'),
    ]:
        request = json.dumps(dict(contract_version=2, operation_id='PAPER.READONLY.CHECK', command_type=command, actor='admin', source=source, metadata=metadata, lines=[], units=[]))
        outcome = cursor.var(str, size=4000)
        start = time.perf_counter()
        cursor.execute("""declare r clob;begin
            begin RRL_STOCK_POSTING_API.prepare_command(:request,'admin',r);:outcome:='UNEXPECTED_SUCCESS';
            exception when others then :outcome:=sqlerrm;end;
            RRL_STOCK_POSTING_API.reset_connection;
            end;""", request=request, outcome=outcome)
        result = outcome.getvalue()
        assert expected in result, (package, expected, result)
        report['checks'].append(dict(package=package, expected=expected, actual=result, ms=round((time.perf_counter() - start) * 1000, 2)))
    cursor.execute("select STATUS from USER_OBJECTS where OBJECT_NAME in ('RRL_STOCK_HU_TASK','RRL_STOCK_CASE_MOVE_CMD')")
    assert all(row[0] == 'VALID' for row in cursor)
    cursor.execute('select RRL_WAREHOUSE_TASK_ACCESS.task_signature(1231)from dual')
    assert cursor.fetchone()[0] == signature
    cursor.execute('select count(*)from USER_OBJECTS where STATUS=\'INVALID\'')
    assert cursor.fetchone()[0] == 0
    connection.rollback()
report['status'] = 'PASS'
destination = ROOT / 'runtime/test-evidence/tradecase/2026-10-23/T11/paper-version-native.json'
destination.write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(dict(status=report['status'], checks=len(report['checks']), evidence=str(destination))))
