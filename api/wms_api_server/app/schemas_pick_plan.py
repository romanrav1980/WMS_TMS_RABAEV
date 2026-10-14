from pydantic import BaseModel, Field

class PickingPlanCreateRequest(BaseModel):
    operation_id: str | None=Field(default=None,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    customer_order_id: int
    plan_strategy: str = "FEFO"
    created_by: str | None = None


