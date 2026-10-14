class TransportPlanError(ValueError):
    def __init__(self,code: str,message: str,status: int=409) -> None:
        super().__init__(message);self.code=code;self.status=status

