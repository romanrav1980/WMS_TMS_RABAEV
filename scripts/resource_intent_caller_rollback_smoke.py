"""PREPARED caller-rollback only CASE1138/admin metadata proof; no DDL/HTTP/quantity writer.
Default plan does not connect. Native late-original/committed replay races require a separate fixture.
"""
import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / 'reports/retailcase/2026-10-15/resource-metadata-intents'
PREFIX = 'RMI15.RB1138.'
TASK = 1138
ACTOR = 'admin'
PARENT = 'REUSE.RETURN:e6c16d0bbd'
CHILD = 'CASELOT:E8EAB9A962B9D19BA5AC8FCEE19D8021895BD0:1'


def call(cursor: Any, procedure: str, *args: Any) -> dict[str, Any]:
    import oracledb
    output = cursor.var(oracledb.DB_TYPE_CLOB)
    cursor.callproc(procedure, [*args, output])
    value = output.getvalue()
    return value if isinstance(value, dict) else json.loads(value.read() if hasattr(value, 'read') else value)


def denied(cursor: Any, procedure: str, args: list[Any], marker: str) -> None:
    import oracledb
    try:
        call(cursor, procedure, *args)
    except oracledb.DatabaseError as error:
        assert marker in str(error), (marker, str(error))
        return
    raise AssertionError('Unexpected native acceptance: ' + marker)


def snapshot(gateway: Any) -> dict[str, Any]:
    result = dict(
        task=gateway.fetch_all('select STATUS,PICKED_QTY,ASSIGNED_TO,ASSIGNED_RESOURCE_ID,RESOURCE_SESSION_ID,EQUIPMENT_ID,CONTENT_VERSION,ASSIGNMENT_VERSION,STARTED_AT_INSTANT from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t', {'t': TASK}),
        lines=gateway.fetch_all('select CASE_PICK_LINE_ID,STATUS,PLANNED_QTY,PICKED_QTY from RRL_CASE_PICK_LINE where CASE_PICK_TASK_ID=:t order by CASE_PICK_LINE_ID fetch first 201 rows only', {'t': TASK}),
        stock=gateway.fetch_all('select r.UID_POLETA,r.CELL,r.REMAIN,r.HARD_RESERVED_BASE,r.STOCK_VERSION,p.STOCK_ORIGIN_UID,p.CREATED_BY_STOCK_OP from RRL_REMAINS r join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA where r.UID_POLETA in(:p,:c)order by r.UID_POLETA,r.CELL', {'p': PARENT, 'c': CHILD}),
        events=gateway.fetch_all('select CASE_PICK_EVENT_ID,EVENT_TYPE from RRL_CASE_PICK_EVENT where CASE_PICK_TASK_ID=:t order by CASE_PICK_EVENT_ID fetch first 201 rows only', {'t': TASK}),
        receipts=gateway.fetch_all('select OPERATION_ID,SOURCE_SHA256,OUTCOME from RRL_CASE_RESOURCE_COMMAND where CASE_PICK_TASK_ID=:t order by OPERATION_ID fetch first 101 rows only', {'t': TASK}),
        tombstones=gateway.fetch_all('select CONTROL_OPERATION_ID,DOMAIN,ORIGINAL_OPERATION_ID,ORIGINAL_SHA256,CONTROL_SHA256 from RRL_RESOURCE_INTENT_ABANDON where CASE_TASK_ID=:t order by CONTROL_OPERATION_ID fetch first 101 rows only', {'t': TASK}),
        carrier=gateway.fetch_all('select LOT_UID,CREATED_OPERATION from RRL_CASE_CARRIER_LOT where CASE_PICK_TASK_ID=:t order by LOT_UID fetch first 21 rows only', {'t': TASK}))
    assert len(result['task']) == 1 and result['task'][0]['status'] == 'CANCELLED' and result['task'][0]['picked_qty'] == 0
    assert len(result['lines']) <= 200 and len(result['events']) <= 200 and len(result['receipts']) <= 100 and len(result['tombstones']) <= 100 and len(result['carrier']) <= 20
    assert sum(r['remain'] for r in result['stock']) == 24 and sum(r['hard_reserved_base'] for r in result['stock']) == 0
    assert all(r['stock_origin_uid'] == '300000034518661218' for r in result['stock'])
    return json.loads(json.dumps(result, default=str, sort_keys=True))


def no_owned_history(gateway: Any) -> None:
    for table, key in [('RRL_RESOURCE_INTENT_ABANDON', 'CONTROL_OPERATION_ID'), ('RRL_CASE_RESOURCE_COMMAND', 'OPERATION_ID'),
                       ('RRL_WTASK_RESOURCE_COMMAND', 'OPERATION_ID'), ('RRL_STOCK_OPERATION', 'OPERATION_ID'),
                       ('RRL_STOCK_OP_CLOCK', 'OPERATION_ID'), ('RRL_PALLETS', 'CREATED_BY_STOCK_OP')]:
        assert not gateway.fetch_all('select ' + key + ' from ' + table + ' where ' + key + ' like :p fetch first 1 rows only', {'p': PREFIX + '%'})
    keys = ['STOCK:' + hashlib.sha256((PREFIX + name).encode()).hexdigest().upper() for name in ['ABSENT', 'ABANDON', 'RECORDED']]
    assert not gateway.fetch_all('select IDEMPOTENCY_KEY from RRL_EVENT_OUTBOX where IDEMPOTENCY_KEY in(:a,:b,:c)', dict(zip(['a','b','c'], keys)))


def rollback_connection(connection: Any, cursor: Any) -> None:
    try:
        connection.rollback()
    finally:
        cursor.callproc('RRL_STOCK_LOCK_API.clear_plan')


def absent_trial(connect: Any, gateway: Any, before: dict[str, Any], checks: list[str]) -> None:
    import oracledb
    from app.modules.resources.contracts_case_resource import CaseResourceCommand
    from app.modules.resources.contracts_resource_intents import ResourceIntentAbandon, ResourceIntentAbandoned, ResourceIntentResolution
    from app.modules.resources.infrastructure.case_resource_commands import canonical
    from app.modules.resources.infrastructure.resource_intent_commands import control_wire, digest
    command = CaseResourceCommand(operation_id=PREFIX + 'ABSENT', action='CLAIM', expected_assignment_version=before['task'][0]['assignment_version'], resource_session_id=55, reason='TEST_NOT_HARDWARE never-recorded cancelled CASE metadata intent')
    wire = canonical(command)
    body = ResourceIntentAbandon(operation_id=PREFIX + 'ABANDON', domain='CASE', task_id=TASK, reason='TEST explicit absence proof only, no task or quantity cancellation', original_wire=wire)
    with connect() as connection:
        cursor = connection.cursor()
        try:
            assert cursor.callfunc('DBMS_TRANSACTION.LOCAL_TRANSACTION_ID', str, [False]) is None
            ack = call(cursor, 'RRL_RESOURCE_INTENT_API.abandon', control_wire(body), ACTOR)
            result = ResourceIntentAbandoned.model_validate(ack)
            assert (result.operation_id, result.actor, result.task_id, result.original_wire, result.original_request_sha256, result.control_request_sha256) == (body.operation_id, ACTOR, TASK, wire, digest(wire), digest(control_wire(body)))
            assert call(cursor, 'RRL_RESOURCE_INTENT_API.describe', body.operation_id, ACTOR) == ack
            resolved = ResourceIntentResolution.model_validate(call(cursor, 'RRL_RESOURCE_INTENT_API.resolve', 'CASE', TASK, command.operation_id, command.action, ACTOR, digest(wire), ACTOR))
            assert resolved.status == 'ABANDONED' and resolved.abandonment == result
            denied(cursor, 'RRL_RESOURCE_INTENT_API.resolve', ['CASE', TASK, command.operation_id, command.action, ACTOR, '0' * 64, ACTOR], 'RESOURCE_INTENT_ORIGINAL_CONFLICT')
            denied(cursor, 'RRL_RESOURCE_INTENT_API.describe', [body.operation_id, None], 'RESOURCE_INTENT_ORIGINAL_ACTOR_REQUIRED')
            for sql in ["update RRL_RESOURCE_INTENT_ABANDON set CONTROL_SHA256='0'where CONTROL_OPERATION_ID=:o", "delete from RRL_RESOURCE_INTENT_ABANDON where CONTROL_OPERATION_ID=:o", "insert into RRL_RESOURCE_INTENT_ABANDON select * from RRL_RESOURCE_INTENT_ABANDON where CONTROL_OPERATION_ID=:o"]:
                try:
                    cursor.execute(sql, o=body.operation_id)
                except oracledb.DatabaseError as error:
                    assert 'RESOURCE_INTENT_APPEND_ONLY' in str(error), str(error)
                else:
                    raise AssertionError('Direct tombstone mutation admitted')
            # This checks clean-entry enforcement, NOT the late-original tombstone race.
            denied(cursor, 'RRL_CASE_ASSIGNMENT_API.execute_command', [TASK, wire, ACTOR], 'DIRTY_TRANSACTION')
            assert call(cursor, 'RRL_RESOURCE_INTENT_API.describe', body.operation_id, ACTOR) == ack
            checks.extend(['absent_ABANDONED_exact_hash_identity', 'native_describe_resolution_and_wronghash_actor_guards', 'append_only_insert_update_delete', 'dirty_original_entry_denied_not_latefence_claim'])
        finally:
            rollback_connection(connection, cursor)
    assert snapshot(gateway) == before
    no_owned_history(gateway)
    checks.append('absent_tombstone_full_caller_rollback_both_UID_history_exact')


def recorded_trial(connect: Any, gateway: Any, before: dict[str, Any], checks: list[str]) -> None:
    from app.modules.resources.contracts_case_resource import CaseResourceCommand, CaseResourceAck
    from app.modules.resources.contracts_resource_intents import ResourceIntentResolution
    from app.modules.resources.infrastructure.case_resource_commands import canonical
    from app.modules.resources.infrastructure.resource_intent_commands import digest
    # Deliberately stale/future expected version guarantees a recoverable rejection before resource effects.
    command = CaseResourceCommand(operation_id=PREFIX + 'RECORDED', action='CLAIM', expected_assignment_version=before['task'][0]['assignment_version'] + 1, resource_session_id=55, reason='TEST_NOT_HARDWARE recorded rejection only, never start or claim retired CASE')
    wire = canonical(command)
    with connect() as connection:
        cursor = connection.cursor()
        try:
            assert cursor.callfunc('DBMS_TRANSACTION.LOCAL_TRANSACTION_ID', str, [False]) is None
            ack = call(cursor, 'RRL_CASE_ASSIGNMENT_API.execute_command', TASK, wire, ACTOR)
            receipt = CaseResourceAck.model_validate(ack)
            assert receipt.outcome == 'REJECTED' and receipt.error_code == 'CASE_RESOURCE_ASSIGNMENT_VERSION_CHANGED' and not receipt.changed and not receipt.stock_posted
            assert call(cursor, 'RRL_CASE_ASSIGNMENT_API.receipt', command.operation_id, ACTOR) == ack
            result = ResourceIntentResolution.model_validate(call(cursor, 'RRL_RESOURCE_INTENT_API.resolve', 'CASE', TASK, command.operation_id, command.action, ACTOR, digest(wire), ACTOR))
            assert result.status == 'RECORDED' and result.original_receipt == receipt and result.abandonment is None
            cursor.execute('select count(*)from RRL_RESOURCE_INTENT_ABANDON where DOMAIN=\'CASE\'and ORIGINAL_OPERATION_ID=:o', o=command.operation_id)
            assert cursor.fetchone() == (0,)
            checks.extend(['original_REJECTED_unchanged_and_read', 'RECORDED_resolution_does_not_create_ABANDONED'])
        finally:
            rollback_connection(connection, cursor)
    assert snapshot(gateway) == before
    no_owned_history(gateway)
    checks.append('recorded_REJECTED_full_caller_rollback_no_stock_clock_outbox')


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--execute-caller-rollback', action='store_true')
    args = parser.parse_args()
    if not args.execute_caller_rollback:
        print(json.dumps(dict(status='PREPARED_NOT_EXECUTED',case=TASK,actor=ACTOR,quantity_effect=False,scope='Cancelled CASE native absence/read/rejected/guard caller-rollback only; no committed late-fence race')))
        return
    assert os.environ.get('RESOURCE_INTENT_ROOT_APPLIED') == '1', 'Root must confirm applied/readback release'
    sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'api/wms_api_server')]
    from stock_posting_environment import load_local_oracle_environment
    load_local_oracle_environment()
    from app.db import oracle_connection
    from app.oracle_gateway import OracleGateway
    gateway = OracleGateway()
    before = snapshot(gateway)
    no_owned_history(gateway)
    started = time.perf_counter()
    checks: list[str] = []
    absent_trial(oracle_connection, gateway, before, checks)
    recorded_trial(oracle_connection, gateway, before, checks)
    report = dict(status='PASS_CALLER_ROLLBACK_ONLY',checks=checks,elapsed_seconds=time.perf_counter()-started,before=before,after=snapshot(gateway),metadata_commits=0,quantity_effect=False,hardware=False,pending=['committed metadata exact replay/late-original races','fresh active scoped CASE/TASK fixture','HTTP/UI composition','SQL attribution by coordinator'])
    FOLDER.mkdir(parents=True,exist_ok=True)
    (FOLDER/'caller-rollback-1138.json').write_text(json.dumps(report,indent=2,default=str),encoding='utf-8')
    print(json.dumps({'status':report['status'],'checks':len(checks),'metadata_commits':0,'quantity_effect':False}))


if __name__ == '__main__':
    main()
