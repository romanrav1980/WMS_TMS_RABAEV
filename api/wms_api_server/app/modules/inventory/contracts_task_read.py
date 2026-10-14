from dataclasses import dataclass

@dataclass(frozen=True)
class TaskViewScope:
    warehouse_id: int | None
    global_admin: bool

class TaskReadError(RuntimeError):
    def __init__(self,code: str,status: int=403) -> None:
        super().__init__(code)
        self.code=code
        self.status=status
