from pathlib import Path
import json
files={}
report="reports/retailcase/2026-10-13/50-ni062-return-route.md"
files[report]="""# NI06.2 — путь товарного возврата
2026-10-14. Существующее согласование возврата получило сквозную карточку: SAP-документ → рейс вывоза → передача магазином → подпись водителя → складская приёмка → размещение → поставщик/утилизация/исправный возврат.

## Изменение
Delivery владеет новой read model return_progress.py/.sql. Она читает существующие таблицы delivery/inventory в том же Oracle READ ONLY snapshot, что и досье; максимум100 согласований, один batchJSON_TABLE, актуальный RUSERS/store_return_approve + принимающий WARE или GLOBAL_ADMIN. Новых записей/схем/проведения нет.
Для недоступного склада progress явно закрыт, отсутствие доступа не выдаётся за отсутствие приёмки. Поля старого ответа сохранены, approvals[].progress добавлено.
Показываются фактические идентификаторы, партия/источник, срок, ячейка, задание, возвратная СТ и конечный факт. Нельзя принять подготовку СТ за отгрузку или отгрузку за приёмку поставщиком. Внешний ACK отдельно.
Ссылки открывают прежние формы с выбранным складом; автозапросы только GET. Выбор не заполняет сканы и ничего не проводит. Смена исходной приёмки очищает старую цепочку.

## Реальный результат чтения
- STORE383.RECEIPT:c09bc5c0: повреждение1EA → EXRET490.DISPOSE:c09bc5c0; отказ1EA → СТ641481 → EXRET491.LOAD:c09bc5c0. Обе цепочки имеют отдельные складские приёмки и размещения.
- STORE642.RECEIPT:dc1889623c: исправный возврат3EA/исходная партия ORIGINAL_SAP_VERIFIED, задача1066DONE, размещено QK641dc1889623c. Этот старый dev-сценарий уже существовал; новое проведение не создавалось.
- Собственная приёмка B03 STORE.RECEIPT:da46b595-e71c-477b-b0ae-1f3292fdc0c1: согласований нет, пустое состояние показано.
- Переход из карточки поставщика открыл очередь склада38542432. Browser errors=[], business POST=[].
- Пользователю OWN1306_DRIVER без права согласования helper не возвращает складской progress. Это проверка отказа по полномочию; отдельный случай разрешённого согласования чужого склада здесь не выполнялся.

Первый SQL-вариант отклонён Oracle01799 при outer-join с подзапросом; заменён на ограниченный CTE latest_plan + row_number. После исправления реальные API200 и браузерный проход завершены.
Evidence: tmp/read1358.json, tmp/result1361.json, tmp/verify1362.json.
[Возврат поставщику/утилизация](screenshots/92-ni062-return-route.png), [исправный возврат](screenshots/93-ni062-marked-reuse-route.png).
SQL7fgcz9ypbs00a: средние46.538–91.089мс по текущим child cursors, максимум947buffers. Решение delivery: сохранить bounded batch и существующие ключи; без новых индексов, повторный анализ при регулярном>500мс.

Это готовая операторская связка существующих механизмов; реальное новое SAP-сообщение, аппаратура, государственный ACK и независимая приёмка полного NI06.2 не подтверждены.
"""
page="wiki/components/retailcase_ni062_return_route_20261014.md"
files[page]="# NI06.2: сквозное досье возврата\n\n1354–1363. Аддитивный approvals[].progress в прежнем досье; bounded100/current permission+receivingWARE/same snapshot/read-only cross-owner model. UI показывает фактическую цепочку и открывает существующие формы с принимающим складом, не проводит по клику.\n\n[Отчёт50](../../"+report+"). Retained383 disposal/supplier и642 markedREUSE3/DONE1066 реально прочитаны; новые движения не создавались. Native-инварианты и внешняя приёмка не подменены отображением.\n"
p=Path("wiki/components/retailcase_ni062_return_receiving_queue_20261011.md");files[str(p)]=p.read_text(encoding="utf-8")+"\n## Уточнение1363,14октября\nФраза выше об отсутствии positive markedREUSE evidence относится к моменту283. В текущем dev сохранился более поздний REUSE643.RECEIVE:dc1889623c/REUSE643.DONE:dc1889623c,3EA,ORIGINAL_SAP_VERIFIED,task1066DONE; он прочитан через новое досье report50. Этот проход чтения не является новым физическим испытанием или независимой приёмкой.\n"
p=Path("wiki/index.md");files[str(p)]="- [NI06.2: путь возврата1363](components/retailcase_ni062_return_route_20261014.md): единое досье SAP/вывоз/приёмка/размещение/поставщик/утилизация, report50, read-only.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md");files[str(p)]=p.read_text(encoding="utf-8")+"\n- 2026-10-14 ·1363: return progress currentWARE batch100/UI links, retained supplier/disposal/REUSE facts; report50. Уточнено устаревшее отсутствие markedREUSE evidence283. Tare gate1353 PASS738/0cycles/74debt/24tests/обаTS.\n"
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");d=json.loads(p.read_text(encoding="utf-8"));d["planRevision"]=64;d["currentSprint"]="NI04.1";d["firstChange"]="NI06.2 return route dossier delivered (report50); continue nested handling-unit operator composition. Claude C-0008 owns finance basis/expense workflow; ACK pending."
for item in d["increments"]:
 if item["id"]=="NI06.2":
  item.setdefault("implementedSlices",[]).append("1354–1363 existing return dossier + scoped same-snapshot progress/read-only UI links; actual retained supplier/disposal/markedREUSE paths, report50.")
  item["remainingDeliveryWork"]="Сквозное досье и переходы реализованы report50. Довести оставшиеся исключения возврата/расследования по действующим сценариям; реальные SAP/государственные ACK и независимая приёмка отдельно."
files[str(p)]=json.dumps(d,indent=2,ensure_ascii=False)+"\n"
print(json.dumps(files,ensure_ascii=True))
