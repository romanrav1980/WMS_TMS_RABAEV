"""No stock writer: native ledger fences late original requests permanently."""
from typing import Any
import json
import oracledb
from ...platform.public import read_oracle_json
from ..contracts_assembly_scale import AssemblyScaleError
from ..contracts_assembly_intents import AbandonIntent

class AssemblyIntents:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    def _invoke(self, method: str, arguments: list[Any], readonly: bool=False) -> dict[str, Any]:
        try:
            with self.gateway.transaction("Assembly intent " + method) as cursor:
                if readonly:
                    cursor.execute("set transaction read only")
                output=cursor.var(oracledb.DB_TYPE_CLOB)
                cursor.callproc("RRL_ASM_INTENT_API."+method,[*arguments,output])
                return read_oracle_json(output.getvalue())
        except oracledb.DatabaseError as exc:
            code=exc.args[0].code
            status=403 if code==20882 else 404 if code==1403 else 409 if 20800<=code<=20999 else 503
            raise AssemblyScaleError("ASSEMBLY_INTENT_NATIVE_REJECTED" if status<500 else "ASSEMBLY_INTENT_OUTCOME_UNCERTAIN",str(exc.args[0]).split("\n",1)[0],status) from exc

    def abandon(self, body: AbandonIntent, actor: str) -> dict[str, Any]:
        source=json.dumps(body.model_dump(),ensure_ascii=True,sort_keys=True,separators=(",",":"),allow_nan=False)
        return self._invoke("abandon",[source,actor])

    def read(self, identity: str, actor: str) -> dict[str, Any]:
        return self._invoke("describe",[identity,actor],True)
