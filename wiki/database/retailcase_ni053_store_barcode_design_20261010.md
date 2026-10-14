# NI05.3 — приёмка магазина по идентификатору места
Ticket083 design, 10.10.2026. Not installed. Sources NS49, process10_store_receipt. Delivery owns receipt fact/accepted lines; transport original immutable departed physical load; inventory root owns atomic durable command/outbox. No repeated warehouse stock consumption.

First bounded slice: complete ordinary whole place, all frozen ST destinations equal configured current store. Explicit address policy BARCODE; WEIGHT_PHOTO cannot fall back when weighing/photo absent. Scan real top identifier/SSCC before cameras and confirm historical manifest signature. RUSERS authenticated receiver with STORE_RECEIPT_CONFIRM and explicit store binding, GLOBAL_ADMIN retains legacy all-rights semantics. driver_id alone is not receipt authorization.

One STORE_RECEIPT root operation records immutable original composition, actor/time/destination, all accepted ordinary lines and mandatory business outbox. Unique actual load owner prevents second receipt, exact operation replay and conflicting payload handled by root. P/H in warehouse stays0; this does not fabricate destination warehouse inventory or government ACK.

Marked/physical-unit places require the next exact-code/aggregate and applicable regulatory acknowledgement slice; first ordinary command must refuse them. Missing frozen legacy destination, mixed-store top place, wrong store/identifier/signature, not departed, missing cameras, receiver without binding or WEIGHT_PHOTO all refuse.

Existing DriverMobilePage receives a separate receipt component using actual authenticated RUSERS, not a replacement driver platform. Weight/photo/archive/discrepancy, partial acceptance/return obligations and marked recipient are separate remaining slices.
