import type { Context } from "./contracts";

const STATUS: Record<string, string> = { NEW: "Ожидает принятия", ASSIGNED: "Назначено", IN_PROGRESS: "Сборка идёт",
  PARTIAL: "Подобрано частично", WAIT_REPLENISHMENT: "Ожидает пополнения", WAIT_CONTROL: "Ожидает контроля",
  CONTROLLED: "Контроль пройден", READY_TO_SHIP: "Готово к отгрузке", SHIPPED: "Отгружено", CANCELLED: "Отменено", DONE: "Завершено" };
export function TaskCard({ context }: { context: Context }) {
  return <section className="cw-card cw-task" aria-label="Текущее складское задание">
    <div className="cw-task-icon" aria-hidden="true">▣</div><div className="cw-task-copy">
      <span className="cw-eyebrow">СКЛАДСКОЕ ЗАДАНИЕ · СБОРКА CASE</span>
      <h1>Задание №{context.task_id}</h1><p className="cw-state">{STATUS[context.status || ""] || context.status || "Состояние неизвестно"}</p>
      <p className="cw-muted">{context.assigned_to ? `Исполнитель: ${context.assigned_to}` : "Исполнитель пока не назначен"}</p>
      {context.started_at_instant && <p className="cw-start">Начато <time dateTime={context.started_at_instant}>{new Date(context.started_at_instant).toLocaleString("ru-RU", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" })}</time><span className="cw-muted"> · время этого устройства</span></p>}
    </div>
    <details className="cw-details"><summary title="Показать версии и исходное время сервера для диагностики" data-help-id="case-work.diagnostics">Данные задания</summary>
      <dl><dt>Склад</dt><dd>{context.warehouse_id}</dd><dt>Версия назначения</dt><dd>{context.assignment_version}</dd>
        <dt>Версия состава</dt><dd>{context.content_version ?? "—"}</dd><dt>Исходный момент начала</dt><dd>{context.started_at_instant || "Не задан"}</dd>
        <dt>Зона смены</dt><dd>{context.started_shift_time_zone || "Не подтверждена"}</dd></dl>
    </details>
  </section>;
}
