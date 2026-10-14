from typing import Any,Protocol


class DriverBindingPort(Protocol):
    def configure(self,driver_id: int,user_id: str,active: bool,expected_version: int,actor: str) -> dict[str,Any]: ...
    def get(self,driver_id: int) -> dict[str,Any]: ...


def driver_binding_service() -> DriverBindingPort:
    raise RuntimeError("Driver binding not wired")
