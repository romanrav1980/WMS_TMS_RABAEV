import { useMemo, useRef, useState } from "react";
import { ApiRequestError, apiFetch } from "../../../../api";
import { useApiRead } from "../../access-admin";
import { HelpButton } from "../../help/HelpButton";
import { WarehousePicker } from "../resources/WarehousePicker";
import { TaskPaperPanel } from "../resources/TaskPaperPanel";
import { useUrlWarehouse } from "../useUrlWarehouse";
import { LIMIT, STATE, openTasks, parseReference, route, taskLine } from "./paperQueue";
import { paperHelp } from "./help";
import { CasePaperQueue } from "./CasePaperPanel";
import "./paper.css";

/** Рабочее место «Бумажные задания» (C-0155, BP15): при отказе ТСД руководитель выбирает разрешённые задания склада и печатает
 *  бланки; после восстановления сверяет версию со штрихкода. Права, видимость и версии проверяет сервер; печать ничего не выполняет. */
export function PaperDesk({ reload }: { reload: number }) {
  const [wh, setWh] = useUrlWarehouse(), [mode, setMode] = useState<"tasks" | "case">("tasks");
  return <>
    <div className="ops-panel rg-window paper-mode" style={{ gridColumn: "1/-1" }}>
      <WarehousePicker capability={mode === "case" ? "picking" : "warehouse_tasks"} value={wh} onChange={setWh} />
      <span role="group" aria-label="Вид бланков">{(["tasks", "case"] as const).map(m => <HelpButton key={m} help={paperHelp.mode} aria-pressed={mode === m}
        onClick={() => setMode(m)}>{m === "case" ? "Сборка коробов CASE" : "Складские задания"}</HelpButton>)}</span></div>
    {!wh ? <p className="ops-panel ops-note" style={{ gridColumn: "1/-1" }}>Выберите склад: задания показываются по одному складу.</p>
      : mode === "case" ? <CasePaperQueue key={wh} wh={wh} reload={reload} /> : <PaperQueue key={wh} wh={wh} reload={reload} />}
  </>;
}

function PaperQueue({ wh, reload }: { wh: string; reload: number }) {
  const [assignee, setAssignee] = useState(""), [asked, setAsked] = useState(""), [local, setLocal] = useState(0), [open, setOpen] = useState<number | null>(null);
  const read = useApiRead<unknown>(`/api/warehouse-tasks?ware_id=${encodeURIComponent(wh)}&limit=${LIMIT}${asked ? `&assigned_to=${encodeURIComponent(asked)}` : ""}`, reload + local);
  const parsed = useMemo(() => { try { return { tasks: read.data == null ? null : openTasks(read.data), error: "" }; } catch (e) { return { tasks: null, error: (e as Error).message }; } }, [read.data]);
  const tasks = parsed.tasks, full = Array.isArray(read.data) && read.data.length >= LIMIT;
  return <section className="ops-panel paper-desk" style={{ gridColumn: "1/-1" }} aria-label="Бумажные задания">
    <h3>Бумажные задания при отказе ТСД</h3>
    <p className="ops-note">Бланк — копия текущего складского задания с штрихкодом его версии. Печать и сверка не выполняют задание и не меняют количество.</p>
    <ByReference />
    <form className="paper-filter" onSubmit={e => { e.preventDefault(); setAsked(assignee.trim()); setOpen(null); setLocal(n => n + 1); }}>
      <label>Исполнитель <input value={assignee} maxLength={50} onChange={e => setAssignee(e.target.value)} placeholder="все" title={paperHelp.filter.text} data-help-id={paperHelp.filter.id} /></label>
      <HelpButton help={paperHelp.refresh} type="submit">Показать задания</HelpButton>
    </form>
    {read.loading && <p className="ops-note">Загрузка…</p>}
    {(read.error || parsed.error) && <p role="alert" className="ops-err">Задания не прочитаны: {read.error || parsed.error}</p>}
    {full && <p className="ops-note">Показаны первые {LIMIT} заданий склада — сузьте список по исполнителю.</p>}
    {tasks && tasks.length === 0 && <p className="ops-note">Незавершённых заданий нет (задания, недоступные вам, не показываются).</p>}
    {tasks && tasks.length > 0 && <ul className="ops-list">{tasks.map(t => <li key={t.task_id}>
      <span><b>Задание {t.task_id}</b> <small>{STATE[t.status] ?? t.status} · {t.assigned_to ?? "исполнитель не назначен"}</small><br />
        <small>{taskLine(t)} · {route(t)}{t.uid_pallet || t.sscc ? ` · паллета ${t.uid_pallet ?? t.sscc}` : ""}</small>
        {open === t.task_id && <TaskPaperPanel key={t.task_id} taskId={t.task_id} />}</span>
      <span><HelpButton help={open === t.task_id ? paperHelp.close : paperHelp.open} onClick={() => setOpen(v => v === t.task_id ? null : t.task_id)}>
        {open === t.task_id ? "Скрыть" : "Бланк"}</HelpButton></span></li>)}</ul>}
  </section>;
}

/** Вход по штрихкоду бланка: сервер сверяет версию бланка с текущим заданием; актуальный бланк открывает то же задание. */
function ByReference() {
  const [text, setText] = useState(""), [state, setState] = useState<{ taskId: number | null; message: string; tone: "ok" | "err" | "" }>({ taskId: null, message: "", tone: "" });
  const [busy, setBusy] = useState(false), seq = useRef(0);
  const check = async () => {
    const mine = ++seq.current;  // a late answer of an older check never overwrites a newer one
    const ref = parseReference(text);
    if (!ref) { setState({ taskId: null, message: "Считайте штрихкод с бланка или вставьте его полный текст.", tone: "err" }); return; }
    setBusy(true); setState({ taskId: null, message: "", tone: "" });
    try {
      await apiFetch<unknown>(`/api/warehouse-tasks/${ref.taskId}/paper?expected_signature=${ref.signature}`);
      if (mine !== seq.current) return;
      setState({ taskId: ref.taskId, message: `Бланк задания №${ref.taskId} актуален.`, tone: "ok" });
    } catch (e) {
      if (mine !== seq.current) return;
      const status = e instanceof ApiRequestError ? e.status : 0;
      setState({ taskId: null, tone: "err", message: status === 409 ? `Задание №${ref.taskId} изменилось после печати — бланк устарел. Откройте задание и подготовьте новый бланк.`
        : [401, 403, 404].includes(status) ? "Задание недоступно: проверьте вход и доступ к складу." : "Сверка не выполнена: нет ответа сервера. Повторите позже." });
    } finally { if (mine === seq.current) setBusy(false); }
  };
  return <form className="paper-scan" onSubmit={e => { e.preventDefault(); void check(); }}>
    <label>Штрихкод с бланка <input value={text} onChange={e => setText(e.target.value)} autoComplete="off" spellCheck={false} placeholder="Считайте сканером или вставьте код" /></label>
    <HelpButton help={paperHelp.scan} type="submit" disabled={busy}>Сверить бланк</HelpButton>
    {state.message && <p role={state.tone === "err" ? "alert" : "status"} className={state.tone === "err" ? "ops-err" : "ops-note"}>{state.message}</p>}
    {state.taskId != null && <TaskPaperPanel key={state.taskId} taskId={state.taskId} />}
  </form>;
}
