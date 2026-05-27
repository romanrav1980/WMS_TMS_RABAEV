# Sprint 33 — Usability Checklist: «Кратко» Mode in Routes Table

## Feature: Brief mode checkbox in routes toolbar (§3.8.1 TZ)

### Preconditions
- [ ] Navigate to «Маршруты» tab
- [ ] At least one trip exists in the list

### Checkbox location and appearance
- [ ] «Кратко» checkbox is visible in the routes toolbar (between ⟳ and ⬇ Excel)
- [ ] Label «Кратко» is readable, compact (11px font)
- [ ] Checkbox is unchecked by default (full mode on load)

### Full mode (unchecked) — all 15 columns visible
- [ ] Columns present: Отгрузка, #, Пал., Вес, Объём, Тип, Машина, Водитель, ДОК, Регионы, Цена, ТК, Логист, Статус, 💰
- [ ] Тип column has inline dropdown to change transport type

### Brief mode (checked) — 9 columns
- [ ] Columns visible: Отгрузка, #, Пал., Вес, Машина, Водитель, ДОК, Регионы, Статус
- [ ] Hidden: Объём, Тип, Цена, ТК, Логист, 💰
- [ ] Table is visibly more compact / wider rows
- [ ] DriverOwnerBadge (🏢 / ИП) also hidden in brief mode

### Toggle behavior
- [ ] Checking/unchecking immediately shows/hides columns (no page reload)
- [ ] Selected task remains selected after toggling
- [ ] State is NOT persisted to localStorage (resets to full on page reload)

### Data integrity
- [ ] All visible columns show correct data in both modes
- [ ] Clicking a row selects the task in both modes
- [ ] «Отгружен» rows still show grey styling in brief mode

### Edge cases
- [ ] Empty table: empty row colspan adjusts correctly (9 vs 15)
- [ ] Very long Водитель name: still fits without breaking layout in brief mode
