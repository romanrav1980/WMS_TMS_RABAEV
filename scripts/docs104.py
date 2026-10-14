from pathlib import Path
import json
out={}
p=Path("wiki/index.md");out["wiki/index.updated.tmp"]="- [Недостача тары существующей волны](components/retailcase_ni063_tare_forecast_20261010.md):104 current CASE/type/free/shortage, pending returns separate, API actual2/free1/short1.\n"+p.read_text(encoding="utf-8-sig")
p=Path("wiki/log.md");out[str(p)]=p.read_text(encoding="utf-8-sig")+"\n2026-10-10:104 existing CASE wave forecast and assembly UI delivered; actual wave369 standalone unbooked2/free1/shortage1. No physical availability invented from pending warehouse return offers. SQL73.319ms/2: retain boundedwave10000/types100 and wave/source indexes; NI06.3 owner inspect actual plan at volume.\n"
p=Path("wiki/requirements/retailcase_delivery_v55/execution/active/ni06_3.md");out[str(p)]=p.read_text(encoding="utf-8-sig")+"\nTicket104: [прогноз недостачи](../../../../components/retailcase_ni063_tare_forecast_20261010.md), existing standalone CASE wave demand/type/booked/free; proposed returns separate and nested cases not multiplied. Actual2/free1/short1 API.\n"
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.md");out[str(p)]=p.read_text(encoding="utf-8-sig")+"\n10.10.2026:092–104 NI06.2 ordinary approved/SAP-file/driver custody/warehouse birth/existing putaway and NI06.3 quantity/deadline/damage/booked actual cargo/FULLPAL/shortage slices delivered. Full residual sprint acceptance remains open; current functional work continues NI06.3/NI06.2. Local changes not published.\n"
out["wiki/components/retailcase_ni063_tare_forecast_20261010.md"]="""# NI06.3 — потребность тары существующей волны,104
Read-only inventory port/infrastructure/API and existing tare-assembly screen; Oracle DDL нет. GET /api/inventory/tare/warehouses/{ware}/waves/{wave}/forecast requires tare_view + current warehouse binding; wave must belong to that warehouse.

Для текущих unshipped/uncancelled самостоятельных CASE группируются existing PALLET_TYPE_ID и незакреплённые места. Недостача=max(unbooked-free,0); прежние holds уже исключены из свободного количества, поэтому второй раз не вычитаются. Если физический пересчёт отсутствует, доступность/недостача null и OBSERVATION_REQUIRED.

Вложенные CASE не считаются самостоятельной тарой; их количество показано как scope warning. FULLPAL требует явного физического типа BOOK103. Незавершённые GOOD vehicle→warehouse offers показываются как proposed_return_quantity отдельно, без обещанной даты и без увеличения free. Запрос не резервирует тару и не доказывает обеспеченность всей смены.

[Сценарий](../../scripts/ni063_forecast_case.py) PASS read-only real Oracle/API: существующая wave369 имеет unbooked2/free1/shortage1. Max10000 CASE в волне,100 типов; большее окно требует разделения. SQL cxtnfuakmyw6v73.319ms/2, retain bounded/indexed wave and current-balance PK; NI06.3 owner checks plan/projection if history grows.
"""
out["задания на проведения тестов/NI06.3/104_прогноз_недостачи.md"]="""# Qwen — NI06.3,104
Собственная existing wave CASE: shortage=max(unbooked-free,0); already HELD не расходуется повторно. Изменение BOOK/cancel/warehouse physical return отражается после refresh.
До actual ACCEPT предложенный возврат не увеличивает free. Missing observation даёт null, не ноль.
Nested CASE исключены из standalone count, scope warning показан; unknown FULLPAL type не выдуман. Чужая wave/ware forbidden; current rights/binding required.
Только bounded запрос; SQL analysis actual case. Это scope standalone CASE, не полная packing optimizer acceptance.
"""
print(json.dumps(out,ensure_ascii=True))
