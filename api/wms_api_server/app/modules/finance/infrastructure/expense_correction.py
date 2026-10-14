from decimal import Decimal
from typing import Any
from ..contracts import LogisticsCostError

def confirmed_total(cursor: Any,expense: str) -> Decimal:
    cursor.execute("""select to_char(e.AMOUNT+nvl((select sum(c.AMOUNT*c.ADJUSTMENT_SIGN)
    from RRL_LOGISTICS_EXPENSE c join RRL_LOGISTICS_EXP_DECISION f on f.EXPENSE_OPERATION_ID=c.OPERATION_ID
    and f.PHASE='FINANCE' and f.OUTCOME='APPROVE' where c.CORRECTION_OF_OP=e.OPERATION_ID),0),'TM9','NLS_NUMERIC_CHARACTERS=''.,''')
    from RRL_LOGISTICS_EXPENSE e where e.OPERATION_ID=:id and e.CORRECTION_OF_OP is null and e.COST_CORRECTION_OF_OP is null""",{"id":expense})
    row=cursor.fetchone()
    if not row:raise LogisticsCostError("EXPENSE_ORIGINAL_REQUIRED","Корректировать можно только исходный расход")
    return Decimal(row[0])

def correction_source(cursor: Any,expense: str,expected: Decimal,delta: Decimal,ware: int,code: str,kind: str,object_id: int,currency: str) -> tuple[str,int]:
    cursor.execute("select WARE_ID,ARTICLE_CODE,OBJECT_KIND,OBJECT_ID,CURRENCY,ARTICLE_NAME,ARTICLE_VERSION from RRL_LOGISTICS_EXPENSE where OPERATION_ID=:id and CORRECTION_OF_OP is null and COST_CORRECTION_OF_OP is null for update",{"id":expense})
    row=cursor.fetchone()
    if not row or row[:5]!=(ware,code,kind,object_id,currency):raise LogisticsCostError("EXPENSE_CORRECTION_ORIGINAL_IDENTITY","Коррекция должна сохранять исходный объект, статью, склад и валюту")
    cursor.execute("select count(*)from RRL_LOGISTICS_EXP_DECISION where EXPENSE_OPERATION_ID=:id and PHASE='FINANCE' and OUTCOME='APPROVE'",{"id":expense})
    if cursor.fetchone()[0]!=1:raise LogisticsCostError("EXPENSE_CORRECTION_ORIGINAL_APPROVAL","Исходный расход ещё не подтверждён")
    total=confirmed_total(cursor,expense)
    if total!=expected or total+delta<0:raise LogisticsCostError("EXPENSE_CORRECTION_CURRENT_TOTAL","Подтверждённая сумма изменилась или коррекция превышает расход")
    return row[5],int(row[6])

def lock_correction_root(cursor: Any,expense: str) -> str|None:
    cursor.execute("select CORRECTION_OF_OP from RRL_LOGISTICS_EXPENSE where OPERATION_ID=:id",{"id":expense});row=cursor.fetchone()
    if not row or row[0]is None:return None
    root=row[0]
    cursor.execute("select OPERATION_ID from RRL_LOGISTICS_EXPENSE where OPERATION_ID=:id for update",{"id":root})
    return root

def assert_correction_decision(cursor: Any,expense: str,root: str,phase: str,outcome: str,basis: str) -> None:
    cursor.execute("select DISTRIBUTION_BASIS from RRL_LOGISTICS_EXP_DECISION where EXPENSE_OPERATION_ID=:id and PHASE='FINANCE' and OUTCOME='APPROVE'",{"id":root});original=cursor.fetchone()
    if not original or outcome=="APPROVE" and original[0]!=basis:raise LogisticsCostError("EXPENSE_CORRECTION_ORIGINAL_BASIS","Коррекция сохраняет исходную согласованную базу")
    if phase!="FINANCE" or outcome!="APPROVE":return
    cursor.execute("select to_char(AMOUNT*ADJUSTMENT_SIGN,'TM9','NLS_NUMERIC_CHARACTERS=''.,'''),to_char(EXPECTED_CONFIRMED_TOTAL,'TM9','NLS_NUMERIC_CHARACTERS=''.,''')from RRL_LOGISTICS_EXPENSE where OPERATION_ID=:id",{"id":expense});delta,expected=cursor.fetchone()
    total=confirmed_total(cursor,root)
    if total!=Decimal(expected)or total+Decimal(delta)<0:raise LogisticsCostError("EXPENSE_CORRECTION_CURRENT_TOTAL","Перед подтверждением изменился исходный итог; требуется новый акт коррекции")
