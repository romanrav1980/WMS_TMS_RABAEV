# C-0186 — help hints stay inside a narrow window

## Cause
`help.css`: `.help-tooltip{position:absolute;right:0;width:min(270px,70vw)}`. The hint was anchored to the right edge of the button and extended to the left, so for a button near the left edge of the window it went past it.

## Before the fix (`c0186-tooltip-before.json`)
Real HelpButton in the real app (own Vite → API 8093, GET only), shift desk → yard, hover and focus:
- 390 and 768: "Обновить план" and "Обновить" (dock status): left edge of the hint **−31 px** (out of the window).
- 320/1440 and the buttons near the right edge: inside the window.

## Fix
- `admin/wms_admin_frontend/src/features/platform/help/HelpButton.tsx`:
  - after showing (hover/focus), the hint is placed `position:fixed` from the button rect and clamped horizontally to [8 px, width−8 px];
  - if there is no room above the button, it is shown below it;
  - recalculated on scroll/resize while shown.
- Unchanged: Escape (`help-dismissed`), `aria-describedby` → `role="tooltip"`, `title` fallback, `unavailable`/`disabled`, showing via CSS `:hover/:focus-within`.
- `help.css`: width `min(270px, calc(100vw - 16px))` + `box-sizing:border-box`, so it fits in 320 px with margins. The text is not cut, and there is no horizontal page scroll.

## After the fix (`c0186-tooltip-after.json`, PASS)
Script: `scripts/c0186_tooltip.cjs after`. Widths 320/390/768/1440.

Buttons:
- near the left edge: "Обновить план" (`shift.yard.plan.refresh`, yard plan UI), "Обновить" in dock status;
- near the right edge: "Неисправность…", "Обновить" in the yard.

Results:
- hover and keyboard focus: the hint rect is fully inside the window. For example, at 390 "Обновить план" goes from −31…239 to 8…278;
- Escape hides it; `role=tooltip`, `title` not empty;
- top edge: the button scrolled to the top of the window (top 4 px), so the hint is below it (top 48 px), inside the window, at all 4 widths;
- scrollWidth = viewport at all widths; no page errors.

Screenshots: `screenshots/before-{320,390,768,1440}.png`, `screenshots/after-{…}.png` (hint of "Обновить план").

## Checks (commands)
- `node admin/wms_admin_frontend/node_modules/typescript/bin/tsc --noEmit` (admin): OK
- `python scripts/retailcase_quality_gate.py`: PASS
- `powershell -ExecutionPolicy Bypass -File scripts/check-encoding.ps1`: PASS
- `python scripts/check_architecture.py`: PASS (cycles 0)
- `node reports/tradecase/2026-10-27/claude/C0186/scripts/c0186_tooltip.cjs after`: PASS
- No pre-existing failures in these runs. No live writes; the API was not restarted; my Vite is stopped.
