# Sprint 35 — Usability Checklist: RAION filter in available-sts endpoint

## Feature: Server-side district filter (performance improvement)

### What changed (transparent to user)
- `GET /available-sts?raion=Север` now filters in Oracle SQL, not Python
- `create_task_from_cluster` uses raion parameter directly → 1 DB query instead of 2

### Regression: existing available STs features must still work
- [ ] Flat view (no raion filter) shows all available STs for date
- [ ] Address mask filter still works
- [ ] ST number filter still works
- [ ] Assembled only / not assembled filters still work
- [ ] «По районам» view still correctly groups STs into clusters
- [ ] «⚡ Рейс» button creates trip with correct STs (server-side filter)

### «(без района)» special case
- [ ] Cluster named «(без района)» creates a trip with STs where RAION IS NULL
- [ ] Before fix: Python filter `or "(без район)"` worked, now Oracle IS NULL

### Performance (transparent)
- [ ] «⚡ Рейс» button completes noticeably faster for large datasets
  (was: fetch all STs → filter in Python; now: Oracle filtered query)
- [ ] No regression in response time for standard available-sts without raion filter

### API (optional manual check)
- [ ] `GET /api/admin/transport/available-sts?raion=Север&stdate=2026-05-28`
  returns only STs for that district
- [ ] `GET /api/admin/transport/available-sts?raion=%28без+района%29`
  returns STs without a district (RAION IS NULL)
