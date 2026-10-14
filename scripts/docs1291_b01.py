from pathlib import Path
import json
files={};report="reports/retailcase/2026-10-13/44-b01-layout-loading-departure.md"
text="""# B01: существующие СТ → физическая погрузка → выезд
14.10.2026. RABAEV/orcl, отдельный dev-стенд. Авторская адресная проверка.

## Полученный результат
Сохранённый заказ2135, план2191 и волна559 прошли сквозной сценарий от приёмки до выезда рейса33571. Принято/отобрано/отгружено36EA: два артикула по18. Исходные СТ641507/641508 и назначение рейса сохранены.

1. Плановая укладка A18+B6 / B12 изменена оператором на A18 / B18 через существующую RRL_UPDATE_SBORKA_PALLET_ROWS2, обёрнутую единственным Root. Суммы36EA/6коробок/24кг сохранены, запас не изменялся. Исторический SAP PREPARATION_JSON не переписан.
2. Задания1165/1166 уже доставили товар в B38c0c2a00cE; обе физические паллеты связаны с исходными СТ. Root проверяет текущие права и склад задания, включая повтор.
3. Явно подтверждён тип EURO_PALLET обеих паллет. Для dev-машины10059 заполнен профиль2EU, для рейса — собственные dev-водитель10018 и воротаB01c0c2a00c. Это тестовые реквизиты/измерения, не промышленный допуск.
4. Погрузка обеих СТ выполнена через transport-loading.html. Выезд возвращает DEPARTED,2места,24кг,stock_consumed_again=false. Волна559 завершена DONE,blocking_count0.
5. Карточка заказа использует уже существующий расчёт доставки:36EA отгружено,0 принято,36 ожидает приёмки магазином. Панели отбора и отгрузки расположены рядом; понятия не смешиваются. Чтение доставки проверяет текущий склад пользователя тем же native scope, что и исходный заказ.
6. После физического исполнения редактор плановой укладки показывает причину недоступности. Контроль NONE честно отображается «Контроль не требуется». Пустая погрузка больше не получает фиктивный идентификатор CASE:.

## Факты операций
- Перенос строки: ST.LAYOUT:f840ec86-d60f-4308-8d65-b2be2754fade, outbox5206.
- Привязки паллет: FULLPAL.BIND:2effe8cb-b06c-4a0c-8b9c-925fa3ee3a3e / FULLPAL.BIND:5ec85836-f9b4-424f-8b86-6ee325e60e69; outbox5207/5208.
- Погрузка: TT.LOAD:d00a9887-fee3-4c58-938b-5b18cadebfcb / TT.LOAD:5e037ff9-46be-4c11-8e88-f9d76ed3f3c6; outbox5210/5212.
- Выезд: TT.DEPART:0d35945c-466c-4ccf-88e7-b79c48f529aa, outbox5213.
- Завершение: WAVE.FINISH:0e6508fc-cc84-4167-bb24-00984fd6b555, outbox5214.
- Fulfillment183/184:SHIPPED,18EA каждый. Все строки запаса этих двух UID:REMAIN0/HARD_RESERVED_BASE0.

## Адресная проверка
Реальные UI/API/Oracle, не подменённые ответы. Перенос строки: native эффект с rollback до реального переноса; реальный UI и точный повтор после удаления исходной строки. Выезд: точный повтор возвращает прежний результат, повторного списания нет. USER_ERRORS по изменённым объектам=[], текущие INVALID=[].
Quality gate:726 файлов,0циклов,75пунктов прежнего долга;24теста архитектуры/инструментов и оба TypeScript typecheck PASS. Единственное предупреждение pytest — недоступный каталог кеша, не падение теста. Browser summary:0page errors.
SQL источники миграций1248/1265/006 включены в maintained runtime manifest и bundle; весь bundle на ACTIVE не применялся.

## Долгие SQL
Адресные чтения: delivery170.24мс, wave98.9мс, loading111.14мс (HTTP целиком). В V$SQL относящийся к выезду запрос24.063мс/69buffers, delivery10.535мс/94buffers, loading6.542мс/339buffers за7исполнений. Решение: сохранить bounded чтения, индекс не добавлять по одному короткому кейсу.
RRL_SQL_SLOW_LOG: запись2506 wave execution834мс; текущий повтор98.9мсHTTP. ВладелецCodex: сохранить ограничение1200, повторно смотреть план при регулярном>500мс; нагрузочный вывод не сделан.
Отдельно журнал показывает available-sts5.3–7.7с/62117строк (2504–2511), не запрос данного сценария. Явный backlogCodex/transport: ограничить выдачу/пагинацию и убрать полный периодический опрос; перед изменением сверить текущий контракт двойника и диспетчера. Нельзя выдавать эту проблему за исправленную.

## Скриншоты
- [Погрузка](screenshots/77-b01-loaded.png)
- [Выезд](screenshots/78-b01-departed.png)
- [Завершение волны](screenshots/79-b01-wave-finished.png)
- [Отбор и доставка заказа](screenshots/80-b01-order-summary.png)
- [Укладка после отгрузки](screenshots/81-b01-prepared-layout-current.png)

## Границы результата
Подтверждён один полный dev-проход B01 для немаркированного FULL_PALLET. QC у складаNONE; температурных требований у этих SKU нет. Не заявлены контроль со сканированием/весами, работа государственных систем, реальный SAP/оборудование, нагрузочная и независимая приёмка, завершение всех сценариев входящих спринтов.
Следующий блок — B02: применимые способы отбора и маркировка, с переиспользованием существующих CASE/агрегаций. NI08.1 требует серверного сопоставления норм; Claude продолжает финансовые основания C-0005.
"""
files[report]=text
page="wiki/components/retailcase_b01_departure_20261014.md"
files[page]="# B01: от приёмки до выезда\n\n"+text.split("## Полученный результат")[1].split("## Факты операций")[0]+"\n[Полный отчёт44](../../"+report+") и [план59](../requirements/retailcase_delivery_v55/implementation_plan.md).\n\nОдин dev-сценарий FULL_PALLET завершён. Все входящие спринты и внешняя приёмка не объявлены закрытыми. Следующий блок B02. Долгий available-sts62117строк — отдельный backlogCodex/transport с решением bounded pagination.\n"
p=Path("wiki/database/retailcase_ni022_prepared_row_move_20261014.md");s=p.read_text(encoding="utf-8")
s=s.replace("PREPARED, применение ещё не подтверждено.","INSTALLED; применение, реальные перенос/привязки/погрузка/выезд подтверждены отчётом44.")
files[str(p)]=s+"\n## Итог1291\n006_fullpal_scope установлен: обе реальные привязки прошли текущую проверку задания; USER_ERRORS=[],INVALID=[].007_current_root — source mirror с актуальной спецификацией, не повторное применение. [Отчёт44](../../"+report+").\n"
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");d=json.loads(p.read_text(encoding="utf-8"));d["planRevision"]=59;d["currentSprint"]="NI04.2"
d["firstChange"]="B01 retained order2135/wave559/trip33571 completed dev FULL_PALLET path:36EA shipped,2places departed,waveDONE. Continue B02 existing CASE/marking flows; NI08.1 explicit scope-to-norm mapping; Claude C-0005 finance basis."
for item in d["deliveryBatches"]:
 if item["id"]=="B01":item["verifiedScenario"]="FULL_PALLET unmarked dev end-to-end order2135/trip33571, report44; other applicable variants remain open"
 if item["id"]=="B02":item["status"]="in_progress_existing_baseline"
for item in d["increments"]:
 if item["id"] in ["NI02.2","NI03.3","NI05.2"]:
  item.setdefault("implementedSlices",[]).append("B01 report44: existing ST row layout/physical bindings/36EA shipment/2-place departure/wave559 DONE; own dev full-pallet path, no full sprint acceptance.")
files[str(p)]=json.dumps(d,ensure_ascii=False,indent=2)+"\n"
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.md");s=p.read_text(encoding="utf-8").replace("Редакция 58","Редакция 59")
start=s.index("Текущий B01/NI02.2:");end=s.index("\n\nClaude",start)
s=s[:start]+"B01: заказ2135 прошёл полный dev-путь36EA от приёмки до выезда33571 и завершения волны559. Согласование существующей укладки, привязки паллет, погрузка и повтор выезда подтверждены. [Отчёт44](../../../"+report+"). Следующий блок B02/NI04.2–NI04.3: способы отбора и маркировка. Остальные применимые варианты B01 и внешняя приёмка остаются открыты."+s[end:]
s=s.replace("Claude передал UI-части NI07.2","Claude передал UI-части NI07.1 (основания счёта), NI07.2")
files[str(p)]=s
p=Path("wiki/index.md");files[str(p)]="- [B01 завершённый dev-проход1291](components/retailcase_b01_departure_20261014.md):36EA/2места/33571DEPARTED/559DONE/отчёт44; план59, далееB02. Это актуализирует промежуточные записи1266–1275 ниже.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md");files[str(p)]=p.read_text(encoding="utf-8")+"\n- 2026-10-14 ·1291: B01 полный dev-проход2135 до выезда33571/волны559DONE; отчёт44/screens77–81; миграции1265/006 и runtime mirror, current warehouse delivery scope, plan59/B02. Independent/external/full-sprint acceptance не заявлена; SQL available-sts backlogCodex.\n"
print(json.dumps(files,ensure_ascii=True))
