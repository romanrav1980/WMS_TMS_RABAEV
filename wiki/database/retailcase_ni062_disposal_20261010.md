# NI06.2 — утилизация возвратного брака,110
2026-10-10-110-return-disposal-original-loss-store APPLIED17/0 RABAEV/orcl. New private RRL_STOCK_RETURN_DISPOSE, existing Root/effect and guards VALID. Checkpoint426Root/427Effect; goods facts forward correction only.

Warehouse-bound warehouse_return_dispatch reporter stores immutable disposal receipt/document archive reference/hash/reason. Different active warehouse-bound SC actor store_return_approve conducts entire approved DISPOSAL return with source pallet/cell scan/current stock version. Exact whole source/noHARD/sameWARE blockedcell/noHU/currentBASE policy. Current marked profile denies ordinary command; no silent omitted units.
Existing Root sorted resource closure/recheck/operation replay and native effect consume→unit/balance/journal sole writer. Explicit disposal context permits blocked source; unrelated shipments cannot use it. Immutable disposal fact and STORE_RETURN_DISPOSED SAP pending event same transaction. Loss attribution is original accepted store STORE_ADDR through original return approval, not executing warehouse. No external SAP acknowledgement implied.

API typed port/raw warehouse return-disposal.html has immutable saved operation retry and current source version; report does not affect P. Unknown technical failure remains503/unconfirmed; confirmed business refusals allow corrected new intent.

## Actual author evidence
[Source](../../scripts/ni062_disposal_source_case.py): original accepted STORE.RECEIPT:04633c677f had remaining return allowance1. Ordinary approved DISPOSAL1, assumed SAP file, same existing trip/bound driver/return receiving in blocked cell; DISPOSAL.RECEIVE:b10092cbf0. Own source warehouse387548 initially had no return-zone/default receiving config; additive own cells/QDGb10092cbf0/QDDb10092cbf0/QDSb10092cbf0 configured. Source vehicle own max20kg/4places. Earlier missing BARCODE column/join policy attempts before approval had no goods effect.

[Disposal case](../../scripts/ni062_disposal_case.py) PASS taga2c9f83b4f: non-admin bound report/replay; same reporter403, stale version/foreigncell409; independent Root dispose1→P0H0, one event/fact/outbox; original loss STORE.QA:04633c677f; exact replay, second operation409. Fixture observer/driver retired. Synthetic destruction document means dev evidence only, not real destruction/SAP ACK.

Slow27.200/16.126/1.028ms: retain source unique indexes/current warehouse100; NI06.2 owner checks repeated growing source-history plan. Independent acceptance/actual archive proof/marked regulatory writeoff/partial disputes remain separate.
