from .oracle_gateway import OracleGateway
from .modules.transport.public import TransportPreflight, TransportPreflightPort
from .services.routing import get_active_provider
import httpx


def road_costs(points: list[tuple[float, float]]) -> tuple[str, list[list[float]], list[list[float]]]:
    provider = get_active_provider()
    if provider.name not in {"osrm", "valhalla"}:
        raise ValueError("ROAD_PROVIDER_UNAVAILABLE")
    try:
        distances, durations = provider.build_cost_matrix(points)
    except httpx.HTTPError as exc:
        raise RuntimeError("ROAD_PROVIDER_UNAVAILABLE") from exc
    if durations is None:
        raise ValueError("ROAD_PROVIDER_DURATION_REQUIRED")
    return provider.name, distances, durations


def preflight_service() -> TransportPreflightPort:
    return TransportPreflight(OracleGateway(), road_costs)
