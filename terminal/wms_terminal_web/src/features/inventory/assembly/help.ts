// Local control hints (title/data-help-id). Full guidance is the published "assembly-scale" article via NativeHelp;
// these are short in-place explanations, not a parallel knowledge base.
export const ASSEMBLY_ARTICLE_ID = "assembly-scale";

export const help = {
  taskId: { title: "Номер назначенного задания сборки. Прямая ссылка: ?task_id=<номер>.", id: "assembly.task-id" },
  station: { title: "Выберите пост и фактическую тару сборочной тары, подтверждённую весами.", id: "assembly.station" },
  tare: { title: "Свежий замер пустой тары (EMPTY_TARE) для этого поста.", id: "assembly.tare" },
  containerScan: { title: "Отсканируйте физический идентификатор сборочной тары.", id: "assembly.container" },
  openSession: { title: "Открыть сессию укладки на выбранном посту и таре.", id: "assembly.open-session" },
  line: { title: "Позиция задания: артикул и остаток к укладке. Норматив массы должен быть настроен.", id: "assembly.line" },
  quantity: { title: "Количество штук к этой укладке (не масса).", id: "assembly.quantity" },
  sourceScan: { title: "Отсканируйте ячейку отбора источника.", id: "assembly.source" },
  productScan: { title: "Отсканируйте товар перед укладкой.", id: "assembly.product" },
  consent: { title: "Явное подтверждение: после стабилизации веса укладка этого артикула/количества будет принята автоматически.", id: "assembly.consent" },
  startStep: { title: "Начать укладку выбранной позиции.", id: "assembly.start-step" },
  placed: { title: "Подтвердить, что товар физически положен. Это намерение, не доказанный успех.", id: "assembly.placed" },
  finishOpen: { title: "Перейти к завершению: нужен отдельный финальный замер полной тары.", id: "assembly.finish-open" },
  finishPick: { title: "Выбрать подтверждённый финальный замер той же тары и той же сборочной тары.", id: "assembly.finish-pick" },
  finishConfirm: { title: "Завершить укладку этим финальным замером.", id: "assembly.finish-confirm" },
  retry: { title: "Повторить тот же самый запрос без изменений.", id: "assembly.retry" },
  readFirst: { title: "Сначала прочитать текущий результат у сервера, не отправляя повторно.", id: "assembly.read-first" },
  dismiss: { title: "Скрыть сообщение об ошибке.", id: "assembly.dismiss" },
  diagnostics: { title: "Технические данные: устройство, калибровка, версии, время сервера.", id: "assembly.diagnostics" },
  logout: { title: "Выйти из этого поста.", id: "assembly.logout" },
} as const;
