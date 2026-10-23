# C0162 — права общего пула, включая повтор

Запрос зарегистрирован24-м. После RELEASE C0161 начинай без ожидания владельца. Прочитай AGENTS/wiki/index и focused trade_pool_eligibility_20261023, действующие scoped native patterns. Сначала ACK точных путей. Root принимает C0161, TOPUP-пути не трогай.

## Проверенные факты root

C0160 native9/9/9 установлен. Отдельные root миграции trade_pool_guard5/4/5 и trade_pool_empty5/4/5 установлены. Их payload не переписывать. Текущий POOL_CMD SHA4ABD6C109C87870EF6D042B1F03D25FE7A60F64E7E58EB4A39DA1C45F4DE796F. GUARD7D6E1781DB7F46AC66105865B83D583C2FF35A9A905C1D8B91C97421CF0A68EE. INVALID0.

Реальный MAIN20 получил SOFT20, launch wave620 потребил её в HARD20 ровно раз; следующая потребность300 получила230; неподходящий срок3650дней получил0. Два конкурентных расчёта не задвоили230. Cleanup завершён250/H0, все250кодов/атрибутов/адрес восстановлены, own CASE1175 отменена; чужие данные не трогать. Source TC03.SAP разрешает только SNS: проба BLC справедливо отказала SOURCE_OWNER_NOT_PERMITTED, другой owner не проверен этим тестом.

## Остаток задачи

1. PoolService.preview не получает actor, snapshot отдаёт строки/доли всего пула. API зависимости проверяют permission без warehouse аргумента. Нужна текущая область склада и видимость собственников перед ответом. Не отдавай неполный снимок как полный план: расчету нужен весь авторитетный снимок, пользователю — разрешённое представление/явный отказ по существующему правилу. Минимальное решение по имеющимся контрактам.
2. execute POOL_CMD вызывает legacy RRL_HAS_WRIGHT(stock_reservation_edit), который читает только legacy группы, хотя API принимает современные назначения. Поддержать действующее назначение на правильный склад, сохранив legacy/GLOBAL_ADMIN. Не переписывать глобальный RRL_HAS_WRIGHT ради одного сценария.
3. Текущий owner operate проверяется в execute, но cached receipt возвращается раньше execute. Проверь настоящую текущую RRL_STOCK_POSTING_API (свежий экспорт root: runtime/test-evidence/tradecase/2026-10-23/T08/RRL_STOCK_POSTING_API.sql). До replay нет pool scope-hook. Закрой отзыв warehouse/permission/owner и для неизменного повтора, не пересчитывая старую квитанцию по сегодняшним количествам. Используй владельца/записанный resolved plan для допущенных источников. Не делай второй ledger. Если нужна одна строка hook в POSTING_API — разрешено именно для проверки текущих прав до replay, без изменения проводки/планирования/блокировок прочих команд.
4. Root уже убрал локальный catch PoolService: общий StockPostingError handler сохраняет неизвестный исход,7ASGI tests/retailcase/test_pool_outcomes.py PASS. Это не возвращать назад.

## Передача

Нужны цельный минимальный NOT_APPLIED native kit с before/after SHA/rollback/verify, backend READY, focused tests (scoped role, чужой склад, отзыв owner после сохранённой квитанции), объяснение read/execute/replay границ и точный RELEASE. Native только READ ONLY до root apply; новых stock fixtures не создавать. Root выполнит живые HTTP/Oracle/SQL и завершит приемку. Snapshot для алгоритма должен оставаться reader-independent. Не включать approval_available и не объявлять весь T08 завершённым. Не менять применённые комплекты. Dist не собирать.
