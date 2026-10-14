"""Exact grouping of already recognised costs; no rate selection or postings."""
from decimal import Decimal,InvalidOperation,localcontext
from typing import Any


def recognized_cost_summary(lines: list[dict[str,Any]])->dict[str,Any]:
    groups: dict[tuple[str,...],dict[str,Any]]={}
    totals: dict[str,Decimal]={}
    seen: set[tuple[str,...]]=set()
    with localcontext()as ctx:
        ctx.prec=80
        for row in lines:
            identity=tuple(str(row[name])for name in ("operation_id","load_operation_id","cost_code","currency","rate_date"))
            if identity in seen:
                raise ValueError("Duplicate recognised cost source")
            seen.add(identity)
            try:
                amount=Decimal(str(row["amount"]));quantity=Decimal(str(row["quantity"]))
            except (InvalidOperation,KeyError,TypeError)as exc:
                raise ValueError("Recognised amount and quantity must be exact decimals")from exc
            if not amount.is_finite()or not quantity.is_finite()or quantity<0:
                raise ValueError("Recognised source contains invalid amount or quantity")
            if amount!=amount.quantize(Decimal("0.01")):
                raise ValueError("Recognised monetary amount exceeds currency cent precision")
            fields=("ware_id","rate_date","period_mode","period_time_zone","period_policy_version",
                    "cost_code","currency","basis","version_no","rate_value")
            key=tuple(str(row.get(field))for field in fields)
            if key not in groups:
                groups[key]={field:row.get(field)for field in fields}
                groups[key].update(quantity=Decimal(0),amount=Decimal(0),source_count=0,trips=set())
            group=groups[key];group["quantity"]+=quantity;group["amount"]+=amount
            group["source_count"]+=1;group["trips"].add(row["tt_id"])
            currency=str(row["currency"]);totals[currency]=totals.get(currency,Decimal(0))+amount
        result=[]
        for key in sorted(groups):
            group=groups[key]
            result.append({**group,"quantity":format(group["quantity"],"f"),
                           "amount":format(group["amount"],".2f"),"trips":sorted(group["trips"])})
        return {"groups":result,"currency_totals":[{"currency":c,"original_amount":format(v,".2f")}for c,v in sorted(totals.items())],
                "line_count":len(lines),"visible_warehouses":sorted({row["ware_id"]for row in lines}),
                "scope":"VISIBLE_WAREHOUSES","basis":"ORIGINAL_RECOGNIZED_COSTS",
                "includes_corrections":False,"includes_extra_expenses":False,"stock_changed":False}
