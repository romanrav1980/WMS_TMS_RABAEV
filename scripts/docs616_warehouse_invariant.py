from pathlib import Path
import json
def append(name,text):
 p=Path(name);p.write_text(p.read_text(encoding="utf-8")+"\n"+text+"\n",encoding="utf-8")
text="615–616 уточнение по живому RRL_STOCK_HU_LOAD_CORE:14/57 берётся WARE_ID ворот рейса;35 ST обязан иметь тот же WARE_ID;68 это повторно проверяется под блокировкой;74–75 LOAD_FACT.WARE_ID записывается из ware_no. DEPART требует одинаковые ворота для всех мест. Один действующий выезд относится к одному физическому складу. Пункт о необходимости нового multiWARE-внутри-TT ядра был избыточным: агрегирование разных складов нужно между рейсами счёта и уже поддерживается scoped invoice/source/grouped sums. Ограничение native Q26 защищает существующий инвариант, а не отключает допустимый сценарий. Не расширять погрузку/проводку ради выдуманного требования."
append("wiki/database/nicora_ni071_transport_recognition_20261012.md",text)
append("wiki/database/nicora_ni052_loading_20261010.md",text)
append("wiki/requirements/nikora_delivery_v55/execution/active/ni07_1.md",text)
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json");d=json.loads(p.read_text(encoding="utf-8"));d["planRevision"]=26
d["firstChange"]="Continue genuine remaining NICORA deltas after Q26 recognition/correction; one current trip uses one physical warehouse/dock by existing live load invariant. Do not build a parallel multiwarehouse-TT allocator. Invoice multiwarehouse aggregation already implemented. Actual mixed-date/real ERP/independent evidence remain."
for collection,identifier in (("sprints","NI07"),("increments","NI07.1")):
 row=next(row for row in d[collection]if row["id"]==identifier)
 row["progressNote"]="Normative recognition/correction and multiwarehouse invoice aggregation implemented; existing load invariant one departure warehouse preserved. Remaining actual mixed-date/real ERP/independent evidence and monthly source coverage."
 row["implementedSlices"].append("615–616 live load-core invariant confirmed: ST/LOAD WARE equals dock WARE, same dock for departure; multiWARE-in-one-TT new subsystem removed from proposed residual scope. Existing invoice aggregates across trips/current visible warehouses.")
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.md");v=p.read_text(encoding="utf-8").replace("**Revision 25,","**Revision 26,")
v=v.replace("Multiwarehouse normative recognition/corrections, physical mixed-day rehearsal and real financial ERP","Physical mixed-day/source coverage, real financial ERP and independent evidence")
v+="\nRevision26 /615–616: live loading core enforces one physical warehouse/dock per current departure. Не создавать новое многоскладовое ядро одного TT; разные склады объединяются по рейсам счёта существующими scoped источниками/суммами. Ранее внесённый пункт multiWARE-in-TT удалён как избыточный. Результаты Q26 recognition/correction остаются, реальные недостающие сценарии остальных карточек сохраняются.\n";p.write_text(v,encoding="utf-8")
p=Path("wiki/index.md");p.write_text("- [Checkpoint616: существующий складской инвариант](database/nicora_ni052_loading_20261010.md): current load core ST/LOAD WARE=dock WARE, same dock on departure; no invented multiWARE-TT subsystem, plan26.\n"+p.read_text(encoding="utf-8"),encoding="utf-8")
append("wiki/log.md","2026-10-12 checkpoint616: bounded live USER_SOURCE inspection RRL_STOCK_HU_LOAD_CORE14/35/57/68/74–75 and currentDEPART establishes one warehouse/dock per departure. Removed invented multiWARE-in-TT residual from plan26; multiwarehouse invoice across trips already scoped/grouped. Existing source invariant and financial kernel preserved; no new DDL, no source changes.")
p=Path("wiki/runbooks/nicora_active_work.md");p.write_text("""## Current checkpoint616 — 12Oct2026
- Continue all18; full commit/GitHub only after all completion, exclude SAP. No agents/broad qualification.
- Plan26: normative Q26 recognition + same original expense dual-phase correction done with bounded native evidence. Important:615 live load core confirms ST/LOAD WARE=dock WARE, DEPARTsame dock. DO NOT implement invented multiWARE-in-one-TT kernel. Across-trip/warehouse invoice grouping already implemented.
- 612–614 bounded invoice/source totals now one grouped indexed adjustment SUM, no per-root native calls for pages; Decimal normalization preserves0.613 currency accumulator shadow fixed;614 actual same invoice snapshot original107.25/current0/GEL grouped/source pair, own trip binding changed only in outer rollback and fully restored/PRICE unchanged.
- TS after608 (session90589) completedPASS; UTF8/native (session94161) PASS and ERRORS[]/INVALID[]. New614 backend/late docs need only final changed-case checks, no broad repetition.
- Current617? no: API601 actualstartup/rights verified, watcher later edits may be stuck. Restart rootserv if needed.
- Preserve ctx601 done/retired/allocated/rejected; source586 original107.25/current0, actors retired. Do NOT601/602/603/609/583 factories. Same exact original monetary replay safe.
- Bundle611 has recognition582/rounding594/correction598; maintained only, never apply whole ACTIVE.
- Next genuine NICORA deltas: remaining actual source/month coverage/real ERP/independent proof, marked aggregate-only return/quality inspection, other existing residuals; inspect actual core before adding mechanisms.
- Full18 still not declared accepted. No real external ACK/certificates/hardware/legal proof fabricated.

"""+p.read_text(encoding="utf-8"),encoding="utf-8")
print("616 plan26/wikis corrected to actual existing one-warehouse departure invariant.")
