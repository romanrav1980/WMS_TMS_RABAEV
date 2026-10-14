"""Use the configured origin when present; retain an explicit centroid fallback."""
import math
from typing import Any,Callable

def distance_costs(orders: list[Any],cache: dict | None,origin: dict | None,haversine: Callable) -> tuple[list[list[int]],str | None]:
    size=len(orders);depot=size
    if origin and origin.get("configured"):
        lat=float(origin["latitude"]);lon=float(origin["longitude"]);depot_address=origin["depot_address"]
    else:
        lat=sum(o.lat for o in orders)/size;lon=sum(o.lon for o in orders)/size;depot_address=None
    def km(i: int,j: int) -> float:
        if i==j:return 0
        a=depot_address if i==depot else orders[i].addr
        b=depot_address if j==depot else orders[j].addr
        found=(cache or {}).get((a,b))if a and b else None
        if found is not None and math.isfinite(found)and found>=0:return found
        first=(lat,lon)if i==depot else (orders[i].lat,orders[i].lon)
        second=(lat,lon)if j==depot else (orders[j].lat,orders[j].lon)
        return haversine(*first,*second)
    return [[int(km(i,j)*1000)for j in range(size+1)]for i in range(size+1)],depot_address
