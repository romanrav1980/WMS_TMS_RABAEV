"""Validated assignment contracts; not an authorization engine or database writer."""
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

ScopeKind = Literal["WAREHOUSE", "DC", "STORE", "REGION", "CARRIER", "ZONE", "ORG_BRANCH", "GROUP", "SELF", "NETWORK", "PLATFORM"]
MembershipMode = Literal["CURRENT", "SNAPSHOT"]

@dataclass(frozen=True)
class AccessScope:
    kind: ScopeKind
    object_id: str | None = None
    membership: MembershipMode = "CURRENT"
    snapshot_version: int | None = None

    def __post_init__(self) -> None:
        if self.kind not in {"WAREHOUSE", "DC", "STORE", "REGION", "CARRIER", "ZONE", "ORG_BRANCH", "GROUP", "SELF", "NETWORK", "PLATFORM"}:
            raise ValueError("Unknown scope kind")
        if self.membership not in {"CURRENT", "SNAPSHOT"}:
            raise ValueError("Unknown membership mode")
        needs_id = self.kind not in {"SELF", "NETWORK", "PLATFORM"}
        if needs_id != bool(self.object_id and self.object_id.strip()):
            raise ValueError("Scope identifier is missing or not applicable")
        if not needs_id and self.object_id is not None:
            raise ValueError("Global or SELF scope cannot carry an identifier")
        if self.membership == "SNAPSHOT":
            if self.kind not in {"GROUP", "ORG_BRANCH"} or type(self.snapshot_version) is not int or self.snapshot_version < 1:
                raise ValueError("Snapshot requires a group/branch and positive version")
        elif self.snapshot_version is not None:
            raise ValueError("Current membership cannot carry a snapshot version")

@dataclass(frozen=True)
class RoleAssignment:
    assignment_id: str
    username: str
    role_id: str
    scope: AccessScope
    valid_from: datetime
    valid_until: datetime | None
    assigned_by: str
    reason: str
    version: int = 1
    revoked_at: datetime | None = None

    def __post_init__(self) -> None:
        if any(not value.strip() for value in (self.assignment_id, self.username, self.role_id, self.assigned_by, self.reason)):
            raise ValueError("Identity, author and reason are required")
        if type(self.version) is not int or self.version < 1:
            raise ValueError("Positive version required")
        for instant in (self.valid_from, self.valid_until, self.revoked_at):
            if instant is not None and (instant.tzinfo is None or instant.utcoffset() is None):
                raise ValueError("Timezone-aware timestamps required")
        if self.valid_until is not None and self.valid_until <= self.valid_from:
            raise ValueError("Assignment interval must be non-empty")
