"""One native metadata transaction/receipt; never a quantity posting client."""
import hashlib
import json
from typing import Any
import oracledb
from pydantic import ValidationError
from ..contracts_case_resource import CaseResourceAck,CaseResourceCommand,CaseResourceError,CaseResourceState
from .case_resource_sessions import session_choices


def canonical(body:CaseResourceCommand)->str:
    return json.dumps(body.model_dump(mode="json"),sort_keys=True,separators=(",",":"),ensure_ascii=False)


def oracle_json(value:Any)->dict[str,Any]:
    if hasattr(value,"read"):value=value.read()
    return value if isinstance(value,dict)else json.loads(value)


class CaseResourceCommands:
    def __init__(self,gateway:Any)->None:self.gateway=gateway

    def transfer_receipt(self,task:int,event:str,actor:str)->dict[str,Any]:
        from .case_transfer_receipt import transfer_receipt
        return transfer_receipt(self.gateway,task,event,actor)

    def _call(self,method:str,args:list[Any],readonly:bool,validate:Any,operation:str|None=None)->dict[str,Any]:
        try:
            with self.gateway.transaction("CASE resource "+method)as cursor:
                if readonly:cursor.execute("set transaction read only")
                output=cursor.var(oracledb.DB_TYPE_CLOB)
                cursor.callproc("RRL_CASE_ASSIGNMENT_API."+method,[*args,output])
                data=oracle_json(output.getvalue());validate(data)
                return data
        except oracledb.DatabaseError as error:
            code=error.args[0].code
            status=403 if code==20882 else 404 if code==1403 else 409 if 20800<=code<=20999 else 503
            message=str(error.args[0]).split("\n",1)[0]
            raise CaseResourceError(message,status,operation)from error
        except(ValueError,ValidationError,TypeError,KeyError)as error:
            raise CaseResourceError("CASE_RESOURCE_ACK_INVALID",503,operation)from error

    def context(self,task:int,actor:str)->dict[str,Any]:
        def validate(data:dict[str,Any])->None:
            CaseResourceState.model_validate({k:v for k,v in data.items()if k!="current_actor"})
            if data.get("current_actor")!=actor or data.get("task_id")!=task:raise ValueError("Current context identity mismatch")
        return self._call("task_context",[task,actor],True,validate)

    def sessions(self,task:int,actor:str)->dict[str,Any]:
        try:
            return session_choices(self.gateway,task,actor)
        except oracledb.DatabaseError as error:
            code=error.args[0].code
            status=403 if code==20882 else 404 if code==1403 else 409 if 20800<=code<=20999 else 503
            raise CaseResourceError(str(error.args[0]).split("\n",1)[0],status)from error
        except(ValueError,ValidationError,TypeError,KeyError)as error:
            raise CaseResourceError("CASE_RESOURCE_SESSION_CHOICES_INVALID",503)from error

    def command(self,task:int,body:CaseResourceCommand,actor:str)->dict[str,Any]:
        wire=canonical(body);digest=hashlib.sha256(wire.encode("utf-8")).hexdigest().upper()
        def validate(data:dict[str,Any])->None:
            ack=CaseResourceAck.model_validate(data)
            if(ack.operation_id,ack.action,ack.actor,ack.task_id,ack.request_sha256)!=(body.operation_id,body.action,actor,task,digest):raise ValueError("Original command acknowledgement mismatch")
        return self._call("execute_command",[task,wire,actor],False,validate,body.operation_id)

    def receipt(self,operation:str,actor:str)->dict[str,Any]:
        def validate(data:dict[str,Any])->None:
            ack=CaseResourceAck.model_validate(data)
            if(ack.operation_id,ack.actor)!=(operation,actor):raise ValueError("Receipt identity mismatch")
        return self._call("receipt",[operation,actor],True,validate,operation)
