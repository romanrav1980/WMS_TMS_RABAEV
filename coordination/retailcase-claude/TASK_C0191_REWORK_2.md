# C-0191 rework 2 — exact SHIPMENT intent and fulfillment reconciliation

K-0230 is received but not accepted. This is a correction of the same C0191 request, not a new budget request. Do not edit C0190 or C0192.

Keep ownership limited to the C0191 source, C0191 focused tests, C0191 report, and RESULT.

## Defects

1. metadata_step records only state SENT. It does not persist the exact function/SQL intent and arguments before a metadata write. A resumed run therefore cannot prove that it is reconciling the same intended command.
2. Fulfillment reconciliation accepts any row with the same CUSTOMER_ORDER_ID and legacy ST. It must reject a row that has a different pallet UID, address, status, source, fact quantity, or fact weight.

## Required correction

1. Before each SHIPMENT metadata write, persist a deterministic command descriptor in shipment_writes: operation name, function or SQL identity, and JSON-safe arguments/binds. On a resume, compare the regenerated descriptor with the stored descriptor and stop with a precise content-change code if they differ.
2. Keep the existing read-before-write and read-after-write reconciliation. It must reuse only a fully matching row.
3. For each fulfillment, require one row matching its order, generated ST id, root shipment UID, recipient address, PLANNED status, zero fact quantity/weight, and QA_C0191_ONLY source. A same-order/ST row with another value must stop before a duplicate insert.
4. Add focused tests for persisted intent, changed intent rejection, and a mismatching fulfillment rejection.
5. No live writes, migrations, API restart, publication, or edits outside owned C0191 files.

Start with ACK in CLAUDE_TO_CODEX.md and return RESULT/RELEASE. After the result, wait for Codex acceptance.
