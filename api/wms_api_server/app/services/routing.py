"""
routing.py — RoutingProvider abstraction.

Иерархия провайдеров (§11.12.3):
  1. OsrmProvider   — http://localhost:5000/table/v1/driving/  (точные расстояния)
  2. ValhallaProvider — http://localhost:8002/sources_to_targets  (резерв)
  3. HaversineProvider — всегда доступен (прямолинейные расстояния × 1.35 — поправочный коэф.)

_fallback_chain() берёт первый доступный провайдер.
"""

from __future__ import annotations

import math
import os
from abc import ABC, abstractmethod
from typing import Any

import httpx


# ---------------------------------------------------------------------------
# ABC
# ---------------------------------------------------------------------------

class RoutingProvider(ABC):
    name: str = "base"

    @abstractmethod
    def is_available(self) -> bool:
        ...

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


class OsrmProvider(RoutingProvider):
    name = "osrm"

    def is_available(self) -> bool:
        try:
            r = httpx.get(f"{OSRM_URL}/health", timeout=2.0)
            return r.status_code == 200
        except Exception:
            return False

    def build_matrix(self, points: list[tuple[float, float]]) -> list[list[float]]:
        coords_str = ";".join(f"{lon},{lat}" for lat, lon in points)
        url = f"{OSRM_URL}/table/v1/driving/{coords_str}?annotations=distance"
        r = httpx.get(url, timeout=_OSRM_TIMEOUT)
        r.raise_for_status()
        data = r.json()
        distances = data["distances"]  # in metres
        n = len(points)
        return [
            [round(distances[i][j] / 1000.0, 2) for j in range(n)]
            for i in range(n)
        ]


# ---------------------------------------------------------------------------
# Valhalla
# ---------------------------------------------------------------------------

VALHALLA_URL = os.environ.get("VALHALLA_URL", "http://localhost:8002")
_VALHALLA_TIMEOUT = 15.0


class ValhallaProvider(RoutingProvider):
    name = "valhalla"

    def is_available(self) -> bool:
        try:
            r = httpx.get(f"{VALHALLA_URL}/health", timeout=2.0)
            return r.status_code == 200
        except Exception:
            return False

    def build_matrix(self, points: list[tuple[float, float]]) -> list[list[float]]:
        locations = [{"lat": lat, "lon": lon} for lat, lon in points]
        payload: dict[str, Any] = {
            "sources": locations,
            "targets": locations,
            "costing": "truck",
        }
        r = httpx.post(
            f"{VALHALLA_URL}/sources_to_targets",
            json=payload,
            timeout=_VALHALLA_TIMEOUT,
        )
        r.raise_for_status()
        data = r.json()
        n = len(points)
        return [
            [round((data["sources_to_targets"][i][j]["distance"] or 0.0), 2) for j in range(n)]
            for i in range(n)
        ]


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
