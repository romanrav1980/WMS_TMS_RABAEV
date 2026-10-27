# Cancelled trip assignments

Ignore cancelled trip documents in the authoritative assigned quantity. Active trips and legacy documents without cancelled=true retain their protection. Cancellation of a physical loaded trip still requires the existing unload/return flow; this change does not bypass it. Only the document package body changes; spec and all stock posting packages remain unchanged.
