"""Refresh only a trip's directed legs; provider calls hold no Oracle transaction."""
from hashlib import sha256
import json
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from ...inventory.public import warehouse_metadata_transaction
from ..contracts_preflight import RoadCosts
from ..contracts_plan import TransportPlanError
from ..domain.road_matrix import validate_points, matrix
from .road_leg_estimate import read_snapshot
from .trip_edit import trip_error


def replay(cur: Any, operation: str, trip: int, actor: str, digest: str) -> dict | None:
    cur.execute("select TT_ID,ACTOR,REQUEST_HASH,RESULT_JSON from RRL_TT_ROAD_REFRESH where OPERATION_ID=:op", op=operation)
    row = cur.fetchone()
    if row is None:
        return None
    if row[:3] != (trip, actor, digest):
        raise TransportPlanError("ROAD_REFRESH_OPERATION_CONFLICT", "Номер операции уже связан с другим запросом")
    return read_oracle_json(row[3])


def coordinates(cur: Any, addresses: list[str], lock: bool = False) -> list[tuple[float, float]]:
    params = {f"a{i}": value for i, value in enumerate(addresses)}
    binds = ",".join(":" + key for key in params)
    cur.execute("select ADDR,SHIROTA,DOLGOTA from RRL_ADDR where nvl(DELETED3,0)=0 and ADDR in (" + binds + ")"
                + (" order by ADDR for update wait 5" if lock else ""), params)
    found: dict[str, tuple[float, float]] = {}
    for address, lat, lon in cur:
        if address in found or lat is None or lon is None or lat == 0 or lon == 0:
            raise TransportPlanError("ROAD_ADDRESS_COORDINATES_REQUIRED", "Проверьте единственность адресов и координаты точек", 422)
        found[address] = (float(lat), float(lon))
    if len(found) != len(addresses):
        raise TransportPlanError("ROAD_ADDRESS_COORDINATES_REQUIRED", "У каждой точки должен быть действующий адрес с координатами", 422)
    points = [found[a] for a in addresses]
    validate_points(points)
    return points


def check_basis(snapshot: dict, body: dict) -> list[str]:
    if snapshot["source_hash"] != body["source_hash"] or snapshot["route_input_version"] != body["expected_version"]:
        raise TransportPlanError("ROAD_REFRESH_SOURCE_CHANGED", "Рейс или дорожные данные изменились. Перечитайте маршрут")
    if snapshot["source_issues"] or snapshot["depot_basis"] != "CONFIGURED_WAREHOUSE_REFERENCE":
        raise TransportPlanError("ROAD_REFRESH_ROUTE_REQUIRED", "Задайте адрес склада и порядок точек доставки", 422)
    addresses = list(dict.fromkeys([snapshot["depot_address"], *snapshot["stops"]]))
    if not snapshot["stops"] or not 2 <= len(addresses) <= 200 or any(a == b for a, b in
        zip([snapshot["depot_address"], *snapshot["stops"]], [*snapshot["stops"], snapshot["depot_address"]])):
        raise TransportPlanError("ROAD_REFRESH_ROUTE_BOUND", "Нужны разные соседние точки и не более200 адресов", 422)
    return addresses


def publish(gateway: Any, operation: str, body: dict, actor: str, digest: str, addresses: list[str],
            points: list[tuple[float, float]], provider: str, distances: list, durations: list) -> dict:
    trip = body["trip_id"]
    with warehouse_metadata_transaction(gateway, "Refresh trip road cache", actor, "transport_dispatch_edit") as cur:
        cur.execute("select ID from RRL_TRANSPORT_TASK where ID=:id for update wait 5", id=trip)
        snapshot = read_snapshot(cur, trip, "", 24, actor)
        saved = replay(cur, operation, trip, actor, digest)
        if saved is not None:
            return saved
        if check_basis(snapshot, body) != addresses or coordinates(cur, addresses, lock=True) != points:
            raise TransportPlanError("ROAD_REFRESH_SOURCE_CHANGED", "Координаты или маршрут изменились. Перечитайте данные")
        index = {address: i for i, address in enumerate(addresses)}
        legs = snapshot["legs"]
        for leg in legs:
            a, b = leg["from_address"], leg["to_address"]
            km, minutes = distances[index[a]][index[b]], durations[index[a]][index[b]]
            if km <= 0 or minutes <= 0:
                raise TransportPlanError("ROAD_PROVIDER_LEG_UNREACHABLE", "Дорожный сервис не вернул положительную длительность плеча", 422)
            cur.execute("""merge into RRL_ADDR_DISTANCE_MATRIX m using(select :a A,:b B from dual)s
                on(m.FROM_ADDR=s.A and m.TO_ADDR=s.B)
                when matched then update set DISTANCE_KM=:km,DURATION_MIN=:minutes,DURATION_BASIS='ROAD_PROFILE_ESTIMATE',SOURCE=:provider,UPDATED_AT=sysdate
                when not matched then insert(FROM_ADDR,TO_ADDR,DISTANCE_KM,DURATION_MIN,DURATION_BASIS,SOURCE,UPDATED_AT)
                values(:a,:b,:km,:minutes,'ROAD_PROFILE_ESTIMATE',:provider,sysdate)""", a=a, b=b, km=km, minutes=minutes, provider=provider)
        result = {"operation_id": operation, "trip_id": trip, "updated_legs": len(legs), "provider": provider,
                  "duration_basis": "ROAD_PROFILE_ESTIMATE", "stock_changed": False, "operational_admission": False}
        cur.execute("""insert into RRL_TT_ROAD_REFRESH(OPERATION_ID,TT_ID,ACTOR,REQUEST_HASH,RESULT_JSON)
            values(:op,:trip,:actor,:digest,:result)""", op=operation, trip=trip, actor=actor, digest=digest,
                    result=json.dumps(result, sort_keys=True, separators=(",", ":")))
        return result


def refresh_road(gateway: Any, operation: str, body: dict, actor: str, provider: RoadCosts | None) -> dict:
    digest = sha256(json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()).hexdigest()
    try:
        with gateway.transaction("Trip road refresh basis READ ONLY") as cur:
            cur.execute("set transaction read only")
            snapshot = read_snapshot(cur, body["trip_id"], "", 24, actor)
            saved = replay(cur, operation, body["trip_id"], actor, digest)
            if saved is not None:
                return saved
            addresses = check_basis(snapshot, body)
            points = coordinates(cur, addresses)
        if provider is None:
            raise TransportPlanError("ROAD_PROVIDER_UNAVAILABLE", "Дорожный сервис не подключён", 503)
        try:
            name, distances, durations = provider(points)
            if name not in {"osrm", "valhalla"}:
                raise ValueError("ROAD_PROVIDER_UNAVAILABLE")
            distances, durations = matrix(distances, len(points), 100000), matrix(durations, len(points), 10080)
        except (ValueError, OSError, RuntimeError) as exc:
            raise TransportPlanError("ROAD_PROVIDER_UNAVAILABLE", "Дорожный сервис не вернул расчёт. Повторите исходную команду", 503) from exc
        return publish(gateway, operation, body, actor, digest, addresses, points, name, distances, durations)
    except oracledb.DatabaseError as exc:
        raise trip_error(exc) from exc
