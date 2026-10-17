import { NativeHelp } from "../../platform";
import type { HelpCredentials } from "../../platform";
import { RecoveryPanel } from "../resource-intents/RecoveryPanel";
import type { CaseWorkState } from "./useCaseWork";
import { ReasonNotice } from "./ReasonNotice";

export function JournalPanel({ work, actor, task, credentials }: { work: CaseWorkState; actor: string; task: number | null; credentials?: HelpCredentials }) {
  const pending = work.journal?.pending;
  const last = work.journal?.last;
  const own = pending?.actor === actor && pending.server === location.origin;
  // Один журнал на устройство: архив последнего подтверждения не привязан к открытому заданию. Без проверки task_id
  // карточка «подтверждено» показывалась бы под текущим заданием даже для чужого, ранее открытого номера.
  const lastOwn = last?.intent.actor === actor && last.intent.server === location.origin;
  const result = last && lastOwn && last.intent.task_id === task ? last : null;
  const elsewhere = last && lastOwn && last.intent.task_id !== task ? last : null;
  const abandoned = work.journal?.abandoned;
  const abandonedOwn = abandoned?.intent.actor === actor && abandoned.intent.server === location.origin && abandoned.intent.task_id === task;
  return <>
    {pending && <section className="cw-card cw-pending" aria-label="Сохранённая операция">
      <span className="cw-eyebrow">ОЖИДАЕТ ПОДТВЕРЖДЕНИЯ</span><h2>Запрос сохранён</h2>
      <p>Задание №{pending.task_id} · {pending.body.action === "CLAIM" ? "Принять в работу" : "Начать сборку"}</p>
      <p className="cw-muted">Новая операция недоступна, пока сервер не подтвердит результат этой.</p>
      {!own && <p role="alert">Войдите как {pending.actor} на исходном сервере. Сохранённый запрос остаётся без изменений.</p>}
      <div className="cw-actions">
        <button type="button" onClick={() => void work.readRecovery()} disabled={work.busy || !own || work.blocked} title="Прочитать исходную квитанцию либо подтверждение прекращения; повторного исполнения нет" data-help-id="case-work.receipt.read">Прочитать результат</button>
        <button type="button" onClick={() => void work.retry()} disabled={work.busy || !own || work.blocked || !!work.control}
          title="Явно повторить исходный запрос с теми же данными и operation_id; новая операция не создаётся" data-help-id="case-work.receipt.retry">Повторить исходный запрос</button>
      </div>
      <RecoveryPanel key={pending.body.operation_id} helpSlot={credentials && <NativeHelp articleId="metadata-intent-recovery" credentials={credentials} />} busy={work.busy} own={own} blocked={work.blocked} control={work.control?.body ?? null} read={work.readRecovery} abandon={work.abandon} />
      {pending.task_id !== task && <a href={`/case-work/?task_id=${pending.task_id}`} title="Открыть исходное задание; сохранённый запрос остаётся в журнале" data-help-id="case-work.receipt.task">К исходному заданию</a>}
      <details className="cw-details"><summary title="Показать идентификатор и контрольную сумму сохранённого запроса" data-help-id="case-work.receipt.details">Данные операции</summary><code>{pending.body.operation_id}</code><code>{pending.request_sha256}</code></details>
    </section>}
    {!pending && abandonedOwn && <section className="cw-card" role="status" aria-label="Запрос прекращён сервером"><h2>Исходный запрос прекращён</h2><p>Сервер сохранил подтверждение прекращения. Само задание не отменено; товар не изменён. Новое действие требует свежего состояния задания.</p><details className="cw-details"><summary title="Показать исходную операцию и серверную квитанцию прекращения" data-help-id="metadata-intent.proof.details">Данные подтверждения</summary><code>{abandoned.intent.body.operation_id}</code><code>{abandoned.proof.operation_id}</code></details></section>}
    {!pending && result && <section className={`cw-card ${result.ack.outcome === "APPLIED" ? "cw-confirmed" : "cw-rejected"}`} aria-label="Подтверждённый результат" role="status">
      <h2>{result.ack.outcome === "REJECTED" ? "Сервер сохранил отказ" : result.ack.changed ? "Действие подтверждено" : "Состояние уже установлено"}</h2>
      <p>Задание №{result.intent.task_id} · {result.intent.body.action === "CLAIM" ? "Принятие" : "Запуск"}</p>
      {result.ack.outcome === "REJECTED" && <><ReasonNotice reason={result.ack.error_code} /><p>Исправьте причину и обновите задание. Новое действие отправляется только по вашему нажатию.</p></>}
      <p className="cw-muted">Товарный отбор этой командой не выполняется.</p>
    </section>}
    {!pending && elsewhere && <p className="cw-muted">Есть подтверждённый результат по другому заданию №{elsewhere.intent.task_id}.{" "}
      <a href={`/case-work/?task_id=${elsewhere.intent.task_id}`} title="Открыть задание, к которому относится последний подтверждённый результат" data-help-id="case-work.receipt.elsewhere">Открыть</a></p>}
  </>;
}
