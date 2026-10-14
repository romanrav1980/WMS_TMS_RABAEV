"""Version existing fleet metadata through the native configuration owner."""
import json
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from ..contracts_vehicle_profile import VehicleProfileError

class VehicleProfiles:
    def __init__(self,gateway: Any)->None:
        self.gateway=gateway

    @staticmethod
    def failure(exc: oracledb.DatabaseError)->VehicleProfileError:
        code=getattr(exc.args[0],"code",0)
        if code==1403:return VehicleProfileError("VEHICLE_PROFILE_NOT_FOUND","Автомобиль не найден",404)
        if 20800<=code<=20999:
            return VehicleProfileError("VEHICLE_PROFILE_REJECTED",str(exc.args[0]).split("\n",1)[0],403 if code==20882 else 409)
        raise exc

    def configure(self,body: dict[str,Any],actor: str)->dict[str,Any]:
        try:
            with self.gateway.transaction("Configure versioned existing vehicle physical class")as cursor:
                result=cursor.var(oracledb.DB_TYPE_CLOB)
                cursor.callproc("RRL_VEHICLE_PROFILE_API.configure",[
                    json.dumps(body,sort_keys=True,separators=(",",":"),ensure_ascii=False),actor,result])
                return read_oracle_json(result.getvalue())
        except oracledb.DatabaseError as exc:
            raise self.failure(exc)from exc

    def read(self,vehicle: int,actor: str)->dict[str,Any]:
        try:
            with self.gateway.transaction("Read current vehicle physical profile")as cursor:
                cursor.execute("set transaction read only")
                cursor.execute("""select count(*)from RUSERS where ID=:actor and nvl(DELETED,0)=0
                 and RRL_HAS_WRIGHT(ID,'transport_dispatch_view')=1""",actor=actor)
                if cursor.fetchone()[0]!=1:
                    raise VehicleProfileError("VEHICLE_PROFILE_VIEW_FORBIDDEN","Нет права просмотра автопарка",403)
                return read_oracle_json(cursor.callfunc("RRL_VEHICLE_PROFILE_API.describe_profile",oracledb.DB_TYPE_CLOB,[vehicle]))
        except oracledb.DatabaseError as exc:
            raise self.failure(exc)from exc

    def tare_types(self,actor: str)->list[dict[str,Any]]:
        with self.gateway.transaction("Read existing active fleet tare catalog")as cursor:
            cursor.execute("set transaction read only")
            cursor.execute("""select count(*)from RUSERS where ID=:actor and nvl(DELETED,0)=0
             and RRL_HAS_WRIGHT(ID,'transport_dispatch_view')=1""",actor=actor)
            if cursor.fetchone()[0]!=1:
                raise VehicleProfileError("VEHICLE_PROFILE_VIEW_FORBIDDEN","Нет права просмотра автопарка",403)
            cursor.execute("""select PALLET_TYPE_ID,PALLET_TYPE_CODE,PALLET_TYPE_NAME
             from RRL_PALLET_TYPE where ACTIVE=1 order by PALLET_TYPE_ID fetch first 501 rows only""")
            rows=cursor.fetchall()
            if len(rows)>500:
                raise VehicleProfileError("VEHICLE_TARE_CATALOG_BOUND_500","Справочник превышает допустимый размер",409)
            return [dict(zip(("id","code","name"),row))for row in rows]
