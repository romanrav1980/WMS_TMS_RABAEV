from pathlib import Path
import json
p=Path("wiki/database/nicora_ni011_internal_receipt_identifier_20261012.md");p.write_text(p.read_text(encoding="utf-8")+"""
## Actual687–689
686 применена2/0; USER_ERRORS=[]/INVALID=[] live. Contract687: старый SSCC и новый pallet_identifier, одинаковые GS1 aliases, конфликт/длина/пробел/ошибочный check digit проверены.

Actual688: отдельный новый SAP supply по существующему private SKU669/WARE, новая паллета UID47 символов, CRPT direct UNIT3 + EGAIS BOX3. Root SAP_RECEIPT/P3H0/три новых физических единицы/шесть кодов, оригинальный PUTAWAY DONE. PALLETS.SSCC=NULL/TASK.SSCC=NULL/CRPT parent отсутствует. Exact HTTP birth replay сохранён. Исходник669 и group671 не пересоздавались; новые единицы не являются повторным рождением старых.

Первый XML fixture688 имел OrderNumber39 символов и был отклонён до импорта; сокращён до17 в том же durable NEW-контексте. Supplier order и receipt response сохраняются до последующих assertions. context688.stage=DONE; не повторять source creation, только сохранённый replay/чтение.

Actual689: старый уже отгруженный SSCC receipt669 повторён по его сохранённому CANONICAL_REQUEST, HTTP201 выдаёт точный прежний RESULT_JSON; old shipping P0/H0. Новый alias не меняет старый canonical body.

Slow689 native header insert22.989ms/667buffers, old child11.279ms/499buffers. Решение inventory: retain single bounded header insert/document lookup; увеличение длины UID не добавляет SQL или quantity writes. Индекс без плана не добавлять; native trigger/metadata plan profiling — owner inventory перед промышленным fanout. Широкая нагрузка не проводилась.

Полный внешний SAP/Gov ACK, аппаратные barcode/print checks и независимая приёмка остаются отдельными. Новый internal UID не является государственным SSCC.
""",encoding="utf-8")
p=Path("wiki/index.md");p.write_text("- [NI01.1 checkpoint690: SAP-приёмка внутренней паллеты](database/nicora_ni011_internal_receipt_identifier_20261012.md): native686 VALID, actual688 UID47/P3H0/3units6codes/PUT DONE/SSCC NULL; old689 replay unchanged.\n"+p.read_text(encoding="utf-8"),encoding="utf-8")
p=Path("wiki/log.md");p.write_text(p.read_text(encoding="utf-8")+"\n12.10.2026 checkpoint690: receipt alias/shared UID validation/SAP native registration metadata completed; internal47 actual688 SAP birth+PUT P3H0/3units6codes/SSCC NULL/no fakeCRPT parent; legacy669 exact cached receipt689 unchanged/P0H0. Native686 VALID, SQLheader22.989ms667buffers → retain bounded source/header writes, inventory plan profiling before scale. [[database/nicora_ni011_internal_receipt_identifier_20261012]].\n",encoding="utf-8")
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json");d=json.loads(p.read_text(encoding="utf-8"));d["planRevision"]=30;d["currentSprint"]="NI01.1";d["currentStream"]="NI01"
for x in d["increments"]:
 if x["id"]=="NI01.1":
  x.setdefault("implementedSlices",[]).append("686–690 SAP receipt internal/legacy pallet identifier alias and truthful regulatory SSCC; actual688 UID47/new3units6codes/P3H0/PUT DONE and exact birth replay, old669 replay689 unchanged; same native quantity core")
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.md");s=p.read_text(encoding="utf-8").replace("**Revision 29,","**Revision 30,").replace("**Текущий — [NI05.1](execution/active/ni05_1.md);","**Текущий — [NI01.1](execution/active/ni01_1.md);")
p.write_text(s+"\nRevision30/checkpoint690: real internal UID47 SAP receipt+existing PUT DONE/P3H0/3units6codes/truthful SSCC NULL; old SSCC receipt replay unchanged. Header registration/quantity executor reused. External activation/hardware/full independent acceptance remain open.\n",encoding="utf-8")
p=Path("wiki/requirements/nikora_delivery_v55/execution/active/ni01_1.md");p.write_text(p.read_text(encoding="utf-8")+"\n686–690: SAP scalar receiving accepts internal UID/legacy identifiers as well as SSCC, UI generic field, source/quantity/trace owner unchanged. Actual UID47/new3units6codes/P3H0/PUT DONE/SSCC NULL/native686 VALID; old669 cached receipt exact. [[database/nicora_ni011_internal_receipt_identifier_20261012]].\n",encoding="utf-8")
p=Path("db/migrations/2026-10-12_ni011_internal_receipt_identifier/checkpoint.json");d=json.loads(p.read_text());d["status"]="APPLIED_VALID";d["evidence"]="actual688 internal47 SAP receipt+PUT P3H0/3units6codes/SSCC NULL/replay; old669 exact receipt replay689";p.write_text(json.dumps(d,indent=2)+"\n",encoding="utf-8")
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");d=json.loads(p.read_text(encoding="utf-8"));name="../2026-10-12_ni011_internal_receipt_identifier/apply.sql"
if name not in d["additional_scripts"]:d["additional_scripts"].append(name)
p.write_text(json.dumps(d,indent=2)+"\n",encoding="utf-8")
p=Path("wiki/runbooks/nicora_active_work.md");p.write_text("""## Current checkpoint690 — 12Oct2026
- Continue all18 until actual completion; full commit/GitHub AFTER actual completion, exclude SAP/SAP_INTEGRATION. No agents/model inference/broad qualification. Plan30/currentNI01.1.
- Native686 SAP header registration physical UID vs regulatorySSCC; captured live684/sourcehash/paired rollback, applied2/0/live ERRORS=[]/INVALID=[]. Receipt DTO alias pallet_identifier + old sscc/shared normalization, planner no SSCC-only constraint, UI generic identifier. UID50characters/150UTF8bytes fits live PALLETS50CHAR and native scanner variables; numeric18 retains checkdigit.
- Actual688 new private supply on retained SKU/WARE669 (no source669 recreation), UID47/new3 physical units6codes/CRPT UNIT+EGAIS BOX/root P3H0/existing PUT DONE; PALLETS/TASK SSCC NULL/no CRPT parent. Response stored before asserts, context688 DONE. Initial OrderNumber39 refused pre-import, shortened17 in same NEW context. Do not rerun initial source create; read/exact saved replay only.
- Actual689 original669 SSCC receipt CANONICAL_REQUEST replay returned exact stored RESULT_JSON/P0H0. Legacy body unchanged. Header insert22.989ms667buf/old11.279ms499buf; retain bounded metadata/document insert, inventory plan profiling before scale, no broad index.
- API687 started53940/41816/rootserv/startup complete, loaded686. Existing group673/HTTP675 and QC681 remain protected. Source bundle refresh690 needed after manifest append686; do not apply whole ACTIVE bundle.
- Full offline quality gate682 PASS24 architecture/tooling+bothTS; encoding682 PASS. After686 architecture679/0/76 and contract687/native/HTTP688-689 passed; UTF8 final690 pending.
- QC label680/681 current native actor/status/signature409/no-store and existing UI; actual blocked label/local green/red/escape only. Green native source/hardware/attachment full lifecycle open. Receipt label677 scope current actor/WARE/post-wait USED guard; native helper read PASS but labels table empty/real label fixture still absent.
- UTF8 recent wiki repair680 complete; use UTF8 file-backed scripts for Russian text, no Python heredoc Russian via PowerShell stdin. Historical raw literal???? evidence preserved.
- Native667/674 VALID; groupctx671 actual673 mixed same-profile UNIT+BOX+PALLET/old6units9codes/twoSKU3each/oneTOP/P3H0 each blocked receiving, rollback/replay/current UI/HTTP675. Never rerun669/670/671/672/673 factories; source670 resumed original committed birth via existing replan after equal-distance fixture assumption. Group new673 placement/custody not performed; historical444 full old chain remains.
- Prior protected643/624 P3H0,632 cleaned,565/586/601 money107.25/current0 and P20/H20 fixture unchanged.
- NI02.1 owner auto preparation restoration decision pending. Real Gov provider/gateway/certificates/ACK/hardware/full independent evidence absent; no fabricated completion. All18 still incomplete, continue genuine residuals using original WMS/TMS; no restart original TMS2.
"""+"\n"+p.read_text(encoding="utf-8"),encoding="utf-8")
