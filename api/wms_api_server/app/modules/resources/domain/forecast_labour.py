"""Advisory labour hours from forecast quantity and explicitly matched existing norms."""
from decimal import Decimal,localcontext,ROUND_CEILING
from typing import Any

def forecast_labour(series: list[dict[str,Any]],basis: dict[str,Any]) -> dict[str,Any]:
    norms={(r["article"],r["base_uom"]):r for r in basis["norms"]}
    rows=[]
    with localcontext()as ctx:
        ctx.prec=80
        total=Decimal(0)
        for row in series:
            norm=norms.get((row["article"],row["base_uom"]))
            status="APPLIED"
            if row.get("status")!="READY"or row.get("estimated_quantity")is None:
                status="FORECAST_BLOCKED"
            elif basis["status"]!="MAPPED":
                status=basis["status"]
            elif norm is None:
                status="NO_NORM"
            elif norm["active"]!=1:
                status="NORM_INACTIVE"
            elif Decimal(norm["base_per_hour"])<=0:
                status="NORM_INVALID"
            hours=None
            if status=="APPLIED":
                hours=(Decimal(row["estimated_quantity"])/Decimal(norm["base_per_hour"])).quantize(Decimal("0.000000001"),rounding=ROUND_CEILING)
                total+=hours
            rows.append({"article":row["article"],"base_uom":row["base_uom"],"status":status,
                "forecast_quantity":row.get("estimated_quantity"),"estimated_person_hours":format(hours,"f")if hours is not None else None,
                "norm":norm})
        known=sum(r["status"]=="APPLIED"for r in rows)
        complete=bool(rows)and known==len(rows)
        return {"status":"COMPLETE_ESTIMATE"if complete else"PARTIAL_ESTIMATE"if known else"NO_ESTIMATE",
            "mapping_status":basis["status"],"mapping":basis["mapping"],"rows":rows,
            "covered_series":known,"uncovered_series":len(rows)-known,
            "known_person_hours":format(total,"f")if known else None,
            "total_person_hours":format(total,"f")if complete else None,
            "rounding":"CEILING_9_DECIMAL_HOURS_PER_SERIES","advisory":True,
            "people_required":None,"planned_attendance_applied":False,"task_assignments_changed":False,
            "missing_capacity_inputs":["NAMED_RESOURCE_AVAILABILITY","SHIFT_HOURS_BREAKS","EQUIPMENT_AND_SLOTS"]}
