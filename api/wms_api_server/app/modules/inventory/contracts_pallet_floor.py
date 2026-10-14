from typing import Any,Protocol

class PalletFloorPort(Protocol):
    def read(self,identifier: str,actor: str)->dict[str,Any]: ...
    def confirm(self,operation: str,identifier: str,metadata: dict[str,Any],actor: str)->dict[str,Any]: ...

def pallet_floor_service()->PalletFloorPort:
    raise RuntimeError("Pallet floor type service not wired")
