"""SAP source conversion reuses current published stock rational policy and native exact math."""
from decimal import Decimal
from fractions import Fraction
from typing import Any
import oracledb

def convert_sap_source_quantity(cur: Any,article: str,input_unit: str,raw: str,base: str,units: list[dict]) -> Decimal:
    cur.execute("begin RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),4);end;")
    if input_unit==base:
        expected=Fraction(1)
    else:
        matches=[u for u in units if u["uom"]==input_unit]
        if len(matches)!=1:raise ValueError("SAP unit conversion missing or ambiguous")
        row=matches[0]
        if row.get("numerator")is not None and row.get("denominator")is not None:
            expected=Fraction(int(row["numerator"]),int(row["denominator"]))
        elif row.get("ratio")is not None:
            expected=Fraction(Decimal(row["ratio"]))
        else:
            raise ValueError("SAP rational unit conversion lacks coefficients")
    canonical="EA"if base.upper()in {"EA","PCS","ST","ШТ"}else base.upper()
    cur.execute("""select BASE_UOM,NUMERATOR,DENOMINATOR,BASE_SCALE from RRL_STOCK_UOM_CONVERSION u
        where ARTICUL=:article and INPUT_UOM=:input_unit and POLICY_VERSION=
        (select max(v.POLICY_VERSION)from RRL_STOCK_UOM_CONVERSION v where v.ARTICUL=u.ARTICUL and v.INPUT_UOM=u.INPUT_UOM)""",
        article=article,input_unit=input_unit)
    rows=cur.fetchall()
    if len(rows)!=1 or rows[0][0]!=canonical or Fraction(int(rows[0][1]),int(rows[0][2]))!=expected:
        raise ValueError("Published native unit policy differs from current SAP mapping")
    _,numerator,denominator,scale=rows[0]
    text=format(Decimal(raw),"f")
    if len(text)>30:raise ValueError("SAP source quantity exceeds text bound")
    try:
        cur.execute("""select to_char(RRL_STOCK_MATH.convert_exact(:quantity_text,:numerator,:denominator,:base_scale),
            'TM9','NLS_NUMERIC_CHARACTERS=''.,''')from dual""",quantity_text=text,numerator=numerator,denominator=denominator,base_scale=min(int(scale),6))
    except oracledb.DatabaseError as exc:
        if getattr(exc.args[0],"code",0)in(20830,20831,20833,20834):
            raise ValueError("SAP quantity requires forbidden rounding or violates native base precision")from exc
        raise
    value=Decimal(cur.fetchone()[0])
    if not 0<value<=Decimal("999999999999"):
        raise ValueError("Converted SAP source quantity exceeds warehouse contract")
    return value
