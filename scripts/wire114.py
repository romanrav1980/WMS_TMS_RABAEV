from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/finance/infrastructure/expense_reports.py");s=p.read_text(encoding="utf-8-sig")
s=s.replace("from ..domain.amount import rate_value","from ..domain.amount import rate_value\nfrom ..domain.expense_value import signed_amount\nfrom .expense_correction import correction_source")
s=s.replace("reason: str,actor: str) -> dict[str,Any]:","reason: str,actor: str,correction: str|None=None,expected: str|None=None) -> dict[str,Any]:")
s=s.replace("try:amount=rate_value(value)","try:amount=signed_amount(value,correction is not None)")
a=s.index('    if amount<=0');b=s.index('    with gateway.transaction',a)
s=s[:a]+'''    if (correction is not None)!=(expected is not None):raise LogisticsCostError("EXPENSE_CORRECTION_TOTAL_REQUIRED","Для коррекции нужны исходный расход и ожидаемый итог",422)
    try:expected_value=rate_value(expected) if expected is not None else None
    except ValueError as exc:raise LogisticsCostError("EXPENSE_CORRECTION_TOTAL_INVALID",str(exc),422) from exc
    sign=-1 if amount<0 else 1;quantity=format(amount,".2f")
    source_values=[ware,code,kind,object_id,quantity,currency,day,reference,reason,actor]
    if correction is not None:source_values.extend([correction,format(expected_value,".2f")])
    digest=sha256(json.dumps(source_values,ensure_ascii=False,separators=(",",":")).encode()).digest()
'''+s[b:]
a=s.index('        cur.execute("select NAME,VERSION_NO');b=s.index('        if kind=="TRIP":',a)
s=s[:a]+'''        if correction:
            name,version=correction_source(cur,correction,expected_value,amount,ware,code,kind,object_id,currency);article=(name,version)
        else:
            cur.execute("select NAME,VERSION_NO,OBJECT_SCOPE,INCLUDED_IN_RATE,ACTIVE_FLAG from RRL_LOGISTICS_EXP_ARTICLE where CODE=:code",{"code":code});article=cur.fetchone()
            if not article or article[2]not in(kind,"BOTH")or article[3]!=0 or article[4]!=1:raise LogisticsCostError("EXPENSE_EXTRA_ARTICLE_REQUIRED","Выберите активную дополнительную статью, не включённую в ставку")
'''+s[b:]
s=s.replace('        cur.setinputsizes(result_body=', '        if correction:result.update(correction_of_operation_id=correction,expected_confirmed_total=format(expected_value,".2f"))\n        cur.setinputsizes(result_body=')
s=s.replace("ACTOR,RESULT_JSON)values","ACTOR,RESULT_JSON,ADJUSTMENT_SIGN,CORRECTION_OF_OP,EXPECTED_CONFIRMED_TOTAL)values").replace(":actor,:result_body)\"",":actor,:result_body,:sign,:correction,:expected)\"")
s=s.replace('"amount":amount,"currency":currency','"amount":abs(amount),"currency":currency').replace('"result_body":json.dumps(result)})','"result_body":json.dumps(result),"sign":sign,"correction":correction,"expected":expected_value})')
out[str(p)]=s
for name in ["contracts_expenses.py","infrastructure/logistics_expenses.py"]:
 p=Path("api/wms_api_server/app/modules/finance")/name;s=p.read_text(encoding="utf-8-sig")
 s=s.replace("reason: str,actor: str) -> dict[str,Any]:","reason: str,actor: str,correction: str|None=None,expected: str|None=None) -> dict[str,Any]:",1)
 if name.startswith("infrastructure"):
  s=s.replace("currency,day,reference,reason,actor)","currency,day,reference,reason,actor,correction,expected)")
  s=s.replace("to_char(e.AMOUNT,'TM9') AMOUNT","to_char(e.AMOUNT*e.ADJUSTMENT_SIGN,'TM9') AMOUNT").replace("e.ACTOR REPORTER","e.ACTOR REPORTER,e.CORRECTION_OF_OP,e.EXPECTED_CONFIRMED_TOTAL")
 out[str(p)]=s
p=Path("api/wms_api_server/app/modules/finance/api/logistics_expense_routes.py");s=p.read_text(encoding="utf-8-sig")
needle='    expense_date: date\n';assert needle in s;s=s.replace(needle,needle+'    correction_of_operation_id: str|None=Field(default=None,strict=True,min_length=1,max_length=100)\n    expected_confirmed_total: str|None=Field(default=None,strict=True,min_length=1,max_length=40)\n')
s=s.replace("body.document_reference,body.reason,user.username)","body.document_reference,body.reason,user.username,body.correction_of_operation_id,body.expected_confirmed_total)")
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/finance/infrastructure/expense_decisions.py");s=p.read_text(encoding="utf-8-sig")
s=s.replace("from .cost_access import require_warehouse","from .cost_access import require_warehouse\nfrom .expense_correction import lock_correction_root,assert_correction_decision")
s=s.replace('        cur.execute("select WARE_ID','        root=lock_correction_root(cur,expense)\n        cur.execute("select WARE_ID',1)
s=s.replace('        if source[1]=="VEHICLE"','        if root:assert_correction_decision(cur,expense,root,phase,outcome,basis)\n        if source[1]=="VEHICLE"',1)
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/finance/infrastructure/expense_allocation.py");s=p.read_text(encoding="utf-8-sig")
s=s.replace("CURRENCY from RRL_LOGISTICS_EXPENSE where OPERATION_ID=:id for update","CURRENCY,ADJUSTMENT_SIGN from RRL_LOGISTICS_EXPENSE where OPERATION_ID=:id for update")
s=s.replace("kind,trip,ware,amount,currency=source","kind,trip,ware,amount,currency,sign=source")
s=s.replace('"amount":str(shares[row["key"]])','"amount":str(shares[row["key"]]*sign)')
s=s.replace('"amount":format(amount,".2f")','"amount":format(amount*sign,".2f")')
s=s.replace("to_char(e.AMOUNT,'TM9') AMOUNT","to_char(e.AMOUNT*e.ADJUSTMENT_SIGN,'TM9') AMOUNT")
s=s.replace("e.CURRENCY,e.DOCUMENT_REFERENCE","e.CURRENCY,e.DOCUMENT_REFERENCE,e.CORRECTION_OF_OP")
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
