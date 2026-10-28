# C0197: raw UI for binding a root HU to an ST

## Changed files
- `wiki-raw/wms_admin_ui_reference/warehouse-hus.html`: the section "Привязать корень к СТ" with the ST field and two buttons (each has `title` and `data-help-id`); the script version is bumped.
- `wiki-raw/wms_admin_ui_reference/warehouse-hus.js`: action, saved request, retry and recovery.
- `docs/help/public/warehouse-hus.html`: a `#bind` section and a navigation link.

## User flow
1. **Read the root.** Enter or scan the root and press "Показать состав". The section appears only when the composition is current and the root is a top-level `CONTAINER` (no ancestors, not historical) with at least one CASE.
2. **Choose the ST.** Enter or scan the prepared ST and press "Привязать корень к СТ".
3. **Save before sending.** The request is saved *before* POST: `{operation_id:"HUBIND:<uuid>", shipment_identifier, scanned_root:<root uid from the composition>, expected_root_version:<root node version>}`.
4. **Send.** One POST goes to `/api/warehouse-hus/bind-shipment`. There are no CASE endpoints and no detach/attach.
5. **Outcome:**
   - **Success** is accepted only if `operation_id`, `status=BOUND`, `root`, `shipment_identifier` and a non-empty `cases` match. The saved request is cleared, the page shows "CASE в привязке: N" (or "подтверждена уже проведённая привязка" when `idempotent`), and the composition is re-read.
   - **Confirmed refusal** on the first send: the server's `outcome_confirmed=true`, without `operation_id_conflict` or `retry_same_operation_id`. The page shows the server code and message, and the saved request is cleared.
   - **Uncertain outcome:** network loss, 503, 401/403, `operation_id_conflict`, or a refusal on a retry. The saved request stays. Only "Повторить сохранённую привязку" (the exact same request) or "Показать состав" (re-read) is available. All other HU commands stay blocked until then, and vice versa.
   - **Damaged record:** the existing "Сверить состав и архивировать повреждённый запрос" archives it.
6. **After a reload or another tab:** the saved binding is restored, its root composition is re-read, and the retry button is shown.

## Implementation notes and limitations
- **Separate storage key.** The existing `hu-command-intent.js` validator (not an owned file) accepts only HU command bodies (`identifier`, `scan_container`, `expected_version`). It would mark a binding record as damaged. So the binding uses the same durable store owner (`window.wmsCommandIntent.create`) and the same save/settle/archive/retry semantics, under its own key, `wms-hu-bind-intent:<api>:<user>`.
- **`scanned_root` is the root uid from the read composition.** The server compares it with the snapshot root. The operator may scan the uid or the SSCC; the existing `reviewed()` check applies.
- **Not included:**
  - multi-order shipping, QC slices, loading, electronic final weighing;
  - a list of orders per CASE (the multi-order migration is not applied).
- **Permission:** the section is gated with `data-native-capability="warehouse_tasks dispatch"`, `data-flat-permission="case_pick_execute"`. The final decision is the server's (403 is shown as "нет права").
- **390 px:** existing classes `hu-divider`, `hu-query`, `hu-primary` and `hu-helper` are reused; at ≤700 px `hu-query` becomes a grid. No visual redesign.

## Checks
- `node --check warehouse-hus.js`: syntax OK.
- `scripts/check-encoding.ps1`: PASS.
- No tests were run, and none are claimed. No API calls, Oracle access, screenshots or push.
- Acceptance is Codex's.
