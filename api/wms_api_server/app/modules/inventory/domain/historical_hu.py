"""Read an immutable departure subtree without presenting siblings as its stock."""
from copy import deepcopy


def departure_subtree(snapshot: dict, identifier: str) -> dict:
    nodes = snapshot["nodes"]
    by_id = {node["uid"]: node for node in nodes}
    if identifier not in by_id:
        raise ValueError("Departure does not contain this handling unit")
    edges = snapshot.get("links", [])
    children: dict[str, list[str]] = {}
    parents: dict[str, str] = {}
    for edge in edges:
        children.setdefault(edge["parent"], []).append(edge["child"])
        parents[edge["child"]] = edge["parent"]
    selected: set[str] = set()
    pending = [identifier]
    while pending:
        uid = pending.pop()
        if uid in selected:
            continue
        selected.add(uid)
        if len(selected) > 200:
            raise ValueError("Departure subtree exceeds 200 nodes")
        pending.extend(children.get(uid, []))
    if not selected <= by_id.keys():
        raise ValueError("Departure hierarchy contains an unknown child")
    result = deepcopy(snapshot)
    result["nodes"] = [deepcopy(node) for node in nodes if node["uid"] in selected]
    if result["nodes"][0]["uid"] != identifier:
        raise ValueError("Departure node order is inconsistent")
    base_depth = by_id[identifier]["depth"]
    for node in result["nodes"]:
        node["depth"] -= base_depth
    result["links"] = [deepcopy(edge) for edge in edges if edge["parent"] in selected and edge["child"] in selected]
    ancestors = []
    current = identifier
    while current in parents:
        current = parents[current]
        if len(ancestors) >= 16 or current not in by_id:
            raise ValueError("Departure ancestor hierarchy is inconsistent")
        parent = by_id[current]
        ancestors.append({"uid": current, "version": parent["version"], "cell": parent["cell"], "historical_parent": True})
    result["root"] = identifier
    result["ancestors"] = ancestors
    result["top_place_count"] = 0 if ancestors else 1
    result["leaf_count"] = sum(node["kind"] == "STOCK" for node in result["nodes"])
    if identifier != snapshot["root"]:
        leaf_nodes = [node for node in result["nodes"] if node["kind"] == "STOCK"]
        if snapshot.get("physical_unit_count") == 0:
            result["physical_unit_count"] = 0
        elif all("physical_unit_count" in node for node in leaf_nodes):
            result["physical_unit_count"] = sum(node["physical_unit_count"] for node in leaf_nodes)
        else:
            result["physical_unit_count"] = None
            result["unit_count_known"] = False
    return result
