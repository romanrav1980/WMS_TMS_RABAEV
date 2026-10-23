import { Fragment, useEffect, useRef, useState } from "react";
import { ApiRequestError, apiFetch } from "../../../../api";
import { HelpButton } from "../../help/HelpButton";
import { paperFields, paperSignature, parsePaper, printPaper } from "./taskPaperModel";
import type { PaperSnapshot } from "./taskPaperModel";
import "./taskPaper.css";
import { rawLink } from "../OpsParts";

const article = "/help/warehouse-task-paper.html";
const HELP = {
  open: { id: "task-paper.open", article, text: "Показать бланк выбранного складского задания для работы по бумаге." },
  close: { id: "task-paper.close", article, text: "Скрыть бланк и вернуться к карточке работы." },
  fresh: { id: "task-paper.fresh", article, text: "Прочитать текущее задание и подготовить новый бланк вместо устаревшего." },
  check: { id: "task-paper.check", article, text: "Сравнить версию со штрихкода с текущим заданием. Выполнение не подтверждается." },
  print: { id: "task-paper.print", article, text: "Проверить версию на сервере и открыть бланк для печати. Количество товара не изменяется." },
};

function refusal(error: unknown): string {
  if (error instanceof TypeError) return "Связь с сервером прервана. Повторите чтение бланка после восстановления связи.";
  if (error instanceof ApiRequestError) {
    if (error.status === 409) return "Задание изменилось. Этот бланк устарел; подготовьте новый после проверки задания.";
    if ([401, 403, 404].includes(error.status)) return "Задание недоступно. Проверьте вход в систему и доступ к складу.";
    return "Бланк не получен. Повторите чтение задания.";
  }
  return error instanceof Error ? error.message : "Бланк не получен.";
}

function usePaper(taskId: number) {
  const [paper, setPaper] = useState<PaperSnapshot | null>(null), [busy, setBusy] = useState(false), [error, setError] = useState("");
  const [checked, setChecked] = useState(false);
  const controller = useRef<AbortController | null>(null);
  useEffect(() => () => controller.current?.abort(), [taskId]);
  const reset = () => { controller.current?.abort(); setPaper(null); setBusy(false); setChecked(false); setError(""); };
  const reject = (message: string) => { reset(); setError(message); };
  const load = async (signature?: string, popup?: Window) => {
    controller.current?.abort(); const own = new AbortController(); controller.current = own;
    setPaper(null); setBusy(true); setChecked(false); setError("");
    try {
      const path = `/api/warehouse-tasks/${taskId}/paper` + (signature ? `?expected_signature=${signature}` : "");
      const snapshot = parsePaper(await apiFetch<unknown>(path, { signal: own.signal }), taskId);
      if (own.signal.aborted) { popup?.close(); return; }
      setPaper(snapshot); setChecked(Boolean(signature)); if (popup) printPaper(popup, snapshot);
    } catch (reason) { popup?.close(); if (!own.signal.aborted) { setPaper(null); setError(refusal(reason)); } }
    finally { if (!own.signal.aborted) setBusy(false); }
  };
  const print = () => {
    if (!paper || busy) return;
    const popup = window.open("", "_blank", "width=1120,height=800");
    if (!popup) { setError("Разрешите открытие окна с бланком и повторите печать."); return; }
    popup.opener = null; void load(paper.task.task_signature, popup);
  };
  return { paper, busy, error, checked, load, reset, reject, print };
}

export function TaskPaperPanel({ taskId }: { taskId: number }) {
  const [open, setOpen] = useState(false), [reference, setReference] = useState("");
  const p = usePaper(taskId);
  if (!open) return <div className="task-paper"><HelpButton help={HELP.open} onClick={() => { setOpen(true); void p.load(); }}>Бланк задания</HelpButton></div>;
  return <section className="task-paper" aria-label="Бумажное задание">
    <div className="task-paper-actions"><b>Бланк задания №{taskId}</b><HelpButton help={HELP.close} onClick={() => { p.reset(); setOpen(false); }}>Закрыть</HelpButton></div>
    <form onSubmit={event => { event.preventDefault(); try { void p.load(paperSignature(reference, taskId)); } catch (error) { p.reject(refusal(error)); } }}>
      <label>Штрихкод с бланка<input aria-label="Штрихкод с бланка" value={reference} onChange={event => setReference(event.target.value)} autoComplete="off" spellCheck={false} placeholder="Считайте сканером или вставьте код" title="Сканер должен передать полный код в это поле; Enter запускает сверку версии" /></label>
      <div className="task-paper-actions"><HelpButton help={HELP.check} type="submit" disabled={p.busy}>Проверить бланк</HelpButton>
        <HelpButton help={HELP.fresh} disabled={p.busy} onClick={() => { setReference(""); void p.load(); }}>Новый бланк</HelpButton></div>
    </form>
    {p.busy && <p role="status">Проверка задания…</p>}
    {p.error && <p className="ops-err" role="alert">{p.error}</p>}
    {p.checked && p.paper && <p className="task-paper-verified" role="status">Версия бланка совпадает с версией задания.</p>}
    {p.paper && <><dl className="task-paper-fields">{paperFields(p.paper.task).map(([label, value]) => <Fragment key={label}><dt>{label}</dt><dd>{value}</dd></Fragment>)}</dl>
      <HelpButton help={HELP.print} disabled={p.busy} onClick={p.print}>Печать / PDF</HelpButton>
      {p.checked && !["DONE", "CANCELLED"].includes(String(p.paper.task.status)) && <a
        href={rawLink("warehouse-tasks.html") + "?task_id=" + taskId + "&paper_reference=" + encodeURIComponent(p.paper.reference)}
        target="_blank" rel="noopener noreferrer" title="Открыть карточку задания для проверки бланка, ввода фактического количества и физических сканов"
        data-help-id="task-paper.fact">Внести факт по бланку</a>}
      <p className="ops-note">Печать и сверка версии не подтверждают выполнение.</p>
      <details><summary title="Показать полный код версии для обращения в поддержку">Данные для поддержки</summary><code>{p.paper.reference}</code></details></>}
    <a href={article} target="_blank" rel="noopener noreferrer" title="Открыть инструкцию по бланку и сверке его версии">Инструкция по бланку</a>
  </section>;
}
