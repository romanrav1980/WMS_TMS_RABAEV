"""Reuse the quantity proposal for whole-box layouts; original ST writers remain authoritative."""
from decimal import Decimal
from fractions import Fraction
from hashlib import sha256
import json
from typing import Any
from ...inventory.public import propose_receipt_layout
from ..domain.preparation_quantities import exact_decimal
from .preparation_readiness import preparation_readiness

def preparation_layout(gateway: Any,order: int,counts: dict[str,int],actor: str) -> dict:
    source=preparation_readiness(gateway,order,actor)
    if not source["ready_for_operator_layout"]:
        raise ValueError("SOURCE_PREPARATION_NOT_READY: "+",".join(source["blockers"]+
            [code for line in source["lines"]for code in line["blockers"]]))
    known={line["articul"]for line in source["lines"]}
    if set(counts)-known:raise ValueError("LAYOUT_COUNT_ARTICLE_NOT_IN_SOURCE")
    pallets=[];summary=[]
    for line in source["lines"]:
        pack=Fraction(Decimal(line["pack_quantity"]));total=Fraction(Decimal(line["quantity"]))
        boxes=total/pack
        if boxes.denominator!=1:raise ValueError("WHOLE_PACKAGING_LAYOUT_REQUIRED")
        norm=Fraction(Decimal(line["pallet_norm"]or "0"))
        norm_boxes=norm//pack if norm>0 else 0
        count=counts.get(line["articul"])
        proposal=propose_receipt_layout(str(boxes.numerator),"BOX",str(norm_boxes)if norm_boxes else None,count,None,"1")
        amounts=[format(exact_decimal(Fraction(Decimal(q))*pack,6),"f")for q in proposal["quantities"]]
        for quantity in amounts:
            pallets.append({"lines":[{"articul":line["articul"],"quantity":quantity}]})
        summary.append({"articul":line["articul"],"pallet_count":len(amounts),"quantities":amounts,
                        "pallet_norm":line["pallet_norm"],"whole_pack_quantity":line["pack_quantity"],
                        "above_norm_pallets":proposal["above_norm_pallets"]})
        if len(pallets)>100:raise ValueError("PREPARATION_LAYOUT_PALLET_BOUND_100")
    signature=sha256(json.dumps(source,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()
    return {"customer_order_id":order,"warehouse_id":source["warehouse_id"],"source_signature":signature,
            "pallets":pallets,"articles":summary,"layout_basis":"CURRENT_LEGACY_NORM_WHOLE_BOXES",
            "stock_changed":False,"st_created":False,"mixed_article_optimisation_verified":False,
            "physical_capacity_verified":False,"consistent_snapshot":True}
