# Заполненный предварительный опросник: TMS

Версия 1.0 · исследование 16.09.2026 · 40 вопросов × 9 продуктов = 360 ответов.

**Не ответы вендоров и не итоговый рейтинг.** П — опубликована базовая возможность в подписи; Ч — только частичное/соседнее покрытие; НД — достаточных данных в просмотренных источниках нет. Ни П, ни Ч не подтверждают все подпункты вопроса или успешное демо NIKORA. [Полная методика](evaluation_method.md). Для каждой НД требуется письменный ответ и выполнение теста соответствующей строки [опросника](questionnaire_tms.md).

В каждой клетке с П/Ч ссылка ведёт на конкретный первичный источник. Оценка реализации S0/C/E/D/P/N и числовой балл ещё не установлены: публичные данные не позволяют честно заполнить их вместо поставщика.

## Состав сравнения

Основные: SAP TM (не EWM), Infor Nexus Global TMS (не Infor WMS), Manhattan Active TM, AXELOT TMS. Дополнительные пять: Blue Yonder, Oracle OTM, Infios TMS, e2open, Alpega. Они перечислены в публичном [abstract Gartner MQ TMS 2026](https://www.gartner.com/en/documents/7645129), опубликованном 30.03.2026. Infor и AXELOT в опубликованном списке данного отчёта не указаны; включены по запросу пользователя. Отсутствие в списке не означает отсутствия продукта или непригодности.

Списки WMS и TMS намеренно различаются: наличие Mecalux/EPG в WMS MQ не доказывает наличие их TMS в TMS MQ. Infios на своей странице идентифицирует TMS как развитие MercuryGate; соответствие конкретной предлагаемой редакции проверяется отдельно.

## Запрошенные системы

| ID / предмет вопроса | Вес | SAP TM | Infor Nexus TMS | Manhattan Active TM | AXELOT TMS |
|---|---:|---|---|---|---|
| T01 Сеть и календари | 2 | НД | НД | НД | [Ч география][AT] |
| T02 Заказы и версии | 2 | [Ч orders][ST2] | [Ч orders][IT] | [Ч orders][MT] | [П заявки][AT] |
| T03 План и факт объёма | 2 | НД | НД | НД | НД |
| T04 Объём и совместимость | 2 | [Ч load planning][ST] | [Ч containers][IT] | [Ч loads][MT] | [П совместимость][AT] |
| T05 Транспортные ресурсы | 2 | [Ч ресурсы][ST] | НД | [П fleet][MT] | [П парк/экипажи][AT] |
| T06 Многоостановочные маршруты | 3 | [П routing][ST] | [Ч route optimization][IT] | [П routing][MT] | [Ч SCAP][AT] |
| T07 Многоплечевая сеть | 3 | [П multimodal][ST2] | [П multileg][IT] | [П multimodal][MT] | [П multimodal][AT] |
| T08 Обратное расписание | 3 | [Ч planning][ST] | НД | НД | [Ч расписания][AT] |
| T09 Целевая функция и объяснение | 3 | [Ч optimization][ST] | [Ч optimization][IT] | [П optimization][MT] | [Ч оптимизация][AT] |
| T10 Ручной и автоматический план | 3 | [П manual/auto][ST] | [Ч planning][IT] | [Ч continuous planning][MT] | [Ч replan][AT] |
| T11 Объединение по магазину | 3 | [Ч consolidation][ST] | [Ч consolidation][IT] | [Ч consolidation][MT] | [Ч консолидация][AT] |
| T12 Волны, ворота и линии | 3 | [Ч EWM integration][ST2] | НД | [П appointments][MT] | [Ч WMS доки][AT] |
| T13 Шаттлы и readyBy | 3 | [Ч freight planning][ST] | НД | НД | [Ч обеспечение][AT] |
| T14 Порядок операций | 3 | [Ч 3D loading][ST] | НД | [Ч load planning][MT] | [Ч укладка][AT] |
| T15 Опоздания и частичная волна | 3 | НД | НД | [Ч replan][MT] | [Ч исключения][AT] |
| T16 Жизненный цикл рейса | 3 | [Ч execution][ST2] | [Ч execution][IT] | [Ч execution][MT] | [П события рейса][AT] |
| T17 Диспетчер и контроль рисков | 3 | [П map/Gantt][ST] | [П visibility][IT] | [П dispatch][MT] | [П мониторинг][AT] |
| T18 Видимость и телематика | 2 | [Ч visibility][ST] | [П ETA][IT] | [Ч visibility][MT] | [П RTVP ETA][AT] |
| T19 Наёмные перевозчики | 2 | [П carriers][ST2] | [П tendering][IT] | [Ч carrier management][MT] | [П торги/резерв][AT] |
| T20 Водитель и экипаж | 2 | НД | НД | НД | [Ч MOBILE][AT] |
| T21 Приёмка магазина | 2 | НД | НД | НД | [Ч отказы][AT] |
| T22 Возврат и backhaul | 2 | НД | НД | НД | [Ч исключения][AT] |
| T23 Ответственность за тару | 2 | НД | НД | НД | [Ч активы][AT] |
| T24 Грузовые документы | 2 | [П documents][ST2] | [Ч booking][IT] | НД | [П документы][AT] |
| T25 Импорт и мультимодальность | 2 | [П multimodal][ST2] | [П multimodal][IT] | [П multimodal][MT] | [П multimodal][AT] |
| T26 Тарифы и начисления | 2 | [П charges][ST2] | [П rates][IT] | [П rates][MT] | [П тарифы][AT] |
| T27 Аудит счетов | 2 | [П settlement][ST2] | [П audit/pay][IT] | [П settlement][MT] | [Ч взаиморасчёты][AT] |
| T28 Cost-to-serve | 2 | НД | [Ч allocation][IT] | НД | [П себестоимость заявок][AT] |
| T29 Сервис и экологические KPI | 2 | [Ч analytics][ST2] | [Ч analytics][IT] | [Ч sustainability][MT] | [П аналитика][AT] |
| T30 XML ERP master и orders | 3 | [Ч orders][ST2] | [Ч ERP][IT] | НД | [Ч внешние заявки][AT] |
| T31 Четыре исходящих события ERP | 3 | НД | НД | НД | НД |
| T32 Контракт с несколькими WMS | 3 | [Ч EWM][ST2] | [Ч network][IT] | [Ч unified logistics][MT] | [Ч WMS обмен][AT] |
| T33 Надёжная доставка и сверка | 3 | НД | НД | НД | НД |
| T34 Модель границ и груза | 3 | [Ч freight orders][ST2] | НД | [Ч unified model][MT] | [Ч грузоместа][AT] |
| T35 Нагрузка и непрерывность | 3 | НД | НД | [Ч cloud][MT] | НД |
| T36 Безопасность и аудит | 2 | НД | НД | НД | НД |
| T37 Расширения и выход | 2 | [Ч integration][ST2] | [Ч integration][IT] | [Ч extensibility][MT] | [Ч внешние платформы][AT] |
| T38 Команда и retail-приёмка | 3 | НД | НД | НД | НД |
| T39 Пилот и сопровождение | 3 | НД | НД | НД | НД |
| T40 Комплектность предложения | 2 | НД | НД | [Ч editions][MT2] | [Ч компоненты][AT] |

## Пять дополнительных систем

| ID / предмет вопроса | Вес | Blue Yonder TMS | Oracle OTM | Infios TMS | e2open TMS | Alpega TMS |
|---|---:|---|---|---|---|---|
| T01 Сеть и календари | 2 | НД | НД | НД | НД | НД |
| T02 Заказы и версии | 2 | [Ч demand][BT] | [П orders][OT] | [Ч orders][FT] | [Ч orders][ET] | [П order management][LT] |
| T03 План и факт объёма | 2 | НД | НД | НД | НД | НД |
| T04 Объём и совместимость | 2 | [П 3D load][BT] | [Ч load planning][OT] | [Ч capacity][FT] | [Ч load][ET] | [Ч constraints][LT] |
| T05 Транспортные ресурсы | 2 | [Ч fleet][BT] | [П fleet][OT] | НД | НД | НД |
| T06 Многоостановочные маршруты | 3 | [П optimization][BT] | [П planning][OT] | [Ч routing][FT] | [Ч routing][ET] | [Ч routing][LT] |
| T07 Многоплечевая сеть | 3 | [П multimodal][BT] | [П multileg/crossdock][OT] | [П multimodal][FT] | [П multimode][ET] | [П multimode][LT] |
| T08 Обратное расписание | 3 | НД | [Ч planning][OT] | НД | НД | НД |
| T09 Целевая функция и объяснение | 3 | [П modeling][BT] | [П modeling][OT] | [П optimization][FT] | [П optimization][ET] | [П optimization][LT] |
| T10 Ручной и автоматический план | 3 | [Ч scenarios][BT] | [Ч scenarios][OT] | [Ч planning][FT] | [Ч planning][ET] | [Ч planning][LT] |
| T11 Объединение по магазину | 3 | [Ч load building][BT] | [Ч consolidation][OT] | [Ч consolidation][FT] | [П consolidation][ET] | [П consolidation][LT] |
| T12 Волны, ворота и линии | 3 | НД | [Ч dock coordination][OT] | НД | НД | НД |
| T13 Шаттлы и readyBy | 3 | НД | НД | НД | НД | НД |
| T14 Порядок операций | 3 | [Ч 3D load][BT] | НД | НД | НД | НД |
| T15 Опоздания и частичная волна | 3 | [Ч adaptation][BT] | [Ч exceptions][OT] | [Ч rerouting][FT] | [Ч exceptions][ET] | [Ч exceptions][LT] |
| T16 Жизненный цикл рейса | 3 | [Ч execution][BT] | [Ч execution][OT] | [П execution][FT] | [П execution][ET] | [Ч execution][LT] |
| T17 Диспетчер и контроль рисков | 3 | [П manager][BT] | [П visibility][OT] | [П control tower][FT] | [Ч tracking][ET] | [П control tower][LT] |
| T18 Видимость и телематика | 2 | [Ч visibility][BT] | [Ч tracking][OT] | [Ч tracking][FT] | [Ч visibility][ET] | [П ETA][LT] |
| T19 Наёмные перевозчики | 2 | [П procurement][BT] | [П sourcing][OT] | [П tendering][FT] | [П procurement][ET] | [П carrier selection][LT] |
| T20 Водитель и экипаж | 2 | НД | НД | НД | НД | НД |
| T21 Приёмка магазина | 2 | НД | [Ч delivery][OT] | НД | НД | [Ч POD][LT] |
| T22 Возврат и backhaul | 2 | НД | НД | НД | НД | НД |
| T23 Ответственность за тару | 2 | НД | НД | НД | НД | НД |
| T24 Грузовые документы | 2 | НД | НД | НД | НД | НД |
| T25 Импорт и мультимодальность | 2 | [П multimodal][BT] | [П multimodal][OT] | [П multimodal][FT] | [П multimode][ET] | [П multimode][LT] |
| T26 Тарифы и начисления | 2 | [Ч costs][BT] | [П costing][OT] | [П rates][FT] | [П rating][ET] | [Ч rates][LT] |
| T27 Аудит счетов | 2 | НД | [П payables][OT] | [П audit/payment][FT] | [П settlement][ET] | [Ч invoice analytics][LT] |
| T28 Cost-to-serve | 2 | [Ч cost-to-serve][BT] | [Ч allocation][OT] | НД | НД | НД |
| T29 Сервис и экологические KPI | 2 | [П emissions][BT] | [П analytics][OT] | [П analytics][FT] | [П analytics][ET] | [П analytics][LT] |
| T30 XML ERP master и orders | 3 | НД | [Ч orders][OT] | [Ч ERP][FT] | НД | [Ч ERP templates][LT] |
| T31 Четыре исходящих события ERP | 3 | НД | НД | НД | НД | НД |
| T32 Контракт с несколькими WMS | 3 | [Ч interoperability][BT] | [Ч logistics][OT] | [Ч OMS/WMS suite][FT] | [Ч network][ET] | [Ч WMS templates][LT] |
| T33 Надёжная доставка и сверка | 3 | НД | НД | НД | НД | НД |
| T34 Модель границ и груза | 3 | НД | [Ч shipments][OT] | НД | НД | НД |
| T35 Нагрузка и непрерывность | 3 | [Ч scale][BT] | НД | [Ч transaction scale][FT] | НД | [Ч cloud][LT] |
| T36 Безопасность и аудит | 2 | НД | НД | [Ч security claims][FT] | НД | НД |
| T37 Расширения и выход | 2 | [Ч network][BT] | [Ч integration][OT] | [Ч modularity][FT] | [Ч integration][ET] | [Ч API][LT] |
| T38 Команда и retail-приёмка | 3 | НД | НД | НД | НД | НД |
| T39 Пилот и сопровождение | 3 | НД | НД | НД | НД | [Ч rollout/support][LT] |
| T40 Комплектность предложения | 2 | НД | НД | НД | НД | [Ч modular scope][LT] |

## Архитектура предложений и адресные вопросы

| Продукт | Публичный профиль | Главная проверка NIKORA |
|---|---|---|
| SAP TM | Planning/execution/settlement, загрузка и ресурсы [ST], связь с EWM [ST2]. | Несколько НЕ-SAP WMS, PLAN/ACTUAL_ONLY, freeze и реальный POD; SAP ERP сам по себе не устраняет интеграционные работы. |
| Infor Nexus TMS | Global multi-leg/multimodal, network visibility, sourcing, freight audit/payment [IT]. | Доказать развоз собственным парком по магазинам, камеры, низкоуровневые HU-факты и offline POD. Глобальная сеть перевозчиков не равна локальному retail VRP. |
| Manhattan Active TM | Optimization, appointments, fleet/dispatch и cloud extensibility [MT]; редакции различаются [MT2]. | Какая редакция включает fleet/optimization; совместимость с чужими WMS, T03/T11–15 и четыре ERP события. |
| AXELOT TMS | Заявки, ресурсы, события, тарифы; SCAP/MAPS/RTVP/MOBILE упомянуты отдельными компонентами [AT]. | Цена и ответственность за компоненты, фактическая дорожная модель Грузии, сегментная ёмкость и качество replanning. |
| Blue Yonder TMS | Modeling/procurement/planning/load building/manager/network [BT]. | Не заменить timeline WMS общим transport planning; показать backward-readyBy, freeze и target-WMS ACK. |
| Oracle OTM | Multileg/crossdock planning, fleet, network modeling и финансовый контур [OT]. | Указать необходимые cloud modules; same-HU multi-leg custody, target receipt и partial store receipt. |
| Infios TMS | MercuryGate heritage, multimodal planning/execution/rates/audit [FT]. | Подтвердить конкретное fleet/last-mile предложение, совместимость с независимыми WMS и lineage-ссылками. |
| e2open TMS | Shipper TMS для multimode planning/execution/settlement, carrier network [ET]. | Выбрать shipper, а не freight-forwarder конфигурацию; доказать магазинный own-fleet процесс и точность событий. |
| Alpega TMS | Модульный cloud TMS, carrier planning, visibility/POD, ERP/WMS templates [LT]. | Проверить собственный парк, камеры, XML NIKORA и все исключения; готовый шаблон ERP не доказывает точную семантику сообщений. |

## Вывод по TMS

Для задачи головной TMS недостаточно красивой карты и оптимизации пробега. Решающий тест — T03/T08/T11–15/T31–34: план→факт без двойного спроса, обратное расписание, ресурсы кроссдока, frozen plan, подтверждение target WMS и доказанная доставка магазину. Эти комбинации не подтверждены целиком общими продуктовыми страницами.

Запрашивать единое коммерческое предложение на рабочую цепочку: core TMS, solver, карты, telematics, mobile/POD, XML-adapters и support. Отдельные продукты WMS и TMS не обязаны быть одного вендора; обязательна испытанная пара с одним ответственным за каждый стык.

## Первичные источники таблицы

[ST2]: https://learning.sap.com/courses/discovering-sap-s-4hana-transportation-management/understanding-capabilities-of-sap-transportation-management_cf48b4af-36de-411f-b5f2-9e3073fb8a3a "SAP: возможности TM и integration lifecycle"
[ST]: https://www.sap.com/products/scm/transportation-logistics/features.html "SAP TM: функции"
[IT]: https://www.infor.com/mea/solutions/scm/infor-nexus/transportation-management "Infor Nexus Global Transportation Management"
[MT]: https://www.manh.com/solutions/supply-chain-management-software/transportation-management "Manhattan Active TM"
[MT2]: https://www.manh.com/solutions/supply-chain-management-software/activetransportation "Manhattan ActiveTransportation: редакции"
[AT]: https://www.axelot.ru/product/axelot-tms/functionality/ "AXELOT TMS: функции"
[BT]: https://blueyonder.com/solutions/transportation-management "Blue Yonder Transportation Management"
[OT]: https://www.oracle.com/scm/logistics/transportation-management/ "Oracle Transportation Management"
[FT]: https://www.infios.com/en/supply-chain-solutions/transportation-management "Infios Transportation Management, бывший MercuryGate"
[ET]: https://www.e2open.com/logistics/transportation-management "e2open Transportation Management"
[LT]: https://www.alpegagroup.com/en-en/transport-management-system/ "Alpega TMS"

Сведения о проектах других сетей и ограничения источников — [реестр](sources_and_retail_practices.md). Утверждения о доступности в Грузии, цене, поддержке и лицензиях пока требуют письменного подтверждения.
