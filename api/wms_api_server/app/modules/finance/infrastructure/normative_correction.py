"""Bridge normative cost corrections into the existing two-phase expense workflow."""
from decimal import Decimal
from typing import Any


def validate_report(cursor: Any,cost: str,ware: int,kind: str,object_id: int,currency: str,
                    delta: Decimal,expected: Decimal)->None:
    cursor.callproc("RRL_NORM_COST_CORRECTION.validate_report",[cost,ware,kind,object_id,currency,delta,expected])


def lock_root(cursor: Any,expense: str)->str|None:
    cursor.execute("select COST_CORRECTION_OF_OP from RRL_LOGISTICS_EXPENSE where OPERATION_ID=:id",id=expense)
    row=cursor.fetchone()
    if not row or row[0]is None:return None
    cost=row[0]
    cursor.execute("select OPERATION_ID from RRL_LOGISTICS_COST_RUN where OPERATION_ID=:id for update",id=cost)
    if cursor.fetchone()is None:return None
    return str(cost)


def confirmed_total(cursor: Any,cost: str)->str:
    cursor.execute("select to_char(RRL_NORM_COST_CORRECTION.confirmed_total(:id),'TM9','NLS_NUMERIC_CHARACTERS=''.,''')from dual",id=cost)
    return str(cursor.fetchone()[0])
