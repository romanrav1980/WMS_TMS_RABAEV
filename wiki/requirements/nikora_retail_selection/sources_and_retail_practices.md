# Источники и практики других торговых сетей

Версия 1.0 · материалы прочитаны/проверены 16.09.2026. Источники поддерживают ровно указанные утверждения, а не полную функциональную приёмку продуктов.

## 1. NIKORA — исходные свидетельства

| Код | Материал | Как использован / ограничение |
|---|---|---|
| N01 | [Исходное ТЗ межскладской консолидации](https://docs.google.com/document/d/1mCu7RUoSTZpDSS02E8knazutFAU55Ybe5tSfK8LLiEw/edit) | До шести WMS, XML план/факт, обратное расписание, ворота/волны, SSCC; не готовый контракт каждого исключения |
| N02 | [Карта складов и потоков](https://drive.google.com/file/d/1UtTI-uQP9d-sKC1GEHA328V8V98K5meo/view) | Различная зрелость площадок, температурные/региональные потоки; не live-аудит |
| N03 | [Техническое описание складов](https://drive.google.com/file/d/1ZXBUmnB9pcvKEmGgrd4h66Azz2JDdGDd/view) | Физические процессы vs системная автоматизация, вес/нарезка, возвраты, RS.GE, sizing; разные периоды и противоречия требуют сверки |
| N04 | [Cross-docking proposal](https://drive.google.com/file/d/1fFgwHunPtzZLHuqxwFIQdzl22qr3VkO3/view) | Четыре категории, store calendar, 20–30 магазинов, подвоз от времени отправления, уплотнение HU |
| N05 | [Review and transformation plan v4](https://drive.google.com/file/d/1PRxbejzY_i_vYnQ36_DFaMRBylib9yK4/view) | Governance, dedicated team, cost-to-serve, ночная поддержка; экономический эффект не переносится в гарантию |
| N06 | [Встреча 12.09: SAP EWM, Manhattan, IWM](https://drive.google.com/file/d/1maytTblsDIbvb_fY5RAnbD2zbFjDnYES/view) | Голос заказчика: неудобство RF, replenishment, catch weight, доверительная приёмка, сверка; рассказы о третьих внедрениях не подтверждены независимо |
| N07 | [Выводы и план A4 v4-1](https://drive.google.com/file/d/1by1SYlz4eFgOzIuQX-pF4_5nRNnH9yIe/view) | Роль магазинов, ассортимент/возвраты/инфраструктура вне границ только IT-проекта |
| L01 | [Локальный GAP 15.09](../nikora_gap_analysis_20260915.md) | Синтез актуализированного ТЗ 1.3 / XML 1.1.0 и кода, G01–G22; не доказательство промышленной приёмки |
| L02 | [Минимальное расширение](../../architecture/nikora_minimal_extension.md) | Владение фактами, HU, OutboundWave, интеграционные гарантии |
| L03 | [41 ТЗ](../nikora_sprints/index.md), [21 crossdock-инкремент](../nikora_crossdock_increments.md) | План реализации и тесты; запланированное не считать существующим |
| L04 | [TMS system map](../../architecture/tms2_system_map.md), [status](../../subprojects/tms2_current_status.md) | Собственный стек и исторические checkpoint; последний status датирован 01.06.2026 |
| L05 | [Волна/ресурс/факт](../../architecture/wave_resource_execution_evidence_architecture.md), [UI](../nikora_ui_workplaces_tz.md) | Организация текущих требований и приёмки, не характеристики чужого продукта |

### Противоречия, которые нельзя незаметно исправить

- N06 называет IWM/VMAX. Это **не доказательство**, что речь об Infor WMS. Не переносить замечание о плавающем весе на Infor.
- «SAP HANA ERP» в обследовании не задаёт ECC/S/4HANA, release или EWM deployment. До выбора интеграции требуется паспорт ERP.
- N03 различает наличие физического весового процесса/нарезки и отсутствие автоматизации WMS. Физический процесс существует, даже если в функциональной таблице «отсутствует».
- В N03 сумма перечисленных температурных паллетомест Poti не совпадает с заявленным общим числом, встречаются несовместимые формулировки графика/процентов отбора. Не использовать такие числа как гарантированный sizing.
- Исходные шесть источников, четыре бизнес-категории и два источника технического пилота — разные уровни. Они должны иметь разные акты приёмки.
- Чужие истории неудачных внедрений/санкций в N06 — неподтверждённые мнения участников. Не объявлять на их основании недоступность или техническую непригодность бренда.
- Российские regulatory-модули репозитория не формируют автоматически требования для Грузии.

## 2. Практики других сетей и выводы для NIKORA

Это публичные описания кейсов/выбора, преимущественно опубликованные поставщиками, **не доступ к внутренним RFP торговых сетей**. Следующая колонка — аналитический вывод автора требований; проценты эффекта поставщиков не перенесены в прогноз NIKORA.

| Сеть / первичный источник | Что действительно описано | Выведенное требование NIKORA |
|---|---|---|
| [Asda / Manhattan](https://www.manh.com/about-us/newsroom/press-releases/asda-chooses-manhattan-active-warehouse-management-continue) | Выбор облачной WMS для развития распределительной сети, мобильный опыт и масштабирование | W38/W46/W47: тест на реальном ТСД, пиковая смена, обновление и rollout; пресс-релиз выбора не равен актуальному live-аудиту |
| [Sainsbury’s / Blue Yonder, 2020](https://media.blueyonder.com/sainsburys-feeds-its-supply-chain-strategy-with-blue-yonder/) | Программа объединяет планирование/ассортимент и warehouse/labor/yard | BP01–BP04: общие данные и календарь, но прогноз/ассортимент остаются за пределами WMS; историческая программа не доказывает завершение всех модулей |
| [REWE Dortmund / EPG](https://epg.com/us/newsroom/rewe-dortmund-adopts-lydia-voice/) | Голосовой отбор свежей продукции и сосуществование двух voice-систем через WMS-интерфейс | W38/W44: простота и устойчивое распознавание в реальной среде, постепенная замена устройств; кейс LYDIA не доказывает, что сама WMS — LFS |
| [Hy-Vee / Manhattan](https://www.manh.com/our-insights/resources/videos/customer-success-story-with-hy-vee) | Видимость сложной crossdock-сети и совместная работа WMS/TMS | T07/T17/T32: сквозная трассировка плеч, единый контроль исключений; не утверждает точное совпадение их HU-семантики с нашей |
| [PLUS / Manhattan, 2022](https://www.manh.com/about-us/newsroom/press-releases/plus-turns-manhattan-associates-cloud-solution-streamline) | Управление входящими поставками в РЦ и исходящими доставками из четырёх РЦ | T02/T06/T07: единая транспортная модель inbound/outbound и межплощадочных зависимостей |
| [Giant Eagle / Manhattan](https://www.manh.com/our-insights/resources/case-study/giant-eagle-finds-route-greater-efficiency-manhattan-tms) | Оптимизация своего парка и объединение разрозненных транспортных систем | T05/T06/T17: ресурсная модель парка/экипажа и единый план-факт, а не только закупка перевозки |
| [Mecalux Easy WMS: Espace des Marques](https://www.mecalux.com/software/warehouse-management-system-wms) | На продуктовой странице описана обработка заказов магазинов и интернет-канала | W18/W19: разные потоки на общем запасе. Это fashion, а не доказательство grocery catch weight |
| [Sud-Fresh / Mecalux](https://www.mecalux.com/clients/sud-fresh-food-traceability) | Пищевой логистический оператор, traceability и crossdock | W12/W28: проверять партии/сроки сквозь прямой поток; это смежный food-кейс, не торговая сеть |

Отсюда общий retail-стандарт: единый календарь заказа/доставки, коробочный и штучный отбор, короткий shelf-life, волновое пополнение, store-friendly груз, собственный/наёмный парк, доказанный POD и возвраты. Эти требования синтезированы вместе с NIKORA, а не приписаны каждому упомянутому клиенту дословно.

## 3. Как отобраны дополнительные системы

Публичные abstracts Gartner 2026 подтверждают включение в исследование, но не предоставляют использованные здесь закрытые оценки. В WMS добавлены Blue Yonder, Oracle, Infios, EPG и Mecalux. В TMS — Blue Yonder, Oracle, Infios, e2open и Alpega. Это расширение рынка сравнения, не рейтинг «пять лучших».

Не воспроизводятся диаграммы Gartner и не используются пользовательские Peer Insights-оценки в качестве доказательств функциональности. Важнее соответствие конкретной редакции, команде и D01–D12.

## 4. Каталог публичных первичных источников

Дата обращения для всех строк — 16.09.2026. Страницы продуктов — vendor claims; SAP Help/Oracle docs — документация конкретных версий; Gartner — состав исследования; retail cases — опубликованные описания проектов.

| Код | Источник |
|---|---|
| SW | [SAP EWM: функции](https://www.sap.com/products/scm/extended-warehouse-management/features.html) |
| SW2 | [SAP EWM: Merchandise Distribution Cross-Docking, 2025 FPS01](https://help.sap.com/docs/PRODUCT_ID/9832125c23154a179bfa1784cdc9577a/c9ef2498ef494449ada4cccb97c5ccca.html) |
| IW | [Infor WMS: функции](https://www.infor.com/en-gb/solutions/scm/warehouse-management-system) |
| MW | [Manhattan ActiveWarehouse / Active WM](https://www.manh.com/solutions/supply-chain-management-software/warehouse-management) |
| AW | [AXELOT WMS X5: функции](https://www.axelot.ru/product/axelot-wms-x5/functionality/) |
| AW2 | [AXELOT WMS X5: продукт и платформа](https://www.axelot.ru/product/axelot-wms-x5/) |
| BW | [Blue Yonder Warehouse Management](https://blueyonder.com/solutions/warehouse-management) |
| OW | [Oracle Fusion Cloud Warehouse Management](https://www.oracle.com/scm/logistics/warehouse-management/) |
| OW2 | [Oracle WMS 26A: Waving Overview](https://docs.oracle.com/en/cloud/saas/warehouse-management/26a/owmim/waving-overview.html) |
| FW | [Infios: портфель Warehouse Management Systems](https://www.infios.com/en/supply-chain-solutions/warehouse-management-systems) |
| EW | [EPG LFS: модули](https://www.epg.com/gb/logistics-software/warehouse-management-system-lfswms/lfs-modules/) |
| XW | [Mecalux Easy WMS](https://www.mecalux.com/software/warehouse-management-system-wms) |
| XW2 | [Mecalux: Sud-Fresh, food traceability](https://www.mecalux.com/clients/sud-fresh-food-traceability) |
| ST | [SAP TM: функции](https://www.sap.com/products/scm/transportation-logistics/features.html) |
| ST2 | [SAP: возможности TM и integration lifecycle](https://learning.sap.com/courses/discovering-sap-s-4hana-transportation-management/understanding-capabilities-of-sap-transportation-management_cf48b4af-36de-411f-b5f2-9e3073fb8a3a) |
| IT | [Infor Nexus Global Transportation Management](https://www.infor.com/mea/solutions/scm/infor-nexus/transportation-management) |
| MT | [Manhattan Active TM](https://www.manh.com/solutions/supply-chain-management-software/transportation-management) |
| MT2 | [Manhattan ActiveTransportation: редакции](https://www.manh.com/solutions/supply-chain-management-software/activetransportation) |
| AT | [AXELOT TMS: функции](https://www.axelot.ru/product/axelot-tms/functionality/) |
| BT | [Blue Yonder Transportation Management](https://blueyonder.com/solutions/transportation-management) |
| OT | [Oracle Transportation Management](https://www.oracle.com/scm/logistics/transportation-management/) |
| FT | [Infios Transportation Management, бывший MercuryGate](https://www.infios.com/en/supply-chain-solutions/transportation-management) |
| ET | [e2open Transportation Management](https://www.e2open.com/logistics/transportation-management) |
| LT | [Alpega TMS](https://www.alpegagroup.com/en-en/transport-management-system/) |
| GW | [Gartner MQ WMS 2026 — публичный abstract](https://www.gartner.com/en/documents/7780053) |
| GT | [Gartner MQ TMS 2026 — публичный abstract](https://www.gartner.com/en/documents/7645129) |
| R1 | [Asda: выбор Manhattan Active WM](https://www.manh.com/about-us/newsroom/press-releases/asda-chooses-manhattan-active-warehouse-management-continue) |
| R2 | [Sainsbury’s: стратегия с Blue Yonder, 21.04.2020](https://media.blueyonder.com/sainsburys-feeds-its-supply-chain-strategy-with-blue-yonder/) |
| R3 | [REWE Dortmund: LYDIA Voice, 12.06.2024](https://epg.com/us/newsroom/rewe-dortmund-adopts-lydia-voice/) |
| R4 | [Mecalux: retail и омниканальное выполнение](https://www.mecalux.com/software/warehouse-management-system-wms) |
| GS | [GS1 System Architecture](https://www.gs1.org/standards/gs1-system-architecture-document/current-standard) |
| GE | [GS1 EPCIS](https://ref.gs1.org/standards/epcis) |
| R5 | [Hy-Vee: WMS/TMS и crossdock network](https://www.manh.com/our-insights/resources/videos/customer-success-story-with-hy-vee) |
| R6 | [PLUS: inbound/outbound TMS, 07.02.2022](https://www.manh.com/about-us/newsroom/press-releases/plus-turns-manhattan-associates-cloud-solution-streamline) |
| R7 | [Giant Eagle: fleet TMS case](https://www.manh.com/our-insights/resources/case-study/giant-eagle-finds-route-greater-efficiency-manhattan-tms) |

## 5. Ограничения исследования

Не получены: подписанные ответы вендоров, коммерческие цены/BoM, доступ к их стендам, права на данные референс-клиентов, договоры поддержки в Грузии и подтверждение всех выбранных версий. В этой работе не проводились тесты БД NIKORA, Oracle нашего проекта или vendor load-tests.

Наличие функции в одной версии/редакции не переносится на другую. Публичные «real-time», «AI», «seamless» и «zero downtime» трактуются как заявления поставщика и превращаются в проверяемые критерии, а не в безусловные факты.
