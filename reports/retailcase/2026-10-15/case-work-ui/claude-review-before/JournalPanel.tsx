import type { CaseWorkState } from "./useCaseWork";
import { ReasonNotice } from "./ReasonNotice";

export function JournalPanel({ work, actor, task }: { work: CaseWorkState; actor: string; task: number | null }) {
  const pending = work.journal?.pending;
  const last = work.journal?.last;
  const own = pending?.actor === actor && pending.server === location.origin;
  const result = last?.intent.actor === actor && last.intent.server === location.origin ? last : null;
  return <>
    {pending && <section className="cw-card cw-pending" aria-label="Сохранённая операция">
      <span className="cw-eyebrow">ОЖИДАЕТ ПОДТВЕРЖДЕНИЯ</span><h2>Запрос сохранён</h2>
      <p>Задание №{pending.task_id} · {pending.body.action === "CLAIM" ? "Принять в работу" : "Начать сборку"}</p>
      <p className="cw-muted">Новая операция недоступна, пока сервер не подтвердит результат этой.</p>
      {!own && <p role="alert">Войдите как {pending.actor} на исходном сервере. Сохранённый запрос остаётся без изменений.</p>}
      <div className="cw-actions">
        <button type="button" onClick={work.refresh} disabled={work.busy} title="Прочитать серверный результат сохранённой операции; ничего не отправлять повторно" data-help-id="case-work.receipt.read">Прочитать результат</button>
        <button type="button" onClick={() => void work.retry()} disabled={work.busy || !own || work.blocked}
          title="Явно повторить исходный запрос с теми же данными и operation_id; новая операция не создаётся" data-help-id="case-work.receipt.retry">Повторить исходный запрос</button>
      </div>
      {pending.task_id !== task && <a href={`/case-work/?task_id=${pending.task_id}`} title="Открыть исходное задание; сохранённый запрос остаётся в журнале" data-help-id="case-work.receipt.task">К исходному заданию</a>}
      <details className="cw-details"><summary title="Показать идентификатор и контрольную сумму сохранённого запроса" data-help-id="case-work.receipt.details">Данные операции</summary><code>{pending.body.operation_id}</code><code>{pending.request_sha256}</code></details>
    </section>}
    {!pending && result && <section className={`cw-card ${result.ack.outcome === "APPLIED" ? "cw-confirmed" : "cw-rejected"}`} aria-label="Подтверждённый результат" role="status">
      <h2>{result.ack.outcome === "REJECTED" ? "Сервер сохранил отказ" : result.ack.changed ? "Действие подтверждено" : "Состояние уже установлено"}</h2>
      <p>Задание №{result.intent.task_id} · {result.intent.body.action === "CLAIM" ? "Принятие" : "Запуск"}</p>
      {result.ack.outcome === "REJECTED" && <><ReasonNotice reason={result.ack.error_code} /><p>Исправьте причину и обновите задание. Новое действие отправляется только по вашему нажатию.</p></>}
      <p className="cw-muted">Товарный отбор этой командой не выполняется.</p>
    </section>}
  </>;
}
