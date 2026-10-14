"""Strict road-profile costs; unavailable routes never become zero-cost legs."""
from decimal import Decimal,ROUND_CEILING
from typing import Any

def number(value: Any,maximum: int) -> float:
    if isinstance(value,bool)or not isinstance(value,(int,float)):
        raise ValueError("ROAD_MATRIX_UNREACHABLE_OR_NON_NUMERIC_CELL")
    d=Decimal(str(value))
    if not d.is_finite()or d<0 or d>maximum:
        raise ValueError("ROAD_MATRIX_CELL_BOUND")
    return float(d)

def matrix(values: Any,size: int,maximum: int) -> list[list[float]]:
    if not isinstance(values,list)or len(values)!=size:
        raise ValueError("ROAD_MATRIX_DIMENSION_MISMATCH")
    result=[]
    for row in values:
        if not isinstance(row,list)or len(row)!=size:raise ValueError("ROAD_MATRIX_DIMENSION_MISMATCH")
        result.append([number(v,maximum)for v in row])
    return result

def osrm_costs(data: dict,size: int) -> tuple[list[list[float]],list[list[float]]]:
    if not 1<=size<=200 or data.get("code")!="Ok"or data.get("fallback_speed_cells"):
        raise ValueError("ROAD_MATRIX_NOT_ROUTED")
    metres=matrix(data.get("distances"),size,10**8)
    seconds=matrix(data.get("durations"),size,604800)
    km=[[round(v/1000,2)for v in row]for row in metres]
    minutes=[[float((Decimal(str(v))/Decimal(60)).quantize(Decimal("0.01"),rounding=ROUND_CEILING))for v in row]for row in seconds]
    return km,minutes

def valhalla_costs(data: dict,size: int) -> tuple[list[list[float]],list[list[float]]]:
    raw=data.get("sources_to_targets")
    if not 1<=size<=200 or not isinstance(raw,list)or len(raw)!=size:raise ValueError("ROAD_MATRIX_DIMENSION_MISMATCH")
    distances=[];seconds=[]
    for i,row in enumerate(raw):
        if not isinstance(row,list)or len(row)!=size:raise ValueError("ROAD_MATRIX_DIMENSION_MISMATCH")
        d=[];t=[]
        for j,cell in enumerate(row):
            if not isinstance(cell,dict)or cell.get("from_index",i)!=i or cell.get("to_index",j)!=j:raise ValueError("ROAD_MATRIX_PAIR_MISMATCH")
            d.append(number(cell.get("distance"),100000));t.append(number(cell.get("time"),604800))
        distances.append(d);seconds.append(t)
    return distances,[[float((Decimal(str(v))/60).quantize(Decimal("0.01"),rounding=ROUND_CEILING))for v in row]for row in seconds]


def validate_points(points: list[tuple[float,float]]) -> None:
    if not 1<=len(points)<=200:raise ValueError("ROAD_MATRIX_POINT_BOUND_200")
    for point in points:
        if not isinstance(point,(tuple,list))or len(point)!=2:raise ValueError("ROAD_MATRIX_COORDINATE_SHAPE")
        lat,lon=point
        if any(isinstance(v,bool)or not isinstance(v,(int,float))for v in point):raise ValueError("ROAD_MATRIX_COORDINATE_TYPE")
        if not(-90<=lat<=90 and -180<=lon<=180):raise ValueError("ROAD_MATRIX_COORDINATE_RANGE")
