from pathlib import Path
import json
out={};page="wiki/database/retailcase_ni081_attendance_replace_20261010.md"
out[page]="""# NI08.1 / NS33 — план выхода заменяется атомарно,150

Existing RRL_WORKLOAD_CONFIG_API REPLACE_ATTENDANCE, no second roster registry. Current scoped actor before and after shared metadata fence; existing store_attendance same resource/person/current qualification/aware positive<=24h/other-site-overlap rule. Same immutable source plan ID must still be active; new start future only/reason>=8. Source cancellation and new planned row/operation result one UOW. Result replaced_plan_operation_id plus plan_operation_id; no actual presence/shift/session/task/P/H created or changed.

Native savepoint after metadata admission now protects all configuration actions from placeholder/partial source writes even if outer PL/SQL catches failure and commits. No internal commit. Current role/warehouse checked before replay, saved actor/action/hash exact, changed body rejected. Concurrent different replacement of same source one winner because original cancellationPK and existing global CONFIG serialization. Global fence used only low-volume configuration, physical posting parallel semantics unchanged.

Migration2026-10-10_ni081_attendance_replace6 statements, API spec/body+four guards liveVALID. Manifest current API replaced, generated bundle only, not applied. Tables/guard definitions remain existing134.

Author ni081_attendance_replace_existing_case.py creates metadata-only future source on existing resource43/siteQA150; does not reuse/cancel original134 roster. Late nonexistent resource404 preserves source and removes placeholder; outer SQL catch+commit also leaves source active/operation absent. Two concurrent new operations one200/one409, exact replay, changed same identity409; current config shows relational source identity. Own successful future replacement cancelled for cleanup. Tag646cf96a33 retained immutable history. Original135 P20H20 unchanged. No real physical attendance claimed.

Raw workload UI selects existing plan, operator inputs future interval/resource/site/reason, source label and lineage visible. Local pending original body retained by API+actor, previous session storage migrated; Web Locks serialize mutate/retry where supported, identity-matched removal prevents clearing another saved body. No browser rendering/unsupported-lock multi-window acceptance claimed. Node syntax PASS/architecturePASS499files0cycles79debt.

SQL API32.643ms/7, caught-error9.694ms/1, other37.027ms/1. Decision retain current indexed source/cancellation identity and existing low-volume config fence; no load capacity claim or new global physical lock. Full NS33 subwarehouse workload/approved joint schedule and independent acceptance remain.
"""
out["wiki/index.updated.tmp"]="- [Атомарное изменение планового выхода](database/retailcase_ni081_attendance_replace_20261010.md):150 source cancellation+new plan one UOW/future only/late rollback and concurrent one winner/current lineage/no stock.\n"+Path("wiki/index.md").read_text(encoding="utf-8-sig")
for p,line in [
("wiki/log.md","2026-10-10:150 existing workload REPLACE_ATTENDANCE/current actor after fence/future interval/immutable source version, cancellation+new plan+result oneUOW. Own savepoint protects all config actions even outer caught+commit.6 statements/API+4guardsVALID/current manifestgenerated. Future metadata-only43 QA150 source tag646cf96a33 late404+SQLcaught no partial source/placeholder, concurrent200+409/same replay/changed409/lineage visible; own replacement cancelled/original134 roster and P20H20 unchanged. Raw UI source selection/local original pending/session migration/WebLocks when supported; node/architecturePASS. SQL32.643/9.694/37.027ms keep indexedlowvolumeCFG, no load or independent acceptance."),
("wiki/requirements/retailcase_delivery_v55/execution/active/ni08_1.md","Ticket150 atomic future attendance correction/source lineage/retry/late rollback delivered; see database/retailcase_ni081_attendance_replace_20261010.md. Original134 roster retained, actual presence not changed.")
]:out[p]=Path(p).read_text(encoding="utf-8-sig")+"\n"+line+"\n"
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");m=json.loads(p.read_text(encoding="utf-8-sig"))
for row in m["sprints"]:
 if row.get("id")=="NI08.1":
  row.setdefault("implementedSlices",[]).append("150 atomic future planned attendance correction/source lineage/one winner/durable UI retry")
  row["evidence"]=page
out[str(p)]=json.dumps(m,ensure_ascii=False,indent=2)+"\n"
out["задания на проведения тестов/NI08.1/150_атомарное_изменение_плана_выхода.md"]="""# Qwen —150

Existing workload native action REPLACE_ATTENDANCE, same qualification/aware interval/overlap rule; current actor before and after fence/replay. Future new start, original active plan ID optimistic version and reason8. Cancellation+new plan+operation result sameUOW. Late invalid resource and outer SQL catches+commits must leave source active/no placeholder. Concurrent different replacement same source one winner; exact replay/changed sameID refused/current foreign ware403. No actual presence/session/task/stock change.

Author future-only metadata fixture resource43 siteQA150/tag646cf96a33 cleaned by native cancellation; original134 attendance unchanged/P20H20. Source old and replacement history retained. UI selected old plan visible/new operator fields/reason required, pending original localbody survivesclose/reopen and session migration; WebLocks support and cross-window fallback separately verify. Do not claim unsupported-browser serialization. Node syntax/architectureauthorPASS; no rendered independent acceptance.
"""
print(json.dumps(out,ensure_ascii=True))
