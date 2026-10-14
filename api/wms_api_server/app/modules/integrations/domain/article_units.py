"""Sparse MARM updates preserve established conversion and omitted units."""
from decimal import Decimal,InvalidOperation
from fractions import Fraction
from typing import Any

def rational(numerator: str,denominator: str) -> Fraction:
    if len(numerator)>64 or len(denominator)>64:
        raise ValueError("SAP conversion text exceeds bound")
    try:n=Decimal(numerator);d=Decimal(denominator)
    except InvalidOperation as exc:raise ValueError("Invalid SAP conversion") from exc
    if not n.is_finite()or not d.is_finite()or n<=0 or d<=0 or n>10**9 or d>10**9 or n<Decimal("0.000000001")or d<Decimal("0.000000001"):
        raise ValueError("SAP conversion components must be positive and bounded")
    value=Fraction(n)/Fraction(d)
    if value.numerator>10**9 or value.denominator>10**9:
        raise ValueError("SAP conversion exceeds stock rational contract")
    return value

def decimal_ratio(value: Fraction) -> str | None:
    ticks=value*10**9
    if ticks.denominator!=1:return None
    digits=str(ticks.numerator).zfill(10)
    return str(Decimal(digits[:-9]+"."+digits[-9:]))

def map_units(records: list[dict[str,Any]]) -> list[dict]:
    units=[];seen=set()
    for record in records:
        if record["segment"]!="E1BPE1MARMRT":continue
        data=record["fields"];uom=data.get("ALT_UNIT")
        if not uom or uom in seen:raise ValueError("Missing or duplicate SAP alternative unit")
        seen.add(uom)
        flags=[r["fields"]for r in records if r["segment"]=="E1BPE1MARMRTX"and r["fields"].get("ALT_UNIT")==uom]
        if len(flags)>1:raise ValueError("Ambiguous SAP unit update flags")
        changed={key for key,value in flags[0].items()if value=="X"}if flags else None
        update_ratio=changed is None or bool(changed.intersection({"NUMERATOR","DENOMINATR"}))
        ratio=None
        if update_ratio and (data.get("NUMERATOR")or data.get("DENOMINATR")):
            if not data.get("NUMERATOR")or not data.get("DENOMINATR"):
                raise ValueError("SAP unit ratio update requires numerator and denominator")
            ratio=rational(data["NUMERATOR"],data["DENOMINATR"])
        elif changed is not None and update_ratio:
            raise ValueError("Explicit SAP unit ratio update lacks values")
        update_ean=changed is None and bool(data.get("EAN_UPC"))or changed is not None and "EAN_UPC"in changed
        if update_ean and not data.get("EAN_UPC"):
            raise ValueError("Explicit EAN removal requires separate clearing contract")
        units.append({"uom":uom,"ratio":decimal_ratio(ratio)if ratio is not None else None,
                      "numerator":ratio.numerator if ratio is not None else None,
                      "denominator":ratio.denominator if ratio is not None else None,
                      "ratio_unchanged":changed is not None and not update_ratio,
                      "ean":data.get("EAN_UPC")if update_ean else None})
    return units

def merge_units(previous: list[dict],patches: list[dict],base: str) -> list[dict]:
    known={}
    for row in previous:
        if row["uom"]in known:raise ValueError("Ambiguous stored SAP unit mapping")
        known[row["uom"]]=dict(row)
    for patch in patches:
        uom=patch["uom"];old=known.get(uom)
        if patch["numerator"]is not None:
            ratio=Fraction(patch["numerator"],patch["denominator"])
        elif uom==base:
            ratio=Fraction(1)
        elif patch["ratio_unchanged"]and old:
            ratio=Fraction(int(old["numerator"]),int(old["denominator"]))if old.get("numerator")is not None else Fraction(Decimal(old["ratio"]))
        else:
            raise ValueError("New or incomplete SAP alternative unit requires proven conversion")
        known[uom]={"uom":uom,"numerator":ratio.numerator,"denominator":ratio.denominator,
                    "ratio":decimal_ratio(ratio),"ean":patch["ean"]if patch["ean"]is not None else old.get("ean")if old else None}
    return [known[key]for key in sorted(known)]
