from typing import Any, Protocol

class WaveTimePort(Protocol):
    def context(self,wave: int,actor: str) -> dict[str,Any]: ...
    def approve(self,operation: str,body: dict[str,Any],actor: str) -> dict[str,Any]: ...

def wave_time_service() -> WaveTimePort:
    raise RuntimeError("Wave time plan not wired")
