"""Approved time metadata on the original wave; no stock or task assignment effects."""
import json
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from ..contracts_workload import WorkloadError

def wave_time_error(exc: oracledb.DatabaseError) -> WorkloadError:
    code=getattr(exc.args[0],"code",0)
    if code==1403:return WorkloadError("WAVE_TIME_SOURCE_NOT_FOUND","Волна отсутствует",404)
    if 20800<=code<=20999:return WorkloadError("WAVE_TIME_REJECTED",str(exc.args[0]).split("\n",1)[0],403 if code==20882 else 409)
    if code in {6502,12899,1841,1843,1858,1861}:return WorkloadError("WAVE_TIME_INPUT_INVALID","Проверьте даты, часовой пояс и длину основания",422)
    return WorkloadError("WAVE_TIME_UNCONFIRMED","Повторите исходное утверждение с тем же идентификатором",503)

class WaveTime:
    def __init__(self,gateway: Any) -> None:self.gateway=gateway

    def context(self,wave: int,actor: str) -> dict[str,Any]:
        try:
            with self.gateway.transaction("Existing wave time context READ ONLY") as cur:
                cur.execute("set transaction read only")
                result=cur.var(oracledb.DB_TYPE_CLOB)
                cur.callproc("RRL_WAVE_TIME_API.context",[wave,actor,result])
                return read_oracle_json(result.getvalue())
        except oracledb.DatabaseError as exc:raise wave_time_error(exc) from exc

    def approve(self,operation: str,body: dict[str,Any],actor: str) -> dict[str,Any]:
        serialized=json.dumps(body,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False)
        if len(serialized)>2000 or len(serialized.encode("utf-8"))>4000:
            raise WorkloadError("WAVE_TIME_REQUEST_BOUND","Сократите основание",422)
        try:
            with self.gateway.transaction("Approve existing wave window and immutable aware plan") as cur:
                result=cur.var(oracledb.DB_TYPE_CLOB)
                cur.callproc("RRL_WAVE_TIME_API.approve",[operation,actor,serialized,result])
                return read_oracle_json(result.getvalue())
        except oracledb.DatabaseError as exc:raise wave_time_error(exc) from exc
