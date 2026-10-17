"""A gateway transports evidence; only persisted operator consent chooses the stock actor."""
from collections.abc import Callable
from typing import Any
from ..contracts_assembly_scale import AssemblyScaleError
from ..contracts_stock import StockCommand, StockPostingError

UNCERTAIN = {"RESULT_UNCERTAIN", "REQUEST_DEADLINE", "CONNECTION_UNUSABLE", "LOCK_RETRY_EXHAUSTED"}


def deliver_assembly_step(read_post: Callable[[str, str], dict[str, Any]],
                          post: Callable[[StockCommand], dict[str, Any]], step: str, caller: str) -> dict[str, Any]:
    context = read_post(step, caller)
    if not context["eligible"]:
        return {"step": context["step"], "posting": None}
    command = context["command"]
    # Native context derives this identity from the immutable assigned-session consent.
    # Request bodies and HTTP sender never supply the business actor.
    request = StockCommand(operation_id=command["operation_id"], command_type="CASE_PICK_CONFIRM",
        actor=command["actor"], source=command["source"], metadata=command["metadata"], lines=(), units=())
    try:
        result = post(request)  # The only stock writer owns a fresh transaction and its commit.
    except StockPostingError as exc:
        uncertain = exc.code in UNCERTAIN
        raise AssemblyScaleError("ASSEMBLY_POST_OUTCOME_UNCERTAIN" if uncertain else "ASSEMBLY_POST_REJECTED",
            "Укладка сохранена; проверьте результат исходной операции" if uncertain else "Измерение сохранено; требуется разбор отказа",
            503 if uncertain else 409, dict(operation_id=request.operation_id, step_id=step,
                archive_preserved=True, read_before_retry=True, retry_same_operation_id=True,
                outcome_confirmed=not uncertain, posting_code=exc.code, rule_reason=exc.rule_reason)) from exc
    confirmed = {**context["step"], "state": "APPLIED", "stock_posted": True}
    return {"step": confirmed, "posting": result}
