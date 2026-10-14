from pathlib import Path
def append(name,text):
 p=Path(name);p.write_text(p.read_text(encoding="utf-8")+"\n"+text+"\n",encoding="utf-8")
append("wiki/database/nicora_ni071_transport_rounding_20261012.md","594 applied4 statements/0 errors, USER_ERRORS[]/INVALID[], new CHECK validated against existing financial rows. Retained586 exact read remains107.25; no financial history rewritten. Current native AMOUNT = round(QUANTITY*RATE_VALUE,2).")
append("wiki/database/nicora_ni071_transport_recognition_20261012.md","Актуальное округление594: первоначальное per-charge-unit заменено стандартным для существующего finance.domain.amount.cost_amount — round(quantity*rate,2) по статье. Строки586 quantity1 и сохранённый total107.25 неизменны. 592 invoice source discovery uses original TT/LOAD pairs, not existing BOX cost lines; source200 bound/current warehouse scope. Bundle595 includes582/594, maintained only, not applied on ACTIVE.")
p=Path("wiki/index.md");p.write_text("- [Checkpoint595: деньги и источники счёта](database/nicora_ni071_transport_recognition_20261012.md): recognition582/rounding594 applied VALID, original invoice load sources592, bundle595 maintained; monetary correction/multiWARE remain.\n"+p.read_text(encoding="utf-8"),encoding="utf-8")
append("wiki/log.md","2026-10-12 checkpoint595: source592 original TT/LOAD invoice discovery decoupled from prior BOX costs; architecture672/0/76. Native594 aggregate article rounding applied4/0/VALID, existing financial rows validated/new CHECK, retained107.25 unchanged. Query590 two current reads avg6.083ms16.5buffers; no load benchmark. Bundle595 now includes582/594, never applied wholesale on ACTIVE. Current compile valid and next independent evidence/multiWARE/correction remain.")
p=Path("wiki/runbooks/nicora_active_work.md");p.write_text("""## Current checkpoint595 — 12Oct2026
- Continue all18; full commit/GitHub only after all completion, SAP excluded; no agents/broad qualification.
- Native594 aggregate financial rounding applied4/0/VALID; compute round(quantity*rate,2), aligned with existing finance.domain.amount.cost_amount. Old586 quantity1/total107.25 exact result retained.
- 592 invoice norms/preview discovery now original TT/LOAD pairs, independent of BOX cost journal; current actor warehouse scope, pairs bound200. Existing invoice component shows separate normative costs.
- Bundle595 adds recognition582 + rounding594 after vehicle559/hash561/config564/norm572. Maintained snapshot only, never apply whole ACTIVE.
- Context586 DONE, synthetic dev DEFAULT regional tariff retained/actual107.25 winner immutable; no rerunfactory586. Context583 rollback-only trial BEFORE586 used same departure; DO NOT rerun583 now: real claim exists. Exact original586 replay safe.
- 588 scoped exporter initial run already done, EXPORTED/ACKnull; DO NOT repeat initial checker. Original XML tmp/transport588_export retained.
- Native589/594 ERRORS[]/INVALID[]; last frontend TS587 PASS, latest592 changes need final TS/UTF8 once. Architecture592 PASS672/0cycles/76debt.
- API589 startup and actualread/exactreplay verified; later backend590/592 edit may leave reloader stuck; restart rootserv if necessary.
- Next: financial correction via existing approval owners preserving original normative cost; multiWARE source/period distribution; actual invoice UI/scoped view. Current NI07.1, planrevision24, 17 increments still residuals, no fake full closure.
- Hours/loader missing blocker was erroneous: Q26 already defines vehicle+points+unload/extra loader; native shared formula now correct. Original rates/archive still available for existing carrier billing.
- Current native money detail root receives one cost perDEPART, head/current rights/version cached replay, same-TX header/claim/details/outbox. No qtywriter/carrier invoice mutation.

"""+p.read_text(encoding="utf-8"),encoding="utf-8")
root=next(Path(".").glob("*/NI08.1/178_container_cell_index.md")).parent.parent
p=root/"NI07.1"/"591_transport_money_recognition.md"
p.write_text(p.read_text(encoding="utf-8")+"\n594 округление: точное количество × ставка, затем HALF_UP2 по статье (2×4.125=8.25). Старый total586107.25 не меняется. Не запускать583 на том же уже начисленном выезде; нужен собственный новый isolated source.592 invoice sources из LOAD без обязательного BOX charge.\n",encoding="utf-8")
print("595 current source/rounding/checkpoint/wiki state saved.")
