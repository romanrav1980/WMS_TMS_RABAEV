# NICORA — структура исходников и режим разработки

7 октября 2026 года владелец поручил направлять минимум 80% ресурсов на создание функционала. Дополнительные тестовые прогоны и Oracle-эксперименты остановлены; текущая задача — завершить независимое ревью исходников NS00 и показать структуру. Прежние автоматические gates не возобновлять вопреки этому поручению. Ревью исходников не объявлять независимой проверкой поведения.

## Существующая структура

```text
api/wms_api_server/app/              FastAPI backend
  main.py                           Сборка приложения
  routers/                          HTTP endpoints
  services/                         Существующие прикладные сценарии
  modules/transport/
    public.py                       Публичный контракт
    domain/transport_type.py        Выделенное предметное правило
  workers/                          Фоновые процессы обмена
  middleware/                       Аудит API
  auth.py, schemas.py               Авторизация и модели контрактов
  db.py, oracle_gateway.py          Oracle и legacy-команды
admin/wms_admin_frontend/src/        React интерфейс администратора
  components/, data/, replay/       Экраны, загрузка данных, replay
  api.ts, App.tsx                    API клиент и сборка интерфейса
terminal/wms_terminal_web/src/       React/Web/PWA терминал
  api/, scanner/, store/            API, сканирование, локальный журнал
  components/, App.tsx              Компоненты и сборка терминала
db/
  windowsapplication2_xp12_oracle/   Исходные legacy SQL
  migrations/, compatibility_fixes/ Изменения RABAEV
  fixtures/nicora_ns00/             Тестовые SQL NS00
tools/nicora_environment/            Подготовка стенда NS00
tools/oracle_apply/                  Применение SQL
scripts/                            Подготовка окружения и запуск
serv.bat, front.bat, terminal.bat     Точки локального запуска
wiki/                               Требования, решения, спринты
config/architecture/                Правила модульности и legacy debt
```

Весь backend ещё не переведён в модули. Наличие существующих сервисов и экранов не означает готовность функций по ТЗ NICORA. Инструменты NS00 — инфраструктура, не новый складской функционал.

## Новые функции

Независимое ревью исходников NS00 завершено: **APPROVE_SOURCE**, блокирующих дефектов не найдено. [Итог ревью](../../runtime/test-evidence/nicora_ns00_close/review-summary.md). Новых тестовых прогонов не было.

Развивать связанную функцию в `app/modules/<area>/`: `api` принимает HTTP, `application` координирует сценарий, `domain` содержит правила, `infrastructure` работает с Oracle и внешними системами. `public.py` и `contracts.py` задают доступ соседних модулей. Frontend — `src/features/<area>/` по мере появления функции; пустые каталоги заранее не создавать. Данные остаются в RABAEV.

Основание: [[../architecture/nicora_modular_development_contract]]. Модульность сохраняется; объём проверок подчиняется последнему поручению владельца. Не расширять инфраструктурные задачи вместо реализации бизнес-сценария.

После утверждения источников основной план — NI01–NI08. NI01 завершён по реализации; следующий NI02. Реестр NS01–NS04 ведётся внутри доработки; промышленная приёмка отдельно от статуса кода.

## Реализация NI01

```text
app/modules/master_data/       WMS policy маркировки и версионные профили
app/modules/integrations/
  domain/                      ARTMAS10/товар/нормализованный заказ
  application/                 inbox и Protocol-контракты API
  infrastructure/              Oracle master/supply, amendments, gateway/recovery, outbox/ACK
  api/                         XML ingress и обмен
  public.py                    сборка и доступ соседних модулей
app/modules/inventory/
  domain/                      SSCC/GS1-128/ZPL, canonical mark, количество единицы
  application/ports.py         контракт команд и read models
  infrastructure/              receipt/marks, placement, labels, config, reconciliation, queries
  api/receiving_routes.py       DTO/права/HTTP
  public.py                    команды и публичный состав паллеты
app/workers/sap_*              файловый вход/выход/ACK
wiki-raw/wms_admin_ui_reference/receiving.html + receiving.js
db/migrations/2026-10-07_ni01_sap_retail/001..007_* — RABAEV
exchange/contracts/ni01/       XML-примеры, не импортированные данные
sap-artmas.bat / sap-supply.bat / sap-receipts.bat / sap-ack.bat
```

Транзакцией приёмки владеет Receiving; остаток проводит существующий Oracle event trigger. Регуляторные записи проходят через существующие пакеты. API зависит от application Protocols, конкретные Oracle реализации собираются через public/main. Legacy warehouse-task мост использует публичный модуль. Действующий raw UI дополнен в его принятом месте; отдельный пустой React-проект не создавался. [Запуск и ограничения](../runbooks/nicora_ni01_sap_retail.md).
