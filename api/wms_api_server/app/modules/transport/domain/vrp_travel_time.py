"""One planning time matrix shared by OR-Tools and its displayed schedule."""
import math
from typing import Any

def travel_times(addresses: list[str],distances: list[list[int]],depot: int,cache: dict[tuple[str,str],float] | None,depot_address: str | None=None) -> tuple[list[list[int]],list[list[str]]]:
    size=len(distances);times=[];basis=[]
    for i in range(size):
        tr=[];br=[]
        for j in range(size):
            if i==j:minutes=0;source="SAME_NODE"
            elif (i==depot or j==depot)and not depot_address:
                minutes=math.ceil(distances[i][j]/1000/(50/60));source="VIRTUAL_DEPOT_SPEED_ESTIMATE"
            else:
                a=depot_address if i==depot else addresses[i];b=depot_address if j==depot else addresses[j]
                value=(cache or {}).get((a,b))
                if value is not None and math.isfinite(value)and 0<=value<=10080:
                    minutes=math.ceil(value);source="ROAD_PROFILE_ESTIMATE"
                else:
                    minutes=math.ceil(distances[i][j]/1000/(50/60));source="SPEED_50_ESTIMATE"
            tr.append(minutes);br.append(source)
        times.append(tr);basis.append(br)
    return times,basis
