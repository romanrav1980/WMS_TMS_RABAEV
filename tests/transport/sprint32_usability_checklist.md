# Sprint 32 — Usability Checklist: Overload Warning

## Feature: Overload warning banner (Phase 2 completion)

### Preconditions
- [ ] A transport task is selected with TRANSPORT set to a vehicle with PALLETS defined
- [ ] Add enough STs to the task to exceed the vehicle's pallet capacity

### Warning banner appearance
- [ ] Red warning banner appears BELOW the load bar when tripP > vehicle.PALLETS
- [ ] Banner text: «⚠ Перегруз: N пал > M пал (норма для VehicleNum)»
- [ ] Banner has red background (#fef2f2) and red border
- [ ] Banner font is bold, 11px

### Threshold behavior
- [ ] Warning NOT shown when tripP = vehicle.PALLETS (exactly at capacity)
- [ ] Warning SHOWN when tripP = vehicle.PALLETS + 1 (one pallet over)
- [ ] Load bar is red AND warning banner visible simultaneously at overload

### Dynamic updates
- [ ] Warning appears immediately when last overloading ST is added
- [ ] Warning disappears immediately when overloading ST is removed
- [ ] Warning updates correctly when vehicle is changed to one with higher capacity

### Both panels
- [ ] Warning appears in «Заявки» tab task right panel
- [ ] Warning appears in «Маршруты» tab task right panel

### No vehicle or no PALLETS info
- [ ] When TRANSPORT = null → no bar, no warning (both hidden)
- [ ] When vehicle has PALLETS = null → no bar, no warning

### Phase 2 completion check
- [ ] ✅ GET /clusters endpoint implemented and working
- [ ] ✅ Cluster sidebar (left panel) showing all districts
- [ ] ✅ «⚡ Рейс» button creates task from cluster in one click
- [ ] ✅ Live pallet bar shows fill percentage
- [ ] ✅ Overload warning when pallets exceed vehicle capacity
