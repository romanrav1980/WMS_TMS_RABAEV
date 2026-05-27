# Sprint 37 — Usability Checklist: Select-All + Auto-Refresh

## Feature 1: «Выделить всё» header checkbox (flat view only)

### Checkbox in header
- [ ] First `<th>` in available-STs table shows a checkbox when flat mode is active and list is non-empty
- [ ] No checkbox shown in «По районам» (clusters) mode
- [ ] No checkbox shown when available STs list is empty

### Select-all behaviour
- [ ] Clicking unchecked header checkbox → all rows become checked
- [ ] Row highlight appears on every row after select-all
- [ ] PMV counter (P= M= V=) immediately reflects total of all STs
- [ ] «N выбр.» counter shows total count

### Deselect-all behaviour
- [ ] When all rows are checked, header checkbox shows checked state
- [ ] Clicking checked header checkbox → all rows deselected
- [ ] PMV counter resets to 0
- [ ] Header checkbox shows indeterminate state when only some rows are selected
  (Note: indeterminate via ref is optional; partial = unchecked is acceptable)

### Interaction with row-level actions
- [ ] After select-all, manually unchecking one row makes header checkbox unchecked (not all selected)
- [ ] Shift-click still works after select-all
- [ ] Changing date filter clears selection (existing behaviour preserved)

---

## Feature 2: Auto-refresh every 60 seconds

### Toggle control
- [ ] «Авто» checkbox is visible in the ST toolbar, to the right of the ⟳ button
- [ ] Auto-refresh is ON by default (checkbox checked)
- [ ] Unchecking the checkbox disables the timer

### Refresh indicator
- [ ] When auto-refresh is enabled and at least one refresh has occurred, a small
  time label (HH:MM) appears next to the «Авто» checkbox
- [ ] Time label updates on each auto-refresh tick

### Auto-refresh execution
- [ ] After ~60 s, the available STs list refreshes without user interaction
- [ ] Trips list also refreshes on each tick
- [ ] In «По районам» mode, clusters also refresh

### Blocked states — no refresh occurs while:
- [ ] «Создать маршрут» dialog is open
- [ ] Editing a trip (editMode)
- [ ] «⚡ Рейс» cluster-create dialog is open
- [ ] «Выставить счёт» dialog is open
- [ ] A full-page loading spinner is active

### No disruption to user work
- [ ] Selection (selectedStNums) is NOT cleared on auto-refresh
- [ ] Selected task (selectedTask) stays selected on auto-refresh
- [ ] No visible flash or jump in the UI during background refresh
