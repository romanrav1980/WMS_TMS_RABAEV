from pydantic import BaseModel, Field, StrictBool, model_validator

class CaseCarrierReturnRequest(BaseModel):
    operation_id: str = Field(min_length=1,max_length=100)
    scan_container: str = Field(min_length=1,max_length=150)
    expected_content_version: int = Field(ge=0,strict=True)
    destinations: dict[str,str]

    allow_empty: StrictBool = False
    reason: str | None = Field(default=None, min_length=1, max_length=1000)

    @model_validator(mode="after")
    def validate_empty_decision(self) -> "CaseCarrierReturnRequest":
        if self.allow_empty:
            if self.destinations or not (self.reason or "").strip():
                raise ValueError("Empty cancellation requires no destinations and an explicit reason")
        elif not 1 <= len(self.destinations) <= 200:
            raise ValueError("Scanned destinations required for a physical return")
        if len(self.destinations) > 200 or any(not k or not v or len(v) > 60 for k, v in self.destinations.items()):
            raise ValueError("Bounded scanned destinations required")
        return self
