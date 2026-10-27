"""C-0176: remove selected physical places of one assembly (ST) from a trip; the rest of the assembly stays assigned."""
from typing import Any, Protocol
from pydantic import BaseModel, ConfigDict, Field, StrictInt, model_validator


class PlaceRemovalCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation_id: str = Field(min_length=8, max_length=100, pattern=r"^[A-Za-z0-9_.:-]+$")
    st_number: str = Field(min_length=1, max_length=200)
    member_ids: list[StrictInt] = Field(min_length=1, max_length=200)
    expected_source_hash: str = Field(pattern=r"^[A-F0-9]{64}$")  # the membership version read with the places
    reason: str = Field(min_length=3, max_length=500)

    @model_validator(mode="after")
    def distinct_members(self) -> "PlaceRemovalCommand":
        if len(set(self.member_ids)) != len(self.member_ids) or any(x <= 0 for x in self.member_ids):
            raise ValueError("Distinct positive place ids are required")
        return self


class PlaceRemovalError(RuntimeError):
    def __init__(self, code: str, status: int) -> None:
        self.code, self.status = code, status
        super().__init__(code)


class PlaceRemovalPort(Protocol):
    def places(self, trip: int, st_number: str, actor: str) -> dict[str, Any]: ...
    def remove(self, trip: int, body: PlaceRemovalCommand, actor: str) -> dict[str, Any]: ...


def place_removal_service() -> PlaceRemovalPort:
    raise RuntimeError("Place removal is not wired")
