# NI04.3 / NI07.2 — исходящий обмен не скрывает ответ ERROR,153

Integrations owns response decision; existing Oracle event/request journal and retry counters retained. Only adapter DONE and successful HTTP2xx (or non-HTTP transport with no HTTP status) means transmission completed. ERROR/rejected/unknown or failed HTTP leaves event in native retry/error, preserves response IDs/status/body, never mark_done.

Transport completion does not itself assert legal government acknowledgment. Real ack requires explicit boolean true from non-simulation adapter; MOCK remains visibly simulation and not signed. Disabled default untouched/no queue claim.

Read original CLOB event payload as to_clob expression so native JSON auto-decoding cannot break CLOB binds or reserialize signed/source data. No new government connector/credentials/ACK invented. Author one private target event and simulated failing adapter in real Oracle; default real queues not claimed. Crash leases/status polling remain separate delivery concerns.
