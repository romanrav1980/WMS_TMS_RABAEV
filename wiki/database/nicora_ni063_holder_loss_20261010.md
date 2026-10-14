# NI06.3 — недостача у магазина и автомобиля,106
2026-10-10-106-store-vehicle-tare-loss APPLIED RABAEV/orcl,16 statements/0 errors; LOSS/CMD/RESOLVE/debt VALID. Added source claim/transport source FK fields to existing105 immutable claim, no historical rows rewritten.

REPORT STORE requires current bound receiver and exact original RRL_TARE_STORE_DEBT claim key/owner/type/condition/store. Multiple pending claims cannot exceed that debt or current free physical balance. Vehicle requires current dedicated driver/actual trip vehicle ID and scan. Independent DECIDE retains original custody/source, closes entire claim once, consumes exact same-condition physical balance. STORE writeoff reduces original loan, not a fabricated receipt; original due/policy retained.

All-source OFFER/ACCEPT and DAMAGE/WRITE_OFF now call shared usable quantity check; pending loss cannot be transferred or separately written off. Previous warehouse request canonical metadata excludes new null optional fields, old replay preserved.

[Author](../../scripts/ni063_holder_loss_case.py): original own100 DAMAGED store1→REPORT, other writeoff refused, same observer403, independent loss physical0/debt0/policy1/same due/replay; source historical100 remains, its old current-state verifier must not be rerun. Vehicle report1 succeeded; author first lacked tare_offer and stopped before testing actual denial. [Original continuation](../../scripts/ni063_holder_loss_continue.py) grants explicit role, proves blocked offer409, rejects claim independently/vehicle1/replay/events0. Dedicated original actors retired/binding inactive.

React existing driver TarePanel includes TareLossForm, current balance/version and original debt selector; independent decisions use existing loss register showing actual holder. TypeScript noEmit PASS; independent browser acceptance open.

Slow SQL1udsdar3bn0fj377.890ms and8fkdyyswa5w46238.772ms cold single calls. Added source FK index; retain bounded200 claims/debt and balance PK, no timeout inflation. Owner NI06.3 checks repeated plans/pushdown/incremental projection on growth. No capacity claim.

Remaining: damaged return inspection/current custody disposal, physical repack/cancellation and independent full-sprint review.
