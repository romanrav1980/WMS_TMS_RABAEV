-- =============================================================================
-- Migration 050 — Transport Sprint 6 (no schema changes)
-- =============================================================================
-- Sprint 6 adds the GET /sts/{st_number}/pallets endpoint that reads
-- existing RRL_SBORKA_PALLETS and RRL_SBORKA_PALLET_ROWS tables.
-- No DDL changes required.
-- =============================================================================

COMMIT;
