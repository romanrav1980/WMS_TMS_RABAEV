# C0186 — Keep help hints inside a narrow viewport

## Evidence and objective

The live T10 refusal test at 390 px passed, but its `Обновить план` help hint is clipped at the left viewport edge. Fix this shared HelpButton presentation defect so the full hint remains readable on narrow screens and at desktop widths.

## Ownership

Reserve only:
- `admin/wms_admin_frontend/src/features/platform/help/HelpButton.tsx`
- `admin/wms_admin_frontend/src/features/platform/help/help.css`
- one focused regression test under `tests/retailcase/` or an isolated report script under `reports/tradecase/2026-10-27/claude/C0186/`
- `reports/tradecase/2026-10-27/claude/C0186/**` and `coordination/retailcase-claude/RESULT_C0186.md`

Do not modify the shared `dist`, yard code, API, Oracle, unrelated workspace components, or Codex files. No live writes and no API restart.

## Acceptance

1. Reproduce the clipping with a real HelpButton at viewport width 390 and record the before state or a deterministic bounding-box assertion.
2. Make the tooltip fully visible within the viewport at 320, 390, 768, and 1440 px. Verify both hover and keyboard focus; preserve Escape dismissal, accessible `aria-describedby`, and existing `title` fallback.
3. Cover buttons near both viewport edges, including a HelpButton in the yard-plan UI. Do not solve by hiding text or adding horizontal page scroll.
4. Run focused tests, TypeScript, `python scripts/retailcase_quality_gate.py`, encoding and architecture checks. Report exact commands/results and any pre-existing failure separately.
5. Commit locally, then send RESULT and RELEASE. No GitHub push.

Send ACK with exact paths and test strategy before editing.
