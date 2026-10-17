"""Typed metadata commands; normalize before durable payload identity is computed."""
from datetime import datetime, timezone
from typing import Annotated, Literal, Any
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

Identifier = Annotated[str, StringConstraints(pattern=r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,79}$")]
Permission = Annotated[str, StringConstraints(pattern=r"^[a-z][a-z0-9_]{0,79}$")]
Title = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
Reason = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]
Kind = Literal["WAREHOUSE","DC","STORE","REGION","CARRIER","ZONE"]
class Input(BaseModel):
    model_config = ConfigDict(extra="forbid")
class Versioned(Input):
    expected_version: int = Field(strict=True, ge=0)
class RoleSave(Versioned):
    role_id: Identifier
    title: Title
    permissions: list[Permission] = Field(max_length=200)
    active: bool = Field(strict=True)
class ObjectSave(Versioned):
    kind: Kind
    object_id: Identifier
    title: Title
    parent_kind: Kind | None = None
    parent_id: Identifier | None = None
    active: bool = Field(strict=True)
class Member(Input):
    kind: Kind
    object_id: Identifier
class GroupSave(Versioned):
    group_id: Identifier
    title: Title
    member_kind: Kind
    members: list[Member] = Field(max_length=200)
    active: bool = Field(strict=True)
class Assign(Versioned):
    assignment_id: Identifier
    username: Annotated[str, StringConstraints(strip_whitespace=True,min_length=1,max_length=50)]
    role_id: Identifier
    scope_kind: Literal["WAREHOUSE","DC","STORE","REGION","CARRIER","ZONE","ORG_BRANCH","GROUP","SELF","NETWORK","PLATFORM"]
    scope_id: Annotated[str, StringConstraints(min_length=1,max_length=100)] | None = None
    membership: Literal["CURRENT","SNAPSHOT"] = "CURRENT"
    snapshot_version: int | None = Field(default=None,strict=True,ge=1)
    valid_from: datetime
    valid_until: datetime | None = None
    reason: Reason
    @field_validator("valid_from","valid_until")
    @classmethod
    def timezone_required(cls, value: datetime | None) -> datetime | None:
        if value is not None and (value.tzinfo is None or value.utcoffset() is None):
            raise ValueError("Timezone required")
        return value
class Revoke(Versioned):
    assignment_id: Identifier
    reason: Reason
class SpaceSave(Versioned):
    space_id: Identifier
    title: Title
class ArticleSave(Versioned):
    article_id: Annotated[str,StringConstraints(pattern=r"^[a-z][a-z0-9-]{1,79}$")]
    space_id: Identifier
    title: Title
    summary: Annotated[str,StringConstraints(min_length=1,max_length=1000)]
    body: Annotated[str,StringConstraints(min_length=1,max_length=20000)]
    related: list[Identifier] = Field(default_factory=list,max_length=30)
    sources: list[Annotated[str,StringConstraints(max_length=200)]] = Field(default_factory=list,max_length=20)
    required_permissions: list[Permission] = Field(default_factory=list,max_length=30)
    reason: Reason
class Publish(Versioned):
    article_id: Identifier
    reason: Reason
class Command(Input):
    operation_id: Annotated[str,StringConstraints(pattern=r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,99}$")]
    command_type: str
    payload: dict[str,Any]
class Explain(Input):
    permission: Permission
    object_kind: Literal["WAREHOUSE","DC","STORE","REGION","CARRIER","ZONE","PLATFORM"]
    object_id: Identifier | None = None
    username: str | None = Field(default=None,max_length=50)

ACCESS = {"ROLE_SAVE": RoleSave, "OBJECT_SAVE": ObjectSave, "GROUP_SAVE": GroupSave, "ASSIGN": Assign, "REVOKE": Revoke}
KNOWLEDGE = {"SPACE_SAVE": SpaceSave, "ARTICLE_SAVE": ArticleSave, "PUBLISH": Publish, "ARCHIVE": Publish}

def normalize(command: Command, domain: str) -> dict[str,Any]:
    models = ACCESS if domain == "ACCESS" else KNOWLEDGE
    model = models.get(command.command_type)
    if model is None:
        raise ValueError("Unknown command type")
    payload = model.model_validate(command.payload).model_dump(mode="python")
    for name,value in tuple(payload.items()):
        if isinstance(value, datetime): payload[name] = value.astimezone(timezone.utc).isoformat(timespec="microseconds")
    if "permissions" in payload: payload["permissions"] = sorted(set(payload["permissions"]))
    if "required_permissions" in payload: payload["required_permissions"] = sorted(set(payload["required_permissions"]))
    if command.command_type == "ASSIGN":
        from ..domain.access_assignments import AccessScope, RoleAssignment
        scope = AccessScope(payload["scope_kind"],payload["scope_id"],payload["membership"],payload["snapshot_version"])
        RoleAssignment("validation",payload["username"],payload["role_id"],scope,
                       model.model_validate(command.payload).valid_from,model.model_validate(command.payload).valid_until,"server",payload["reason"])
    return {"operation_id":command.operation_id,"command_type":command.command_type,"payload":payload}
