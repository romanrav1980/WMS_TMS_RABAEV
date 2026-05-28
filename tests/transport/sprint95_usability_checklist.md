# Sprint 95 — Usability Checklist: PRIMECHANIE Tooltip on Trip Rows

## Feature
Trip rows in both **Tasks tab** and **Routes tab** show PRIMECHANIE (note)
as a native browser tooltip on hover when the note is non-empty.

---

## Test Cases

### TC-1: Trip with note
- [ ] Trip has PRIMECHANIE = "Задержка отгрузки"
- [ ] Hover over the row → browser tooltip shows «Примечание: Задержка отгрузки»

### TC-2: Trip without note
- [ ] Trip has PRIMECHANIE = null/empty → NO tooltip on hover (no empty tooltip box)

### TC-3: Both tabs
- [ ] Same trip row in tasks tab shows tooltip
- [ ] Same trip in routes tab also shows tooltip

### TC-4: Note set after editing
- [ ] Edit PRIMECHANIE in the trip detail panel → save → hover the row → updated note shown in tooltip

---

## Expected UX
- Tooltip text: «Примечание: <full text>»
- Shown only when note is non-empty
- Native browser tooltip (no extra DOM elements)
- Available on hover without clicking
