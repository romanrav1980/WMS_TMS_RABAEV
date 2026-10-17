"""The preflight observes current authorization; native posting remains final."""
class CaseConfirmationAccessError(RuntimeError):
    def __init__(self, code: str, message: str, status: int = 403) -> None:
        super().__init__(message)
        self.code, self.status = code, status
