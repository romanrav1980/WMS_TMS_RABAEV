# NI07.2: перенесённые СТ без собственной даты остаются в исходном дне

Prepared652. Existing read uses STDATE or current assigned trip SHIPMENT_DATE when STDATE is NULL. Deferral changes trip; therefore a NULL-date ST can disappear from its original daily register even though the existing immutable deferral result preserves original_shipping_date.

Bounded correction reuses RRL_ST_DEFER_DECISION.RESULT_JSON, current exact WARE/ST member IDs and existing native assignment. Original day becomes an additional candidate source only for NULL-date members. UNION removes overlap for same-day deferrals; existing page/cursor/physical load proof remains. No new ST/assignment registry, stock write or billing change. Additive expression index WARE/original day/ST supports journal lookup; apply/rollback/verify and source checkpoint prepared before live apply. Case on retained276 under outer metadata rollback pending; old factory276 will not run.

## Actual653/654
Index652 applied2/0, VALID; all current native objects VALID. Retained276 source under temporary CFG metadata transaction: set the original two STDATE values NULL, old current-trip fallback finds0 in original3Nov after target4Nov; extended register still finds both exact original IDs/current target/reasonversion1. limit1 pagination covers both once. Full rollback restores source STDATE values; no stock, assignment or billing writes and no original276 factory.
SQL653 updated bounded page25.587ms/69.33buffers. Decision: keep current member IDs/cursor bounds and indexed WARE/original day/ST journal lookup; larger warehouse deferral fanout belongs finance/Oracle plan profiling, no timeout increase/cache. Architecture677/0cycles/76debt PASS.
