"""Atomic GPS history/current-position write, serialized by the existing vehicle row."""
from datetime import datetime
from typing import Any


class GpsVehicleMissing(ValueError):
    pass


def ingest_gps(gateway: Any, vehicle_id: int, lat: float, lon: float,
               speed: float, timestamp: datetime | None) -> dict:
    with gateway.transaction("GPS history and latest position atomically") as cur:
        cur.execute("select ID from RRL_TR_VEHICLE where ID=:vid and nvl(DELETED,0)=0 for update wait 5", vid=vehicle_id)
        if cur.fetchone() is None:
            raise GpsVehicleMissing("GPS_VEHICLE_NOT_FOUND")
        cur.execute("select sysdate from dual")
        received_at = cur.fetchone()[0]
        observed_at = timestamp if timestamp is not None else received_at
        values = {"vid": vehicle_id, "lat": lat, "lon": lon, "speed": speed, "ts": observed_at}
        cur.execute("""insert into RRL_VEHICLE_GPS(ID,VEHICLE_ID,LAT,LON,SPEED_KMH,TS)
            values(SEQ_VEHICLE_GPS.nextval,:vid,:lat,:lon,:speed,:ts)""", values)
        cur.execute("select TS from RRL_VEHICLE_GPS_LAST where VEHICLE_ID=:vid", vid=vehicle_id)
        previous = cur.fetchone()
        current = previous is None or previous[0] is None or observed_at >= previous[0]
        if current:
            values["received_at"] = received_at
            if previous is None:
                cur.execute("""insert into RRL_VEHICLE_GPS_LAST(VEHICLE_ID,LAT,LON,SPEED_KMH,TS,UPDATED_AT)
                    values(:vid,:lat,:lon,:speed,:ts,:received_at)""", values)
            else:
                cur.execute("""update RRL_VEHICLE_GPS_LAST set LAT=:lat,LON=:lon,SPEED_KMH=:speed,
                    TS=:ts,UPDATED_AT=:received_at where VEHICLE_ID=:vid""", values)
        return {"ok": True, "vehicle_id": vehicle_id, "current_position_updated": current,
                "observed_at": observed_at.isoformat(), "timestamp_basis": "DATABASE_LOCAL_DATE"}
