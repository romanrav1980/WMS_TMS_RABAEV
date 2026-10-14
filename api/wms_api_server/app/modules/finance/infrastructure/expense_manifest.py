from decimal import Decimal
from typing import Any
from ...platform.public import read_oracle_json
from ..contracts import LogisticsCostError
from .expense_box_weight import missing_leaf_weight
from ..domain.physical_boxes import physical_box_count

def actual_goods(cursor: Any,trip: int,ware: int,basis: str) -> list[dict[str,Any]]:
    cursor.execute("select l.LOAD_OPERATION_ID,l.WARE_ID,l.STATUS,l.COMPOSITION_JSON from RRL_TT_HU_LOAD_FACT l join RRL_STOCK_OPERATION op on op.OPERATION_ID=l.LOAD_OPERATION_ID and op.STATE='APPLIED' where l.TT_ID=:id order by l.LOAD_OPERATION_ID fetch first 201 rows only",{"id":trip})
    loads=cursor.fetchall()
    if not loads or len(loads)>200:raise LogisticsCostError("EXPENSE_LOAD_BOUND","Нужны от 1 до 200 фактических мест рейса")
    cursor.execute("""select b.LOAD_OPERATION_ID,b.BOX_UID,b.GROSS_WEIGHT_KG,b.BOX_CONTENT_VERSION,
       b.CASE_BOX_TASK_ID,b.MEASUREMENT_ORIGIN,b.FINAL_SCALE_CAPTURE,b.WAREHOUSE_QC_OPERATION,
       b.TARE_WEIGHT_KG,b.NET_WEIGHT_KG,b.SIGNATURE_VERSION,b.MEASURED_CONTENT_VERSION,b.COVERAGE_COMPLETE
       from RRL_TT_LOAD_BOX_WEIGHT b join RRL_TT_HU_LOAD_FACT l on l.LOAD_OPERATION_ID=b.LOAD_OPERATION_ID
       where l.TT_ID=:id order by b.LOAD_OPERATION_ID,b.BOX_UID fetch first 10001 rows only""",id=trip)
    columns=[x[0].lower()for x in cursor.description]
    measurements=[dict(zip(columns,row))for row in cursor.fetchall()]
    if len(measurements)>10000:raise LogisticsCostError("EXPENSE_BOX_PROOF_BOUND","Не более 10000 измерений коробок")
    proofs: dict[str,dict[str,Decimal]]={}
    full_proofs: dict[str,list[dict[str,Any]]]={}
    for proof in measurements:
        load=proof["load_operation_id"];proofs.setdefault(load,{})[proof["box_uid"]]=Decimal(str(proof["gross_weight_kg"]))
        full_proofs.setdefault(load,[]).append(proof)
    rows=[];keys=set();units=set()
    for load,source_ware,status,composition in loads:
        if source_ware!=ware or status!="DEPARTED":raise LogisticsCostError("EXPENSE_FULL_DEPARTED_TRIP_REQUIRED","Для распределения нужны все выехавшие места одного склада")
        tree=read_oracle_json(composition);nodes=tree.get("nodes",[])
        leaves=[n for n in nodes if n.get("kind")=="STOCK"]
        if not leaves:raise LogisticsCostError("EXPENSE_EXACT_STOCK_MANIFEST_REQUIRED","Нужен точный состав товарных паллет; CASE требует собственного источника строк")
        if len(nodes)>200 or len({n["uid"]for n in nodes})!=len(nodes):
            raise LogisticsCostError("EXPENSE_FROZEN_TREE_BOUND","Нужен точный ограниченный архив физических мест")
        if basis=="WEIGHT"and any(n.get("kind")=="CASE"and n.get("scale_qc")for n in nodes):
            try:physical_box_count(tree,full_proofs.get(load,[]))
            except ValueError as exc:raise LogisticsCostError("EXPENSE_CASE_BOX_PROOF_REQUIRED",str(exc))from exc
        for node in leaves:
            key=load+":"+node["uid"]
            if key in keys:raise LogisticsCostError("EXPENSE_DUPLICATE_PHYSICAL_SOURCE","Физический источник повторён в составе")
            keys.add(key);units.add(node["base_uom"])
            quantity=Decimal(node["quantity"]);weight=Decimal(node["weight_kg"]) if node.get("weight_kg")is not None else None
            weight_source="FROZEN_STOCK" if weight is not None else "NONE";source_box=None
            if basis=="WEIGHT" and weight is None:
                weight,source_box=missing_leaf_weight(node,tree,proofs.get(load,{}));weight_source="MEASURED_CASE_NET"if any(x["uid"]==source_box and x.get("kind")=="CASE"for x in nodes)else "MEASURED_BOX_NET"
            value=quantity if basis=="BASE_QUANTITY" else weight
            if quantity<=0 or not quantity.is_finite() or value is None or not value.is_finite() or value<=0:
                raise LogisticsCostError("EXPENSE_POSITIVE_SOURCE_BASIS_REQUIRED","Для каждого товара нужна положительная подтверждённая база")
            rows.append({"key":key,"load_operation_id":load,"uid":node["uid"],"article":node["article"],"quantity":quantity,"base_uom":node["base_uom"],"weight_kg":weight,"basis_value":value,"weight_source":weight_source,"weight_box_uid":source_box})
            if len(rows)>10000:raise LogisticsCostError("EXPENSE_LEAF_BOUND","Не более 10000 товарных источников в расчёте")
    if basis=="BASE_QUANTITY" and len(units)!=1:raise LogisticsCostError("EXPENSE_MIXED_BASE_UNITS","Количество нельзя складывать между разными базовыми единицами; выберите массу")
    return rows
