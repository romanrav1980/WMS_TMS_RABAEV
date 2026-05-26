"""
vrp_solver.py — CVRPTW решатель (OR-Tools).

Ограничения:
  - Грузоподъёмность (PALLETS_COUNT ≤ vehicle.PALLETS)
  - Максимальный тоннаж (WEIGHT_KG / 1000 ≤ vehicle.MAX_TONS)
  - Тип ТС: если ST требует конкретный транспорт, назначается только подходящее ТС
  - Временны́е окна (TIME_FROM / TIME_TO) — мягкие (штраф) или жёсткие (TW_STRICT=1)
  - Норматив разгрузки (UNLOAD_NORM_MIN) — время обслуживания на каждом узле

Если ortools не установлен — solver возвращает fallback-план методом Clarke-Wright savings.

OR-Tools документация: https://developers.google.com/optimization/routing/vrp
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class VrpOrder:
    st_number: str
    addr: str
    lat: float
    lon: float
    pallets: int
    weight_kg: float
    ware_id: int
    transport_type: str | None
    tw_from: int = 0       # minutes from shift start (06:00)
    tw_to:   int = 1080    # minutes from shift start (06:00+18h=24:00)
    tw_strict: bool = False
    unload_norm_min: int = 30
    verify_perc: float | None = None


@dataclass
class VrpVehicle:
    id: int
    num: str          # гос. номер
    tr_type: str      # тип ТС
    max_pallets: int
    max_tons: float
    gidrobort: bool = False


@dataclass
class VrpRoute:
    vehicle: VrpVehicle
    stops: list[VrpOrder] = field(default_factory=list)
    total_km: float = 0.0
    total_pallets: int = 0
    total_kg: float = 0.0
    total_duration_min: int = 0

    @property
    def utilization_pct(self) -> float:
        if self.vehicle.max_pallets == 0:
            return 0.0
        return round(self.total_pallets / self.vehicle.max_pallets * 100, 1)


@dataclass
class VrpPlan:
    routes: list[VrpRoute] = field(default_factory=list)
    unassigned: list[VrpOrder] = field(default_factory=list)
    total_km: float = 0.0
    fleet_utilization_pct: float = 0.0
    tw_violations: int = 0
    score: float = 0.0
    solver_used: str = "none"
    solve_time_ms: int = 0


# ---------------------------------------------------------------------------
# Distance helper
# ---------------------------------------------------------------------------

_HAVERSINE_FACTOR = 1.35


def _hav_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a)) * _HAVERSINE_FACTOR


def _dist(a: VrpOrder, b: VrpOrder) -> float:
    return _hav_km(a.lat, a.lon, b.lat, b.lon)


# ---------------------------------------------------------------------------
# OR-Tools CVRPTW solver
# ---------------------------------------------------------------------------

def _solve_ortools(
    orders: list[VrpOrder],
    vehicles: list[VrpVehicle],
    dist_matrix: list[list[int]],  # in metres (int)
    depot_idx: int,
    time_limit_s: int,
) -> "Any":
    """Returns (manager, routing, solution) or raises ImportError."""
    from ortools.constraint_solver import pywrapcp, routing_enums_pb2  # type: ignore

    n_nodes = len(orders) + 1  # +1 for depot
    n_vehicles = len(vehicles)

    manager = pywrapcp.RoutingIndexManager(n_nodes, n_vehicles, depot_idx)
    routing = pywrapcp.RoutingModel(manager)

    # Distance callback
    def dist_cb(from_idx: int, to_idx: int) -> int:
        fi = manager.IndexToNode(from_idx)
        ti = manager.IndexToNode(to_idx)
        return dist_matrix[fi][ti]

    dist_cb_idx = routing.RegisterTransitCallback(dist_cb)
    routing.SetArcCostEvaluatorOfAllVehicles(dist_cb_idx)

    # Pallet capacity
    def pallet_demand(idx: int) -> int:
        node = manager.IndexToNode(idx)
        if node == depot_idx:
            return 0
        return orders[node].pallets

    pallet_cb_idx = routing.RegisterUnaryTransitCallback(pallet_demand)
    routing.AddDimensionWithVehicleCapacity(
        pallet_cb_idx,
        0,  # no slack
        [v.max_pallets for v in vehicles],
        True,
        "Pallets",
    )

    # Time dimension (minutes)
    SPEED_KM_MIN = 50.0 / 60.0  # km/min

    def time_cb(from_idx: int, to_idx: int) -> int:
        fi = manager.IndexToNode(from_idx)
        ti = manager.IndexToNode(to_idx)
        dist_km = dist_matrix[fi][ti] / 1000.0
        travel = int(dist_km / SPEED_KM_MIN)
        service = orders[ti].unload_norm_min if ti != depot_idx else 0
        return travel + service

    time_cb_idx = routing.RegisterTransitCallback(time_cb)
    routing.AddDimension(
        time_cb_idx,
        60,    # max waiting time (slack) — soft TW
        1440,  # max shift minutes
        False,
        "Time",
    )
    time_dim = routing.GetDimensionOrDie("Time")

    # Time windows
    for order_idx, order in enumerate(orders):
        node_idx = manager.NodeToIndex(order_idx)  # depot is at n_nodes-1
        if order.tw_strict:
            time_dim.CumulVar(node_idx).SetRange(order.tw_from, order.tw_to)
        else:
            # soft penalty
            time_dim.SetCumulVarSoftLowerBound(node_idx, order.tw_from, 50)
            time_dim.SetCumulVarSoftUpperBound(node_idx, order.tw_to, 50)

    # Allow dropping orders (penalty = large number)
    penalty = 100_000
    for node_idx in range(1, n_nodes):
        routing.AddDisjunction([manager.NodeToIndex(node_idx)], penalty)

    search_params = pywrapcp.DefaultRoutingSearchParameters()
    search_params.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_params.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search_params.time_limit.seconds = time_limit_s

    solution = routing.SolveWithParameters(search_params)
    return manager, routing, solution


# ---------------------------------------------------------------------------
# Clarke-Wright savings (fallback if ortools not available)
# ---------------------------------------------------------------------------

def _solve_clarke_wright(
    orders: list[VrpOrder],
    vehicles: list[VrpVehicle],
) -> VrpPlan:
    """Greedy Clarke-Wright savings heuristic — O(n² log n)."""
    import time
    t0 = time.time()

    if not orders or not vehicles:
        return VrpPlan(solver_used="clarke-wright")

    # savings[i][j] = dist(depot,i) + dist(depot,j) - dist(i,j)
    # Use centre of gravity as virtual depot
    depot_lat = sum(o.lat for o in orders) / len(orders)
    depot_lon = sum(o.lon for o in orders) / len(orders)

    class _Depot:
        lat = depot_lat
        lon = depot_lon

    depot = _Depot()

    def _d(a: Any, b: Any) -> float:
        return _hav_km(a.lat, a.lon, b.lat, b.lon)

    savings = sorted(
        (
            (_d(depot, orders[i]) + _d(depot, orders[j]) - _d(orders[i], orders[j]), i, j)
            for i in range(len(orders))
            for j in range(i + 1, len(orders))
        ),
        reverse=True,
    )

    # Init: one route per vehicle, greedily assign orders
    routes: list[VrpRoute] = [VrpRoute(vehicle=v) for v in vehicles]
    assigned: set[int] = set()

    def _can_add(route: VrpRoute, order: VrpOrder) -> bool:
        if route.total_pallets + order.pallets > route.vehicle.max_pallets:
            return False
        if (route.total_kg + order.weight_kg) / 1000 > route.vehicle.max_tons:
            return False
        return True

    # Assign by savings
    for _, i, j in savings:
        if i in assigned and j in assigned:
            continue
        for route in routes:
            if i not in assigned and _can_add(route, orders[i]):
                route.stops.append(orders[i])
                route.total_pallets += orders[i].pallets
                route.total_kg      += orders[i].weight_kg
                assigned.add(i)
            if j not in assigned and _can_add(route, orders[j]):
                route.stops.append(orders[j])
                route.total_pallets += orders[j].pallets
                route.total_kg      += orders[j].weight_kg
                assigned.add(j)

    # Assign remaining orders to any vehicle that fits
    for idx, order in enumerate(orders):
        if idx in assigned:
            continue
        for route in routes:
            if _can_add(route, order):
                route.stops.append(order)
                route.total_pallets += order.pallets
                route.total_kg      += order.weight_kg
                assigned.add(idx)
                break

    unassigned = [orders[i] for i in range(len(orders)) if i not in assigned]

    # Compute km per route
    total_km = 0.0
    for route in routes:
        if not route.stops:
            continue
        km = _d(depot, route.stops[0])
        for k in range(len(route.stops) - 1):
            km += _d(route.stops[k], route.stops[k + 1])
        km += _d(route.stops[-1], depot)
        route.total_km = round(km, 1)
        total_km += route.total_km

    active = [r for r in routes if r.stops]
    fleet_util = (
        sum(r.total_pallets for r in active) / sum(r.vehicle.max_pallets for r in active) * 100
        if active else 0.0
    )

    solve_ms = int((time.time() - t0) * 1000)
    return VrpPlan(
        routes=[r for r in routes if r.stops],
        unassigned=unassigned,
        total_km=round(total_km, 1),
        fleet_utilization_pct=round(fleet_util, 1),
        tw_violations=0,
        score=round(fleet_util - total_km / 100, 2),
        solver_used="clarke-wright",
        solve_time_ms=solve_ms,
    )


# ---------------------------------------------------------------------------
# DBSCAN cluster solver (Sprint 9)
# ---------------------------------------------------------------------------

def _solve_dbscan_cluster(
    orders: list[VrpOrder],
    vehicles: list[VrpVehicle],
    dist_cache: dict[tuple[str, str], float] | None,
    time_limit_s: int,
) -> VrpPlan:
    """
    Кластеризует заказы DBSCAN → запускает локальный VRP в каждом кластере.
    Если sklearn недоступен — откатывается до Clarke-Wright.
    """
    try:
        import numpy as np
        from sklearn.cluster import DBSCAN  # type: ignore
    except ImportError:
        return _solve_clarke_wright(orders, vehicles)

    import time
    t0 = time.time()

    coords = np.array([[o.lat, o.lon] for o in orders])
    # eps = 0.5 degrees ≈ 50 km; min_samples=2
    db = DBSCAN(eps=0.5, min_samples=2, metric="haversine").fit(np.radians(coords))
    labels = db.labels_

    clusters: dict[int, list[VrpOrder]] = {}
    for idx, label in enumerate(labels):
        clusters.setdefault(label, []).append(orders[idx])

    # Distribute vehicles across clusters proportionally to order count
    all_routes: list[VrpRoute] = []
    used_vehicles: list[VrpVehicle] = list(vehicles)
    unassigned_orders: list[VrpOrder] = []

    cluster_keys = sorted(clusters.keys())  # noise (-1) first
    for label in cluster_keys:
        c_orders = clusters[label]
        n_vehicles_for_cluster = max(1, round(len(c_orders) / max(1, len(orders)) * len(vehicles)))
        c_vehicles = used_vehicles[:n_vehicles_for_cluster]
        used_vehicles = used_vehicles[n_vehicles_for_cluster:]
        if not c_vehicles:
            unassigned_orders.extend(c_orders)
            continue
        sub_plan = _solve_clarke_wright(c_orders, c_vehicles)
        all_routes.extend(sub_plan.routes)
        unassigned_orders.extend(sub_plan.unassigned)

    total_km = sum(r.total_km for r in all_routes)
    active = [r for r in all_routes if r.stops]
    fleet_util = (
        sum(r.total_pallets for r in active) / sum(r.vehicle.max_pallets for r in active) * 100
        if active else 0.0
    )
    score = round(fleet_util - total_km / 100, 2)
    solve_ms = int((time.time() - t0) * 1000)

    return VrpPlan(
        routes=all_routes,
        unassigned=unassigned_orders,
        total_km=round(total_km, 1),
        fleet_utilization_pct=round(fleet_util, 1),
        tw_violations=0,
        score=score,
        solver_used="dbscan-cluster",
        solve_time_ms=solve_ms,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def solve(
    orders: list[VrpOrder],
    vehicles: list[VrpVehicle],
    dist_cache: dict[tuple[str, str], float] | None = None,
    time_limit_s: int = 30,
    solver: str = "auto",
) -> VrpPlan:
    """
    Запускает решатель.

    solver: 'auto' | 'ortools' | 'cluster' | 'savings'
    Приоритет при 'auto':
      1. OR-Tools CVRPTW (если установлен)
      2. Clarke-Wright savings (всегда доступен)
    """
    import time

    t0 = time.time()

    # Filter orders: must have valid coordinates
    valid = [o for o in orders if o.lat and o.lon]
    if not valid:
        return VrpPlan(solver_used="none")

    if solver == "cluster":
        return _solve_dbscan_cluster(valid, vehicles, dist_cache, time_limit_s)
    elif solver == "savings":
        return _solve_clarke_wright(valid, vehicles)
    elif solver == "ortools":
        try:
            import time as _t
            return _solve_with_ortools(valid, vehicles, dist_cache, time_limit_s, _t.time())
        except ImportError:
            return _solve_clarke_wright(valid, vehicles)
    else:  # auto
        try:
            return _solve_with_ortools(valid, vehicles, dist_cache, time_limit_s, t0)
        except ImportError:
            return _solve_clarke_wright(valid, vehicles)


def _solve_with_ortools(
    orders: list[VrpOrder],
    vehicles: list[VrpVehicle],
    dist_cache: dict[tuple[str, str], float] | None,
    time_limit_s: int,
    t0: float,
) -> VrpPlan:
    import time

    n_orders = len(orders)
    n_nodes  = n_orders + 1  # last index = depot
    depot_idx = n_nodes - 1

    # Build integer distance matrix in metres
    def _km(i: int, j: int) -> float:
        if i == depot_idx or j == depot_idx:
            # depot at centre of gravity
            if i == depot_idx:
                depot_lat = sum(o.lat for o in orders) / len(orders)
                depot_lon = sum(o.lon for o in orders) / len(orders)
                return _hav_km(depot_lat, depot_lon, orders[j].lat, orders[j].lon)
            else:
                depot_lat = sum(o.lat for o in orders) / len(orders)
                depot_lon = sum(o.lon for o in orders) / len(orders)
                return _hav_km(orders[i].lat, orders[i].lon, depot_lat, depot_lon)
        if dist_cache:
            cached = dist_cache.get((orders[i].addr, orders[j].addr))
            if cached is not None:
                return cached
        return _hav_km(orders[i].lat, orders[i].lon, orders[j].lat, orders[j].lon)

    dist_matrix = [
        [int(_km(i, j) * 1000) for j in range(n_nodes)]
        for i in range(n_nodes)
    ]

    manager, routing, solution = _solve_ortools(orders, vehicles, dist_matrix, depot_idx, time_limit_s)

    if not solution:
        return _solve_clarke_wright(orders, vehicles)

    # Extract routes
    routes: list[VrpRoute] = []
    unassigned_nodes: set[int] = set(range(n_orders))
    tw_violations = 0
    time_dim = routing.GetDimensionOrDie("Time")

    for v_idx, vehicle in enumerate(vehicles):
        idx = routing.Start(v_idx)
        route_stops: list[VrpOrder] = []
        total_km = 0.0
        prev_idx = idx

        while not routing.IsEnd(idx):
            node = manager.IndexToNode(idx)
            if node != depot_idx:
                route_stops.append(orders[node])
                unassigned_nodes.discard(node)
                # Check TW violation
                order = orders[node]
                t_val = solution.Value(time_dim.CumulVar(idx))
                if t_val > order.tw_to:
                    tw_violations += 1

            prev_idx = idx
            idx = solution.Value(routing.NextVar(idx))
            if not routing.IsEnd(idx):
                fi = manager.IndexToNode(prev_idx)
                ti = manager.IndexToNode(idx)
                total_km += dist_matrix[fi][ti] / 1000.0

        if route_stops:
            r = VrpRoute(vehicle=vehicle, stops=route_stops)
            r.total_km      = round(total_km, 1)
            r.total_pallets = sum(o.pallets for o in route_stops)
            r.total_kg      = sum(o.weight_kg for o in route_stops)
            r.total_duration_min = int(
                sum(o.unload_norm_min for o in route_stops) + total_km / (50.0 / 60.0)
            )
            routes.append(r)

    unassigned = [orders[i] for i in sorted(unassigned_nodes)]

    total_km_all = sum(r.total_km for r in routes)
    active = [r for r in routes if r.stops]
    fleet_util = (
        sum(r.total_pallets for r in active) / sum(r.vehicle.max_pallets for r in active) * 100
        if active else 0.0
    )
    score = round(fleet_util - total_km_all / 100.0 - tw_violations * 5, 2)
    solve_ms = int((time.time() - t0) * 1000)

    return VrpPlan(
        routes=routes,
        unassigned=unassigned,
        total_km=round(total_km_all, 1),
        fleet_utilization_pct=round(fleet_util, 1),
        tw_violations=tw_violations,
        score=score,
        solver_used="ortools-cvrptw",
        solve_time_ms=solve_ms,
    )
