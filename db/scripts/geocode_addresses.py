"""
geocode_addresses.py — Массовое геокодирование адресов из RRL_ADDR через DaData.ru.

Заполняет поля SHIROTA / DOLGOTA для адресов без координат.
Запускается вручную или по расписанию перед первым запуском оптимизатора.

Требования:
  pip install dadata cx_Oracle
  export DADATA_TOKEN=<ваш токен>
  export ORACLE_DSN=host:port/service_name
  export ORACLE_USER=RABAEV
  export ORACLE_PASSWORD=<пароль>

Использование:
  python db/scripts/geocode_addresses.py
  python db/scripts/geocode_addresses.py --limit 100          # только 100 адресов за раз
  python db/scripts/geocode_addresses.py --dry-run             # без записи в БД
  python db/scripts/geocode_addresses.py --addr-like "ДЦ%"    # только seed-адреса
"""

from __future__ import annotations

import argparse
import math
import os
import sys
import time
from typing import Any


# ---------------------------------------------------------------------------
# Haversine-fallback (если DaData недоступен)
# ---------------------------------------------------------------------------

MOSCOW_LAT = 55.7558
MOSCOW_LON = 37.6173
EARTH_R_KM = 6371.0


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_lat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2
    return EARTH_R_KM * 2 * math.asin(math.sqrt(a))


# ---------------------------------------------------------------------------
# DaData geocoder
# ---------------------------------------------------------------------------

class DaDataGeocoder:
    """Геокодер через DaData Suggestions API."""

    API_URL = "https://suggestions.dadata.ru/suggestions/api/4_1/rs/geolocate/address"

    def __init__(self, token: str) -> None:
        self.token = token
        try:
            import requests
            self._sess = requests.Session()
            self._sess.headers.update({
                "Authorization": f"Token {token}",
                "Content-Type": "application/json",
            })
        except ImportError:
            print("WARN: requests not installed. pip install requests", file=sys.stderr)
            self._sess = None

    def geocode(self, address: str) -> tuple[float, float] | None:
        """Возвращает (lat, lon) или None при ошибке."""
        if self._sess is None:
            return None
        try:
            import requests
            r = self._sess.post(
                "https://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest/address",
                json={"query": address, "count": 1},
                timeout=5,
            )
            if r.status_code != 200:
                return None
            data = r.json()
            suggestions = data.get("suggestions", [])
            if not suggestions:
                return None
            geo = suggestions[0].get("data", {})
            lat = geo.get("geo_lat")
            lon = geo.get("geo_lon")
            if lat and lon:
                return float(lat), float(lon)
        except requests.exceptions.RequestException:
            pass
        return None


# ---------------------------------------------------------------------------
# Oracle connection
# ---------------------------------------------------------------------------

def get_connection() -> Any:
    try:
        import cx_Oracle as ora
    except ImportError:
        try:
            import oracledb as ora  # type: ignore
        except ImportError:
            print("ERROR: ни cx_Oracle, ни oracledb не установлен", file=sys.stderr)
            sys.exit(1)

    dsn  = os.environ.get("ORACLE_DSN",      "localhost:1521/orcl")
    user = os.environ.get("ORACLE_USER",     "RABAEV")
    pwd  = os.environ.get("ORACLE_PASSWORD", "")
    return ora.connect(user=user, password=pwd, dsn=dsn)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run(limit: int, dry_run: bool, addr_like: str, token: str | None) -> None:
    geocoder = DaDataGeocoder(token) if token else None

    conn = get_connection()
    cur = conn.cursor()

    # Получить адреса без координат
    query = """
        SELECT ADDR, REGION
          FROM RABAEV.RRL_ADDR
         WHERE (SHIROTA IS NULL OR SHIROTA = 0)
    """
    params: dict[str, Any] = {}
    if addr_like:
        query += " AND ADDR LIKE :addr_like"
        params["addr_like"] = addr_like
    if limit:
        query += f" AND ROWNUM <= {limit}"

    cur.execute(query, params)
    rows = cur.fetchall()

    print(f"Найдено адресов без координат: {len(rows)}")
    if not rows:
        print("Нечего геокодировать.")
        return

    updated = 0
    failed  = 0

    for addr, region in rows:
        # Попытка геокодирования через DaData
        coords = None
        if geocoder:
            full_addr = f"{region or ''} {addr}".strip()
            coords = geocoder.geocode(full_addr)
            time.sleep(0.05)  # rate-limit: 20 req/s

        if coords is None:
            failed += 1
            print(f"  NO COORDS: {addr}")
            continue

        lat, lon = coords
        if not dry_run:
            cur.execute(
                "UPDATE RABAEV.RRL_ADDR SET SHIROTA = :lat, DOLGOTA = :lon WHERE ADDR = :addr",
                {"lat": lat, "lon": lon, "addr": addr},
            )
        updated += 1
        print(f"  OK: {addr} → ({lat:.6f}, {lon:.6f})")

    if not dry_run:
        conn.commit()

    cur.close()
    conn.close()
    print(f"\nГеокодировано: {updated}  Не найдено: {failed}")
    if dry_run:
        print("[DRY RUN] Изменения не записаны в БД")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Geocode RRL_ADDR via DaData.ru")
    p.add_argument("--limit",     type=int, default=500, help="Максимум адресов за один запуск")
    p.add_argument("--dry-run",   action="store_true",   help="Не писать в БД")
    p.add_argument("--addr-like", default="",            help="Фильтр ADDR LIKE '%...%'")
    p.add_argument("--token",     default=os.environ.get("DADATA_TOKEN"),
                   help="DaData API токен (или DADATA_TOKEN env)")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if not args.token:
        print("WARN: DADATA_TOKEN не задан. Геокодирование будет пропущено для всех адресов.",
              file=sys.stderr)
    run(args.limit, args.dry_run, args.addr_like, args.token)
