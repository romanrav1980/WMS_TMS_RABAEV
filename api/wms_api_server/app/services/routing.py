"""
routing.py — RoutingProvider abstraction.

Иерархия провайдеров (§11.12.3):
  1. OsrmProvider   — http://localhost:5000/table/v1/driving/  (точные расстояния)
  2. ValhallaProvider — http://localhost:8002/sources_to_targets  (резерв)
  3. HaversineProvider — всегда доступен (прямолинейные расстояния × 1.35 — поправочный коэф.)

_fallback_chain() берёт первый доступный провайдер.
"""

from __future__ import annotations

import atexit
import math
import os
import socket
import time
from urllib.parse import urlparse
from abc import ABC, abstractmethod
from typing import Any

import httpx

# Reuse the client: constructing one for each matrix took ~1.3 s in the local run.
_HTTP_CLIENT = httpx.Client()
atexit.register(_HTTP_CLIENT.close)


# ---------------------------------------------------------------------------
# ABC
# ---------------------------------------------------------------------------

class RoutingProvider(ABC):
    name: str = "base"

    @abstractmethod
    def is_available(self) -> bool:
        ...

    def build_cost_matrix(self,points: list[tuple[float,float]]) -> tuple[list[list[float]],list[list[float]] | None]:
        return self.build_matrix(points),None

    @abstractmethod
    def build_matrix(
        self,
        points: list[tuple[float, float]],
    ) -> list[list[float]]:
        """Возвращает матрицу расстояний (км) N×N."""
        ...


# ---------------------------------------------------------------------------
# Haversine (всегда работает)
# ---------------------------------------------------------------------------

_HAVERSINE_FACTOR = 1.35  # поправочный коэффициент прямолинейное → автодорога


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


class HaversineProvider(RoutingProvider):
    name = "haversine"

    def is_available(self) -> bool:
        return True

    def build_matrix(self, points: list[tuple[float, float]]) -> list[list[float]]:
        n = len(points)
        matrix: list[list[float]] = []
        for i in range(n):
            row: list[float] = []
            for j in range(n):
                if i == j:
                    row.append(0.0)
                else:
                    d = _haversine_km(
                        points[i][0], points[i][1],
                        points[j][0], points[j][1],
                    ) * _HAVERSINE_FACTOR
                    row.append(round(d, 2))
            matrix.append(row)
        return matrix


# ---------------------------------------------------------------------------
# OSRM
# ---------------------------------------------------------------------------

OSRM_URL = os.environ.get("OSRM_URL", "http://localhost:5000")
_OSRM_TIMEOUT = 15.0
_HEALTH_TIMEOUT = float(os.environ.get("ROUTING_HEALTH_TIMEOUT", "0.05"))
_AVAILABILITY_TTL_SEC = 30.0
_AVAILABILITY_CACHE: dict[str, tuple[float, bool]] = {}


def _cached_availability(name: str, loader: Any) -> bool:
    now = time.monotonic()
    cached = _AVAILABILITY_CACHE.get(name)
    if cached and now - cached[0] <= _AVAILABILITY_TTL_SEC:
        return cached[1]
    value = bool(loader())
    _AVAILABILITY_CACHE[name] = (time.monotonic(), value)
    return value


def _tcp_url_available(url: str) -> bool:
    parsed = urlparse(url)
    host = parsed.hostname or "localhost"
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    try:
        with socket.create_connection((host, port), timeout=_HEALTH_TIMEOUT):
            return True
    except OSError:
        return False


class OsrmProvider(RoutingProvider):
    name = "osrm"

    def is_available(self) -> bool:
        return _cached_availability(self.name, lambda: _tcp_url_available(OSRM_URL))

    def build_matrix(self,points: list[tuple[float,float]]) -> list[list[float]]:
        return self.build_cost_matrix(points)[0]

    def build_cost_matrix(self,points: list[tuple[float,float]]) -> tuple[list[list[float]],list[list[float]]]:
        from ..modules.transport.public import osrm_costs,validate_points
        validate_points(points)
        coords_str=";".join(f"{lon},{lat}"for lat,lon in points)
        radii=";".join("1000"for _ in points)
        url=f"{OSRM_URL}/table/v1/driving/{coords_str}?annotations=distance,duration&radiuses={radii}"
        response=_HTTP_CLIENT.get(url,timeout=_OSRM_TIMEOUT);response.raise_for_status()
        return osrm_costs(response.json(),len(points))


# ---------------------------------------------------------------------------
# Valhalla
# ---------------------------------------------------------------------------

VALHALLA_URL = os.environ.get("VALHALLA_URL", "http://localhost:8002")
_VALHALLA_TIMEOUT = 15.0


class ValhallaProvider(RoutingProvider):
    name = "valhalla"

    def is_available(self) -> bool:
        return _cached_availability(self.name, lambda: _tcp_url_available(VALHALLA_URL))

    def build_matrix(self,points: list[tuple[float,float]]) -> list[list[float]]:
        return self.build_cost_matrix(points)[0]

    def build_cost_matrix(self,points: list[tuple[float,float]]) -> tuple[list[list[float]],list[list[float]]]:
        from ..modules.transport.public import valhalla_costs,validate_points
        validate_points(points)
        locations=[{"lat":lat,"lon":lon,"radius":1000,"search_cutoff":1000}for lat,lon in points]
        response=_HTTP_CLIENT.post(f"{VALHALLA_URL}/sources_to_targets",json={"sources":locations,"targets":locations,"costing":"truck","units":"kilometers"},timeout=_VALHALLA_TIMEOUT)
        response.raise_for_status();return valhalla_costs(response.json(),len(points))


# ---------------------------------------------------------------------------
# Fallback chain
# ---------------------------------------------------------------------------

_PRIORITY: list[RoutingProvider] = [
    OsrmProvider(),
    ValhallaProvider(),
    HaversineProvider(),
]


def get_active_provider() -> RoutingProvider:
    """Возвращает первый доступный провайдер (OSRM → Valhalla → Haversine)."""
    for p in _PRIORITY:
        if p.is_available():
            return p
    return HaversineProvider()
