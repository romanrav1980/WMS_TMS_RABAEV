# Sprint 30 — Usability Checklist: Live Load Metrics Bar

## Feature: LoadBar in task right panel

### Preconditions
- [ ] A transport task is selected (appears in right panel)
- [ ] The task has TRANSPORT set to a vehicle that has PALLETS defined
- [ ] The task has at least 1 ST assigned (tripP > 0)

### Visual checks
- [ ] Load bar appears between task meta fields and ST table
- [ ] Bar shows label «Паллеты», filled track, and text «N / M пал (P%)»
- [ ] Bar is green when fill < 85%
- [ ] Bar turns amber/yellow when fill is 85%–99%
- [ ] Bar turns red when fill reaches 100%
- [ ] Bar turns red and stays at 100% width when over capacity

### Interactive behavior
- [ ] Bar updates in real-time when STs are added to the task (without page reload)
- [ ] Bar updates in real-time when STs are removed from the task
- [ ] Bar disappears when all STs are removed (tripP = 0)
- [ ] Bar disappears when task has no vehicle assigned (TRANSPORT = null)
- [ ] Bar disappears when vehicle has no PALLETS value (PALLETS = null)

### Threshold boundary tests (manual)
- [ ] 8/11 палл (72%) → green
- [ ] 9/11 палл (82%) → green
- [ ] 10/11 палл (91%) → amber
- [ ] 11/11 палл (100%) → red
- [ ] 12/11 палл (109% → shown as 100%) → red

### Edge cases
- [ ] Vehicle with PALLETS = null → bar hidden (no NaN display)
- [ ] Task in «Отгружен» status → bar still shows (read-only is fine)
- [ ] Bar does not overflow container when very long text

### Performance
- [ ] Bar renders without flicker when switching between tasks
- [ ] No layout shift when bar appears/disappears
