import { useEffect, useMemo, useRef, useState } from "react";
import { ApiRequestError, apiFetch } from "../../../../api";
import { useApiRead } from "../../access-admin";
import { HelpButton } from "../../help/HelpButton";
import { CASE_STATE, DEVICE, LIMIT, WORKING, casePaper, lineOpen, openCaseTasks, parseCaseReference, qty, readCasePending, refusal,
  saveCasePending, sendCasePending, type CaseIntent, type CaseLine, type CasePaper } from "./casePaper";
import { paperHelp } from "./help";

/** Сборка коробов CASE на бумаге (C-0156): очередь CASE-заданий склада, бланк по строкам с версией каждой строки (CPICK),
 *  после восстановления — факт строки существующей командой с версией бланка. Права, версии и сканы проверяет сервер. */
export function CasePaperQueue({ wh, reload }: { wh: string; reload: number }) {
  const [local, setLocal] = useState(0), [open, setOpen] = useState<number | null>(null);
  const read = useApiRead<unknown>(`/api/case-pick/tasks?scope=all&ware_id=${encodeURIComponent(wh)}&limit=${LIMIT}`, reload + local);
  const parsed = useMemo(() => { try { return { tasks: read.data == null ? null : openCaseTasks(read.data), error: "" }; } catch (e) { return { tasks: null, error: (e as Error).message }; } }, [read.data]);
  const tasks = parsed.tasks, full = Array.isArray(read.data) && read.data.length >= LIMIT;
  return <section className="ops-panel paper-desk" style={{ gridColumn: "1/-1" }} aria-label="Бумажная сборка CASE">
    <h3>Сборка коробов CASE при отказе ТСД</h3>
    <p className="ops-note">Бланк — строки текущего CASE-задания с версией каждой строки. Печать не начинает и не завершает сборку; факт вносится после восстановления по штрихкоду строки с бланка.</p>
    <CaseByReference />
    <p><HelpButton help={paperHelp.caseRefresh} onClick={() => { setOpen(null); setLocal(n => n + 1); }}>Показать задания CASE</HelpButton></p>
    {read.loading && <p className="ops-note">Загрузка…</p>}
    {(read.error || parsed.error) && <p role="alert" className="ops-err">Задания CASE не прочитаны: {read.error || parsed.error}</p>}
    {full && <p className="ops-note">Показаны первые {LIMIT} заданий CASE склада.</p>}
    {tasks && tasks.length === 0 && <p className="ops-note">Незавершённых заданий CASE нет (недоступные вам не показываются).</p>}
    {tasks && tasks.length > 0 && <ul className="ops-list">{tasks.map(t => <li key={t.case_pick_task_id}>
      <span><b>CASE {t.case_pick_task_id}</b> <small>{CASE_STATE[t.status] ?? t.status} · {t.assigned_to ?? "исполнитель не назначен"}</small><br />
        <small>короб {t.sscc ?? "—"} · заказ {t.order_no ?? "—"}{t.customer_name ? ` · ${t.customer_name}` : ""} · строк {t.total_lines ?? "—"}, собрано {t.picked_lines ?? 0}</small>
        {open === t.case_pick_task_id && <CaseSheet taskId={t.case_pick_task_id} />}</span>
      <span><HelpButton help={open === t.case_pick_task_id ? paperHelp.caseClose : paperHelp.caseOpen} onClick={() => setOpen(v => v === t.case_pick_task_id ? null : t.case_pick_task_id)}>
        {open === t.case_pick_task_id ? "Скрыть" : "Бланк"}</HelpButton></span></li>)}</ul>}
  </section>;
}

function readError(e: unknown): string {
  const status = e instanceof ApiRequestError ? e.status : 0;
  const code = e instanceof ApiRequestError && typeof e.detail === "object" && e.detail ? (e.detail as { code?: string }).code : "";
  if (status === 503 && code === "CASE_PAPER_NOT_AVAILABLE") return "Бланки CASE ещё не включены на сервере (версия строк не установлена).";
  return [401, 403, 404].includes(status) ? "Задание недоступно: проверьте вход и доступ к складу." : "Бланк не прочитан: нет ответа сервера. Повторите позже.";
}

/** Бланк одного CASE-задания: что собрать по строкам, версия каждой строки и печать. Ничего не выполняет. */
function CaseSheet({ taskId }: { taskId: number }) {
  const [state, setState] = useState<{ paper: CasePaper | null; error: string }>({ paper: null, error: "" });
  useEffect(() => {
    let live = true;  // ответ закрытого/сменившегося бланка не показывается
    apiFetch<unknown>(`/api/case-pick/tasks/${taskId}/paper`).then(r => { if (live) setState({ paper: casePaper(r), error: "" }); })
      .catch(e => { if (live) setState({ paper: null, error: e instanceof Error && e.message.startsWith("Неожиданный") ? e.message : readError(e) }); });
    return () => { live = false; };
  }, [taskId]);
  if (state.error) return <p role="alert" className="ops-err">{state.error}</p>;
  if (!state.paper) return <p className="ops-note">Готовим бланк…</p>;
  const p = state.paper;
  return <div className="case-paper">
    <p className="ops-note">Короб {p.task.sscc} · исполнитель {p.task.assigned_to ?? "не назначен"} · {CASE_STATE[p.task.status] ?? p.task.status}</p>
    <div className="case-paper-scroll"><table className="ops-table">
      <thead><tr><th>Ячейка</th><th>Товар</th><th>План</th><th>Уже собрано</th><th>Ввод с бумаги</th></tr></thead>
      <tbody>{p.lines.map(l => <tr key={l.line_id}><td>{l.cell_code ?? "—"}</td><td>{l.articul} {l.product_name ?? ""}</td><td>{qty(l.planned_qty)}</td>
        <td>{qty(l.picked_qty)}</td><td>{!lineOpen(l) ? "строка закрыта" : l.device_required ? DEVICE[l.device_required] : l.scale_reading ? "можно, вес с весов (кг)" : "можно"}</td></tr>)}</tbody>
    </table></div>
    <HelpButton help={paperHelp.casePrint} onClick={() => printSheet(p)}>Печать / PDF</HelpButton>
  </div>;
}

const esc = (s: unknown) => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]!));

function printSheet(p: CasePaper) {
  const w = window.open("", "_blank", "width=1120,height=800");
  if (!w) return;
  const rows = p.lines.filter(lineOpen).map(l => `<section><h2>Ячейка ${esc(l.cell_code)} · ${esc(l.articul)} ${esc(l.product_name)}</h2>
    <dl><dt>План</dt><dd>${esc(qty(l.planned_qty))}</dd><dt>Уже собрано</dt><dd>${esc(qty(l.picked_qty))}</dd>
    <dt>Собрано всего${l.scale_reading ? ", кг с весов" : ""} (вписать)</dt><dd class="blank"></dd><dt>Время / подпись</dt><dd class="blank"></dd></dl>
    ${l.device_required ? `<p class="warn">${esc(DEVICE[l.device_required])}: на бумаге не подтверждается</p>` : ""}${l.barcode_svg}<code>${esc(l.reference)}</code></section>`).join("");
  w.document.write(`<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>CASE ${p.task.task_id}</title><style>
    @page{size:A4 portrait;margin:10mm}body{font:12px system-ui,sans-serif;margin:0}h1{font-size:16px}h2{font-size:13px;margin:0 0 4px}
    section{border:1px solid #000;padding:6px;margin:0 0 6px;break-inside:avoid}dl{display:grid;grid-template-columns:repeat(4,auto 1fr);gap:4px;margin:0 0 4px}
    dt{font-weight:600}dd{margin:0}dd.blank{border-bottom:1px solid #000;min-height:16px}svg{display:block;width:100%;max-width:180mm;height:18mm}code{font-size:8px;word-break:break-all}.warn{font-weight:700}
    </style></head><body><h1>Сборка короба CASE ${p.task.task_id} · короб ${esc(p.task.sscc)}</h1>
    <p>Заказ ${esc(p.task.order_no)} · ${esc(p.task.customer_name)} · волна ${esc(p.task.wave_code)} · исполнитель ${esc(p.task.assigned_to ?? "не назначен")} · подготовлено ${esc(new Date(p.prepared_at).toLocaleString("ru-RU"))}</p>
    <p>Печать не подтверждает выполнение. Сканы ячейки, короба и товара обязательны при вводе факта.</p>${rows}</body></html>`);
  w.document.close();
  w.focus(); w.print();
}

/** Вход по штрихкоду строки бланка: сервер сверяет версию бланка с текущей строкой; актуальный бланк открывает ввод факта этой строки. */
function CaseByReference() {
  const [text, setText] = useState(""), [busy, setBusy] = useState(false), seq = useRef(0);
  const [state, setState] = useState<{ found: { taskId: number; signature: string; line: CaseLine; status: string } | null; message: string; tone: "ok" | "err" | "" }>({ found: null, message: "", tone: "" });
  const check = async () => {
    const mine = ++seq.current;  // поздний ответ прежней сверки не перетирает новую
    const ref = parseCaseReference(text);
    if (!ref) { setState({ found: null, message: "Считайте штрихкод строки с бланка CASE (CPICK) или вставьте его полный текст.", tone: "err" }); return; }
    setBusy(true); setState({ found: null, message: "", tone: "" });
    try {
      const p = casePaper(await apiFetch<unknown>(`/api/case-pick/tasks/${ref.taskId}/paper?line=${ref.lineId}&expected_signature=${ref.signature}`));
      if (mine !== seq.current) return;
      const line = p.lines.find(l => l.line_id === ref.lineId);
      if (!line) throw new Error("Неожиданный ответ бланка CASE");
      setState({ found: { taskId: ref.taskId, signature: ref.signature, line, status: p.task.status }, message: `Бланк строки ${ref.lineId} задания CASE ${ref.taskId} актуален.`, tone: "ok" });
    } catch (e) {
      if (mine !== seq.current) return;
      const status = e instanceof ApiRequestError ? e.status : 0;
      setState({ found: null, tone: "err", message: status === 409 ? `Строка ${ref.lineId} задания CASE ${ref.taskId} изменилась после печати — бланк устарел. Проверьте, что сделано, и подготовьте новый бланк.`
        : e instanceof Error && e.message.startsWith("Неожиданный") ? e.message : readError(e) });
    } finally { if (mine === seq.current) setBusy(false); }
  };
  return <><form className="paper-scan case-scan" onSubmit={e => { e.preventDefault(); void check(); }}>
    <label>Штрихкод строки с бланка CASE <input value={text} onChange={e => setText(e.target.value)} autoComplete="off" spellCheck={false} placeholder="CPICK:…" /></label>
    <HelpButton help={paperHelp.caseScan} type="submit" aria-busy={busy}>Сверить строку</HelpButton>
    {state.message && <p role={state.tone === "err" ? "alert" : "status"} className={state.tone === "err" ? "ops-err" : "ops-note"}>{state.message}</p>}
  </form>
  {state.found && <LineFact key={`${state.found.taskId}:${state.found.line.line_id}:${state.found.signature}`} {...state.found} />}</>;
}

/** Факт строки с бумаги: накопленное количество и обязательные сканы; уходит существующей командой с версией бланка. */
function LineFact({ taskId, signature, line, status }: { taskId: number; signature: string; line: CaseLine; status: string }) {
  const [pending, setPending] = useState(() => readCasePending(taskId, line.line_id));
  const [form, setForm] = useState({ fact_qty: "", scan_cell: "", scan_container: "", scan_product: "" });
  const [msg, setMsg] = useState<{ text: string; tone: "ok" | "err" }>({ text: "", tone: "ok" }), [busy, setBusy] = useState(false);
  const blocked = !lineOpen(line) ? "строка уже закрыта" : line.device_required ? DEVICE[line.device_required]
    : !WORKING.has(status) ? "задание не начато — начните его штатно в карточке CASE" : "";
  const send = async (intent: CaseIntent) => {
    setBusy(true);
    const r = await sendCasePending(intent);
    setPending(readCasePending(taskId, line.line_id));  // журнал браузера — источник: снят только подтверждённым исходом
    setBusy(false);
    setMsg(r.kind === "ack" ? { text: "Факт строки принят сервером.", tone: "ok" } : r.kind === "refused" ? { text: refusal(r.code), tone: "err" } : { text: r.message, tone: "err" });
  };
  const submit = () => {
    try { const intent = saveCasePending(taskId, line.line_id, { ...form, expected_case_signature: signature }); setPending({ intent, damaged: "" }); void send(intent); }
    catch (e) { setMsg({ text: (e as Error).message, tone: "err" }); }
  };
  const field = (k: keyof typeof form, label: string, help: { id: string; text: string }) =>
    <label>{label} <input value={form[k]} onChange={e => setForm(f => ({ ...f, [k]: e.target.value }))} autoComplete="off" spellCheck={false}
      inputMode={k === "fact_qty" ? "decimal" : undefined} title={help.text} data-help-id={help.id} disabled={Boolean(blocked) || Boolean(pending.intent) || busy} /></label>;
  return <form className="paper-scan case-fact" aria-label="Факт строки с бланка" onSubmit={e => { e.preventDefault(); submit(); }}>
    <p className="ops-note">Строка {line.line_id}: ячейка {line.cell_code ?? "—"}, {line.articul} {line.product_name ?? ""}; план {qty(line.planned_qty)}, уже собрано {qty(line.picked_qty)}.
      Факт записывается под вашим входом; за назначенного другого сотрудника — только при штатном праве управления сборкой CASE.</p>
    {blocked && <p role="alert" className="ops-err">С бумаги не вносится: {blocked}.</p>}
    {pending.damaged && <p role="alert" className="ops-err">{pending.damaged}</p>}
    {field("scan_cell", "Скан ячейки", paperHelp.caseCell)}{field("scan_container", "Скан короба (SSCC)", paperHelp.caseContainer)}
    {field("scan_product", "Скан товара", paperHelp.caseProduct)}{field("fact_qty", line.scale_reading ? "Собрано всего по строке, кг (показание весов)" : "Собрано всего по строке", paperHelp.caseQty)}
    {pending.intent ? <HelpButton help={paperHelp.caseRetry} type="button" disabled={busy} onClick={() => void send(pending.intent!)}>Повторить отправку</HelpButton>
      : <HelpButton help={paperHelp.caseSend} type="submit" disabled={busy || Boolean(blocked) || Boolean(pending.damaged)}>Внести факт</HelpButton>}
    {pending.intent && <p className="ops-note">Сохранённый факт {pending.intent.operation_id} ждёт подтверждения; повтор отправит те же данные.</p>}
    {msg.text && <p role={msg.tone === "err" ? "alert" : "status"} className={msg.tone === "err" ? "ops-err" : "ops-note"}>{msg.text}</p>}
  </form>;
}
