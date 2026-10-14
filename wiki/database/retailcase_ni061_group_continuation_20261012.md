# NI06.1: размещение и продолжение смешанной группы

704/708/713 применены в RABAEV, USER_ERRORS=[]/INVALID=[]. Сохранены live исходники, SHA и парные rollback. Общий HU slot разрешает системные ворота только исходному whole group из RRL_IW_GROUP_RECEIPT и его неизменного outbound dock. Остальные системные ячейки сохраняют запрет. Исполнение прежнего HU task восстанавливает receipt ID из RRL_IW_GROUP_PUT_PLAN, а не ввода оператора. Quantity owner прежний RRL_STOCK_POSTING_API.

Actual702: task 1HU передвинул два товарных листа по3EA; поздний rollback отменяет оба движения и proof, точный повтор сохранён. Private target получил явные limits2.5M/100KG и HU_CELL_HEIGHT_UNIT=M вместо неопределённого legacy значения. Actual709 освобождает ответственность первого плеча без изменения количества. Actual710 использует прежние конструкторы СТ/назначение/контроль9 кодов.

713 снимает прежний UNIT-only запрет консолидации исключительно для authoritative interwarehouse_onward_source с group_receipt_operation_id. Проверки целого дерева, исходных единиц/версий/остатка, существующего QC, первоначальных адресатов и двух original ST сохранены. Actual711: whole load второго плеча, два dispatch по3EA, P0/H0; поздний rollback и replay пройдены.

712: выезд второго плеча записан и сохранён в context671. Приёмка магазина ещё не выполнена: текущий RRL_STORE_MARK_CORE не поддерживает BOX/PALLET receipt profiles и возвращает supported=false. Это следующий конкретный функциональный пробел. Не повторять factory669/670/671/672/673 и промежуточные P3 assertions702/711; context671 содержит все результаты. Контрольный P20/H20 сохранён.

Миграции: [system target](../../db/migrations/2026-10-12_ni061_group_system_target/apply.sql), [task origin](../../db/migrations/2026-10-12_ni061_group_task_origin/apply.sql), [load profiles](../../db/migrations/2026-10-12_ni061_group_load_profiles/apply.sql). SQL decision ожидает адресного чтения после полного цикла.
