"""Bounded saved-plan structure; never substitute missing sources or schedule."""
from typing import Any
from .plan_error import TransportPlanError


def plan_routes(document: dict[str, Any]) -> list[dict[str, Any]]:
    if not isinstance(document, dict):
        raise TransportPlanError("PLAN_SOURCE_INVALID", "Некорректное содержимое плана")
    routes = document.get("routes")
    if not isinstance(routes, list) or not 1 <= len(routes) <= 100:
        raise TransportPlanError("PLAN_ROUTE_BOUND_1_100", "Требуется от1 до100 маршрутов")
    seen: set[str] = set()
    vehicles: set[int] = set()
    for route in routes:
        if not isinstance(route, dict):
            raise TransportPlanError("PLAN_ROUTE_INVALID", "Некорректный маршрут")
        vehicle = route.get("vehicle_id")
        stops = route.get("stops")
        if type(vehicle) is not int or vehicle < 1 or vehicle in vehicles:
            raise TransportPlanError("PLAN_DISTINCT_CURRENT_VEHICLES_REQUIRED", "Требуются разные действующие машины")
        vehicles.add(vehicle)
        if not isinstance(stops, list) or not 1 <= len(stops) <= 200:
            raise TransportPlanError("PLAN_ROUTE_ST_BOUND_1_200", "В маршруте требуется от1 до200 СТ")
        for number in stops:
            if not isinstance(number, str) or not number.strip() or len(number) > 100 or number in seen:
                raise TransportPlanError("PLAN_DUPLICATE_OR_INVALID_ST", "Повторная или некорректная СТ")
            seen.add(number)
    if len(seen) > 2000:
        raise TransportPlanError("PLAN_ST_BOUND_2000", "План ограничен2000 СТ")
    return routes
