# Заполненный предварительный опросник: WMS

Версия 1.0 · исследование 16.09.2026 · 48 вопросов × 9 продуктов = 432 ответов.

**Не ответы вендоров и не итоговый рейтинг.** П — опубликована базовая возможность в подписи; Ч — только частичное/соседнее покрытие; НД — достаточных данных в просмотренных источниках нет. Ни П, ни Ч не подтверждают все подпункты вопроса или успешное демо NIKORA. [Полная методика](evaluation_method.md). Для каждой НД требуется письменный ответ и выполнение теста соответствующей строки [опросника](questionnaire_wms.md).

В каждой клетке с П/Ч ссылка ведёт на конкретный первичный источник. Оценка реализации S0/C/E/D/P/N и числовой балл ещё не установлены: публичные данные не позволяют честно заполнить их вместо поставщика.

## Состав сравнения

Основные: SAP EWM, Infor WMS, Manhattan Active WM (на текущей странице также ActiveWarehouse), AXELOT WMS X5. Дополнительные пять: Blue Yonder, Oracle, Infios, EPG LFS, Mecalux Easy WMS. Все пять перечислены в публичном [abstract Gartner MQ WMS 2026](https://www.gartner.com/en/documents/7780053), опубликованном 29.04.2026. AXELOT в этом списке не указан; сравнивается по запросу заказчика. Положение по осям/квадрантам и закрытые оценки Gartner не воспроизводятся.

*Infios WMS — предварительная оценка публичного портфеля: требуется выбрать конкретный продукт, поколение и редакцию. Нельзя сложить возможности разных решений портфеля и объявить их одной лицензией.*

## Запрошенные системы

| ID / предмет вопроса | Вес | SAP EWM | Infor WMS | Manhattan Active WM | AXELOT WMS X5 |
|---|---:|---|---|---|---|
| W01 Площадки и владельцы | 2 | [П владельцы][SW] | [П sites/owners][IW] | НД | [Ч topology/owners][AW] |
| W02 Артикулы и упаковки | 2 | НД | НД | НД | [Ч упаковки][AW] |
| W03 Адреса магазинов | 2 | НД | НД | НД | НД |
| W04 Топология склада | 2 | НД | [Ч bins/3D][IW] | [Ч digital twin][MW] | [П топология][AW] |
| W05 Профиль товара и клиента | 2 | НД | [Ч rotation][IW] | НД | [Ч ограничения][AW] |
| W06 ASN и поставки | 2 | [П ASN][SW] | [Ч receiving][IW] | [Ч supplier portal][MW] | [П ожидаемый приход][AW] |
| W07 Доверительная приёмка | 2 | НД | НД | НД | [Ч этапная приёмка][AW] |
| W08 Неполные коробки | 2 | НД | НД | НД | [Ч расхождения][AW] |
| W09 Входное качество | 2 | НД | [П QC][IW] | НД | [П карантин][AW] |
| W10 Размещение и прямой поток | 2 | [Ч crossdock][SW] | [П flowthrough][IW] | НД | [П размещение][AW] |
| W11 Учёт и резервы | 2 | [Ч stock][SW] | [Ч inventory][IW] | [Ч inventory][MW] | [Ч статусы][AW] |
| W12 FEFO и прослеживаемость | 3 | [Ч партии][SW] | [Ч rotation][IW] | НД | [П партии/сроки][AW] |
| W13 Плавающий вес | 3 | [П catch weight][SW] | НД | НД | НД |
| W14 Инвентаризация | 2 | [П cycle count][SW] | НД | НД | [Ч пересчёт][AW] |
| W15 Корректировки и причины | 2 | [Ч движения][SW] | НД | НД | [Ч движения][AW] |
| W16 Заказы и волны | 3 | [П волны][SW] | [П waves][IW] | [П Order Streaming][MW] | [П волны][AW] |
| W17 Пополнение под волну | 3 | НД | [П replenishment][IW] | [Ч slotting][MW] | [П пополнение][AW] |
| W18 Методы комплектации | 2 | [Ч pick/pack][SW] | [Ч picking][IW] | [П multichannel][MW] | [Ч отбор][AW] |
| W19 Маршрут и store-friendly | 2 | НД | НД | НД | [Ч маршруты][AW] |
| W20 Исключения отбора | 2 | НД | НД | НД | [Ч недостача][AW] |
| W21 Slotting | 2 | НД | НД | [П slotting][MW] | НД |
| W22 Два прохода сканирования | 3 | НД | НД | НД | НД |
| W23 Весовая проверка | 2 | НД | НД | НД | НД |
| W24 Осмотр и допуск | 2 | НД | [Ч QC][IW] | НД | [Ч контроль][AW] |
| W25 Версия состава | 2 | НД | НД | НД | НД |
| W26 VAS и фасовка | 1 | [П VAS][SW] | [П VAS][IW] | НД | НД |
| W27 Внешние грузоместа | 3 | НД | [Ч LPN][IW] | НД | [Ч грузоместа][AW] |
| W28 Линии консолидации | 3 | [Ч crossdock][SW2] | [Ч crossdock][IW] | НД | [Ч консолидация][AW] |
| W29 Агрегация HU | 2 | НД | [Ч mixed pallets][IW] | НД | НД |
| W30 Разделение по шву | 2 | НД | НД | НД | НД |
| W31 Перепаковка и дробление | 2 | НД | [Ч mixed pallets][IW] | НД | НД |
| W32 Физические факты | 2 | НД | НД | НД | НД |
| W33 Погрузка по плану | 2 | НД | НД | НД | [Ч отгрузка][AW] |
| W34 Возвраты товара | 2 | НД | НД | НД | [Ч возвраты][AW] |
| W35 Оборотная тара | 2 | НД | НД | НД | НД |
| W36 3PL и показатели | 2 | [Ч multiowner][SW] | [Ч owners][IW] | [Ч performance][MW] | НД |
| W37 Начальник склада | 2 | [Ч labor][SW] | [Ч visibility][IW] | [П facility visibility][MW] | [Ч диспетчеризация][AW] |
| W38 Сборщик и контролёр | 2 | [Ч voice][SW] | [Ч RF/voice][IW] | [Ч workflows][MW] | [Ч ТСД][AW] |
| W39 Ричтрак и диспетчер | 2 | [Ч labor][SW] | [Ч tasks][IW] | [Ч resource orchestration][MW] | [Ч задания][AW] |
| W40 Оборудование и разрыв связи | 2 | НД | [Ч RF][IW] | [Ч mobile][MW] | [Ч online ТСД][AW] |
| W41 XML API и сверка | 3 | НД | [Ч platform integration][IW] | [Ч API][MW] | [Ч обмен][AW] |
| W42 Наблюдаемость обмена | 2 | НД | НД | НД | НД |
| W43 Интеграция TMS и событий ERP | 2 | [Ч docks][SW] | НД | [Ч unified logistics][MW] | [Ч TMS обмен][AW] |
| W44 Автоматизация и локальные адаптеры | 1 | [Ч automation][SW] | [П automation][IW] | [П WES][MW] | [Ч автоматизация][AW] |
| W45 Безопасность и полномочия | 2 | НД | НД | [Ч audit][MW] | НД |
| W46 Надёжность и нагрузка | 2 | НД | НД | [Ч cloud updates][MW] | НД |
| W47 Обновления и переносимость | 1 | [Ч варианты deployment][SW] | [Ч extensibility][IW] | [П microservices][MW] | [Ч открытый код][AW2] |
| W48 Внедрение и поддержка | 1 | НД | НД | НД | НД |

## Пять дополнительных систем

| ID / предмет вопроса | Вес | Blue Yonder WMS | Oracle WMS Cloud | Infios WMS* | EPG LFS | Mecalux Easy WMS |
|---|---:|---|---|---|---|---|
| W01 Площадки и владельцы | 2 | НД | [П multi-site][OW] | НД | [Ч multiowner][EW] | [П multiowner/site][XW] |
| W02 Артикулы и упаковки | 2 | НД | НД | НД | НД | НД |
| W03 Адреса магазинов | 2 | НД | НД | НД | НД | НД |
| W04 Топология склада | 2 | НД | НД | НД | [П storage strategies][EW] | НД |
| W05 Профиль товара и клиента | 2 | НД | НД | НД | [П restrictions][EW] | НД |
| W06 ASN и поставки | 2 | НД | [Ч inbound][OW] | [Ч receiving][FW] | [Ч receipt][EW] | [Ч receiving][XW] |
| W07 Доверительная приёмка | 2 | НД | НД | НД | НД | НД |
| W08 Неполные коробки | 2 | НД | НД | НД | НД | НД |
| W09 Входное качество | 2 | НД | НД | НД | [П quality][EW] | НД |
| W10 Размещение и прямой поток | 2 | НД | [П flowthrough][OW] | [Ч put-away][FW] | [П crossdock][EW] | [Ч crossdock][XW2] |
| W11 Учёт и резервы | 2 | [Ч inventory][BW] | [Ч inventory][OW] | [Ч inventory][FW] | [П stock states][EW] | [Ч stock][XW] |
| W12 FEFO и прослеживаемость | 3 | НД | [П lot/batch][OW] | НД | [П lot/BBD][EW] | [Ч traceability][XW2] |
| W13 Плавающий вес | 3 | НД | НД | НД | НД | НД |
| W14 Инвентаризация | 2 | НД | НД | НД | [Ч inventory][EW] | НД |
| W15 Корректировки и причины | 2 | НД | НД | НД | НД | НД |
| W16 Заказы и волны | 3 | [Ч orchestration][BW] | [П waves][OW2] | НД | [Ч work packages][EW] | НД |
| W17 Пополнение под волну | 3 | НД | [Ч replenishment][OW2] | НД | [П replenishment][EW] | НД |
| W18 Методы комплектации | 2 | [Ч operations][BW] | [П task grouping][OW] | [Ч pick/pack/ship][FW] | [П multiorder][EW] | [П omnichannel][XW] |
| W19 Маршрут и store-friendly | 2 | [Ч load building][BW] | [П store-friendly][OW] | НД | [Ч pick route][EW] | НД |
| W20 Исключения отбора | 2 | НД | НД | НД | НД | НД |
| W21 Slotting | 2 | [П slotting][BW] | НД | [П slotting module][FW] | [П ABC placement][EW] | НД |
| W22 Два прохода сканирования | 3 | НД | НД | НД | НД | НД |
| W23 Весовая проверка | 2 | НД | [Ч scales][OW] | НД | НД | НД |
| W24 Осмотр и допуск | 2 | НД | НД | [Ч inspection module][FW] | [Ч quality][EW] | [Ч food control][XW2] |
| W25 Версия состава | 2 | НД | НД | НД | НД | НД |
| W26 VAS и фасовка | 1 | НД | [П VAS][OW] | НД | [П repack][EW] | НД |
| W27 Внешние грузоместа | 3 | НД | НД | НД | НД | НД |
| W28 Линии консолидации | 3 | НД | [П put-to-store][OW] | НД | [Ч crossdock][EW] | [Ч crossdock][XW2] |
| W29 Агрегация HU | 2 | НД | НД | НД | НД | НД |
| W30 Разделение по шву | 2 | НД | НД | НД | НД | НД |
| W31 Перепаковка и дробление | 2 | НД | НД | НД | [Ч repack][EW] | НД |
| W32 Физические факты | 2 | НД | [Ч inbound/outbound][OW] | НД | НД | НД |
| W33 Погрузка по плану | 2 | НД | [Ч multistop loads][OW] | [Ч ship][FW] | [П load scan][EW] | НД |
| W34 Возвраты товара | 2 | [П returns][BW] | [П returns][OW] | НД | НД | НД |
| W35 Оборотная тара | 2 | НД | НД | НД | [Ч empties accounts][EW] | НД |
| W36 3PL и показатели | 2 | [Ч workbench][BW] | [Ч 3PL][OW] | [Ч analytics][FW] | [Ч owner accounts][EW] | [Ч analytics][XW] |
| W37 Начальник склада | 2 | [П resource forecast][BW] | [Ч wave insights][OW] | [Ч reporting][FW] | НД | [Ч dashboards][XW] |
| W38 Сборщик и контролёр | 2 | [Ч labor][BW] | НД | [Ч voice][FW] | [П voice/RF][EW] | [Ч UI languages][XW] |
| W39 Ричтрак и диспетчер | 2 | [П resources][BW] | [Ч tasks][OW] | [Ч labor][FW] | [Ч transport control][EW] | [Ч labor module][XW] |
| W40 Оборудование и разрыв связи | 2 | НД | НД | НД | НД | [Ч RF equipment][XW] |
| W41 XML API и сверка | 3 | НД | НД | [Ч ERP][FW] | НД | [Ч ERP integration][XW] |
| W42 Наблюдаемость обмена | 2 | НД | НД | НД | НД | НД |
| W43 Интеграция TMS и событий ERP | 2 | [Ч yard][BW] | [Ч logistics][OW] | [Ч suite][FW] | НД | НД |
| W44 Автоматизация и локальные адаптеры | 1 | [П robotics][BW] | [П WCS][OW] | [П WCS/AMR][FW] | [Ч automation][EW] | [П automation][XW] |
| W45 Безопасность и полномочия | 2 | НД | НД | НД | НД | НД |
| W46 Надёжность и нагрузка | 2 | [Ч scale][BW] | [Ч cloud][OW] | НД | НД | [Ч SaaS][XW] |
| W47 Обновления и переносимость | 1 | НД | [Ч updates][OW] | [Ч cloud/on-prem][FW] | НД | [П cloud/on-prem][XW] |
| W48 Внедрение и поддержка | 1 | НД | НД | НД | НД | НД |

## Архитектура предложений и адресные вопросы

| Продукт | Что установлено публично | Что запросить именно для NIKORA |
|---|---|---|
| SAP EWM | Basic/advanced, embedded S/4HANA или отдельное развёртывание; catch weight, waves, advanced crossdock [SW]. Merchandise distribution имеет отдельную документацию [SW2]. | Точная ERP-версия вместо слова «HANA», лицензии advanced/TM/yard; D02–D07; короткий RF-процесс и replenishment под волну. |
| Infor WMS | Multi-site/owner, flowthrough, wave/cluster picking, отдельные labor/VAS-возможности и облачная платформа [IW]. | D02/D04/D07 для фактического веса и lineage; состав platform/integration лицензий; не заменять демонстрацию картинкой 3D. |
| Manhattan Active WM | Cloud-native microservices, Order Streaming, WES, labor, объединённое исполнение [MW]. | Точная редакция, SLA связи, update-regression, экспорт; доказать D05–D10 с чужими WMS, а не только с Active TM. |
| AXELOT WMS X5 | Процессные стратегии и ТСД, платформа 1С:Предприятие 8.3; заявлен открытый код [AW2]. | В договоре разграничить настройку/изменение конфигурации и обновления; D02/D07/D12, Georgian UI и работа при разрыве связи. Открытый код не доказывает производительность. |
| Blue Yonder | WM, resources, slotting, robotics, load building и returns представлены как возможности решения [BW]. | Ведомость обязательных модулей; dual-UoM, два прохода/вес и произвольный repack; границы локального исполнения при недоступности облака. |
| Oracle WMS Cloud | Store-friendly waves, put-to-store/flowthrough, multi-stop allocations и WCS [OW], настройки волн документированы [OW2]. | Не путать Oracle WMS Cloud с текущей нашей БД Oracle; D07/D10, API limits и точная политика версии HU. |
| Infios WMS | Модульный портфель с labor/voice/slotting/inspection и вариантами размещения [FW]. | Сначала название конкретного продукта/версии; затем ответ на каждую строку. Ссылки на другой WMS портфеля не засчитываются. |
| EPG LFS | Модульные складские стратегии, партии/сроки, replenishment, crossdock, empties [EW]. | Проверить кг+шт., assetId vs empties balance, две формы split и подключение сторонней TMS; перечень LFS/DOCK/WFM/voice компонентов. |
| Mecalux Easy WMS | Multi-owner/site, cloud/on-prem, ERP/automation и омниканальность [XW]. | Grocery catch weight/FEFO/QA на реальных данных, не только кейс автоматизированного склада; exact SLA/экспорт и внешняя головная TMS. |

## Вывод по WMS

Нет достаточных оснований назвать одного победителя. Каталожные различия помогают выбрать демонстрации, но риск NIKORA находится в частичных коробах/весе, пополнении, идентичности HU, качестве и стыках. Для полного сценария «матрёшка → шов → произвольный repack → повторный контроль» публичного доказательства всех инвариантов в просмотренных материалах нет ни по одному продукту.

Рекомендация — сначала одинаковая квалификация четырёх запрошенных продуктов; расширять короткий список из пяти дополнительных по наличию команды в регионе и готовности выполнить D01–D12. Не считать прежний негативный опыт участника встречи универсальным свойством нынешнего продукта.

## Первичные источники таблицы

[SW]: https://www.sap.com/products/scm/extended-warehouse-management/features.html "SAP EWM: функции"
[SW2]: https://help.sap.com/docs/PRODUCT_ID/9832125c23154a179bfa1784cdc9577a/c9ef2498ef494449ada4cccb97c5ccca.html "SAP EWM: Merchandise Distribution Cross-Docking, 2025 FPS01"
[IW]: https://www.infor.com/en-gb/solutions/scm/warehouse-management-system "Infor WMS: функции"
[MW]: https://www.manh.com/solutions/supply-chain-management-software/warehouse-management "Manhattan ActiveWarehouse / Active WM"
[AW]: https://www.axelot.ru/product/axelot-wms-x5/functionality/ "AXELOT WMS X5: функции"
[AW2]: https://www.axelot.ru/product/axelot-wms-x5/ "AXELOT WMS X5: продукт и платформа"
[BW]: https://blueyonder.com/solutions/warehouse-management "Blue Yonder Warehouse Management"
[OW]: https://www.oracle.com/scm/logistics/warehouse-management/ "Oracle Fusion Cloud Warehouse Management"
[OW2]: https://docs.oracle.com/en/cloud/saas/warehouse-management/26a/owmim/waving-overview.html "Oracle WMS 26A: Waving Overview"
[FW]: https://www.infios.com/en/supply-chain-solutions/warehouse-management-systems "Infios: портфель Warehouse Management Systems"
[EW]: https://www.epg.com/gb/logistics-software/warehouse-management-system-lfswms/lfs-modules/ "EPG LFS: модули"
[XW]: https://www.mecalux.com/software/warehouse-management-system-wms "Mecalux Easy WMS"
[XW2]: https://www.mecalux.com/clients/sud-fresh-food-traceability "Mecalux: Sud-Fresh, food traceability"

Сведения о проектах других сетей и ограничения источников — [реестр](sources_and_retail_practices.md). Утверждения о доступности в Грузии, цене, поддержке и лицензиях пока требуют письменного подтверждения.
