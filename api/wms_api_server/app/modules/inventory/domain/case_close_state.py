"""Closing cannot move a controlled/shipped place backwards."""
CLOSED_STATES = frozenset({"WAIT_CONTROL", "CONTROL_IN_PROGRESS", "CONTROLLED", "READY_TO_SHIP", "SHIPPED"})
OPEN_STATES = frozenset({"NEW", "ASSIGNED", "IN_PROGRESS", "PARTIAL", "WAIT_REPLENISHMENT", "PICKED"})


def close_transition(status: str | None, shipped_operation: str | None) -> str:
    if status in CLOSED_STATES:
        return "ALREADY_CLOSED"
    if shipped_operation:
        return "SHIPPED_SOURCE_CONFLICT"
    return "CLOSE" if status in OPEN_STATES else "STATE_CONFLICT"
