from pathlib import Path
import json
files={}
p=Path("wiki-raw/wms_admin_ui_reference/interwarehouse-groups.js");t=p.read_text(encoding="utf-8");old='if(!current()||plan!==el("ggPlan").value)return;detail=result;';new='if(!current()||plan!==el("ggPlan").value)return;\n if(Number(result.plan.target_warehouse_id)!==Number(el("ggWare").value))throw Error("План относится к другому принимающему складу. Обновите очередь.");detail=result;'
assert old in t;t=t.replace(old,new);files[str(p)]=t
p=Path("wiki-raw/wms_admin_ui_reference/interwarehouse-workspace.js");t=p.read_text(encoding="utf-8")
t=t.replace('a.href=url;return a;','a.href=url;a.title="Открыть существующий экран: "+text;return a;')
t=t.replace('b.type="button";b.onclick=()=>prepare','b.type="button";b.title="Открыть форму; проведение потребует отдельного подтверждения и фактических сканов";b.onclick=()=>prepare')
t=t.replace('b.type="button";b.dataset.plan=','b.type="button";b.title="Показать маршрут и доступные действия для этого места";b.dataset.plan=')
files[str(p)]=t
report="reports/nicora/2026-10-13/48-b04-interwarehouse-workspace.md"
files[report]="""# NI06.1 — единый межскладской маршрут
2026-10-14. Доработан существующий interwarehouse.html: поиск по паллете/товару/рейсу, дата прибытия, этап; карточка обоих плеч, последовательность выгрузки/приёмки/размещения/ответственности/СТ. Отдельно показаны составные места принимающего склада с переходом к существующей форме и матрице маркировки.

Кнопки выбирают документы и раскрывают прежние формы. Сканы автомобиля, паллеты, ячейки, товара не подставляются. Подготовленная СТ явно отделена от погрузки, выезда и приёмки покупателем. Смена склада/истории/пользователя исключает устаревший результат; сохранённая команда блокирует начало другой операции. Ссылка на составное место сверяется с принимающим складом ответа.

Владелец: inventory UI; правила и транзакции остаются в существующих Oracle-командах. Новых таблиц, API, движений и второго ядра нет.

Авторская браузерная проверка реального API: склад59619048, план IW464.PLAN:913fc8a45e — 3EA приняты, требуется размещение; старая форма истории открылась. Смена склада56524567 очистила карточки; GROUP672.PLAN:6207f7b382 открылся с двумя товарами и профилями CRPT/TOBACCO и EGAIS/ALCOHOL. Фактический статус — принято покупателем. JavaScript errors=[], business POST=[]; tmp/result1344.json. Ничего повторно не принималось.

[Маршрут](screenshots/88-b04-interwarehouse-route.png), [составное место](screenshots/89-b04-group-link.png).
SQL: bounded group queue, SQL_ID2yv9m25yumubg, среднее27.28мс/2,1011buffers. Решение: сохранить лимит100 и существующую keyset-пагинацию; чтение состава только по выбору. Inventory отвечает за повторный анализ при регулярном>500мс. Это измерение групповой очереди, не нагрузочный вывод по всему процессу.

Полный NI06.1 и независимая/внешняя приёмка этим UI-проходом не закрыты. Существующие физические сценарии сохранены; этот блок соединяет их для оператора.
"""
page="wiki/components/nicora_b04_interwarehouse_workspace_20261014.md"
files[page]="# NI06.1: операторский маршрут между складами\n\n1342–1346. Существующий interwarehouse.html получил карточки обоих рейсов, фильтры, этапы и переходы в прежние команды; составные места открываются по warehouse+plan. Сканирование остаётся ручным физическим фактом. Новых stock writers нет.\n\n[Отчёт48](../../"+report+") содержит реальное read-only browser evidence и SQL решение. Полная независимая приёмка спринта отдельно.\n"
p=Path("wiki/index.md");files[str(p)]="- [B04: маршрут между складами1346](components/nicora_b04_interwarehouse_workspace_20261014.md): карточки/этапы/существующие формы/составные места, report48, screenshots88–89.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md");files[str(p)]=p.read_text(encoding="utf-8")+"\n- 2026-10-14 ·1346: NI06.1 interwarehouse workspace соединяет существующие операции, реальные read-only переходы PASS, bounded SQL27.28мс; report48. Далее B05/NI06.3.\n"
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json");d=json.loads(p.read_text(encoding="utf-8"));d["planRevision"]=62;d["currentSprint"]="NI06.3";d["firstChange"]="B04 operator route workspace delivered (report48); continue B05 two-party tare driver/store UI. Claude owns C-0005 finance basis."
for item in d["increments"]:
 if item["id"]=="NI06.1":item.setdefault("implementedSlices",[]).append("1342–1346 existing interwarehouse workspace unified route/filter/stage/next-action/grouped-place links, scoped stale response guards; real read-only browser evidence report48. Physical commands reused.")
files[str(p)]=json.dumps(d,indent=2,ensure_ascii=False)+"\n"
print(json.dumps(files,ensure_ascii=True))
