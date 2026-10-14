"""Extract actual cumul values from the existing OR-Tools model."""
import math
from typing import Any
from ..domain.vrp_models import VrpOrder, VrpVehicle, VrpRoute


def extract_solver_routes(
    orders: list[VrpOrder], vehicles: list[VrpVehicle],
    distances: list[list[int]], depot: int,
    manager: Any, routing: Any, solution: Any,
    time_matrix: list[list[int]] | None = None,time_basis: list[list[str]] | None = None,
) -> tuple[list[VrpRoute], list[VrpOrder], int]:
    dimension = routing.GetDimensionOrDie("Time")
    routes: list[VrpRoute] = []
    remaining = set(range(len(orders)))
    violations = 0
    for vehicle_index, vehicle in enumerate(vehicles):
        index = routing.Start(vehicle_index)
        start = solution.Value(dimension.CumulVar(index))
        distance = 0
        stops: list[VrpOrder] = []
        schedule: list[dict[str, Any]] = []
        previous_distance = 0;previous_node=depot;road_legs=0
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            next_index = solution.Value(routing.NextVar(index))
            next_node = manager.IndexToNode(next_index)
            leg = distances[node][next_node]
            if node != depot:
                order = orders[node]
                arrival = solution.Value(dimension.CumulVar(index))
                departure = arrival + order.unload_norm_min
                next_arrival = solution.Value(dimension.CumulVar(next_index))
                travel = time_matrix[node][next_node]if time_matrix is not None else math.ceil(leg / 1000 / (50 / 60))
                violation = max(order.tw_from - arrival, arrival - order.tw_to, 0)
                violations += int(violation > 0)
                schedule.append({
                    "st_number": order.st_number,
                    "arrival_min": arrival,
                    "departure_min": departure,
                    "tw_violation_min": violation,
                    "wait_after_service_min": next_arrival - departure - travel,
                    "distance_from_prev_km": previous_distance / 1000,
                    "duration_from_prev_min":time_matrix[previous_node][node]if time_matrix is not None else math.ceil(previous_distance/1000/(50/60)),
                    "duration_from_prev_basis":time_basis[previous_node][node]if time_basis is not None else "SPEED_50_ESTIMATE",
                })
                stops.append(order)
                remaining.discard(node)
            if time_basis is not None and time_basis[node][next_node]=='ROAD_PROFILE_ESTIMATE':road_legs+=1
            previous_node=node
            distance += leg
            previous_distance = leg
            index = next_index
        end = solution.Value(dimension.CumulVar(index))
        if stops:
            routes.append(VrpRoute(
                vehicle=vehicle, stops=stops, total_km=round(distance / 1000, 1),
                total_pallets=sum(order.pallets for order in stops),
                total_kg=sum(order.weight_kg for order in stops),
                total_duration_min=end - start,
                schedule=schedule, schedule_status="RELATIVE_SOLVER_SCHEDULE",
                schedule_start_min=start, schedule_end_min=end,road_profile_legs=road_legs,
            ))
    return routes, [orders[index] for index in sorted(remaining)], violations
