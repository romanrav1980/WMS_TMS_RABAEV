# Qwen:227 — штатное размещение маркированной паллеты
Новая собственная фикстура исходной отгрузки->225manifest->226receipt. Уже DONE953 не повторять/не удалять.
Проверить original INTERWARE_PUTAWAY_PLAN/TaskPlan/TaskCore/TransferCore; exact physical keys/quantity/UOM/no HARD/versioned current snapshot; чужая единица/нецелый состав/резерв/несколько cell/изменённые target trip/dock/capacity ->отказ без P.
PLANNED->ASSIGNED->COMPLETE с настоящей квалифицированной PUTAWAY машинной сессией; без сессии обычный actor получает TASK_MACHINE_SESSION_REQUIRED. Не выдавать forceassign для обхода.
Outer rollback после native execute сохраняет sourceP/units/task/session; concurrency different IDs один победитель; sameID saved replay без второй проводки.
DONE953/sync читать из RRL_WAREHOUSE_TASK_SYNC, не несуществующий task.SYNC_STATUS. Source0/target3H0/same units3/codes6/version+1/no births/original first customer fulfillment retained/immutableplacement1.
Current actor warehouse/right before saved planning and completion replay; UI existing task workflow uses confirmed native results.
Длинные SQL matrix bounded10000/currentUID/indexed original key; явное решение по slow SQL.
Не заявлять полную агрегацию/матрешку/межскладское второе плечо/госACK этим срезом.
