from pathlib import Path
import json
out={}
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
matches=[item for item in m["components"]if item=="../2026-10-10_ni042_composition_epoch/011_mes_birth.sql"]
assert len(matches)==1,matches
m["components"]=[ "../2026-10-10_ni043_mes_scope/001_core.sql" if item==matches[0] else item for item in m["components"]]
out[str(p)]=json.dumps(m,indent=2)+"\n"
page="wiki/database/nicora_ni043_mes_scope_20261010.md"
out[page]="""# NI04.3 — актуальный склад исполнителя MES,127
Migration2026-10-10-127-mes-current-warehouse-scope APPLIED4/0. Existing RRL_STOCK_MES_MOVEMENT_CORE body validates current activeRUSERS: actorWARE=production orderWARE or legacyGLOBAL_ADMIN; API existing apply reader checks same current scope before resolving pending movements/replay. Existing rightmes_wms_bridge_apply mandatory. Sole Root transaction/native core/balance/event/outbox unchanged.
Checkpoint442_before127_mes_movement_core.sql captured live source. New body/current manifest source represented, core/rootVALID verified. Migration adds no data table; removing this boundary refused rollback forward-only. Source snapshots/generated bundle must not be applied to ACTIVE.
Author scripts/ni043_mes_scope_case.py: own native BOM/order99/completion25/FGrelease123/UIDMES.MARKED.INTERNAL.PALLET:e9732e1188; own nonadminQM127e9732e1188 with current mes_wms_bridge_apply+trace_manifest_import. After WARE changed to9104 actual HTTP403 MES_CURRENT_WAREHOUSE_ACTOR_REQUIRED and P rows0. Correct ownWARE10828603 then original MES126.BIRTH:e9732e1188/capture/native release→APPLIED_TO_WMS/P3H0/physical3; nativeJSON HTTP exact replay/no increment; foreign sender source409. Actor retired. This actor-scope case reused existing native MES path and separate own fixture, not shared production.
Native guard source verified VALID; actual denial is API current-scope boundary. Do not claim a separately bypassed direct-core refusal case. No factory/raw consumption/regulatory real ACK evidence.
Slow SQL decisions reuse126 exact order/movement PK/current actor/source bounds200/units10000; inventory owner watches scope lookup and plans after volume growth.
"""
out["wiki/index.updated.tmp"]="- [Актуальный склад исполнителя MES](database/nicora_ni043_mes_scope_20261010.md):127 APPLIED/core+rootVALID/current nonadmin wrongWARE403/P0 then ownWARE native P3H0/replay; no new stock writer.\n"+Path("wiki/index.md").read_text(encoding="utf-8-sig")
for name,line in [("wiki/log.md","2026-10-10:127 current warehouse scope enforced in existing MES API and native core, APPLIED4/0/sourcecheckpoint442/current manifest/core+rootVALID. Actual nonadmin order99/release123 wrongWARE403/P0→ownWARE/P3H0/units3/APPLIED/replay, actor retired. Full marked sprint/regulatory evidence remainsopen."),("wiki/requirements/nikora_delivery_v55/execution/active/ni04_3.md","Ticket127: [[database/nicora_ni043_mes_scope_20261010]] current MES actorWARE enforced API/native core; existing nonadmin99/123/foreign403→native3/replay. Next direct UNIT scanning operator form alongside aggregation evidence.")]:
 p=Path(name);out[name]=p.read_text(encoding="utf-8-sig")+"\n"+line+"\n"
out["задания на проведения тестов/NI04.3/127_склад_исполнителя_MES.md"]="""# Qwen — NI04.3,127
Existing MES current right is necessary, and current activeRUSERS WARE must equal nativeproduction orderWARE (GLOBAL_ADMIN existingbypass). API validates before replay/resolving pending set, native core repeats under existing locked order. Scope migration body/sourcecheckpoint442/ledger/core+rootVALID/current source manifest.
Author actual order99/release123/nonadminQM127e9732e1188 foreignWARE403/P0 then ownWARE3/replay; actorretired. Do not rerunfreshfixture or assume independent validation. Examine native scope placement before movements/effects; current actor deactivation/binding change/replay mustnot bypass, foreigncurrent marked/unmarked/RAW operations denied. No actor supplied by client accepted. SameOP conflict and stock conservation/outbox retained. No removal ofguard in rollback.
"""
print(json.dumps(out,ensure_ascii=True))
