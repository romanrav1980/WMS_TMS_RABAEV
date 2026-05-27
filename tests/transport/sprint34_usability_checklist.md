# Sprint 34 — Usability Checklist: Cancel Task Unassigns STs (Bug Fix)

## Feature: «Отменить» рейс теперь освобождает все СТ

### Preconditions
- [ ] Create a test trip with 3–5 STs assigned
- [ ] Note the ST numbers
- [ ] Make sure the trip is NOT linked to a billing order (no 💰 badge)

### Cancel flow
- [ ] Click «Отменить» button in task panel
- [ ] Confirm the dialog
- [ ] Trip disappears from the routes list

### STs are freed after cancel (the bug fix)
- [ ] Switch to «Заявки» tab with same date
- [ ] The STs from the cancelled trip NOW appear in the available STs table
- [ ] Before this fix: STs stayed "assigned" to a deleted task and were invisible

### Billing protection still works
- [ ] Select a trip that has 💰 billing badge
- [ ] «Отменить» button is disabled (disabled prop with PAY_ORDER_ID check)
- [ ] Even if somehow called, API returns 409

### Edge cases
- [ ] Cancel empty trip (0 STs): works without error, trip deleted
- [ ] Cancel trips with 10+ STs: all are freed
- [ ] «Кластеры» view refreshes correctly after cancel (freed STs re-appear in cluster)
