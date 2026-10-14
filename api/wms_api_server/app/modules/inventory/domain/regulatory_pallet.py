"""An internal pallet identifier is not a regulatory SSCC."""
from typing import Any

def sscc_value(value: Any) -> str|None:
    if not isinstance(value,str):
        return None
    code=value
    if code.startswith("]C1"):
        code=code[3:]
    if code.startswith("(00)"):
        code=code[4:]
    elif len(code)==20 and code.startswith("00"):
        code=code[2:]
    if len(code)!=18 or not code.isascii() or not code.isdigit():
        return None
    weighted=sum(int(digit)*(3 if position%2==0 else 1) for position,digit in enumerate(reversed(code[:-1])))
    return code if int(code[-1])==(10-weighted%10)%10 else None

def receipt_sscc(pallet: str,declared: Any,scanned: list[dict[str,Any]]) -> str|None:
    declared_code=sscc_value(declared)
    scanned_codes={code for item in scanned if item["system"]=="CRPT" and item["level"]=="PALLET" if (code:=sscc_value(item["code"]))}
    if len(scanned_codes)>1 or declared_code and scanned_codes and scanned_codes!={declared_code}:
        raise ValueError("Conflicting regulatory pallet SSCC evidence")
    return declared_code or next(iter(scanned_codes),None) or sscc_value(pallet)
