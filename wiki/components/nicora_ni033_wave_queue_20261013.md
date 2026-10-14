# NI03.3: единая выбранная волна и очередь

886–890: lean GET /api/picking/waves/{id}/header переиспользует выделенный existing SQL header. PickingService get_wave/get_wave_header остаются фасадами. Монолит уменьшен2320→2284 lines, baseline tightened downward; architecture690/0cycles/76 allowances PASS.

WaveQueueReads оборачивает существующие readers в native current actor scope и одну READ ONLY транзакцию. Список: active RUSERS/pick_wave_view; GLOBAL_ADMIN сохраняет заданный фильтр, прочим автоматически свойWARE и отказ явно чужого фильтра. Detail/readiness/reservations/replenishment/tasks проверяют wave scope перед legacy query. Header не подтягивает all composition. Legacy full-detail unbounded order/line lists остаются inventory backlog для крупных волн.

UI deep link вне первых100: header, pinned selected wave, связанные execution/pick/progress/queue. Loading до read отключает старые действия; epoch/actor/API guard игнорирует поздние ответы, saved pending удерживает wave. Source availability скрывается при смене выбора.

Actual889: header403 безorders, admin scoped warehouse20052672 returned8 matching rows; inactive/foreign wave551 denied403 до legacy read. Browser888: selected403/MIXED172 иall3panels403. JS891 delayedA cannot overwriteB/savedB blocksA/no writes. Latest890 pinned/loading browser ожидает; nonadmin ownWARE positive ещё не live proved.

SQL892: header18.61ms/273buf, filtered list22.792ms/37buf, actor/currentright41.049ms/27buf (2executions). Inventory decision retain existingkeys/bounded queue/noindex; sustained>500ms→plan/stats. Не нагрузочная приёмка.
