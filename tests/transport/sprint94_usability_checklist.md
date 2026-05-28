# Sprint 94 — Usability Checklist: Amber Border for Trips with Unready STs

## Feature
Trips in both the **Tasks tab** and **Routes tab** tables get an amber (yellow-orange)
left border when `0 < READY_PERC < 100` — i.e., assembly has started but is not complete.
Mirrors Sprint 83 behavior for individual STs in the available-STs table.

---

## Test Cases

### TC-1: Active trip, partial assembly
- [ ] Trip with READY_PERC = 60 → amber left border visible in tasks tab row
- [ ] Same trip visible in routes tab → amber left border there too

### TC-2: Fully assembled trip (READY_PERC = 100)
- [ ] Trip is fully assembled → NO amber border

### TC-3: Not-started assembly (READY_PERC = 0)
- [ ] Trip has 0 % assembly → NO amber border (0 % trips are not highlighted)

### TC-4: Closed trip (Отгружен)
- [ ] Closed trip with partial READY_PERC → NO amber border (already shipped, irrelevant)

### TC-5: Cancelled trip
- [ ] Cancelled trip with READY_PERC > 0 → NO amber border

### TC-6: Selected + unready
- [ ] Click on an amber-border trip to select it → blue "selected" styling applies,
      amber border still visible on the left

### TC-7: Requires include_readiness
- [ ] READY_PERC populated only when list loaded with `include_readiness=true` → verify toolbar loads correctly

---

## Expected UX
- Amber left border: 3px solid #f59e0b
- Condition: active trip (not Отгружен/Отменён) + 0 < READY_PERC < 100
- Same visual language as Sprint 83 (available STs) for consistency
