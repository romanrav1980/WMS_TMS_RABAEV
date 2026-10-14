from pathlib import Path
import json
p=Path("api/wms_api_server/app/modules/integrations/domain/article_logistics.py");s=p.read_text(encoding="utf-8").replace("from typing import Any","from typing import Any\nfrom fractions import Fraction")
start=s.index("def positive_measure(");end=s.index("\ndef factor(",start)
s=s[:start]+"""def positive_measure(raw: str,factor: Decimal) -> Decimal:
    if not isinstance(raw,str)or len(raw)>64:
        raise ValueError("SAP logistics measurement text exceeds bound")
    try:value=Decimal(raw)
    except InvalidOperation as exc:raise ValueError("Invalid SAP logistics measurement") from exc
    if not value.is_finite()or value<=0 or value>Decimal("1000000000")or value<Decimal("0.000000000001"):
        raise ValueError("SAP logistics measurement outside supported range")
    exact=Fraction(value)*Fraction(factor)
    ticks=exact*10**9
    if exact>1000000 or ticks.denominator!=1:
        raise ValueError("SAP logistics measurement must be bounded and exact to 9 decimals")
    count=ticks.numerator
    return Decimal(str(count//10**9)+"."+str(count%10**9).zfill(9))
"""+s[end:]
print(json.dumps({str(p):s},ensure_ascii=True))
