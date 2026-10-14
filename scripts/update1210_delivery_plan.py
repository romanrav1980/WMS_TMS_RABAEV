"""Update the working delivery plan, preserving revision57 and all source evidence."""
import json
from pathlib import Path
root=Path("wiki/requirements/retailcase_delivery_v55")
path=root/"implementation_plan.json"
plan=json.loads(path.read_text(encoding="utf-8"))
assert plan["planRevision"]==57,"Reconcile current revision before updating"
rows=[
("NI01.1","Приёмка по SAP","Довести рабочий путь XML → основание → паллеты → задания размещения; применять существующие подсказки укладки и историю изменений."),
("NI02.1","Автоматическая подготовка СТ","Сохранить готовый расчёт и общий ORDERS/SBORKA writer; использовать его результат в сквозном сценарии."),
("NI02.2","Допуск заказа и ограничения рейса","Показать плановый тип от адресата; переопределение при сборке; связать сроки сборки/ворота и существующее назначение рейса."),
("NI03.1","Доступность и резервы","Использовать проверенный общий допуск P−H, партии, сроки и доступность ячеек; карантин блокируется ячейками."),
("NI03.2","Исполнение складских заданий","Довести операторский путь частичного исполнения, продолжения, недостачи и смены исполнителя через текущих владельцев."),
("NI03.3","Исполнение заказа и волны","В одном рабочем месте показать факт комплектации, оставшееся количество, блокирующую причину и следующее действие."),
("NI04.1","Матрёшка грузовых мест","Довести общий UI вложенных CASE/HU, вскрытия, перепаковки и движения верхнего места с сохранением состава."),
("NI04.2","Способы комплектации","Закрыть подтверждённые пробелы UI коробочного, поштучного, весового отбора и pick-by-line; сохранить существующие алгоритмы."),
("NI04.3","Маркировка и Track & Trace","Довести работу с QR единицы/агрегацией, настройками SKU и локальным lifecycle; реальный государственный ACK учитывать отдельно."),
("NI05.1","Контроль и допуск","Довести контроль состава/веса, исправление и повторный допуск текущей версии через существующий QC."),
("NI05.2","Экспедиция, погрузка и выезд","Довести единый UI staging → ворота → физическая погрузка → выезд; сохранить готовые проверки типа, температуры и возврата до выезда."),
("NI05.3","Приёмка магазина","Довести водительский/магазинный путь количеств, применимых весов/фото, отказа и расхождения."),
("NI06.1","Два плеча межскладского потока","Довести общий UI отправления, консолидации, целевой приёмки/размещения и следующего плеча; готовые количественные механизмы сохранить."),
("NI06.2","Возвраты и расследования","Довести согласованный путь магазин → решение → возврат/брак/поставщик с партиями, кодами и SAP-основанием."),
("NI06.3","Оборотная тара","Довести магазинный/водительский UI выдачи, двухстороннего возврата, повреждений и долгов через существующий баланс."),
("NI07.1","Расчёты и биллинг","Довести периодные фактические источники и рабочий путь нормативов, допрасходов, согласования и счетов; готовый биллинг сохранить."),
("NI07.2","Сверка и закрытие дня","Довести общий экран незавершённых обязательств, физических мест, P/H, маркировки и решений; ACK показывать отдельно."),
("NI08.1","Прогноз и рекомендации","Довести объяснимые рекомендации ресурсов/слотов и единый ручной/автоматический допуск через существующие VRP, карту и Ганту.")
]
batches=[
("B01","Заказ SAP → СТ → рейс → склад → погрузка",["NI01.1","NI02.1","NI02.2","NI03.1","NI03.2","NI03.3","NI04.1","NI05.1","NI05.2"],"Оператор проходит весь путь в интерфейсе; физический товар проводится единственным ядром; сканы, версии и повтор сохраняются."),
("B02","Способы отбора и маркированный товар",["NI04.2","NI04.3"],"Тот же путь работает для применимых способов отбора и профилей маркировки SKU; QR единицы не заменяется EAN."),
("B03","Доставка, магазинная приёмка и возврат",["NI05.3","NI06.2"],"Водитель и магазин подтверждают факт; расхождение ведёт к решению и возврату без повторного списания."),
("B04","Межскладской поток двух плеч",["NI06.1"],"Отправление, целевая приёмка/размещение и следующее плечо сохраняют исходные партии, коды и обязательства."),
("B05","Оборотная тара",["NI06.3"],"Выдача и подтверждённый возврат объясняют текущий баланс и долг каждого участника."),
("B06","Расчёты и закрытие дня",["NI07.1","NI07.2"],"Фактические операции отражаются в расчётах; экран сверки объясняет незакрытые обязательства."),
("B07","Прогноз и рекомендации",["NI08.1"],"Предложения ресурсов и плана объясняются фактом исполнения и утверждаются пользователем.")
]
assert sorted(i for _,_,ids,_ in batches for i in ids)==sorted(i for i,_,_ in rows)
byid={i["id"]:i for i in plan["increments"]}
verified={"NI03.1","NI02.1"}
for ident,title,remaining in rows:
 inc=byid[ident]
 inc["deliveryCodeStatus"]="targeted_dev_verified" if ident in verified else "partially_implemented"
 inc["remainingDeliveryWork"]=remaining
 inc["deliveryBatch"]=next(code for code,_,ids,_ in batches if ident in ids)
 inc["externalAcceptanceStatus"]="real_exchange_pending" if ident in {"NI01.1","NI04.3"} else "applicable_external_equipment_acceptance_not_confirmed"
 inc["pilotStatus"]="not_confirmed"
 inc["independentReviewStatus"]="not_confirmed"
ni02=byid["NI02.2"]
ni02["implementedSlices"]+=["1206 explicit whole STOCK pallet type via existing Root zero goods effect; physical LOAD retained proof;1207 API read/UI wired; browser type write pending","1208–1209 recipient default connected to existing planning capacity; store beats general client; actual CASE beats planned default; rollback2trolley→2EU→unknown"]
ni02["changeRequired"]="Довести UI планового типа адресата/явного переопределения при сборке и deadline сборки/ворота; сохранить существующее назначение и физические guards."
byid["NI05.2"]["implementedSlices"]+=["1168–1207 physical thermal/load/departure and normative TOP type through existing Root and scoped UI; no new stock writer; retained whole STOCK loading proof"]
stream=next(s for s in plan["sprints"]if s["id"]=="NI02")
stream["pendingSlices"]=[ni02["changeRequired"],"Реальные нормы, внешний ERP обмен и промышленный пилот учитываются отдельно от готовности локального кода."]
stream["changeRequired"]=ni02["changeRequired"]
plan["planRevision"]=58
plan["date"]="2026-10-14"
plan["currentSprint"]="NI02.2"
plan["currentStream"]="NI02"
plan["firstChange"]="Show recipient planned pallet type and explicit assembly override through existing UI; complete B01 end-to-end using existing WMS/TMS owners."
plan["currentSprintMeaning"]="Текущий стык B01: тип адресата → фактическая сборка → проверка рейса; не новый TMS allocator."
plan["activeExecutionOrder"]=[ident for _,_,ids,_ in batches for ident in ids]
plan["deliveryBatches"]=[{"id":code,"title":title,"incrementIds":ids,"businessResult":result,"status":"in_progress" if code=="B01" else "queued_existing_baseline"}for code,title,ids,result in batches]
plan["codeVerifiedIncrementIds"]=sorted(verified)
plan["readinessAxes"]=["code","independent_review","external_exchange_and_equipment","production_pilot"]
plan["verificationPolicy"].update({"functionalShareMinimum":0.8,"reportCadence":"one_completed_end_to_end_block","checks":"changed_business_effect_no_double_posting_material_refusal","fullChecks":"before_release","externalAcceptanceBlocksFurtherCode":False})
plan["palletTypePolicy"]={"plannedSource":"RRL_CUSTOMER_PALLET_TYPE_RULE","priority":["recipient_store_rule","general_customer_rule"],"actualOverride":"explicit_at_assembly","capacitySource":"actual_type_when_confirmed_else_planned_type","newAutomaticEuroFallback":False}
plan["deliveryEstimate"]={"status":"not_measured","previous80To160Hours":"withdrawn_unreliable","nextEstimate":"after_B01_remaining_work_reconciliation"}
lines=["# RETAILCASE: список спринтов и план реализации","", "Редакция58 · 14.10.2026 · 18 спринтов в8 направлениях и7 сквозных блоках.","","## Правила исполнения","","Минимум80% усилий на функционал. Перед новой реализацией использовать существующих владельцев WMS/TMS. Поставка — законченный бизнес-сценарий с рабочим интерфейсом, адресной проверкой и одним отчётом/скриншотами на блок.","","Готовность кода, независимое ревью, реальная внешняя интеграция/оборудование и промышленный пилот учитываются отдельно. Неподтверждённые внешние результаты не объявляются завершёнными; их ожидание не блокирует дальнейшую разработку кода. Обязательный runtime gate внешней системы сохраняется по применимости товара.","","## Текущий результат","","NI03.1 и NI02.1 имеют адресно подтверждённую dev-реализацию. Остальные спринты содержат работающие части; таблица ниже показывает доведение этих частей до целого результата, а не разработку всего заново. Полная независимая/промышленная приёмка не заявлена.","","Текущий NI02.2: серверная проверка уже использует тип адресата, для CASE — фактический тип. Целая STOCK-паллета сохраняет физический тип через единое ядро без изменения количества. Следующий шаг — показать плановый тип в существующей сборке и дать явно переопределить фактический тип.","","## Очерёдность сквозных блоков",""]
for code,title,ids,result in batches:
 lines += [f"### {code}. {title}","",f"Спринты: {', '.join(ids)}.", "",result,""]
lines+=["Порядок блоков задаёт приоритет доведения функций; исходные зависимости спринтов сохраняются в JSON. Внутри B01 уже готовые базовые зависимости используются повторно. Применимые локальные правила маркировки действуют с первого блока.","","## Полный список18 спринтов","","| Спринт | Результат | Код сейчас | Что довести |","|---|---|---|---|"]
for ident,title,remaining in rows:
 lines.append(f"| {ident} | {title} | {'Dev подтверждён' if ident in verified else 'Частично реализован'} | {remaining} |")
lines+=["","## Непосредственная последовательность B01","","1. Плановый тип паллеты из настроек адресата → явное переопределение в сборке; фактический тип передаётся в контроль и погрузку.","2. Сохранённая подготовка СТ → прежний выбор/назначение рейса; текущие тара, температура и сроки сборки/ворота показываются оператору.","3. Существующая волна/задания → частичное исполнение и оставшееся количество → CASE/HU → контроль версии.","4. Staging/ворота → погрузка → выезд, с повтором той же команды при неизвестном результате.","5. Один показ рабочего сквозного пути, адресные проверки изменённых эффектов и один отчёт. Выявленные пробелы фиксировать внутри блока; не создавать новые подсистемы без подтверждения необходимости.","","## Учёт приёмки и сроков","","Для каждого спринта JSON хранит deliveryCodeStatus, independentReviewStatus, externalAcceptanceStatus и pilotStatus. Калибровка реальных нормативов и внешние ACK остаются отдельными фактами. Старые статусы/счётчики завершения сохранены для совместимости и не означают промышленную готовность.","","Надёжная календарная оценка пока не установлена. Предыдущие80–160часов не являются обещанием. Следующая оценка — по конкретному остатку B01.","","## Источники","","- [Машиночитаемый план58](implementation_plan.json): зависимости, исходные anchors, выполненные slices и новые оси готовности.","- [История плана до редакции57](implementation_history_r57.md): сохранена без удаления прежних результатов.","- [Все363 сценария](execution/execution_plan.json): объём требований не сокращён.","- [Правила исполнения](../../concepts/retailcase_execution_delivery_rules.md).","- [Тип адресата1209](../../database/retailcase_ni022_recipient_floor_20261014.md), [отчёт39](../../../reports/retailcase/2026-10-13/39-recipient-pallet-type-report.md).",""]
files={str(path):json.dumps(plan,ensure_ascii=False,indent=2)+"\n",str(root/"implementation_plan.md"):"\n".join(lines)}
history=root/"implementation_history_r57.md"
assert not history.exists(),"Preserve existing history"
files[str(history)]=(root/"implementation_plan.md").read_text(encoding="utf-8")
print(json.dumps(files,ensure_ascii=True))
