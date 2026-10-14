# NI06 — граница HTTP для пересчёта остатков
10.10.2026. Inventory owner, no DDL and no changed posting rule. HTTP inventory_count_routes now validates the wire input and calls explicit InventoryObservationsPort; read SQL/profile batching/replay comparison/scan resolution/revision creation are in the inventory infrastructure adapter. Framework-free CountSubmission/CountObservation/CountScan contracts preserve requested counts separately from resolved physical unit identities. Composition root injects the existing gateway/root posting service.

Quantity effect remains one RRL_STOCK_POSTING_API operation with existing revision/version/marking checks. Adapter resolves scans read-only and never locks domain rows ahead of root. Exact repeated original request reuses saved metadata; changed payload refuses OPERATION_CONTENT_CONFLICT.

Author scripts/ni06_inventory_observation_api_case.py passed actual HTTP8088 revision, lot birth5, observation4, exact replay, content-conflict refusal, own count0/P0H0 cleanup. OpenAPI imports and builds (385 paths). No new API route, broad regression or independent acceptance claim. Slow lot read7jtwv7x4r440w7.561ms/6: retain201-row bound, no new index.
