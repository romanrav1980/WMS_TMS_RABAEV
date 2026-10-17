import { PickerTimePanel } from "../picker-time";
import { useState } from "react";
import { NativeHelp, ScanField } from "../../platform";
import { LoginGate } from "../assembly/components/LoginGate";
import { useAssemblyAuth } from "../assembly/useAssemblyAuth";
import { useCaseWork } from "./useCaseWork";
import { TaskCard } from "./TaskCard";
import { WorkPanel } from "./WorkPanel";
import { JournalPanel } from "./JournalPanel";
import "./case-work.css";

function taskNumber(value: string): number | null { return /^\d+$/.test(value) && Number.isSafeInteger(Number(value)) && Number(value) > 0 ? Number(value) : null; }
export function CaseWorkApp() {
  const initial = new URLSearchParams(location.search).get("task_id") || "";
  const [task, setTask] = useState<number | null>(() => taskNumber(initial));
  const [input, setInput] = useState(initial);
  const [inputError, setInputError] = useState("");
  const auth = useAssemblyAuth();
  const work = useCaseWork(task, auth.credentials);
  function openTask(value: string) {
    const id = taskNumber(value.trim());
    if (id === null) { setInputError("Введите или считайте положительный номер задания."); return; }
    setInputError(""); setTask(id);
    const url = new URL(location.href); url.searchParams.set("task_id", String(id)); history.replaceState(null, "", url);
    work.refresh();
  }
  return <main className="cw-app">
    <header className="cw-header"><span className="cw-brand" title="Рабочее место: принять задание сборки и начать его в своей рабочей сессии. Переходы к сборке — внизу экрана" data-help-id="case-work.nav.assembly">◈ Склад <span>Задания и ресурсы</span></span>
      {auth.identity && <div className="cw-header-actions"><span className="cw-operator" title={`Текущий оператор: ${auth.identity.display_name || auth.identity.username} (${auth.identity.username})`} data-help-id="case-work.operator.identity">{auth.identity.display_name || auth.identity.username}</span>
        {auth.credentials && <NativeHelp articleId="case-work" credentials={auth.credentials} />}
        <button type="button" onClick={auth.logout} title="Выйти и удалить пароль из памяти страницы; исходная операция останется в журнале" data-help-id="case-work.logout">Выйти</button></div>}
    </header>
    {!auth.credentials ? <section className="cw-login"><LoginGate auth={auth} purpose="Рабочее место комплектовщика" />
      {work.journal?.pending && <p className="cw-warning">Есть сохранённая операция задания №{work.journal.pending.task_id}. Войдите исходным оператором {work.journal.pending.actor}, чтобы прочитать результат.</p>}
      {work.blocked && work.error && <p role="alert" className="cw-error">{work.error}</p>}</section>
      : <div className="cw-body">
        <section className="cw-task-picker" aria-label="Открыть задание"><ScanField label="Номер задания" value={input} onChange={setInput} onSubmit={openTask} disabled={work.busy} />
          <button type="button" onClick={() => openTask(input)} disabled={work.busy} title="Прочитать состояние указанного задания и ваши рабочие сессии; товарных действий нет" data-help-id="case-work.task.open">Открыть</button>
          <button type="button" onClick={work.refresh} disabled={work.busy} title="Обновить данные и прочитать сохранённый результат; повторная отправка не выполняется" data-help-id="case-work.refresh">Обновить</button></section>
        {inputError && <p className="cw-error" role="alert">{inputError}</p>}
        {work.error && <p className="cw-error" role="alert">{work.error}</p>}
        {work.busy && <p className="cw-muted" role="status">Читаем подтверждённое состояние…</p>}
        <JournalPanel work={work} actor={auth.credentials.username} task={task} credentials={auth.credentials} />
        <PickerTimePanel credentials={auth.credentials} context={work.context} sessions={work.sessions} metadataBlocked={work.busy || work.blocked || !!work.journal?.pending || !work.context} />
        <div className="cw-grid">{work.context && <TaskCard context={work.context} />}<WorkPanel work={work} /></div>
        {!task && <section className="cw-card"><h1>Откройте складское задание</h1><p>Считайте номер задания сканером или перейдите по ссылке старшего смены.</p></section>}
        {work.context && <nav className="cw-card cw-owner-links" aria-label="Продолжить работу">
          <h2>Дальше — отбор товара</h2><p className="cw-muted">Принятие и запуск закрепляют ресурс и время. Товар подтверждается в соответствующем рабочем месте.</p>
          <a href={`/wms-admin/case-pick-tsd.html?case_task_id=${work.context.task_id}`} title="Открыть прежнее рабочее место обычного отбора; нужны отдельная авторизация и legacy-допуск, текущие scoped-права не гарантируют доступ" data-help-id="case-work.nav.pick">Обычная сборка · отдельный допуск →</a>
          <a href={`/assembly/?task_id=${work.context.task_id}`} title="Открыть отдельный пост весовой сборки; он требует самостоятельного допуска, текущие scoped-права запуска не гарантируют доступ" data-help-id="case-work.nav.weigh">Весовая сборка →</a>
        </nav>}
        <footer className="cw-footer">Задание → своя сессия → подтверждённое действие</footer>
      </div>}
  </main>;
}
