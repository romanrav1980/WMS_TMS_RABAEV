"""Fault recovery contract: preserve committed work and immutable source command identities."""
from contextlib import contextmanager
from copy import deepcopy
import json
import sys
from pathlib import Path
import pytest
from fastapi import HTTPException

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "api/wms_api_server"))
from app.modules.fulfillment.application.wave_launch_continuation import run_wave_launch, STEPS
from app.modules.fulfillment.infrastructure.wave_continuation import source_request
from app.modules.fulfillment.infrastructure.wave_launch_adapter import post_frozen_sources


class Ledger:
    def __init__(self):
        self.done, self.effects, self.failures, self.frozen = set(), [], {}, None
        self.current, self.authorized, self.in_metadata = 0, True, False
        self.step_calls = 0

    def completed(self):
        if not self.authorized:
            raise PermissionError("current warehouse grant revoked")
        return self.done == set(range(1, 8))

    @contextmanager
    def step(self, number):
        self.step_calls += 1
        if not self.authorized:
            raise PermissionError("current warehouse grant revoked")
        before = deepcopy((self.done, self.effects, self.frozen))
        self.current, self.in_metadata = number, True
        try:
            yield self, number not in self.done
        except Exception:
            self.done, self.effects, self.frozen = before
            raise
        finally:
            self.in_metadata = False

    def finish(self, bound):
        self.done.add(self.current)

    def fail(self, number, code):
        if not self.authorized:
            raise PermissionError("revoked")
        self.failures[number] = code

    def freeze_sources(self, bound):
        if self.frozen is None:
            self.frozen = [source_request("launch-A", 10, "actor", 15, None, None, None)]


def execute(repo, *, fault=None, post=None, launch=None):
    def actions(bound, wave, actor):
        def action(name):
            bound.effects.append(name)
            if name == fault:
                raise RuntimeError("middle-step failure")
        return {name: lambda name=name: action(name) for name in STEPS}
    return run_wave_launch(10, "launch-A", "actor", launch or (lambda: None), repo,
                          actions, post or (lambda repository: None))


def test_middle_metadata_failure_rolls_back_action_and_resumes_only_remaining():
    repo = Ledger()
    with pytest.raises(HTTPException) as caught:
        execute(repo, fault="RELEASE_QUEUE")
    assert caught.value.detail["launch_outcome"] == "APPLIED"
    assert caught.value.detail["continuation_state"] == "FAILED"
    assert repo.done == {1, 2, 3, 4}
    assert "RELEASE_QUEUE" not in repo.effects
    original = list(repo.effects)
    execute(repo)
    assert repo.effects[:len(original)] == original
    assert repo.effects.count("SETTINGS") == 1
    assert repo.effects.count("RELEASE_QUEUE") == 1
    assert repo.done == set(range(1, 8))


def test_unknown_source_outcome_keeps_frozen_body_and_separate_stock_transaction():
    repo, calls = Ledger(), []
    def uncertain(repository):
        assert not repository.in_metadata
        calls.append(repository.frozen[0])
        raise TimeoutError("answer lost after possible commit")
    with pytest.raises(HTTPException):
        execute(repo, post=uncertain)
    assert repo.done == {1, 2}
    def recovered(repository):
        assert not repository.in_metadata
        calls.append(repository.frozen[0])
    execute(repo, post=recovered)
    assert calls[0] == calls[1]
    assert repo.effects.count("SETTINGS") == 1


def test_complete_replay_still_checks_current_access_and_executes_no_step():
    repo = Ledger()
    execute(repo)
    before = list(repo.effects)
    count = repo.step_calls
    execute(repo)
    assert repo.effects == before
    assert repo.step_calls == count
    repo.authorized = False
    with pytest.raises(HTTPException) as caught:
        execute(repo)
    assert caught.value.detail["continuation_state"] == "UNCONFIRMED"
    assert repo.effects == before


def test_launch_uncertainty_does_not_create_continuation_failure_or_run_steps():
    repo = Ledger()
    def unknown():
        raise HTTPException(503, detail={"outcome_confirmed": False})
    with pytest.raises(HTTPException) as caught:
        execute(repo, launch=unknown)
    assert caught.value.detail == {"outcome_confirmed": False}
    assert not repo.done and not repo.effects and not repo.failures


def test_source_key_is_bound_to_original_launch_and_row_not_retry_time():
    a = source_request("launch-A", 10, "actor", 15, None, None, None)
    assert a == source_request("launch-A", 10, "actor", 15, None, None, None)
    assert json.loads(a)["operation_id"] != json.loads(source_request("launch-B", 10, "actor", 15, None, None, None))["operation_id"]
    assert json.loads(a)["metadata"]["launch_operation_id"] == "launch-A"


def test_existing_request_is_returned_byte_for_byte_without_new_id():
    body = source_request("launch-A", 10, "actor", 15, None, None, None)
    op = json.loads(body)["operation_id"]
    assert source_request("other-launch", 10, "other-actor", 15, op, body, len(body)) == body
    with pytest.raises(ValueError, match="IDENTITY_CONFLICT"):
        source_request("launch-A", 10, "actor", 16, op, body, len(body))


@pytest.mark.parametrize("operation,saved,length", [("old", None, None), (None, "{}", 2), ("old", "{}", 4001)])
def test_incomplete_or_oversized_old_source_never_gets_replacement_key(operation, saved, length):
    with pytest.raises(ValueError, match="EXISTING_INTENT_INCOMPLETE"):
        source_request("launch-A", 10, "actor", 15, operation, saved, length)


def test_applied_source_is_not_reevaluated_or_posted_again(monkeypatch):
    class Repository:
        def sources(self):
            return [{"operation_id": "old", "body": "not needed", "state": "APPLIED"}]
    monkeypatch.setattr("app.modules.fulfillment.infrastructure.wave_launch_adapter.StockPosting",
                        lambda: pytest.fail("APPLIED source must remain finished"))
    post_frozen_sources(Repository())
