# NI04.3 / NI07.2 — lease и fencing существующего outbox,154

Existing event/request journal remains owner. Add monotonically increasing CLAIM_VERSION and aware LEASE_UNTIL to events, claim version/worker/finish hash/aware response time to requests. New native delivery coordinator claims one eligible row with explicit one-row FETCH FOR UPDATE SKIP LOCKED, including expired aware leases. No global delivery mutex and no HTTP call inside transaction.

Expired claim counts unconfirmed failure against existing retry/MAX, bounded candidates, never interprets old naive LOCKED_AT as UTC. Atomic request outcome plus event finalization checks event generation/worker; stale result only records its old request evidence, cannot finish/retry current generation. Stable event idempotency key is unchanged; at-least-once transport requires provider dedup/status reconciliation before real deployment.

Managed rows guarded against old/direct delivery writes. Existing unclaimed legacy exports remain; manual retry uses current native permission, blocks active lease/DONE/EXPORTED and increments generation. Default real adapter disabled. Short UOW per claim/attempt/finish, durable response hash repeat identity, savepoint catches native failure without partial bookkeeping. Metadata-only private target case, no real provider/stock.
