"""Bounded geofences from the authoritative legacy address key and WGS84 fields."""
from typing import Any


def list_address_geofences(gateway: Any, addr_mask: str | None = None) -> list[dict]:
    params: dict[str, Any] = {}
    predicate = ""
    if addr_mask:
        predicate = " AND UPPER(ADDR) LIKE UPPER(:mask)"
        params["mask"] = f"%{addr_mask}%"
    rows = gateway.fetch_all("""
        SELECT ADDR, SHIROTA AS LATITUDE, DOLGOTA AS LONGITUDE,
               NVL(GEO_FENCE_RADIUS_M,200) AS RADIUS_M
          FROM RABAEV.RRL_ADDR
         WHERE NVL(DELETED3,0)=0
           AND SHIROTA BETWEEN -90 AND 90 AND DOLGOTA BETWEEN -180 AND 180
    """ + predicate + " ORDER BY ADDR FETCH FIRST 200 ROWS ONLY", params)
    return [{"addr_id": row["addr"], "addr_key": row["addr"], "addr": row["addr"],
             "lat": float(row["latitude"]), "lon": float(row["longitude"]),
             "radius_m": int(row["radius_m"])} for row in rows]


def update_address_geofence(gateway: Any, address: str, radius: int, actor: str) -> dict | None:
    with gateway.transaction("Update address geofence under existing CONFIG owner") as cur:
        entered = False
        try:
            cur.callproc("RRL_STOCK_METADATA_TX.begin_change", [actor, "warehouse_settings_edit"])
            entered = True
            cur.execute("select ADDR from RRL_ADDR where ADDR=:address and nvl(DELETED3,0)=0 for update wait 5", address=address)
            if cur.fetchone() is None:
                return None
            cur.execute("update RRL_ADDR set GEO_FENCE_RADIUS_M=:radius where ADDR=:address", radius=radius, address=address)
            return {"addr_id": address, "addr_key": address, "radius_m": radius}
        finally:
            if entered:
                cur.callproc("RRL_STOCK_METADATA_TX.end_change")
