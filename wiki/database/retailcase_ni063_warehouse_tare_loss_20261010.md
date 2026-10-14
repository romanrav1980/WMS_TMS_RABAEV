# NI06.3 — складская недостача тары,105
2026-10-10-105-warehouse-tare-loss APPLIED RABAEV/orcl,26 statements/0 errors plus bounded resolve correction2/0. LOSS/Root/planning/views/guards VALID. New RRL_TARE_LOSS_CLAIM and RRL_TARE_LOSS_DECISION immutable, full decision unique per original claim.

REPORT requires tare_loss_report, current warehouse binding, exact current balance version, positive integer quantity no larger than currently free. It leaves physicalqty unchanged and immediately excludes suspect quantity from availability. Shared held_quantity includes active BOOK plus unresolved loss; BOOK/COUNT/OFFER/ACCEPT/DAMAGE and warehouse damaged WRITE_OFF cannot consume a claimed unit. Pending claim remains part of history, not erased.

DECIDE requires tare_writeoff and another active actor. WRITE_OFF closes full claim and reduces original same-condition warehouse physical balance once. REJECT closes full claim and releases suspect quantity without physical correction. Partial decisions/outside store/vehicle loss claims are outside this slice. One short Root transaction: claim/decision, balance version, journal fact table, mandatory outbox; no goods P/H/events.

[Dedicated UI](../../wiki-raw/wms_admin_ui_reference/tare-loss.html) reads own warehouse catalog/current balance/claims, stores exact operation intent before sending and retains unknown result. API loss-report/loss-decide/warehouses/{ware}/loss-cases; view supports GOOD and DAMAGED source histories, usable planning currently GOOD.

[Author](../../scripts/ni063_loss_case.py) first stopped before REPORT because new zero-line types were absent from Python stock contract; fixed type registry, then [original continuation](../../scripts/ni063_loss_continue.py) PASS, without second fixture count: non-admin REPORT physical3/free2, count0/damage3 refused, same actor403, independent loss physical2/free2/replay, second claim REJECT free restored. Goods events0; own count0 cleanup and user retired. Long SQL58.532/43.623/39.215ms: retain balance/time index, claim unique decision PK and bounds200, NI06.3 owner reviews plan on real growth.

Full NI06.3 remains open: store/vehicle loss and claims, moving damaged custody, repack/packing, independent acceptance.
