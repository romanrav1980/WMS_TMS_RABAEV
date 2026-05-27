# Sprint 31 — Usability Checklist: Cluster Sidebar

## Feature: Cluster left sidebar panel

### Preconditions
- [ ] Switch to «По районам» view mode in Заявки tab
- [ ] There are at least 2 clusters (2 different RAION values)

### Sidebar visibility
- [ ] Sidebar appears on the LEFT side of the workspace when in «По районам» mode
- [ ] Sidebar is hidden in «По СТ» (flat) mode
- [ ] Sidebar is hidden in «Маршруты» and «Биллинг» tabs

### Sidebar header
- [ ] Shows «Кластеры» title
- [ ] Shows total summary: «N р-нов · M СТ · K пал»

### Cluster cards
- [ ] Each cluster has its own card
- [ ] Card shows district name (RAION) in bold
- [ ] Card shows ST count, pallet count, weight in small badges
- [ ] Cards are sorted alphabetically (А-Я); «(без района)» appears last
- [ ] Card highlighted/active border when its cluster is expanded in table

### Cluster card interactions
- [ ] Clicking card body toggles cluster expand/collapse in the main table
- [ ] «⚡ Рейс» button on each card opens ClusterQuickCreateDialog
- [ ] Clicking «⚡ Рейс» does NOT toggle expand/collapse

### After creating task from sidebar card
- [ ] Dialog closes
- [ ] Sidebar refreshes (created cluster card disappears or ST count decreases)
- [ ] Main table cluster row also refreshes

### Layout and scrolling
- [ ] Sidebar has fixed width (~200px), does not push content off-screen
- [ ] Sidebar scrolls independently if there are many clusters
- [ ] Main content area still scrollable
- [ ] No horizontal overflow on 1440px minimum width

### Edge cases
- [ ] When clusters reload (⟳), sidebar updates without flicker
- [ ] Sidebar shows «Нет свободных СТ» when all STs are assigned
