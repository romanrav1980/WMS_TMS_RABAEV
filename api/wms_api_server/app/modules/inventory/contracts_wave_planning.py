"""Errors for the existing warehouse wave metadata entry points."""


class WavePlanningError(RuntimeError):
    def __init__(self, code: str, status: int = 409) -> None:
        super().__init__(code)
        self.code = code
        self.status = status
