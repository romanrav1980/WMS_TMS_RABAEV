"""Published topology classification of the current WMS cell catalog, read-only."""
from typing import Any

# Explicit existing map roles; EMPTY and arbitrary text do not classify a cell.
CLASSIFIED_ROLES = ("PICK_FACE", "DYNAMIC_PICK_FACE", "STORAGE", "TRANSPORT_STAGING",
    "GATE", "FILM_WRAP", "AISLE", "BLOCKED", "FRACTIONAL_PICK_FACE", "FRACTIONAL_STORAGE")


def published_cell_coverage(cur: Any, ware: int) -> dict[str, Any]:
    cur.execute("select max(TOPOLOGY_ID)from RRL_WAREHOUSE_TOPOLOGY where WARE_ID=:ware and STATUS='PUBLISHED'", ware=ware)
    topology = cur.fetchone()[0]
    params = {"ware": ware, "topology": topology}
    for number, role in enumerate(CLASSIFIED_ROLES):
        params["role" + str(number)] = role
    roles = ",".join(":role" + str(number) for number in range(len(CLASSIFIED_ROLES)))
    source = """with classified as(
        select LEGACY_CELL_CODE,count(*) MAPPED_COUNT,
        sum(case when CELL_KIND in (""" + roles + """)then 1 else 0 end) VALID_COUNT from RRL_TOPOLOGY_CELL
        where WARE_ID=:ware and TOPOLOGY_ID=:topology and ACTIVE=1
        and LEGACY_CELL_CODE is not null
        group by LEGACY_CELL_CODE), matched as(
        select c.CELL,nvl(m.MAPPED_COUNT,0) MAPPED_COUNT,nvl(m.VALID_COUNT,0) VALID_COUNT from RRL_CELLS c
        left join classified m on m.LEGACY_CELL_CODE=c.CELL where c.WARE_ID=:ware) """
    cur.execute(source + """select count(*),
        nvl(sum(case when MAPPED_COUNT=1 and VALID_COUNT=1 then 1 else 0 end),0),
        nvl(sum(case when MAPPED_COUNT=0 or VALID_COUNT!=MAPPED_COUNT then 1 else 0 end),0),
        nvl(sum(case when MAPPED_COUNT>1 then 1 else 0 end),0)from matched""", params)
    total, classified, missing, ambiguous = (int(value) for value in cur.fetchone())
    sample: list[str] = []
    if missing or ambiguous:
        cur.execute(source + "select CELL from matched where MAPPED_COUNT!=1 or VALID_COUNT!=1 order by CELL fetch first 20 rows only", params)
        sample = [row[0] for row in cur.fetchall()]
    complete = topology is not None and total > 0 and missing == 0 and ambiguous == 0
    return {"scope": "CURRENT_WMS_CELL_CATALOG", "topology_id": topology,
        "registered_cell_count": total, "classified_cell_count": classified,
        "unclassified_cell_count": missing, "ambiguous_cell_count": ambiguous,
        "incomplete_cell_sample": sample, "classification_complete": complete,
        "unregistered_physical_areas_verified": False,
        "status": "PUBLISHED_CATALOG_COMPLETE" if complete else
            "PUBLISHED_TOPOLOGY_REQUIRED" if topology is None else "CELL_CLASSIFICATION_INCOMPLETE"}
