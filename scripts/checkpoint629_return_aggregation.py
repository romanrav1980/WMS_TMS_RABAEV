from pathlib import Path
import json
p=Path("wiki/database/nicora_ni062_return_aggregation_20261012.md")
v=p.read_text(encoding="utf-8")
v += """
## Checkpoint629: реализован путь коробки, ограничение паллеты сохранено

619/626 применены в dev RABAEV/orcl; USER_ERRORS/INVALID пусты (627). Shared resolver подключён к handover, driver pickup и warehouse receive. API621 принимает aggregation_scans через публичный inventory-контракт, пустой новый список удаляется для старого canonical request.

622/623/624: собственная SAP-поставка3EA, прежняя ST/LOAD/DEPART/магазин, текущие профили CRPT UNIT + EGAIS BOX-only. Возврат прошёл согласование/SAP/план/передачу/независимую подпись водителя/полную исправную коробку/приёмку/PUT. Прямой unit fallback для BOX отвергнут. Неверное количество коробок отвергнуто. Точные receive/PUT повторы сохранены. 627 read-only подтверждает P3/H0, 3 прежних физических ключа, 6 прежних кодов, одну передачу и удалённого тестового пользователя. Не запускать исходные factories622/623/624 заново.

Важное уточнение исходного предложения: RRL_STOCK_STORE_RETURN_REC_CMD требует fresh PALLET_IDENTIFIER. Поэтому PALLET aggregation старого контейнера не должна подтверждать новый контейнер. 626 явно отклоняет её RETURN_PALLET_AGGREGATION_REQUIRES_PRESERVED_CONTAINER_IDENTITY. Полный PALLET-only возврат ещё не реализован; нужен явный сценарий сохранённой идентичности или зарегистрированная новая агрегация. Прежний PALLET-код не разрешается автоматически после перепаковки/изменения UID. BOX-путь не объявляется доказательством PALLET-пути.

629 UI: ReturnMarkPanel в прежней ReturnCustodyPanel и return-mark-draft.js на прежней складской странице. Режимы UNIT/BOX/UNIT_OR_AGGREGATION, никаких прямых unit fallback для BOX. Черновик связан с API/пользователем/исходником/составом; сохранённая команда использует прежний механизм точного повтора. PALLET-only блокируется с понятной причиной. Сервер остаётся валидатором полного состава.

SQL627: lookup aggregation0.510ms/5.43buffers; count2.249ms/27.57buffers; insert2.656ms/29buffers. Решение: сохранить текущие indexed registered-origin queries и ограничения1000/10000/20000; отдельный индекс не оправдан этим dev случаем. Это не нагрузочное подтверждение миллионов операций. Native VALID и architecture676/0cycles/76debt; changed frontend typecheck PASS. Нет настоящего государственного ACK или независимой приёмки.
"""
p.write_text(v,encoding="utf-8")
p=Path("wiki/runbooks/nicora_active_work.md")
v=p.read_text(encoding="utf-8")
p.write_text("""## Current checkpoint629 — 12Oct2026
- Continue all18; commit/GitHub after all completion, exclude SAP. No agents/model review/broad qualification.
- Native619/626 current VALID; API621 shared return aggregate contract. 624 mixed CRPT UNIT/EGAIS BOX-only whole return completed P3H0/3originalunits6codes; 627 retained read-only PASS, actor retired/binding restored. Never recreate622/623/624 factories.
- Existing return requires fresh pallet UID; original PALLET aggregate is explicitly blocked until preserved physical identity/new registration implemented. Do not claim PALLET path completed.
- Existing return React + raw warehouse UI support BOX aggregation, durable scoped drafts, native exact composition; typecheck PASS, architecture676/0cycles/76debt. Encoding after docs still pending.
- Bundle611 predates619; append final native sources without applying whole ACTIVE bundle. Keep earlier money586 original107.25/current0 and601 completed correction contexts untouched.
- NI02.1 original auto-split source unavailable; owner question sent to authorize restoration from existing preparation, dependent work waits. Continue independent residuals meanwhile.
- Details [[database/nicora_ni062_return_aggregation_20261012]]. All18 not complete, no external/hardware evidence fabricated.

"""+v,encoding="utf-8")
p=Path("wiki/index.md");v=p.read_text(encoding="utf-8")
p.write_text("- [Checkpoint629: возврат по агрегации коробки](database/nicora_ni062_return_aggregation_20261012.md): complete mixed-profile dev cycle, existing UI, PALLET identity limitation explicit.\n"+v,encoding="utf-8")
p=Path("wiki/log.md")
with p.open("a",encoding="utf-8")as f:f.write("\n2026-10-12 checkpoint629: native619/626 VALID, existing API/UI return BOX path; retained624 P3H0/3keys6codes/no rebirth/actor retired;627 indexed slow SQL decision. PALLET limitation recorded, not full sprint closure; NI02.1 decision question pending.\n")
p=Path("wiki/requirements/nikora_delivery_v55/execution/active/ni06_2.md")
with p.open("a",encoding="utf-8")as f:f.write("\nCheckpoint629: registered BOX return implemented through shared resolver and existing custody/warehouse screens. Actual624 mixed CRPT UNIT/EGAIS BOX-only P3H0/3oldkeys6codes; native VALID. PALLET-only requires preserved physical identity/new aggregate registration and remains open. See [[database/nicora_ni062_return_aggregation_20261012]].\n")
d=Path("db/migrations/2026-10-08_stock_posting_core");p=d/"current_runtime_manifest.json";m=json.loads(p.read_text(encoding="utf-8"))
for name in ("../2026-10-12_ni062_return_aggregation/001_shared_resolver_access.sql","../2026-10-12_ni062_return_aggregation/002_return_unit_core.sql"):
 if name not in m["additional_scripts"]:m["additional_scripts"].append(name)
p.write_text(json.dumps(m,indent=2)+"\n",encoding="utf-8")
print("629 durable checkpoint/wiki/manifest updated; no whole-bundle apply")
