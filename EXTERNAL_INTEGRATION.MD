# Манифест внешней интеграции

Этот документ описывает интеграцию desktop-приложения `WindowsApplication2` с внешней ERP-системой.

Важное уточнение по терминологии:
- `Сфера` и `SUPERMAG` в рамках этого проекта это одна и та же внешняя система
- `Сфера` это бизнес-название, которым пользуются сотрудники
- `SUPERMAG` это техническое имя Oracle-схемы и объектов, которое используется в коде и SQL

## Внешние объекты SUPERMAG и поля, которые читает приложение

Ниже перечислены таблицы, представления и процедуры внешней системы `SUPERMAG`, которые реально используются приложением.

### `SUPERMAG.MON_WMS_STBYPALL`

Назначение:
- предрассчитанное разбиение заказа по паллетам на стороне `SUPERMAG`

Поля, которые читаются:
- `DOCID`
- `ARTICLE`
- `SHORTNAME`
- `BC`
- `ABBREV`
- `TAREWEIGHT`
- `PATH`
- `ORDER_WEIGHT`
- `TARESIZE`
- `QUANTITY`
- `DD1`
  номер паллеты
- `SORTFIELD`
  порядок внутри паллеты
- `AQ`
  коробки / упаковка

Где используется:
- построение WMS-паллет
- создание строк паллет
- импорт данных для сборки и отгрузки

Ссылки на код:
- [Form1.cs](C:\projects\TMS\MINI%20WMS\WindowsApplication2\WindowsApplication2\Form1.cs#L5184)
- [Form1.cs](C:\projects\TMS\MINI%20WMS\WindowsApplication2\WindowsApplication2\Form1.cs#L5199)

### `SUPERMAG.SMCARD`

Назначение:
- справочник товаров

Поля, которые читаются:
- `ARTICLE`
  код товара / основной ключ товара для связки с WMS
- `SHORTNAME`
  краткое наименование товара
- `IDCLASS`
  класс товара
- `NAME`
  полное наименование товара

Где используется:
- обновление и синхронизация карточек товара в WMS
- получение наименования товара
- классификация товара
- join с документными строками

Куда потом попадает:
- `RABAEV.RRL_ARTICULS.NAME`
- запросы и формы, где нужен текст товара и его класс

Ссылки на код:
- [Form1.cs](C:\projects\TMS\MINI%20WMS\WindowsApplication2\WindowsApplication2\Form1.cs#L3931)
- [Form1.cs](C:\projects\TMS\MINI%20WMS\WindowsApplication2\WindowsApplication2\Form1.cs#L5556)
- [Form1.cs](C:\projects\TMS\MINI%20WMS\WindowsApplication2\WindowsApplication2\Form1.cs#L24940)

### `SUPERMAG.SMCARDPROPERTIES`

Назначение:
- дополнительные свойства товара

Поля, которые читаются:
- `ARTICLE`
  код товара
- `PROPID`
  идентификатор или имя свойства
- `PROPVAL`
  значение свойства

Известные свойства, которые используются:
- `User.RCComplect`
- `User.pcsort`
- `4`
- `5`

По смыслу используются для:
- порядка отбора
- признаков комплектации
- настройки адреса/ячейки отбора
- количества мест в ряду
- количества рядов на паллете

Куда потом попадает:
- в логику заполнения `RABAEV.RRL_ARTICULS`
- в WMS-процедуры и расчеты последовательности отбора

Ссылки на код:
- [Form1.cs](C:\projects\TMS\MINI%20WMS\WindowsApplication2\WindowsApplication2\Form1.cs#L3760)
- [Form1.cs](C:\projects\TMS\MINI%20WMS\WindowsApplication2\WindowsApplication2\Form1.cs#L3906)
- [Form1.cs](C:\projects\TMS\MINI%20WMS\WindowsApplication2\WindowsApplication2\Form1.cs#L3919)

### `SUPERMAG.vcardstoreprop_rc`

Назначение:
- представление с адресом хранения / маршрутом размещения товара

Поля, которые читаются:
- `ARTICLE`
  код товара
- `PATH`
  путь или адрес хранения

Где используется:
- заполнение ячейки / адреса товара в WMS

Куда потом попадает:
- `RABAEV.RRL_ARTICULS.CELL`

Ссылка на код:
- [Form1.cs](C:\projects\TMS\MINI%20WMS\WindowsApplication2\WindowsApplication2\Form1.cs#L3894)

### `SUPERMAG.SMSTOREUNITS`

Назначение:
- единицы хранения, упаковка и штрихкоды товара

Поля, которые читаются:
- `ARTICLE`
  код товара
- `QUANTITY`
  количество единиц в упаковке
- `WEIGHT`
  вес упаковки
- `BARCODE`
  штрихкод
- `BARCODETYPE`
  тип штрихкода
- `FLAGS`
  служебные признаки

Наблюдаемая логика отбора данных:
- `MAX(QUANTITY)` при `FLAGS = 0`
- `MAX(WEIGHT)` при `FLAGS = 0`
- `BARCODETYPE = 7` используется как штрихкод коробки
- `BARCODETYPE = 1` используется как штрихкод штуки

Где используется:
- загрузка кратности упаковки
- загрузка веса коробки
- загрузка штрихкодов штуки и коробки

Куда потом попадает:
- `RABAEV.RRL_ARTICULS`
- связанные WMS-расчеты по упаковке и размещению

Ссылки на код:
- [Form1.cs](C:\projects\TMS\MINI%20WMS\WindowsApplication2\WindowsApplication2\Form1.cs#L3944)
- [Form1.cs](C:\projects\TMS\MINI%20WMS\WindowsApplication2\WindowsApplication2\Form1.cs#L3956)
- [Form1.cs](C:\projects\TMS\MINI%20WMS\WindowsApplication2\WindowsApplication2\Form1.cs#L3968)
- [Form1.cs](C:\projects\TMS\MINI%20WMS\WindowsApplication2\WindowsApplication2\Form1.cs#L3989)

### `SUPERMAG.SMDOCUMENTS`

Назначение:
- заголовки документов ERP

Поля, которые читаются:
- `ID`
  номер документа
- `DOCTYPE`
  тип документа
- `DOCSTATE`
  состояние документа
- `CREATEDAT`
  дата создания
- `LOCATION`
  локация / магазин / склад
- `CLIENTINDEX`
  ссылка на контрагента

Известные типы документов:
- `SO`
- `OR`
- `WI`
- `WO`

Известные состояния:
- `1`
- `2`
- `3`

Где используется:
- импорт заказов
- проверка существования и состояния документа
- поиск связанных документов
- определение источника и назначения
- обогащение данных по поставщику или клиенту

Ссылки на код:
- [Form1.cs](C:\projects\TMS\MINI%20WMS\WindowsApplication2\WindowsApplication2\Form1.cs#L4162)
- [Form1.cs](C:\projects\TMS\MINI%20WMS\WindowsApplication2\WindowsApplication2\Form1.cs#L5148)
- [Form1.cs](C:\projects\TMS\MINI%20WMS\WindowsApplication2\WindowsApplication2\Form1.cs#L18184)
- [СверкаЦен.cs](C:\projects\TMS\MINI%20WMS\WindowsApplication2\WindowsApplication2\СверкаЦен.cs#L104)

### `SUPERMAG.SMSPEC`

Назначение:
- строки документов ERP

Поля, которые читаются:
- `DOCID`
  номер документа
- `DOCTYPE`
  тип документа
- `ARTICLE`
  код товара
- `QUANTITY`
  количество
- `ITEMPRICE`
  цена позиции

Где используется:
- загрузка строк заказа
- загрузка количества и цены
- сверка заказов и поставщиков

Ссылки на код:
- [Form1.cs](C:\projects\TMS\MINI%20WMS\WindowsApplication2\WindowsApplication2\Form1.cs#L5557)
- [Form1.cs](C:\projects\TMS\MINI%20WMS\WindowsApplication2\WindowsApplication2\Form1.cs#L5787)
- [СверкаЦен.cs](C:\projects\TMS\MINI%20WMS\WindowsApplication2\WindowsApplication2\СверкаЦен.cs#L104)

### `SUPERMAG.SMCLIENTINFO`

Назначение:
- справочник контрагентов, связанный с документами

Поля, которые читаются:
- `ID`
  идентификатор контрагента
- `NAME`
  наименование контрагента
- `INN`
  ИНН
- `KPP`
  КПП

Где используется:
- заполнение реквизитов поставщика или клиента в WMS

Куда потом попадает:
- `RABAEV.RRL_PRIHOD_NAKLAD.POSTAVSHIK_NAME`
- `RABAEV.RRL_PRIHOD_NAKLAD.SUPP_INN`
- `RABAEV.RRL_PRIHOD_NAKLAD.SUPP_KPP`

Ссылки на код:
- [Form1.cs](C:\projects\TMS\MINI%20WMS\WindowsApplication2\WindowsApplication2\Form1.cs#L4162)
- [СверкаЦен.cs](C:\projects\TMS\MINI%20WMS\WindowsApplication2\WindowsApplication2\СверкаЦен.cs#L104)

### `SUPERMAG.SMSTORELOCATIONS`

Назначение:
- справочник локаций, магазинов и иерархии размещения

Поля, которые читаются:
- `ID`
  идентификатор локации
- `NAME`
  имя локации
- `PARENTLOC`
  родительская локация

Где используется:
- определение названий источника и назначения документа

Ссылки на код:
- [Form1.cs](C:\projects\TMS\MINI%20WMS\WindowsApplication2\WindowsApplication2\Form1.cs#L5148)
- [Form1.cs](C:\projects\TMS\MINI%20WMS\WindowsApplication2\WindowsApplication2\Form1.cs#L5517)

### `SUPERMAG.SMCOMMONBASES`

Назначение:
- связи между документами ERP

Поля, которые читаются:
- `ID`
  идентификатор документа
- `BASEID`
  базовый документ
- `BASEDOCTYPE`
  тип базового документа
- `DOCTYPE`
  тип текущего документа

Где используется:
- поиск связанных документов для заказа WMS
- проверка цепочки документов вверх и вниз

Ссылки на код:
- [Form1.cs](C:\projects\TMS\MINI%20WMS\WindowsApplication2\WindowsApplication2\Form1.cs#L12428)
- [Form1.cs](C:\projects\TMS\MINI%20WMS\WindowsApplication2\WindowsApplication2\Form1.cs#L18186)

### `SUPERMAG.fill_mon_wms_stbypall`

Назначение:
- внешняя процедура, которая подготавливает данные в `MON_WMS_STBYPALL`

Где используется:
- перед чтением паллетизированного разбиения заказа

Требование:
- у пользователя Oracle должны быть права на `EXECUTE`

### `SUPERMAG.SMCARDASSORT` и `SUPERMAG.SACARDASSORT`

Назначение:
- ассортиментные связи товара

Где используется:
- вспомогательные запросы для товарной аналитики и отбора

### `SUPERMAG.SMGOODS`

Назначение:
- товарные группы и дерево категорий

Поля, которые читаются:
- `ID`
- `NAME`
- `PARENTID`

Где используется:
- классификация и аналитика товара

Ссылка на код:
- [Form1.cs](C:\projects\TMS\MINI%20WMS\WindowsApplication2\WindowsApplication2\Form1.cs#L19934)

### `SUPERMAG.SACARDCLASS`

Назначение:
- классы карточек товаров

Поля, которые читаются:
- `ID`
- `NAME`

Где используется:
- получение класса товара

Ссылка на код:
- [Form1.cs](C:\projects\TMS\MINI%20WMS\WindowsApplication2\WindowsApplication2\Form1.cs#L24940)

## Общая схема интеграции

Направление обмена:
- `Сфера / SUPERMAG -> WindowsApplication2 -> RABAEV`

Основные сценарии:
- синхронизация карточек товара
- загрузка заказов и строк заказов
- обогащение данных по поставщику и клиенту
- разбиение заказа по паллетам
- проверка статусов документов
- получение товарной классификации

Что важно:
- в проверенном коде не найдено стабильной двусторонней записи обратно в `SUPERMAG`
- интеграция в основном read-side: приложение читает из внешней ERP и записывает результат в свои таблицы `RABAEV.*`

## Подключение к SUPERMAG

Источник строки подключения:
- `RABAEV.RRL_CONSTANTS`
- ключ: `EXT_BASE_CONNECTION_STRING`

Ссылка на код:
- [Form1.cs](C:\projects\TMS\MINI%20WMS\WindowsApplication2\WindowsApplication2\Form1.cs#L241)

Поведение:
- приложение открывает отдельное Oracle-подключение во внешнюю схему `SUPERMAG`
- строка подключения не зашита в обычный код сценариев
- если константа отсутствует или неверна, все экраны и функции, завязанные на `SUPERMAG`, падают во время выполнения

## Потоки данных из SUPERMAG в WMS

### 1. Синхронизация товара

Источники:
- `SMCARD`
- `SMCARDPROPERTIES`
- `vcardstoreprop_rc`
- `SMSTOREUNITS`

Что затягивается:
- код товара
- краткое и полное наименование
- адрес хранения / ячейка
- упаковка и кратность
- вес коробки
- штрихкоды штуки и коробки
- свойства для логики отбора и размещения

Куда записывается:
- `RABAEV.RRL_ARTICULS`
- связанные WMS-процедуры

### 2. Импорт заказов и накладных

Источники:
- `SMDOCUMENTS`
- `SMSPEC`
- `SMCARD`
- `SMSTORELOCATIONS`
- `MON_WMS_STBYPALL`
- `fill_mon_wms_stbypall`

Что затягивается:
- номер и дата документа
- статус документа
- источник и получатель
- строки заказа
- товар
- количество
- цена
- вес
- разбиение по паллетам

Куда записывается:
- заказы WMS
- паллеты WMS
- строки паллет
- локальные документы в `RABAEV`

### 3. Обогащение данных поставщика и клиента

Источники:
- `SMDOCUMENTS`
- `SMCLIENTINFO`
- `SMSPEC`
- `SMCARD`

Что затягивается:
- наименование контрагента
- ИНН
- КПП

Куда записывается:
- `RABAEV.RRL_PRIHOD_NAKLAD.POSTAVSHIK_NAME`
- `RABAEV.RRL_PRIHOD_NAKLAD.SUPP_INN`
- `RABAEV.RRL_PRIHOD_NAKLAD.SUPP_KPP`

### 4. Проверка связанных документов и статусов

Источники:
- `SMCOMMONBASES`
- `SMDOCUMENTS`

Что затягивается:
- связанные документы
- типы документов
- состояния документов

Где используется:
- проверка жизненного цикла документа за пределами WMS
- поиск связанных ERP-документов по заказу или СТ

## Локальная проекция данных Сферы в WMS

Кроме прямого чтения из `SUPERMAG`, в системе есть локальная таблица `RABAEV.SFERA_EAN`.

Ее назначение:
- хранить упаковочные и штрихкодовые данные товара, относящиеся к `Сфере`
- использовать эти данные в отчетах, поиске и локальных WMS-формах

Важно:
- несмотря на имя `SFERA_EAN`, это не вторая ERP
- это локальная таблица WMS, в которую попадают данные той же внешней системы `Сфера / SUPERMAG`

### `RABAEV.SFERA_EAN`

Поля:
- `УИД`
  локальный идентификатор записи
- `TMC_UID`
  внешний код товара
- `NAME`
  наименование товара
- `EAN_SHT`
  штрихкод штуки
- `EAN_BL`
  штрихкод блока
- `EAN_KOR`
  штрихкод коробки
- `SHT_IN_BL`
  штук в блоке
- `BL_IN_KOR`
  блоков в коробке
- `MANUALENTER`
  источник записи:
  `N` импортировано из внешней системы
  `Y` введено вручную пользователем

Связанные объекты:
- `RABAEV.SFERA_EAN_ID`
- `RABAEV.SFERA_EAN_TRG`
- `RABAEV.ADD_SFERA_EAN`
- `RABAEV.ADD_SFERA_EAN2`
- `RABAEV.RRL_SFERA_EAN_EAN_SHT`
- `RABAEV.RRL_SFERA_EAN_EAN_BL`
- `RABAEV.RRL_SFERA_EAN_EAN_KOR`

Ссылки:
- [01_tables.sql](C:\projects\TMS\db\windowsapplication2_xp12_oracle\01_tables.sql#L619)
- [03_functions.sql](C:\projects\TMS\db\windowsapplication2_xp12_oracle\03_functions.sql#L1691)
- [04_procedures.sql](C:\projects\TMS\db\windowsapplication2_xp12_oracle\04_procedures.sql#L3)

## Поведение desktop-приложения по `SFERA_EAN`

Наблюдаемое поведение:
- в `WindowsApplication2` есть форма редактирования записей `SFERA_EAN`
- при создании новой записи вызывается `ADD_SFERA_EAN2`
- при изменении существующей записи выполняется прямой `UPDATE RABAEV.SFERA_EAN`

Какие поля редактируются:
- `TMC_UID`
- `SHT_IN_BL`
- `BL_IN_KOR`
- `EAN_SHT`
- `EAN_BL`
- `EAN_KOR`
- `УИД`

Что важно:
- UI пишет ручные записи с `MANUALENTER = 'Y'`
- функции чтения `RRL_SFERA_EAN_*` отдают только записи с `MANUALENTER = 'N'`
- значит ручная правка и внешний импорт в логике системы разделены

Ссылки на код:
- [Form1.cs](C:\projects\TMS\MINI%20WMS\WindowsApplication2\WindowsApplication2\Form1.cs#L1041)
- [Form1.cs](C:\projects\TMS\MINI%20WMS\WindowsApplication2\WindowsApplication2\Form1.cs#L1069)

## Обязательный внешний контракт

Со стороны `Сферы / SUPERMAG` должны быть доступны:
- схема `SUPERMAG`
- права чтения на все перечисленные таблицы и представления
- права `EXECUTE` на `SUPERMAG.fill_mon_wms_stbypall`
- согласованные связи между `SMDOCUMENTS`, `SMSPEC`, `SMCARD`, `SMCLIENTINFO`

Что ожидает WMS:
- `ARTICLE` во внешней системе совпадает с кодом товара WMS
- `SMDOCUMENTS.ID` доступен для поиска как идентификатор заказа
- `SMCLIENTINFO.ID = SMDOCUMENTS.CLIENTINDEX`
- `SMSPEC.DOCID = SMDOCUMENTS.ID`
- `SMSPEC.DOCTYPE = SMDOCUMENTS.DOCTYPE`

Для загрузки упаковочных данных в `RABAEV.SFERA_EAN` желательно:
- одна актуальная импортная запись на один `TMC_UID`
- `MANUALENTER = 'N'` для внешних данных
- нормализованные штрихкоды
- не `NULL` в обязательных упаковочных коэффициентах

## Риски и ограничения

- интеграция жестко привязана к именам таблиц и к SQL-строкам, собранным в коде
- отдельного стабильного API или версии контракта в коде нет
- отсутствие прав хотя бы на один объект `SUPERMAG` ломает отдельные экраны во время выполнения
- некоторые запросы ожидают, что во внешней системе всегда есть одиночный скалярный результат
- приложение фактически считает `SUPERMAG / Сферу` каноническим источником товарных и заказных данных
- для `RABAEV.SFERA_EAN` не найден уникальный индекс по `TMC_UID`
- функции `RRL_SFERA_EAN_*` используют `ROWNUM <= 1`, поэтому дубли по одному товару делают результат недетерминированным

## Минимальный чек-лист запуска интеграции

Чтобы интеграция `WindowsApplication2` с `Сферой / SUPERMAG` заработала, нужно проверить:
- в `RABAEV.RRL_CONSTANTS` заполнен `EXT_BASE_CONNECTION_STRING`
- Oracle-пользователь может подключиться к `SUPERMAG`
- есть права чтения на все перечисленные объекты
- есть права `EXECUTE` на `SUPERMAG.fill_mon_wms_stbypall`
- существует тестовый документ в `SMDOCUMENTS` и строки к нему в `SMSPEC`
- существует тестовый товар в `SMCARD`, `SMCARDPROPERTIES` и `SMSTOREUNITS`
- при необходимости создана и заполнена `RABAEV.SFERA_EAN`
