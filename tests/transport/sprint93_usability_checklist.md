# Sprint 93 — Usability Checklist: Empty Trips Warning in Day Summary

## Feature
Day summary bar shows **⚠ N пустых** (amber text) when there are active trips
with 0 pallets/STs. Helps dispatcher notice forgotten empty trips before end of shift.

---

## Test Cases

### TC-1: No empty trips
- [ ] All active trips have STs assigned → «⚠ N пустых» NOT shown in day summary

### TC-2: One empty trip
- [ ] Create a trip, add no STs → «⚠ 1 пустых» appears in day summary
- [ ] Badge is amber/orange colored

### TC-3: Multiple empty trips
- [ ] Two empty trips → «⚠ 2 пустых»

### TC-4: Closed/cancelled not counted
- [ ] Close (Отгружен) or cancel (Отменён) an empty trip → counter decreases
- [ ] A closed trip with 0 STs does NOT count as «пустой»

### TC-5: Fill trip — badge disappears
- [ ] Add STs to the empty trip → «⚠ пустых» disappears (or count decreases)

### TC-6: Tooltip
- [ ] Hover over «⚠ N пустых» → shows tooltip «Активные рейсы без СТ»

---

## Expected UX
- Badge only visible when `dayEmptyTasks > 0`
- Color: amber (#b45309)
- Format: `⚠ N пустых`
- Position: rightmost item in the day summary bar
- No page reload required; auto-updates with trips data
