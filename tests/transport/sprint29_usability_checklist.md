# Sprint 29 — Usability Checklist: Create Task from Cluster

## Feature: ⚡ «Рейс» button in Cluster view

### Preconditions
- [ ] There are unassigned STs with filled RAION field for today's date
- [ ] At least one cluster appears in «Кластеры» view mode

### Visual checks in Cluster view
- [ ] Each cluster header row shows «⚡ Рейс» button on the right
- [ ] Button color is indigo/violet (distinct from green "Создать маршрут")
- [ ] Clicking ⚡ button does NOT toggle the cluster expand/collapse
- [ ] Cluster header still expands/collapses when clicking elsewhere on the row

### ClusterQuickCreateDialog checks
- [ ] Dialog opens with cluster name in title: «⚡ Рейс из кластера «<RAION>»»
- [ ] Summary line shows: N СТ · M пал · W кг · V м³
- [ ] Date line shows stDate (top filter date, read-only — no date picker)
- [ ] Transport type select pre-filled with first available type
- [ ] Vehicle select shows availability dots (🟢🟡🔴) if API responds
- [ ] Driver select shows full names
- [ ] Dock field is a free text input
- [ ] «Создать рейс (N СТ)» button shows count of STs in the cluster
- [ ] «Отмена» closes dialog without any action
- [ ] Clicking overlay backdrop closes dialog

### After creating task from cluster
- [ ] Dialog closes automatically
- [ ] Cluster view refreshes (created STs no longer appear in cluster)
- [ ] Routes tab opens automatically with new task selected
- [ ] New task is highlighted/selected in task list
- [ ] If API returns warnings, error bar shows them

### Edge cases
- [ ] If district has 0 unassigned STs → API returns 404 → error shown, dialog stays open
- [ ] If vehicle is already busy (🔴) → warning shown in dialog, but task CAN still be created
- [ ] «(без района)» cluster (RAION = null) — button works, creates task for STs without district
- [ ] Button disabled + spinner during loading

### Performance
- [ ] Dialog opens within 200ms (local UI)
- [ ] Vehicle availability loads within 1s
- [ ] Task creation completes within 3s for cluster with ≤50 STs
