"""Read-only cross-owner return timeline, scoped to current receiving warehouse."""
from ..contracts import StoreReceiptError
from pathlib import Path
from typing import Any
import json


def return_progress(cursor: Any,approval_ids: list[str],actor: str|None)->dict[str,dict[str,Any]]:
    if not approval_ids or actor is None:
        return {}
    if len(approval_ids)>100:
        raise ValueError("RETURN_PROGRESS_BOUND_100")
    cursor.execute(Path(__file__).with_suffix(".sql").read_text(encoding="utf-8"),
                   ids=json.dumps(approval_ids),actor=actor)
    columns=[d[0].lower()for d in cursor.description]
    result={}
    for raw in cursor.fetchmany(101):
        row=dict(zip(columns,raw))
        if row["approval_operation_id"]in result:
            raise StoreReceiptError("RETURN_PROGRESS_AMBIGUOUS","Неоднозначная цепочка возврата; требуется сверка",409)
        row["warehouse_progress_visible"]=True
        result[row["approval_operation_id"]]=row
    return result
