"""Assumed ARTMAS10 MARMRT logistics profile, normalized to existing WMS mm/kg fields."""
from decimal import Decimal,InvalidOperation
from typing import Any
from fractions import Fraction

BOX_UNITS={"BOX","CAR","CS","KAR"}
_DIM={"MM":Decimal(1),"MMT":Decimal(1),"CM":Decimal(10),"CMT":Decimal(10),"M":Decimal(1000),"MTR":Decimal(1000)}
_MASS={"KG":Decimal(1),"KGM":Decimal(1),"G":Decimal("0.001"),"GRM":Decimal("0.001")}

def positive_measure(raw: str,factor: Decimal) -> Decimal:
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

def factor(data: dict[str,str],name: str,iso: str,units: dict[str,Decimal]) -> Decimal:
    codes=[data.get(name),data.get(iso)]
    values=[]
    for code in codes:
        if code:
            if code.upper() not in units:
                raise ValueError("Unsupported explicit SAP measurement unit: "+code)
            values.append(units[code.upper()])
    if not values or len(set(values))!=1:
        raise ValueError("SAP measurement unit missing or contradictory")
    return values[0]

def box_logistics(records: list[dict[str,Any]]) -> dict[str,Decimal]:
    boxes=[r["fields"]for r in records if r["segment"]=="E1BPE1MARMRT"and r["fields"].get("ALT_UNIT")in BOX_UNITS]
    if len(boxes)>1:
        raise ValueError("Ambiguous SAP box logistics unit")
    if not boxes:return {}
    data=boxes[0];uom=data["ALT_UNIT"]
    flags=[r["fields"]for r in records if r["segment"]=="E1BPE1MARMRTX"and r["fields"].get("ALT_UNIT")==uom]
    if len(flags)>1:raise ValueError("Ambiguous MARMRTX logistics change flags")
    changed={key for key,value in flags[0].items()if value=="X"}if flags else None
    out={}
    mass_fields={"GROSS_WT","UNIT_OF_WT","UNIT_OF_WT_ISO"}
    if (changed is None and data.get("GROSS_WT")) or (changed is not None and changed.intersection(mass_fields)):
        if not data.get("GROSS_WT"):raise ValueError("Explicit gross-weight change requires a positive value")
        out["BRUTTO_WEIGHT_OF_KOR"]=positive_measure(data["GROSS_WT"],factor(data,"UNIT_OF_WT","UNIT_OF_WT_ISO",_MASS))
    dimensions={"LENGTH":"DIMKOR_X","WIDTH":"DIMKOR_Y","HEIGHT":"DIMKOR_Z"}
    selected=[key for key in dimensions if data.get(key)]if changed is None else [key for key in dimensions if key in changed]
    unit_changed=changed is not None and bool(changed.intersection({"UNIT_DIM","UNIT_DIM_ISO"}))
    if unit_changed:
        selected=list(dimensions)
    if selected:
        conversion=factor(data,"UNIT_DIM","UNIT_DIM_ISO",_DIM)
        for key in selected:
            if not data.get(key):raise ValueError("Explicit dimension change requires its positive value")
            out[dimensions[key]]=positive_measure(data[key],conversion)
    return out
