"""Existing published candidate faces, current SKU template, no assignment mutations."""
from decimal import Decimal, localcontext
from typing import Any
import oracledb
import json
from ..domain.slotting_recommendation import recommend_range
from ..contracts_slotting import SlottingError

def native_template_volumes(cur: Any, article: str, templates: list[tuple[Any, ...]]) -> tuple[Decimal | None, list[dict[str, Any]]]:
    volumes = set()
    volume_evidence = []
    complete = True
    for face, cell, _volume, _numerator, _denominator in templates:
        error = None
        native_volume = None
        try:
            cur.execute("""select to_char(RRL_STOCK_REPL_CAPACITY.unit_volume(:cell,:article),
                'TM9',q'[NLS_NUMERIC_CHARACTERS='.,']')from dual""", cell=cell, article=article)
            value = cur.fetchone()[0]
            if value is not None and Decimal(value) > 0:
                native_volume = Decimal(value)
                volumes.add(native_volume)
            else:
                complete = False
                error = "NATIVE_UNIT_VOLUME_NOT_CONFIRMED"
        except oracledb.DatabaseError as exc:
            if not 20800 <= getattr(exc.args[0], "code", 0) <= 20999:
                raise
            complete = False
            error = str(exc.args[0]).split("\n", 1)[0]
        volume_evidence.append({"pick_face_id": face, "cell": cell,
            "native_unit_volume_m3": None if native_volume is None else format(native_volume,"f"),
            "refusal": error})
    return (next(iter(volumes)) if complete and len(volumes) == 1 else None), volume_evidence

def recommendation_sources(cur: Any, ware: int, article: str, scenario: dict[str, Any],
                           layout: dict[str, Any], pallet_weight: Decimal | None,
                           costs: list[dict[str, Any]], candidate_route: int | None = None) -> dict[str, Any]:
    cur.execute("""select pf.PICK_FACE_ID,pf.CELL_CODE,
        to_char(coalesce(case when a.USE_ARTICUL_REPLENISH_RULE=1 then ar.BOX_VOLUME_M3 end,a.BOX_VOLUME_M3),'TM9',q'[NLS_NUMERIC_CHARACTERS='.,']'),
        to_char(cv.NUMERATOR,'TM9',q'[NLS_NUMERIC_CHARACTERS='.,']'),to_char(cv.DENOMINATOR,'TM9',q'[NLS_NUMERIC_CHARACTERS='.,']')
        from RRL_PICK_FACE pf join RRL_PICK_FACE_ARTICUL a on a.PICK_FACE_ID=pf.PICK_FACE_ID
        left join RRL_ARTICUL_REPLENISH_RULE ar on ar.ARTICUL=a.ARTICUL
        left join RRL_STOCK_UOM_CONVERSION cv on cv.ARTICUL=a.ARTICUL and cv.INPUT_UOM='BOX'
         and cv.POLICY_VERSION=(select max(POLICY_VERSION)from RRL_STOCK_UOM_CONVERSION x where x.ARTICUL=a.ARTICUL and x.INPUT_UOM='BOX')
        where pf.WARE_ID=:ware and pf.ACTIVE=1 and a.ACTIVE=1 and a.ARTICUL=:article
        order by a.PRIORITY,pf.PICK_FACE_ID fetch first 101 rows only""", ware=ware, article=article)
    templates = cur.fetchall()
    if len(templates) > 100:
        raise SlottingError("SLOTTING_TEMPLATE_BOUND_100", "Сузьте действующий диапазон")
    unit_volume, volume_evidence = native_template_volumes(cur, article, templates)
    if candidate_route is not None:
        cur.execute("select count(*)from RRL_PICK_ROUTE where PICK_ROUTE_ID=:route and WARE_ID=:ware and ACTIVE=1 and STATUS='PUBLISHED'",
                    route=candidate_route,ware=ware)
        if cur.fetchone()[0]!=1:
            raise SlottingError("SLOTTING_CURRENT_CANDIDATE_ROUTE_REQUIRED", "Нужен действующий опубликованный маршрут этого склада",404)
    route_clause=" and pf.PICK_ROUTE_ID=:route "if candidate_route is not None else" "
    candidate_binds={"ware":ware,**({"route":candidate_route}if candidate_route is not None else{})}
    # Empty dynamic faces; active mappings/reserves/tasks retained and never overwritten.
    cur.execute("""select pf.PICK_FACE_ID,pf.CELL_CODE,to_char(pf.MAX_VOLUME,'TM9',q'[NLS_NUMERIC_CHARACTERS='.,']'),
        to_char(pf.MAX_WEIGHT,'TM9',q'[NLS_NUMERIC_CHARACTERS='.,']'),
        case when pr.PICK_ROUTE_ID is not null and rc.PICK_ROUTE_CELL_ID is not null then pf.PICK_ROUTE_ID end,
        case when pr.PICK_ROUTE_ID is not null and rc.PICK_ROUTE_CELL_ID is not null then pf.PICK_ROUTE_CELL_ID end
        from RRL_PICK_FACE pf join RRL_CELLS c on c.CELL=pf.CELL_CODE and c.WARE_ID=pf.WARE_ID
        left join RRL_PICK_ROUTE pr on pr.PICK_ROUTE_ID=pf.PICK_ROUTE_ID and pr.WARE_ID=pf.WARE_ID and pr.ACTIVE=1 and pr.STATUS='PUBLISHED'
        left join RRL_PICK_ROUTE_CELL rc on rc.PICK_ROUTE_CELL_ID=pf.PICK_ROUTE_CELL_ID and rc.PICK_ROUTE_ID=pf.PICK_ROUTE_ID
         and rc.WARE_ID=pf.WARE_ID and rc.CELL_CODE=pf.CELL_CODE and rc.ACTIVE=1
        where pf.WARE_ID=:ware and pf.ACTIVE=1 """+route_clause+"""and (pf.PICK_FACE_TYPE='DYNAMIC' or pf.ALLOW_DYNAMIC_ASSIGNMENT=1)
         and c.OTBOR=1 and nvl(c.IS_SYSTEM,0)=0 and nvl(c.BLOCKED_FOR_REMAINS,0)=0 and nvl(c.BLOCKED_FOR_POPOLNENIE,0)=0
         and not exists(select 1 from RRL_PICK_FACE_ARTICUL a where a.PICK_FACE_ID=pf.PICK_FACE_ID and a.ACTIVE=1)
         and not exists(select 1 from RRL_PICK_FACE_ASSIGNMENT a where a.CELL_CODE=pf.CELL_CODE and a.STATUS='ACTIVE')
         and not exists(select 1 from RRL_REMAINS r where r.CELL=pf.CELL_CODE and (r.REMAIN>0 or r.HARD_RESERVED_BASE>0))
         and not exists(select 1 from RRL_WAREHOUSE_TASK t where (t.TO_CELL=pf.CELL_CODE or t.FROM_CELL=pf.CELL_CODE)and t.STATUS not in('DONE','CANCELLED'))
         and not exists(select 1 from RRL_PICK_WAVE_REPLENISH_TASK t where t.TARGET_CELL_CODE=pf.CELL_CODE and t.STATUS not in('DONE','CANCELLED','FAILED'))
         and not exists(select 1 from RRL_CASE_PICK_LINE l join RRL_CASE_PICK_TASK t on t.CASE_PICK_TASK_ID=l.CASE_PICK_TASK_ID
          where l.CELL_CODE=pf.CELL_CODE and t.STATUS not in('DONE','CANCELLED')and l.PLANNED_QTY>nvl(l.PICKED_QTY,0))
        order by pf.PICK_FACE_ID fetch first 101 rows only""", candidate_binds)
    empty = cur.fetchall()
    if len(empty) > 100:
        return {"status": "CANDIDATE_SCOPE_REQUIRED", "selected_faces": [], "physical_admission": False,
                "applied": False, "old_faces_preserved": True, "candidate_limit": 100}
    multiple = None
    if scenario["nominal_additional_quantity"] is not None and Decimal(scenario["nominal_additional_pallets"]) > 0:
        multiple = Decimal(scenario["nominal_additional_quantity"]) / Decimal(scenario["nominal_additional_pallets"])
    candidates = []
    with localcontext() as ctx:
        ctx.prec = 80
        pallet_volume = None if unit_volume is None or multiple is None else unit_volume * multiple
        def add(face: int, cell: str, volume: str | None, weight: str | None,
                route: int | None, route_cell: int | None, old: bool, budget: str | None) -> None:
            reasons = []
            if multiple is None: reasons.append("PALLET_MULTIPLE_REQUIRED")
            if pallet_volume is None or volume is None: reasons.append("PALLET_VOLUME_NOT_CONFIRMED")
            elif (Decimal(budget) < multiple if old and budget is not None else Decimal(volume) < pallet_volume):
                reasons.append("WHOLE_PALLET_VOLUME_INSUFFICIENT")
            if old and budget is None: reasons.append("CURRENT_VOLUME_BUDGET_UNKNOWN")
            if weight is None or pallet_weight is None: reasons.append("DECLARED_GROSS_PALLET_WEIGHT_REQUIRED")
            elif Decimal(weight) < pallet_weight: reasons.append("WHOLE_PALLET_WEIGHT_INSUFFICIENT")
            if old:
                # Gross free weight cannot be derived from net SKU weight/current P alone.
                reasons.append("EXISTING_OCCUPIED_GROSS_WEIGHT_NOT_CONFIRMED")
            if route is None or route_cell is None: reasons.append("PUBLISHED_PICK_ROUTE_REQUIRED")
            candidates.append({"pick_face_id": int(face), "cell": cell, "existing": old,
                "nominal_pallet_base_quantity": None if multiple is None else format(multiple, "f"),
                "nominal_pallet_volume_m3": None if pallet_volume is None else format(pallet_volume, "f"),
                "declared_pallet_gross_weight_kg": None if pallet_weight is None else format(pallet_weight, "f"),
                "max_volume_m3": volume, "max_weight_kg": weight, "pick_route_id": route,
                "pick_route_cell_id": route_cell, "whole_pallet_nominal_fit": not reasons, "refusal_reasons": reasons})
        for row in layout["cells"]:
            add(row["pick_face_id"], row["cell"], row["configured_volume_m3"], row["configured_weight_kg"],
                row["pick_route_id"], row["pick_route_cell_id"], True, row["remaining_volume_base_quantity"])
        for face, cell, volume, weight, route, route_cell in empty:
            add(face, cell, volume, weight, route, route_cell, False, None)
    unique = {row["cell"] for row in candidates}
    if len(unique) != len(candidates):
        raise SlottingError("SLOTTING_SHARED_CELL_CANDIDATES_AMBIGUOUS", "Одна ячейка опубликована несколько раз")
    cur.execute("""select PICK_FACE_ARTICUL_ID,to_clob(json_object(* returning clob))
        from RRL_PICK_FACE_ARTICUL where ARTICUL=:article and ACTIVE=1
         and PICK_FACE_ID in(select ID from json_table(:faces,'$[*]'columns(ID number path '$')))
        order by PICK_FACE_ARTICUL_ID fetch first 101 rows only""",
        article=article, faces=json.dumps([row[0]for row in templates]))
    configuration = [{"pick_face_articul_id": identity,
        "native_configuration_json": raw.read() if hasattr(raw,"read") else raw} for identity,raw in cur.fetchall()]
    if len(configuration)>100:
        raise SlottingError("SLOTTING_TEMPLATE_CONFIGURATION_BOUND", "Сузьте область настроек")
    result = recommend_range(scenario, layout["cells"], candidates, costs)
    return {**result, "candidates": candidates, "reference_templates": [
        {"pick_face_id": face, "cell": cell, "box_volume_m3": volume, "box_to_base_numerator": num,
         "box_to_base_denominator": den} for face, cell, volume, num, den in templates],
        "template_unit_volume_complete": unit_volume is not None, "native_volume_evidence": volume_evidence,
        "candidate_pick_route_id":candidate_route,"candidate_scope":"WAREHOUSE_EMPTY_DYNAMIC_FACES"if candidate_route is None else"PUBLISHED_ROUTE_EMPTY_DYNAMIC_FACES",
        "demand_and_old_range_scope":"WHOLE_ARTICLE_WAREHOUSE", "template_configuration": configuration, "declared_costs": costs, "weight_basis": "OPERATOR_DECLARED_GROSS_PALLET_WEIGHT"}
