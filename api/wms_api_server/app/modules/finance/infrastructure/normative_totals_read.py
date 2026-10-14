"""One indexed grouped read for bounded, already-authorised normative sources."""
from decimal import Decimal,localcontext
from typing import Any
from ..contracts import LogisticsCostError


def confirmed_totals(cursor: Any,originals: dict[str,str])->dict[str,str]:
    if not originals:return {}
    if len(originals)>200:
        raise LogisticsCostError("NORMATIVE_TOTAL_SOURCE_BOUND","Не более 200 исходных финансовых записей")
    binds={"cost_"+str(i):op for i,op in enumerate(originals)}
    placeholders=",".join(":"+name for name in binds)
    cursor.execute("""select e.COST_CORRECTION_OF_OP,
     to_char(sum(e.AMOUNT*e.ADJUSTMENT_SIGN),'TM9',q'[NLS_NUMERIC_CHARACTERS='.,']')
     from RRL_LOGISTICS_EXPENSE e join RRL_LOGISTICS_EXP_DECISION f
      on f.EXPENSE_OPERATION_ID=e.OPERATION_ID and f.PHASE='FINANCE'and f.OUTCOME='APPROVE'
     where e.COST_CORRECTION_OF_OP in ("""+placeholders+")group by e.COST_CORRECTION_OF_OP",binds)
    adjustments=dict(cursor.fetchall());result={}
    with localcontext()as context:
        context.prec=80
        for op,value in originals.items():
            total=Decimal(value)+Decimal(adjustments.get(op,"0"))
            if not total.is_finite()or total<0:
                raise LogisticsCostError("NORMATIVE_CONFIRMED_TOTAL_INVALID","Некорректный итог исходного финансового документа")
            result[op]=format(total.normalize(),"f")
    return result
