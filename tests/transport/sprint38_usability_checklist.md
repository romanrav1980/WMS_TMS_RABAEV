# Sprint 38 — Usability Checklist: «Копировать рейс»

## Feature: Clone a trip with same details but no STs

### Button placement
- [ ] «📋 Копировать» button is visible in trip detail header on the «Заявки» tab
- [ ] «📋 Копировать» button is visible in trip detail header on the «Маршруты» tab
- [ ] Button is enabled for active trips
- [ ] Button is enabled for shipped (Отгружен) trips (useful to re-use same vehicle/driver)
- [ ] Button is enabled for billed trips
- [ ] Button is disabled while a loading operation is in progress

### Copy behaviour
- [ ] Clicking the button immediately creates a new trip (no dialog needed)
- [ ] New trip inherits: machine (Машина), driver (Водитель), dock (Докст.), shipment time, transtype, date
- [ ] New trip starts with CONDITION = «Активен»
- [ ] New trip has zero STs
- [ ] New trip has no price (price = —)
- [ ] New trip has no PAY_ORDER_ID

### Post-copy navigation
- [ ] After copy, the UI navigates to the «Заявки» tab if on «Маршруты»
- [ ] The newly created trip is selected in the trips list
- [ ] The new trip appears at the top/bottom of the trips list for the same date

### Edge cases
- [ ] Copying a trip with no vehicle/driver/dock → still works, just fewer fields filled
- [ ] Copying the same trip twice → two separate trips are created with different IDs
- [ ] Trips list refreshes automatically after copy (no manual reload needed)

### Visual feedback
- [ ] Trip detail panel updates to show the new trip
- [ ] Trip header shows the new ID, not the source ID
- [ ] The source trip remains unchanged after copy
