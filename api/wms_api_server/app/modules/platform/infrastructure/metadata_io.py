"""One native metadata command, one receipt, one gateway transaction."""
import hashlib
import json
import re
from datetime import datetime
from typing import Any
import oracledb

class MetadataError(Exception):
    def __init__(self, code: str, status: int, confirmed: bool | None = None) -> None:
        super().__init__(code)
        self.code = code
        self.status = status
        self.confirmed = status < 500 if confirmed is None else confirmed

def rows(cursor: Any) -> list[dict[str,Any]]:
    names = [column[0].lower() for column in cursor.description]
    result = []
    for values in cursor.fetchall():
        result.append(dict(zip(names,[value.read() if hasattr(value,"read") else value.isoformat() if isinstance(value,datetime) else value for value in values])))
    return result

def translate(error: Exception) -> MetadataError:
    value = error.args[0] if error.args else error
    number = getattr(value,"code",0)
    message = str(getattr(value,"message",""))
    if number in (20851,20852):
        code = message.splitlines()[0].split(":",1)[-1].strip()
        forbidden = any(word in code for word in ("DENIED","MANDATE","GLOBAL_ADMIN","DELEGATION","REVOKE_OUTSIDE"))
        return MetadataError(code,403 if forbidden else 409)
    if number == 1: return MetadataError("IDENTITY_ALREADY_EXISTS",409)
    if number in (2290,2291,1400,12899,40441,40566): return MetadataError("INVALID_METADATA",422)
    if number == 1403: return MetadataError("OBJECT_NOT_FOUND",404)
    return MetadataError("METADATA_UNAVAILABLE",503)

def native_command(gateway: Any, domain: str, actor: str, command: dict[str,Any]) -> dict[str,Any]:
    text = json.dumps(command,ensure_ascii=False,sort_keys=True,separators=(",",":"))
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    package = {"ACCESS":"RRL_ACCESS_API","KNOWLEDGE":"RRL_KNOWLEDGE_API"}[domain]
    try:
        with gateway.transaction(domain.lower()+".command") as cursor:
            output = cursor.var(oracledb.DB_TYPE_CLOB)
            cursor.callproc(package+".execute_command",[actor,command["operation_id"],digest,text,output])
            value = output.getvalue()
            return json.loads(value.read() if hasattr(value,"read") else value)
    except oracledb.DatabaseError as error:
        raise translate(error) from error

def json_object(value: Any) -> dict[str,Any]:
    return value if isinstance(value,dict) else json.loads(value.read() if hasattr(value,"read") else value)

def receipt(gateway: Any, domain: str, actor: str, operation_id: str) -> dict[str,Any]:
    data = gateway.fetch_all("""select RESULT_JSON from RRL_PLATFORM_COMMAND
      where DOMAIN=:domain and OPERATION_ID=:operation_id and ACTOR=:actor""",
      {"domain":domain,"operation_id":operation_id,"actor":actor})
    if not data: raise MetadataError("RECEIPT_NOT_VISIBLE",404)
    return json_object(data[0]["result_json"])
