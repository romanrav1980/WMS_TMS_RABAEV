"""Scoped completion admission is distinct from viewing and metadata assignment."""


class TaskCompletionAccessError(RuntimeError):
    def __init__(self, code: str, status: int = 403) -> None:
        self.code = code
        self.status = status
        super().__init__(code)
