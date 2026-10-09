# Источники и практики для общего retail стандарта

Версия 1.0 · 17 сентября 2026 года.

## Метод исследования

Использованы официальные страницы поставщиков, публичные abstracts Gartner, стандарты GS1, материалы Smart Freight Centre и опубликованные клиентские кейсы. Это не доступ к закрытым RFP сетей и не результаты независимых испытаний коммерческих продуктов. Отраслевые наблюдения преобразованы в предлагаемые требования заказчика; конкретные политики и тесты не приписываются исходному клиенту без подтверждения.

Материалы предыдущего проекта NIKORA использованы только для понимания структуры репозитория и ранее обсуждённых решений. Его число складов, язык персонала, обязательность XML, конкретные сроки, два прохода контроля и способ межскладской консолидации не перенесены как универсальные свойства розницы.

## Что определяет формат магазина у дома

Малая подсобка ограничивает разовый объём доставки; высокая частота рейсов повышает цену каждой ошибки приёмки. Для коротких сроков годности важна свежесть в момент передачи магазину, а не только при выходе из РЦ. Улицы, входы, отсутствие рампы и короткое окно ограничивают автомобиль и грузоместо. Смешанные короба и роллы требуют удобства разгрузки и выкладки; возврат пустой тары и непринятого товара меняет загрузку по маршруту. Это аналитические следствия операционного профиля, которые необходимо подтвердить обследованием будущего заказчика.

## Практики других участников рынка

| Пример | Что сообщает источник | Требование для нашего стандарта | Ограничение вывода |
|---|---|---|---|
| PLUS и Manhattan TMS, S22 | Единое управление входящими и исходящими потоками, моделирование сети | RT12 RT13 RT39; единый транспортный план с разными потоками | Сообщение 2022 года, не аудит текущей версии или всей эффективности |
| Sainsburys и Blue Yonder, S23 | Программа охватывает WMS, labor и yard вместе с планированием | RW41 RW43, RT19 и разделение владельцев данных | Анонс выбора и будущего развития не равен завершённому внедрению |
| REWE Dortmund и LYDIA, S24 | Голосовое исполнение в свежих овощах и фруктах, параллельность голосовых систем | RW44 RW46; эргономика и совместимость исполнителей | Не доказывает использование LFS как основной WMS |
| HAVI и Infor, S25 | Стандартизация распределительных площадок и доступ к данным | RW04 RW53 RW54; шаблон площадки с локальными политиками | Пищевой логистический оператор, а не магазин у дома |
| Grocery обзор Manhattan, S21 | Согласование склада, труда и перевозки, отраслевые кейсы | BP04 BP06 BP08 и сквозные показатели | Маркетинговый обзор, не независимый бенчмарк |
| Mecalux Store Fulfillment, S27 | Отдельная связь склада и магазинных операций | Явная граница WMS и магазинной системы | Дополнительный модуль, не обязательное ядро всех WMS |

Экономические проценты из клиентских историй не перенесены в прогноз эффекта для абстрактной сети. Для оценки эффекта требуется собственный baseline ошибок, трудозатрат, потерь и стоимости доставки.

## Из каких решений собран стандарт

Из процессной декомпозиции SAP полезно разделение входа, внутреннего потока, выхода и cross functional scope. Из каталога Infor — соединение запаса, разных методов отбора и управления трудом. Manhattan подчёркивает непрерывное исполнение и связь автоматизации с ресурсами. AXELOT даёт подробный пример настройки стратегий и контроля операций. Эти принципы используются как структура требований; они не делают обязательной конкретную платформу, лицензию или микросервисный подход.

Blue Yonder расширяет набор сравнения оркестрацией ресурсов и slotting, Oracle — retail ориентированным распределением и flow through, Infios — выбором модульного состава, EPG — подробной декомпозицией складских технологий, Mecalux — сопряжением ручного и автоматизированного склада. Каждая возможность включается по необходимости процесса и проверяется отдельным тестом.

## Дополнительные кандидаты Gartner

Публичный WMS abstract от 29.04.2026 включает Blue Yonder, Oracle, Infios, EPG и Mecalux; они добавлены к четырём запрошенным WMS. Для TMS abstract от 30.03.2026 использованы Blue Yonder, Oracle, Infios, e2open и Alpega. Это два разных списка рынка. AXELOT и Infor Nexus не объявляются участниками TMS списка. Закрытые графики, точные позиции и оценки Gartner не воспроизводились.

## Экологические показатели

В WMS имеет смысл измерять порчу, истечение срока, расход упаковки и оборот тары по фактам. В TMS — топливо, порожний пробег и расчётные выбросы с методикой и версией коэффициентов. [GLEC Framework](https://smartfreightcentre.org/news/13311209) служит возможной методологической основой; это не требование собственной сертификации продукта. Показатели должны различать фактическое измерение и оценку, чтобы оптимизация километров не выдавалась за измеренное снижение CO2e.

## Реестр первичных материалов

Дата обращения ко всем материалам 17 сентября 2026 года. Относительные даты поискового индекса не заменяют указанную дату публикации документа.

### S01 SAP EWM функции

[SAP EWM функции](https://www.sap.com/products/scm/extended-warehouse-management/features.html). Официальный каталог; базовая и расширенная поставки; функциональные семейства, не доказательство конкретного внедрения.

### S02 Infor WMS функции

[Infor WMS функции](https://www.infor.com/en-gb/solutions/scm/warehouse-management-system). Официальный каталог; конфигурация, модули и условия облачной поставки требуют уточнения.

### S03 Manhattan ActiveWarehouse

[Manhattan ActiveWarehouse](https://www.manh.com/solutions/supply-chain-management-software/warehouse-management). Официальный каталог; редакции Essentials, Enterprise и Enterprise Premier не считаются одинаковыми.

### S04 AXELOT WMS X5 функции

[AXELOT WMS X5 функции](https://www.axelot.ru/product/axelot-wms-x5/functionality/). Официальный процессный каталог; SCAP, MOBILE и другие компоненты учитывать отдельно.

### S05 Blue Yonder Warehouse Management

[Blue Yonder Warehouse Management](https://blueyonder.com/solutions/warehouse-management). Официальный каталог семейства; подробная граница модулей уточняется в предложении.

### S06 Oracle Warehouse Management Cloud

[Oracle Warehouse Management Cloud](https://www.oracle.com/scm/logistics/warehouse-management/). Официальный продуктовый каталог; наличие Oracle Database в нашем проекте не означает наличие этого WMS продукта.

### S07 Infios Warehouse Management Systems

[Infios Warehouse Management Systems](https://www.infios.com/en/supply-chain-solutions/warehouse-management-systems). Официальный каталог портфеля. До ответа вендора нельзя суммировать возможности разных продуктов и редакций как один внедряемый пакет.

### S08 EPG LFS модули

[EPG LFS модули](https://epg.com/gb/logistics-software/warehouse-management-system-lfswms/lfs-modules/). Официальный каталог основных и дополнительных модулей.

### S09 Mecalux Easy WMS

[Mecalux Easy WMS](https://www.mecalux.com/software/warehouse-management-system-wms). Официальная страница прочитана через поисковый индекс; прямое открытие иногда возвращало неполное содержимое. Утверждения ограничены доступным текстом.

### S10 SAP Transportation Management функции

[SAP Transportation Management функции](https://www.sap.com/products/scm/transportation-logistics/features.html). Официальный каталог; функции TM не приписываются EWM.

### S11 Infor Nexus Global Transportation Management

[Infor Nexus Global Transportation Management](https://www.infor.com/mea/solutions/scm/infor-nexus/transportation-management). Официальный каталог глобального сетевого TMS; не доказательство подходящего мобильного контура для городского собственного парка.

### S12 Manhattan ActiveTransportation

[Manhattan ActiveTransportation](https://www.manh.com/solutions/supply-chain-management-software/transportation-management). Официальный каталог планирования, исполнения, парка и расчётов.

### S13 AXELOT TMS функции

[AXELOT TMS функции](https://www.axelot.ru/product/axelot-tms/functionality/). Официальный каталог; отдельно уточнять SCAP, MAPS, RTVP, MOBILE, лицензирование и интеграцию.

### S14 Blue Yonder Transportation Management

[Blue Yonder Transportation Management](https://blueyonder.com/solutions/transportation-management). Официальный каталог; сеть и дополнительные компоненты не объявляются автоматически включёнными.

### S15 Oracle Transportation Management

[Oracle Transportation Management](https://www.oracle.com/scm/logistics/transportation-management/). Официальный каталог OTM, Fleet и финансовых возможностей; состав подписки уточняется.

### S16 Infios Transportation Management

[Infios Transportation Management](https://www.infios.com/en/supply-chain-solutions/transportation-management). Официальная страница прямо связывает текущее название с MercuryGate TMS; отдельные DSD и routing решения проверяются по составу поставки.

### S17 e2open Transportation Management

[e2open Transportation Management](https://www.e2open.com/logistics/transportation-management). Официальный каталог. В сравнении используется решение для грузовладельца, а не отдельный продукт для экспедитора или услуга LaaS.

### S18 Alpega TMS для грузовладельца

[Alpega TMS для грузовладельца](https://www.alpegagroup.com/en-en/transport-management-system/). Официальный каталог; дополнительные модули и сетевые подключения должны быть перечислены в смете.

### S19 Gartner WMS 2026

[Gartner WMS 2026](https://www.gartner.com/en/documents/7780053). Публичный abstract от 29.04.2026 подтверждает включение в исследование; закрытые оценки и размещение в квадранте не использовались.

### S20 Gartner TMS 2026

[Gartner TMS 2026](https://www.gartner.com/en/documents/7645129). Публичный abstract от 30.03.2026 подтверждает список участников. Infor и AXELOT не указаны в этом списке.

### S21 Manhattan решения для grocery

[Manhattan решения для grocery](https://www.manh.com/industries/grocery). Отраслевой обзор и ссылки на клиентские истории; не конфиденциальный RFP ритейлера.

### S22 PLUS использует Manhattan TMS

[PLUS использует Manhattan TMS](https://www.manh.com/en-au/about-us/newsroom/press-releases/plus-turns-manhattan-associates-cloud-solution-streamline). Сообщение 07.02.2022: входящие и исходящие потоки, моделирование сети; будущие цели не равны измеренным результатам.

### S23 Sainsburys и Blue Yonder

[Sainsburys и Blue Yonder](https://media.blueyonder.com/sainsburys-feeds-its-supply-chain-strategy-with-blue-yonder/). Сообщение 21.04.2020 о выборе и программе развития; не подтверждает завершение всех внедрений к текущей дате.

### S24 REWE Dortmund и LYDIA VOICE

[REWE Dortmund и LYDIA VOICE](https://epg.com/us/newsroom/rewe-dortmund-adopts-lydia-voice/). Кейс голосового исполнения. Наличие LYDIA не доказывает, что базовая WMS у REWE — LFS.

### S25 HAVI стандартизация складов

[HAVI стандартизация складов](https://prd-xme.infor.com/en-nl/customer-stories/havi-warehouse-transformation-at-scale). Публичная история пищевого логистического оператора, а не магазинов у дома; полезна как практика типизации площадок.

### S26 Mecalux фото при приёмке и отправке

[Mecalux фото при приёмке и отправке](https://www.mecalux.com/software/updates/photo-capture). Описание конкретной возможности регистрации изображений и инцидентов.

### S27 Mecalux Store Fulfillment

[Mecalux Store Fulfillment](https://www.mecalux.com/software/store-fulfillment). Отдельный модуль. Нельзя считать управление магазином обязательной частью любого WMS.

### S28 GS1 System Architecture

[GS1 System Architecture](https://ref.gs1.org/architecture/system-architecture/). Первичный архитектурный стандарт; дополнительно проверен официальный справочник GS1 id keys через индекс. Прямой gs1.org иногда возвращал 403.

### S29 GS1 EPCIS

[GS1 EPCIS](https://ref.gs1.org/standards/epcis/). Первичный стандарт обмена событиями. EPCIS — возможный контракт, а не требование внедрять отдельную платформу.

### S30 GLEC Framework версия 3 2

[GLEC Framework версия 3 2](https://smartfreightcentre.org/news/13311209). Страница издателя, опубликована 30.06.2026, с названием версии October 2025. Версию документа не путать с датой веб публикации.

### S31 SAP merchandise distribution

[SAP merchandise distribution](https://help.sap.com/docs/SAP_SUPPLY_CHAIN_MANAGEMENT/dc8e3ce481cc493aad2145b99e6c53eb/47264dbd1bc94575b37a520acf8fcdf9.html). Доступное описание EWM 7.0 EHP1 подтверждает семантику flow through и crossdock; оно не доказывает лицензирование или API текущей редакции.

## Локальное основание

[Реестр доказательств E01–E33](08_current_system_gap.md) содержит конкретные файлы текущего проекта. Для code gap использовались найденные реализации, а не только тексты будущих ТЗ. При этом обследование было целевым, а не полным запуском всех legacy процедур. Неизвестные области сохранены как неизвестные.
