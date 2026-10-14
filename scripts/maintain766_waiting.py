from pathlib import Path
import json
out={}
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json")
d=json.loads(p.read_text(encoding="utf-8"));v="../2026-10-12_ni072_waiting_cell/apply.sql"
if v not in d["additional_scripts"]:d["additional_scripts"].append(v)
out[str(p)]=json.dumps(d,indent=2)+"\n"
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json")
d=json.loads(p.read_text(encoding="utf-8"))
for x in d["increments"]:
 if x["id"]=="NI07.2":x.setdefault("implementedSlices",[]).append("766 explicit sameWARE waiting-cell setting/native guard/API/existing form; case762 metadata rollback/invalid target/source P3H3; physical task handler remains")
out[str(p)]=json.dumps(d,ensure_ascii=False,indent=2)+"\n"
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.md")
out[str(p)]=p.read_text(encoding="utf-8")+"\nCheckpoint766 NI07.2: явная ячейка ожидания в существующих настройках и форме. Штатный physical task handler ещё открыт; статус спринта не изменён.\n"
p=Path("wiki/database/nicora_ni072_waiting_cell_20261012.md")
out[str(p)]=p.read_text(encoding="utf-8").replace("Общий quality gate запущен отдельно; итог фиксируется после завершения.","Quality gate763 PASS: 24 tooling/architecture tests, оба TypeScript проекта; architecture682/0cycles/76debt. Encoding764 PASS.")
out["задания на проведение тестов/NI07.2/766_ячейка_ожидания.md"]="""# Ячейка ожидания перенесённых СТ

Использовать собственный dev склад и metadata ячейки. Не пересоздавать SAP688/context744, не изменять P20/H20 и старые движения.

Через текущий settings API: сохранить доступную несистемную ячейку хранения того же склада вне отгрузки; проверить GET. Запрос без defer_wait_cell сохраняет значение, явный null очищает его. Отклонить чужой склад, неизвестную ячейку, OTBOR, IS_SYSTEM, блокировки, EXPEDITION_GROUP, TRANSPORT_STAGING/GATE/FILM_WRAP последней опубликованной topology. Проверить rollback всей конфигурации при отказе.

После любого изменения настроек количество, HARD, маркированные ключи и история движений неизменны. Задание физического переноса этим ticket не создаётся; отсутствие товара в зоне отгрузки не утверждать. Browser UI/hardware остаются отдельным приёмочным случаем.
"""
p=Path("wiki/runbooks/nicora_active_work.md")
out[str(p)]=p.read_text(encoding="utf-8").replace("Quality gate763 running session33883: architecture PASS682/0/76, 24 tests PASS; both TS started, final pending.","Quality gate763 PASS: architecture682/0/76, 24 tests and both TS. Encoding764 PASS.")
print(json.dumps(out,ensure_ascii=True))
