# Манифест нового окружения БД

Этот документ описывает рекомендуемое целевое окружение БД для проекта `WindowsApplication2`, чтобы избежать конфликтов по правам, Oracle client, сервисам и переменным окружения.

## Цель

Нужно получить отдельное, чистое и воспроизводимое Oracle-окружение для:
- схемы WMS `RABAEV`
- внешней ERP-интеграции `SUPERMAG` / `Сфера`
- безопасного подключения desktop-приложения `WindowsApplication2`

Главный принцип:
- сервер Oracle должен быть изолирован от рабочей Windows-машины разработчика
- приложение должно подключаться к БД по сети
- системные DBA-права не должны использоваться приложением

## Рекомендуемая ОС для VM

Рекомендуемый вариант:
- `Windows Server 2012 R2` или `Windows Server 2016`

Почему:
- проще сопровождать старый Oracle 11g XE и старые Windows-клиенты
- меньше сюрпризов с сетевыми именами, кодировкой и Oracle Net
- ближе к историческому стилю эксплуатации этого проекта

Допустимый вариант:
- `Windows 10 x64` в отдельной VM

Менее предпочтительный вариант:
- Linux VM

Почему Linux хуже для этого проекта:
- сама БД на Linux работать будет, но исторически проект ближе к Windows-окружению
- больше накладных различий при настройке путей, служб и администрирования
- сложнее отлаживать старую интеграцию, если команда работает в Windows

Итог:
- для минимизации рисков лучше отдельная `Windows VM`

## Какой Oracle ставить

Рекомендуемая версия:
- `Oracle Database 11g Express Edition`

Почему именно 11g XE:
- лучше совместим со старым приложением на `System.Data.OracleClient`
- ближе по эпохе и поведению к исходному проекту
- проще для небольшого тестового и эксплуатационного стенда
- достаточно для одной схемы WMS и одной схемы внешней ERP

Не рекомендую как основной вариант:
- Oracle 18c/21c/23c

Почему:
- выше риск несовместимости со старым приложением и историческими SQL-объектами
- больше шансов поймать проблемы не в бизнес-логике, а в версии Oracle

Если нужен только тестовый стенд:
- можно использовать не XE, а обычный Oracle Standard/Enterprise той версии, которая доступна в инфраструктуре
- но для этого проекта ориентир все равно лучше держать на семействе `11g`

## Сетевая и инстансная модель

Рекомендуемая модель:
- одна отдельная VM
- один Oracle instance
- один service name, например `WMS11G`

Не нужно:
- поднимать несколько SID вроде `XE`, `DBWMS`, `DBWMS01` на одной машине без строгой необходимости
- смешивать старые и новые инстансы в одном listener

Рекомендуемые сетевые параметры:
- hostname VM, например `wms-db`
- порт `1521`
- service name `WMS11G`

Пример TNS-алиаса:

```ora
WMS11G =
  (DESCRIPTION =
    (ADDRESS = (PROTOCOL = TCP)(HOST = wms-db)(PORT = 1521))
    (CONNECT_DATA =
      (SERVER = DEDICATED)
      (SERVICE_NAME = WMS11G)
    )
  )
```

## Какие пользователи создать

Минимально рекомендованный набор пользователей:

### `SYSTEM`

Назначение:
- только для первичной установки Oracle
- только для создания схем, выдачи прав и обслуживания

Правило:
- не использовать из приложения

### `RABAEV`

Назначение:
- основная схема WMS
- все таблицы, функции, процедуры, пакеты и триггеры приложения

Что хранится в схеме:
- WMS-таблицы
- права пользователей
- транспортные и складские сущности
- локальная проекция `SFERA_EAN`
- PL/SQL-логика приложения

Правило:
- это основной пользователь, под которым подключается `WindowsApplication2`

### `SUPERMAG`

Назначение:
- отдельная схема внешней ERP `Сфера`

Что хранится в схеме:
- ERP-таблицы и представления, которые читает WMS
- `SMCARD`
- `SMCARDPROPERTIES`
- `SMDOCUMENTS`
- `SMSPEC`
- `SMCLIENTINFO`
- `SMSTORELOCATIONS`
- `SMCOMMONBASES`
- `MON_WMS_STBYPALL`
- процедура `fill_mon_wms_stbypall`

Правило:
- приложение не должно логиниться как `SUPERMAG`
- схема нужна как внешний источник данных

### Опционально `WMS_DEPLOY`

Назначение:
- технический пользователь для развертывания и обновления схем

Когда нужен:
- если хочется отделить эксплуатацию от DBA
- если обновления схемы будет выполнять не `SYSTEM`, а отдельный техпользователь

Для небольшого стенда можно обойтись без него.

## Как развести `RABAEV` и `SUPERMAG`

Правильное разделение:
- `RABAEV` это схема WMS
- `SUPERMAG` это схема внешней ERP
- это должны быть разные пользователи и разные пространства ответственности

Почему это важно:
- WMS не должен иметь права владельца над внешней ERP
- ERP-данные должны читаться как внешние
- проще понимать, какие таблицы являются мастер-источником, а какие локальной копией или операционным слоем

Рекомендуемая модель прав:
- владелец объектов WMS: `RABAEV`
- владелец объектов ERP: `SUPERMAG`
- приложение подключается под `RABAEV`
- `RABAEV` получает только нужные права `SELECT` и `EXECUTE` на объекты `SUPERMAG`

Рекомендуемые grants:
- `GRANT SELECT ON SUPERMAG.SMCARD TO RABAEV`
- `GRANT SELECT ON SUPERMAG.SMCARDPROPERTIES TO RABAEV`
- `GRANT SELECT ON SUPERMAG.SMSTOREUNITS TO RABAEV`
- `GRANT SELECT ON SUPERMAG.SMDOCUMENTS TO RABAEV`
- `GRANT SELECT ON SUPERMAG.SMSPEC TO RABAEV`
- `GRANT SELECT ON SUPERMAG.SMCLIENTINFO TO RABAEV`
- `GRANT SELECT ON SUPERMAG.SMSTORELOCATIONS TO RABAEV`
- `GRANT SELECT ON SUPERMAG.SMCOMMONBASES TO RABAEV`
- `GRANT SELECT ON SUPERMAG.MON_WMS_STBYPALL TO RABAEV`
- `GRANT SELECT ON SUPERMAG.vcardstoreprop_rc TO RABAEV`
- `GRANT EXECUTE ON SUPERMAG.fill_mon_wms_stbypall TO RABAEV`

Что не нужно делать:
- не создавать объекты `SUPERMAG` внутри `RABAEV`
- не выдавать `DBA` пользователю `RABAEV`
- не подключать приложение под `SYSTEM`

## Как наполнять схемы

### Схема `RABAEV`

Разворачивается из подготовленного набора:
- [create_schema.sql](C:\projects\TMS\db\windowsapplication2_xp12_oracle\create_schema.sql)

После создания схемы нужно:
- создать таблицы
- создать последовательности
- создать функции, процедуры, пакеты и триггеры
- загрузить стартовые данные

Стартовые данные должны включать минимум:
- справочники товаров WMS
- пользователей WMS
- группы пользователей
- права
- склады
- ячейки
- маршруты и транспортные справочники, если используются
- константы `RRL_CONSTANTS`, включая строку подключения к `SUPERMAG`

### Схема `SUPERMAG`

Есть два варианта:

1. Полная схема ERP
- если доступен реальный дамп или реальная БД `SUPERMAG`
- лучший вариант для полноценной интеграции

2. Минимальный тестовый слой
- создать только те таблицы и представления, которые реально читает `WindowsApplication2`
- загрузить туда тестовые товары, документы, строки и контрагентов

Для разработки и первого запуска этого достаточно.

## Как подключить `WindowsApplication2` без конфликтов

Главное правило:
- Oracle Server живет в отдельной VM
- на машине с приложением локальный Oracle Client больше не обязателен

Рекомендуемый режим на машине приложения:
- `Oracle.ManagedDataAccess` в составе самого приложения
- без установленного Oracle Client
- без зависимости от `oci.dll`

Почему так:
- проект переведен на `Oracle.ManagedDataAccess`
- managed-провайдер работает без установленного Oracle Client
- это убирает конфликт разрядностей `x86/x64` и проблему `BadImageFormatException`

Что важно на клиентской машине:
- не держать старые Oracle client в `PATH`
- не смешивать старые XE server bin и старые client bin
- держать один актуальный способ резолва `Data Source`
- при необходимости использовать `tnsnames.ora` или явный `HOST:PORT/SERVICE`

Рекомендуемая клиентская конфигурация:
- локальный Oracle Client не установлен
- строка подключения использует прямой `Data Source=(DESCRIPTION=...)`
- приложение подключается как `RABAEV`
- внешняя ERP читается через grants на `SUPERMAG`

Пример строки подключения WMS:

```text
Data Source=(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=wms-db)(PORT=1521))(CONNECT_DATA=(SERVICE_NAME=WMS11G)));User ID=RABAEV;Password=<пароль RABAEV>
```

Пример строки подключения к внешней ERP в `RRL_CONSTANTS`:

```text
Data Source=(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=wms-db)(PORT=1521))(CONNECT_DATA=(SERVICE_NAME=WMS11G)));User ID=RABAEV;Password=<пароль RABAEV>
```

Почему строка такая же:
- в текущей архитектуре приложение сначала подключается к Oracle как `RABAEV`
- а доступ к `SUPERMAG` идет через SQL и grants внутри того же Oracle-инстанса

Если `SUPERMAG` будет жить в другой БД:
- тогда в `EXT_BASE_CONNECTION_STRING` нужно указывать отдельный service name
- например `Data Source=(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=supermag-db)(PORT=1521))(CONNECT_DATA=(SERVICE_NAME=SUPERMAG11G)));User ID=<integration_user>;Password=<pwd>`

## Рекомендованная финальная архитектура

Лучший практический вариант для этого проекта:
- отдельная Windows VM
- Oracle 11g XE
- один service name `WMS11G`
- схема `RABAEV` для WMS
- схема `SUPERMAG` для внешней ERP
- приложение `WindowsApplication2` запускается на другой машине
- на клиентской машине Oracle Client не установлен

## Что это дает

- нет зависимости от локального Oracle Client
- нет коллизий по `PATH`
- нет смешения старых сервисов и listener-конфигураций
- DBA-права отделены от прикладного пользователя
- `RABAEV` и `SUPERMAG` разведены по ответственности
- проще переносить стенд, делать резервные копии и воспроизводить окружение

## Минимальный план внедрения

1. Поднять отдельную Windows VM.
2. Установить Oracle 11g XE.
3. Создать service name `WMS11G`.
4. Создать схему `RABAEV`.
5. Развернуть WMS-объекты из [create_schema.sql](C:\projects\TMS\db\windowsapplication2_xp12_oracle\create_schema.sql).
6. Создать схему `SUPERMAG`.
7. Загрузить в `SUPERMAG` минимальный набор таблиц и тестовых данных.
8. Выдать `RABAEV` права `SELECT/EXECUTE` на `SUPERMAG`.
9. На клиентской машине убрать старые Oracle client и их следы из `PATH`.
10. Настроить `tnsnames.ora` или прямой `HOST:PORT/SERVICE` и подключить `WindowsApplication2`.

Для админской зачистки хвостов Oracle в Windows можно использовать скрипт:
- [cleanup-oracle-remnants-admin.ps1](c:/projects/TMS/scripts/cleanup-oracle-remnants-admin.ps1)
