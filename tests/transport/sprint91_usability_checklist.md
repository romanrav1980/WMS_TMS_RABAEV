# Sprint 91 — Usability Checklist: Sort Trip STs by Time Window

## Feature
Button **⏱ Окна** in trip detail STs toolbar sorts the ST list by `TIME_FROM` (ascending, nulls last).

## Pre-conditions
- Open dispatcher page, navigate to «Маршруты» or «Заявки» tab
- Select a trip that has STs with delivery time windows set

---

## Test Cases

### TC-1: Button visibility
- [ ] «⏱ Окна» button appears in the trip STs toolbar ONLY when at least one ST has `TIME_FROM` set
- [ ] Button is NOT shown when no STs have time windows

### TC-2: Activate sort
- [ ] Click «⏱ Окна» → button turns indigo/active (highlighted border + background)
- [ ] ST rows re-order: STs with earliest `TIME_FROM` appear first
- [ ] STs without `TIME_FROM` move to the bottom of the list

### TC-3: Deactivate sort
- [ ] Click «⏱ Окна» again → button reverts to inactive state
- [ ] ST rows return to original `ORD`-based order (as loaded from server)

### TC-4: Combination with other filters
- [ ] Text filter in search box + time sort: filtering still works, sorted result is filtered
- [ ] «⚠ Несобр.» toggle + time sort: only unready STs shown, sorted by time window

### TC-5: Reset on trip switch
- [ ] While time sort is active, click a different trip → sort resets (button inactive)
- [ ] New trip STs shown in default ORD order

### TC-6: Count label
- [ ] Count label «N СТ» unchanged when sort is active (sort doesn't change count)

### TC-7: Edge cases
- [ ] Trip with all STs having identical `TIME_FROM` → no visible reorder, no errors
- [ ] Trip with single ST → button appears if ST has time window; sort has no effect

---

## Expected UX
- Button label: `⏱ Окна`
- Active: indigo border + light indigo background, bold text
- Tooltip: «Сортировать по временному окну доставки»
- No page reload; instant client-side reorder
