"""Public error contract for warehouse-scoped resource session reads."""


class ResourceReadError(RuntimeError):
    def __init__(self, code: str, status: int = 403) -> None:
        super().__init__(code)
        self.code, self.status = code, status
