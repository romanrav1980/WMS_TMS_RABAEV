# NI04.1: матрёшка в существующем задании размещения

052 APPLIED в RABAEV/orcl, RRL_STOCK_HU_TASK/read/commands/task-plan/root VALID. [[retailcase_ni041_hu_move_20261009]].

HU_PLAN_MOVE создаёт прежнее MANUAL/PUTAWAY с qty1/unit HU/QTY_MODE PALLET, фактическим parent UID/from/to и frozen HU_CONTENT_VERSION. Количество1 означает верхнее физическое место, не товарную BASE единицу. Исходный план immutable; изменение требует отмены/нового планирования.

Назначение/начало используют существующий WarehouseTaskService и RRL_TASK_RESOURCE_POLICY (права, смена, сессия, оборудование, текущее физическое действие). Тот же complete API распознаёт container и вызывает root HU_TASK_COMPLETE. Root перемещает всё дерево, пишет по каждому количественному листу actual BASE move, завершает задание1HU, resource fact/session и существующий WT sync key в одной транзакции. Второй планировщик/журнал/очередь не созданы.

При движении собственной задачей read snapshot исключает только её ID; другие physical tasks/ancestor tasks блокируют упаковку/движение. Direct root HU_MOVE не может обойти выданное задание. Child CASE lot требуется включать через целый carrier; этот следующий slice ещё открыт.

Адресный real case: plan/replay → existing assign/start → complete/replay1HU, TOP/BOX/leaf5/H2 в target, owner retained; stock move5EA и sync ровно один. Private P/H очищены после explicit unpack через root. Admin force path в dev не объявляет отдельную приёмку обычного квалифицированного водителя.

API plan-move и кнопка создания задания добавлены в existing HU ARM; далее оператор идёт в прежние складские задания/ТСД. GS1 incoming normalization переиспользуется. Physical slot/weight/height пока сохраняют ограничения051, следующий ticket их реализует. Независимый browser/marked/concurrency scope остаётся открытым.

SQL decision after052: HU snapshot4.23ms/14, bounded200 nodes/depth16 with current key lookups retained; no new index without bottleneck. Physical-slot continuation is now [[retailcase_ni041_hu_slots_20261010]], not full NI04.1 closure.
