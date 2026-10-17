"""Each evidence transaction finishes before the existing stock runner receives its command."""
from collections.abc import Callable
import json
import re
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from ..application.assembly_scale_post import deliver_assembly_step
from ..contracts_assembly_recovery import AssemblyReconciliationRequest, AssemblyReconciliationAuthorization, AssemblyReconciliationCapture
from ..contracts_stock import StockCommand
from ..contracts_assembly_scale import (
    AssemblyScaleError, AssemblyStationPolicy, AssemblySkuPolicy, AssemblySessionOpen,
    AssemblyStepOpen, AssemblyCapture, AssemblyFinish,
)


def wire(body: Any) -> str:
    return json.dumps(body.model_dump(), ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False)


class AssemblyScales:
    def __init__(self, gateway: Any, posting: Callable[[StockCommand], dict[str, Any]]) -> None:
        self.gateway, self.posting = gateway, posting

    def _invoke(self, method: str, arguments: list[Any], readonly: bool = False, package: str = "RRL_ASSEMBLY_SCALE_API") -> dict[str, Any]:
        try:
            with self.gateway.transaction("Assembly scale " + method) as cursor:
                if readonly:
                    cursor.execute("set transaction read only")
                output = cursor.var(oracledb.DB_TYPE_CLOB)
                cursor.callproc(package + "." + method, [*arguments, output])
                return read_oracle_json(output.getvalue())
        except oracledb.DatabaseError as exc:
            code = exc.args[0].code
            status = 403 if code == 20882 else 404 if code == 1403 else 409 if 20800 <= code <= 20999 else 503
            message = str(exc.args[0]).split("\n", 1)[0]
            rule = re.search(r"ASSEMBLY_[A-Z0-9_]+", message)
            raise AssemblyScaleError(rule.group() if rule else "ASSEMBLY_NATIVE_REJECTED" if status < 500 else "ASSEMBLY_OUTCOME_UNCERTAIN",
                message, status) from exc

    def _read_post(self, step: str, caller: str) -> dict[str, Any]:
        return self._invoke("posting_request", [step, caller], True)

    def context(self, task: int, actor: str) -> dict[str, Any]:
        return self._invoke("context", [task, actor], True)

    def read_session(self, session: str, actor: str) -> dict[str, Any]:
        return self._invoke("read_session", [session, actor], True)

    def read_step(self, step: str, actor: str) -> dict[str, Any]:
        return self._invoke("read_step", [step, actor], True)

    def gateway_requests(self, device: str, sender: str) -> dict[str, Any]:
        return self._invoke("gateway_requests", [device, sender], True)

    def station_policy(self, device: str, body: AssemblyStationPolicy, actor: str) -> dict[str, Any]:
        return self._invoke("station_policy", [device, wire(body), actor])

    def sku_policy(self, body: AssemblySkuPolicy, actor: str) -> dict[str, Any]:
        return self._invoke("sku_policy", [wire(body), actor])

    def open_session(self, body: AssemblySessionOpen, actor: str) -> dict[str, Any]:
        return self._invoke("open_session", [wire(body), actor])

    def open_step(self, session: str, body: AssemblyStepOpen, actor: str) -> dict[str, Any]:
        return self._invoke("open_step", [session, wire(body), actor])

    def capture(self, body: AssemblyCapture | AssemblyReconciliationCapture, sender: str) -> dict[str, Any]:
        if isinstance(body, AssemblyReconciliationCapture):
            return self._capture_reconciliation(body, sender)
        # _invoke returns only after its evidence transaction commits; no dirty pre-writes reach posting.
        archived = self._invoke("capture", [wire(body), sender])
        try:
            outcome = deliver_assembly_step(self._read_post, self.posting, body.step_id, sender)
        except AssemblyScaleError as exc:
            exc.details["archive"] = archived
            exc.details["archive_preserved"] = True
            raise
        return {"archive": archived, **outcome}

    def placed(self, step: str, actor: str) -> dict[str, Any]:
        self._invoke("placed", [step, actor])
        return deliver_assembly_step(self._read_post, self.posting, step, actor)

    def finish(self, session: str, body: AssemblyFinish, actor: str) -> dict[str, Any]:
        return self._invoke("finish", [session, wire(body), actor])

    def _recover(self, method: str, arguments: list[Any], readonly: bool = False) -> dict[str, Any]:
        return self._invoke(method, arguments, readonly, package="RRL_ASSEMBLY_RECOVERY_API")

    def request_reconciliation(self, session: str, body: AssemblyReconciliationRequest, actor: str) -> dict[str, Any]:
        return self._recover("request_reconciliation", [session, wire(body), actor])

    def authorize_reconciliation(self, identity: str, body: AssemblyReconciliationAuthorization, actor: str) -> dict[str, Any]:
        return self._recover("authorize", [identity, wire(body), actor])

    def read_reconciliation(self, identity: str, actor: str) -> dict[str, Any]:
        return self._recover("read_reconciliation", [identity, actor], True)

    def _capture_reconciliation(self, body: AssemblyReconciliationCapture, sender: str) -> dict[str, Any]:
        archived = self._recover("capture", [wire(body), sender])
        try:
            state = self._recover("capture_state", [body.reconciliation_id, sender], True)
        except AssemblyScaleError as exc:
            exc.details.update(archive=archived, archive_preserved=True)
            raise
        return {"archive": archived, **state, "posting": None}
