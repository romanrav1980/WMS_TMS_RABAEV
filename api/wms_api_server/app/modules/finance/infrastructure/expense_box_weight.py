from decimal import Decimal
from typing import Any
from ..contracts import LogisticsCostError

def missing_leaf_weight(node: dict[str,Any],tree: dict[str,Any],proofs: dict[str,Decimal]) -> tuple[Decimal,str]:
    nodes={n["uid"]:n for n in tree["nodes"]};parents={link["child"]:link["parent"]for link in tree.get("links",[])}
    children: dict[str,list[str]]={}
    for link in tree.get("links",[]):children.setdefault(link["parent"],[]).append(link["child"])
    current=node["uid"];seen=set();box=None
    while current in parents:
        if current in seen:raise LogisticsCostError("EXPENSE_SOURCE_TREE_CYCLE","Состав места содержит цикл")
        seen.add(current);current=parents[current]
        if (nodes[current].get("type")=="BOX"or(nodes[current].get("kind")=="CASE"and nodes[current].get("scale_qc")))and current in proofs:box=current;break
    if box is None:raise LogisticsCostError("EXPENSE_GOODS_WEIGHT_PROOF_REQUIRED","Нет массы товара или измеренной коробки с точным составом")
    descendants=[];stack=[box];seen=set()
    while stack:
        uid=stack.pop()
        if uid in seen:raise LogisticsCostError("EXPENSE_SOURCE_TREE_DUPLICATE","Состав коробки повторяет источник")
        seen.add(uid);descendants.append(nodes[uid]);stack.extend(children.get(uid,[]))
        if len(seen)>10000:raise LogisticsCostError("EXPENSE_BOX_SOURCE_BOUND","Коробка превышает предел состава")
    stock=[n for n in descendants if n.get("kind")=="STOCK"]
    if len(stock)!=1 or stock[0]["uid"]!=node["uid"]:
        raise LogisticsCostError("EXPENSE_SINGLE_LEAF_BOX_NET_REQUIRED","Без массы каждого товара допустима только измеренная коробка с одним товарным источником")
    case_proof=nodes[box].get("scale_qc")if nodes[box].get("kind")=="CASE"else None
    if case_proof:
        net=Decimal(case_proof["net_weight_kg"])
        if not net.is_finite()or net<=0:raise LogisticsCostError("EXPENSE_CASE_BOX_POSITIVE_NET_REQUIRED","Нужна положительная измеренная масса товара малой тары")
        return net,box
    tare=sum((Decimal(n["tare_weight_kg"])for n in descendants if n.get("kind")=="CONTAINER" and n.get("tare_weight_kg")is not None),Decimal("0"))
    if any(n.get("kind")=="CONTAINER" and n.get("tare_weight_kg")is None for n in descendants):raise LogisticsCostError("EXPENSE_BOX_TARE_REQUIRED","Для расчёта массы товара нужна известная тара коробки")
    net=proofs[box]-tare
    if not net.is_finite() or net<=0:raise LogisticsCostError("EXPENSE_BOX_POSITIVE_NET_REQUIRED","Масса товара после вычета тары должна быть положительной")
    return net,box
