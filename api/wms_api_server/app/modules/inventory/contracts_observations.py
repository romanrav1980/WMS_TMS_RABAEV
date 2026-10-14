"""Framework-free inputs and port for existing inventory observation commands."""
from dataclasses import asdict, dataclass, field
from typing import Any, Protocol


class InventoryObservationError(RuntimeError):
    def __init__(self, code: str, status: int = 409, operation_id: str = "") -> None:
        self.code = code
        self.status = status
        self.operation_id = operation_id
        super().__init__(code)


@dataclass(frozen=True)
class CountScan:
    system_code: str
    profile_code: str
    code: str


@dataclass(frozen=True)
class CountObservation:
    uid: str
    cell: str
    article: str
    unit: str
    quantity: str
    expected_stock_version: int
    scans: list[CountScan] = field(default_factory=list)
    unit_keys: list[str] = field(default_factory=list)

    def wire(self, include_scans: bool = True) -> dict[str, Any]:
        result = asdict(self)
        if not include_scans:
            result.pop("scans")
        return result


@dataclass(frozen=True)
class CountSubmission:
    operation_id: str
    revision_id: int
    reason: str
    counts: list[CountObservation]
    inventory_task_id: int | None = None

    @classmethod
    def from_wire(cls, value: dict[str, Any]) -> "CountSubmission":
        counts=[]
        for row in value["counts"]:
            counts.append(CountObservation(**{**row,"scans":[CountScan(**scan) for scan in row.get("scans",[])]}))
        return cls(operation_id=value["operation_id"],revision_id=value["revision_id"],
                   reason=value["reason"],counts=counts,inventory_task_id=value.get("inventory_task_id"))


class InventoryObservationsPort(Protocol):
    def lots(self, revision_id: int, cell: str, article: str | None, actor: str) -> dict[str, Any]: ...
    def count(self, request: CountSubmission, actor: str) -> dict[str, Any]: ...
    def create_revision(self, warehouse_id: int, actor: str) -> dict[str, Any]: ...
    def register_lot(self, operation_id: str, revision_id: int, metadata: dict[str, Any], actor: str) -> dict[str, Any]: ...


def inventory_observations_service() -> InventoryObservationsPort:
    raise RuntimeError("Inventory observation service not wired")
