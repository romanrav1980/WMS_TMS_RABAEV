"""Focused transaction-runner checks; no claim of Oracle concurrency acceptance."""
import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "api/wms_api_server"))
import oracledb
from pydantic import ValidationError
from app.modules.inventory.contracts_stock import StockCommand, StockLine, StockPostingError
from app.modules.inventory.api.stock_command_routes import ManualMoveRequest
from app.modules.inventory.infrastructure import stock_posting_uow as uow


class Variable:
    def __init__(self):
        self.value = None
    def getvalue(self):
        return self.value
    def setvalue(self, position, value):
        self.value = value


class Cursor:
    def __init__(self, connection):
        self.connection = connection
    def var(self, kind):
        return Variable()
    def execute(self, sql, binds=None):
        c = self.connection
        if "prepare_command" in sql:
            c.requests.append(binds["payload"].getvalue())
        elif "execute_prepared" in sql:
            c.pending += 1
            if c.fail_once:
                c.fail_once = False
                raise oracledb.DatabaseError(SimpleNamespace(code=60))
            binds["result"].setvalue(0, json.dumps({"operation_id": "same-id", "status": "APPLIED"}))
        elif "reset_connection" in sql:
            c.resets += 1
    def fetchone(self):
        return ("ACTIVE",)
    def close(self):
        pass


class Connection:
    call_timeout = 0
    autocommit = False
    def __init__(self, fail_once=False, uncertain=False):
        self.fail_once = fail_once
        self.uncertain = uncertain
        self.pending = 0
        self.committed = 0
        self.rollbacks = 0
        self.resets = 0
        self.requests = []
    def cursor(self):
        return Cursor(self)
    def rollback(self):
        self.pending = 0
        self.rollbacks += 1
    def commit(self):
        self.committed += self.pending
        self.pending = 0
        if self.uncertain:
            raise oracledb.DatabaseError(SimpleNamespace(code=3113))


class Pool:
    def __init__(self, connection):
        self.connection = connection
        self.acquires = self.drops = self.releases = 0
    def acquire(self):
        self.acquires += 1
        return self.connection
    def release(self, connection):
        self.releases += 1
    def drop(self, connection):
        self.drops += 1


def command():
    return StockCommand("same-id", "MANUAL_MOVE", "authenticated-user",
                        (StockLine(1, "legacy-pallet", "ART", "2.5", "EA", "A", "B"),),
                        {"type": "MANUAL", "warehouse_id": 1, "reason": "Transfer"})


class StockRunnerTests(unittest.TestCase):
    def test_deadlock_rolls_back_the_whole_attempt_and_reuses_exact_request(self):
        connection = Connection(fail_once=True)
        pool = Pool(connection)
        with patch.object(uow, "_oracle_pool", return_value=pool):
            result = uow.StockPosting(wait=lambda _: None).post(command())
        self.assertEqual(result["status"], "APPLIED")
        self.assertEqual((connection.committed, connection.rollbacks, pool.acquires), (1, 1, 1))
        self.assertEqual(connection.requests, [command().canonical_json()] * 2)
        self.assertEqual((connection.resets, pool.releases), (2, 1))

    def test_unknown_commit_is_never_automatically_retried(self):
        connection = Connection(uncertain=True)
        pool = Pool(connection)
        with patch.object(uow, "_oracle_pool", return_value=pool):
            with self.assertRaises(StockPostingError) as error:
                uow.StockPosting(wait=lambda _: None).post(command())
        self.assertEqual(error.exception.code, "RESULT_UNCERTAIN")
        self.assertEqual((len(connection.requests), connection.committed, pool.drops), (1, 1, 1))

    def test_api_rejects_float_quantity_and_actor_override(self):
        body = {"operation_id": "x", "warehouse_id": 1, "reason": "Transfer",
                "lines": [{"line_number": 1, "uid": "legacy-pallet", "article": "ART", "quantity": 2.5,
                           "unit": "EA", "source_cell": "A", "target_cell": "B"}]}
        with self.assertRaises(ValidationError):
            ManualMoveRequest(**body)
        body["lines"][0]["quantity"] = "2.5"
        body["actor"] = "admin"
        with self.assertRaises(ValidationError):
            ManualMoveRequest(**body)

    def test_pool_cleanup_failure_does_not_hide_a_known_committed_result(self):
        connection = Connection()
        pool = Pool(connection)
        def failed_release(connection):
            raise RuntimeError("Pool release failed")
        pool.release = failed_release
        with patch.object(uow, "_oracle_pool", return_value=pool):
            result = uow.StockPosting(wait=lambda _: None).post(command())
        self.assertEqual(result["status"], "APPLIED")
        self.assertEqual((connection.committed, pool.drops), (1, 1))

    def test_expired_request_does_not_start_a_posting(self):
        connection = Connection()
        pool = Pool(connection)
        with patch.object(uow, "_oracle_pool", return_value=pool), patch.object(uow, "monotonic", side_effect=[0, 31]):
            with self.assertRaises(StockPostingError) as error:
                uow.StockPosting(wait=lambda _: None).post(command())
        self.assertEqual(error.exception.code, "REQUEST_DEADLINE")
        self.assertEqual(connection.requests, [])
        self.assertEqual(connection.committed, 0)


if __name__ == "__main__":
    unittest.main()
