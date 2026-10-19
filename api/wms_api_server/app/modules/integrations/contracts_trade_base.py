from typing import Annotated
from pydantic import BaseModel,ConfigDict,Field

Key = Annotated[str, Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_.:/-]+$")]

class TradeModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


