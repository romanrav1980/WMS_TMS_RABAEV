from typing import Any,Protocol

class VehicleProfileError(Exception):
    def __init__(self,code: str,message: str,status: int=409)->None:
        super().__init__(message)
        self.code,self.status=code,status

class VehicleProfilePort(Protocol):
    def configure(self,body: dict[str,Any],actor: str)->dict[str,Any]: ...
    def tare_types(self,actor: str)->list[dict[str,Any]]: ...
    def read(self,vehicle: int,actor: str)->dict[str,Any]: ...

def vehicle_profile_service()->VehicleProfilePort:
    raise RuntimeError("Vehicle profile service not wired")
