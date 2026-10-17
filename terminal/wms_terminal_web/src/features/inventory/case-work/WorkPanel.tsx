import { useEffect, useState } from "react";
import type { CaseWorkState } from "./useCaseWork";
import { ReasonNotice } from "./ReasonNotice";

const DEFAULT_CLAIM = "Принимаю задание в своей рабочей сессии";
const DEFAULT_START = "Начинаю сборку в своей рабочей сессии";

export function WorkPanel({ work }: { work: CaseWorkState }) {
  const [selection, setSelection] = useState("");
  const context = work.context, sessions = work.sessions;
  // Текст по умолчанию соответствует действию; введённый оператором текст при смене действия не затирается.
  const defaultReason = context?.status === "ASSIGNED" ? DEFAULT_START : DEFAULT_CLAIM;
  const [reason, setReason] = useState(defaultReason);
  useEffect(() => { setReason(old => (old === DEFAULT_CLAIM || old === DEFAULT_START ? defaultReason : old)); }, [defaultReason]);
  useEffect(() => { setSelection(context?.resource_session_id ? String(context.resource_session_id) : ""); }, [context?.task_id, context?.assignment_version, context?.resource_session_id]);
  if (!context || !sessions) return null;
  const session = sessions.items.find(row => String(row.resource_session_id) === selection);
  const foreign = context.assigned_to !== null && context.assigned_to !== context.current_actor;
  const supported = !foreign && (context.status === "NEW" || context.status === "ASSIGNED");
  const pending = !!work.journal?.pending;
  const disabled = work.busy || work.blocked || pending;
  const ready = supported && !!session?.ready && Array.from(reason.trim()).length >= 8 && Array.from(reason).length <= 500 && !disabled;
  return <section className="cw-card" aria-label="Рабочая сессия и действие">
    <div className="cw-section-heading"><span className="cw-resource-icon" aria-hidden="true">◉</span><div><span className="cw-eyebrow">ВАШ РЕСУРС</span><h2>Рабочая сессия</h2></div></div>
    {sessions.items.length > 0 ? <label className="cw-field">Выберите свою сессию
      <select value={selection} disabled={disabled || !supported} onChange={event => setSelection(event.target.value)}
        title="Выбрать собственную активную сессию текущего склада; сервер повторно проверит её перед действием" data-help-id="case-work.session.select">
        <option value="">Выберите сессию</option>{sessions.items.map(row => <option key={row.resource_session_id} value={row.resource_session_id}>
          {row.resource_code}{row.equipment_id ? ` · техника ${row.equipment_id}` : ""}{row.ready ? " · доступна" : " · требуется проверка"}
        </option>)}
      </select>
    </label> : <p>Нет собственных активных сессий на этом складе. Обратитесь к старшему смены для назначения ресурса и открытия смены.</p>}
    {session && !session.ready && <ReasonNotice reason={session.reason} />}
    {supported ? <>
      <label className="cw-field">Комментарий к действию<textarea value={reason} maxLength={500} rows={2} disabled={disabled}
        onChange={event => setReason(event.target.value)} title="Указать причину принятия или запуска; минимум 8 значимых символов, запись сохраняется в журнале" data-help-id="case-work.reason" /></label>
      <p className="cw-muted">Сессия проверена на момент чтения. Перед запуском сервер заново проверит назначение, смену и готовность задания.</p>
      <button className="cw-primary" type="button" disabled={!ready} onClick={() => session && void work.submit(session, reason)}
        title={pending ? "Сначала получите подтверждение сохранённой операции" : context.status === "NEW" ? "Закрепить задание за вами и выбранной рабочей сессией; товар не списывается" : "Зафиксировать начало сборки в вашей рабочей сессии; сам отбор товара выполняется отдельно"}
        data-help-id="case-work.command.submit">{work.busy ? "Проверка…" : context.status === "NEW" ? "Принять в работу" : "Начать сборку"}</button>
    </> : <p>{foreign ? "Задание назначено другому оператору. Передача выполняется старшим смены через отдельное действие."
      : context.status === "IN_PROGRESS" || context.status === "PARTIAL" || context.status === "WAIT_REPLENISHMENT"
      ? "Задание уже запущено. Продолжите отбор в рабочем месте сборки."
      : "Принятие или запуск недоступны в текущем состоянии. Обновите данные или обратитесь к старшему смены."}</p>}
  </section>;
}
