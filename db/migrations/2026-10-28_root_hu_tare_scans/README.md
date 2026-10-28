# Root-HU tare scans

This migration changes only `RRL_STOCK_TARE_BOOK_CMD`. A booking for a top-level container can carry the root composition version, physical root scan and current cell scan. It rejects mismatches with `TARE_ROOT_VERSION_CHANGED`, `TARE_ROOT_SCAN_REQUIRED` or `TARE_ROOT_CELL_SCAN_REQUIRED`.

The fields remain optional for compatibility. A physical-root workflow sends all three. The migration creates no floor record and does not change loading, QC, stock movement or cancellation.

`900_before_tare_book_cmd.sql` is a read-only capture of the live package on 2026-10-28. It is not applied. Apply requires explicit Oracle DDL approval, then an isolated booking, exact replay, stale-version refusal and rollback proof.
