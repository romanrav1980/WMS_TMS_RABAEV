# Sprint 36 — Usability Checklist: Bulk ST removal from trip

## Feature: Multi-select checkboxes in trip detail table

### Basic interaction
- [ ] Checkbox column appears as first column in trip detail table (width ≈ 22 px)
- [ ] Clicking checkbox on a row marks it checked (row highlighted in amber/selected style)
- [ ] Clicking checked row unchecks it
- [ ] Multiple rows can be checked simultaneously
- [ ] Checkboxes are independent of the existing row-click → unassign action

### Bulk action bar
- [ ] Amber bar appears above the table as soon as at least one row is checked
- [ ] Bar shows count: «N СТ выбрано»
- [ ] «Снять выбранные» button is in the bar
- [ ] «Отмена» button clears selection without removing any STs
- [ ] Bar disappears immediately after clicking «Отмена»

### «Снять выбранные» action
- [ ] Clicking «Снять выбранные» shows a browser confirm dialog with count and trip ID
- [ ] Confirming removes all selected STs from the trip in one operation
- [ ] After removal: selection is cleared, table refreshes, STs reappear in available STs list
- [ ] Cancelling confirm dialog leaves everything unchanged

### Guard conditions (no checkboxes shown)
- [ ] Checkboxes are NOT shown for trips in «Отгружен» condition
- [ ] Checkboxes are NOT shown for trips included in a billing order (PAY_ORDER_ID set)
- [ ] «Снять выбранные» button is disabled while removal is in progress (loading state)

### Task switching
- [ ] Switching to a different trip clears all checkbox selections
- [ ] Switching tabs (tasks → routes → tasks) preserves no stale checkboxes

### Edge cases
- [ ] Single ST removal via checkbox is functionally equivalent to the existing ✕ button
- [ ] Removing all STs from a trip via bulk works without error
- [ ] Trip counter (ST count) in tasks list updates correctly after bulk removal
