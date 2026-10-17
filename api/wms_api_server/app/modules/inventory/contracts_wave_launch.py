"""A committed launch and its pending continuation are different outcomes."""
class WaveLaunchContinuationError(RuntimeError):
    def __init__(self, operation: str, step: str) -> None:
        super().__init__("WAVE_LAUNCHED_CONTINUATION_UNCONFIRMED")
        self.operation, self.step = operation, step
