from typing import Any

# K-0007: строка допрасхода счёта вместе с основанием суммы.
# Решения стадий присоединяются однозначно: unique(EXPENSE_OPERATION_ID,PHASE); распределение — unique(EXPENSE_OPERATION_ID).
# AMOUNT — подписанная сумма самой строки; CONFIRMED_TOTAL — исходный расход плюс подтверждённые финконтролем коррекции
# (как expense_correction.confirmed_total), только для исходного расхода; сумма распределения сюда не подмешивается.
INVOICE_EXPENSES_SQL="""select e.OPERATION_ID,e.ARTICLE_CODE,e.ARTICLE_NAME,e.OBJECT_ID TT_ID,e.WARE_ID,to_char(e.EXPENSE_DATE,'YYYY-MM-DD') EXPENSE_DATE,
e.ACTOR REPORTER,to_char(e.AMOUNT*e.ADJUSTMENT_SIGN,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') AMOUNT,e.CURRENCY,e.DOCUMENT_REFERENCE,
e.CORRECTION_OF_OP,e.COST_CORRECTION_OF_OP,to_char(e.EXPECTED_CONFIRMED_TOTAL,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') EXPECTED_CONFIRMED_TOTAL,
case when e.CORRECTION_OF_OP is null and e.COST_CORRECTION_OF_OP is null then to_char(e.AMOUNT+nvl((select sum(cx.AMOUNT*cx.ADJUSTMENT_SIGN)
 from RRL_LOGISTICS_EXPENSE cx join RRL_LOGISTICS_EXP_DECISION cf on cf.EXPENSE_OPERATION_ID=cx.OPERATION_ID and cf.PHASE='FINANCE' and cf.OUTCOME='APPROVE'
 where cx.CORRECTION_OF_OP=e.OPERATION_ID),0),'TM9','NLS_NUMERIC_CHARACTERS=''.,''') end CONFIRMED_TOTAL,
l.OPERATION_ID LOGIST_OPERATION_ID,l.OUTCOME LOGIST_OUTCOME,l.ACTOR LOGIST_ACTOR,l.DECISION_REFERENCE LOGIST_DECISION_REFERENCE,
f.OPERATION_ID FINANCE_OPERATION_ID,f.OUTCOME FINANCE_OUTCOME,f.ACTOR FINANCE_ACTOR,f.DECISION_REFERENCE FINANCE_DECISION_REFERENCE,
a.OPERATION_ID ALLOCATION_OPERATION_ID,a.DISTRIBUTION_BASIS,(select count(*)from RRL_LOGISTICS_EXP_ALLOC_LINE al where al.OPERATION_ID=a.OPERATION_ID) GOODS_LINES
from RRL_LOGISTICS_EXPENSE e join RRL_TRANSPORT_TASK t on e.OBJECT_KIND='TRIP' and t.ID=e.OBJECT_ID
join RUSERS u on u.ID=:actor and nvl(u.DELETED,0)=0 and(u.WARE_ID=e.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN')
left join RRL_LOGISTICS_EXP_DECISION l on l.EXPENSE_OPERATION_ID=e.OPERATION_ID and l.PHASE='LOGIST'
left join RRL_LOGISTICS_EXP_DECISION f on f.EXPENSE_OPERATION_ID=e.OPERATION_ID and f.PHASE='FINANCE'
left join RRL_LOGISTICS_EXP_ALLOCATION a on a.EXPENSE_OPERATION_ID=e.OPERATION_ID
where t.PAY_ORDER_ID=:id order by e.EXPENSE_DATE,e.OPERATION_ID fetch first 200 rows only"""

def invoice_expenses(gateway: Any,invoice_id: int,actor: str) -> list[dict[str,Any]]:
    return gateway.fetch_all(INVOICE_EXPENSES_SQL,{"id":invoice_id,"actor":actor})
