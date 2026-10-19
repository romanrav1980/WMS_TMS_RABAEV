import { useState } from "react";
import { journal } from "./intent";
import { useCommand } from "./useCommand";
import { useRead } from "./useRead";
import { Act, HelpLink, Tech, UOM } from "./ui";

type Body = { operation_id: string; case_task_id: number; scan_container: string; expected_content_version: number; destinations: Record<string, string> };
type Context = { case_pick_task_id: number; ware_id: number; sscc: string; content_version: number; current_cell: string; return_allowed: boolean; return_blocking_reason: string | null;
  lines: { case_pick_line_id: number; product_name: string; cell_code: string }[]; physical_lots: { uid: string; case_pick_line_id: number; physical_qty: string; base_uom: string }[] };
type Result = { operation_id: string; task: number; status: string; warehouse: number };
const returns = journal<Body>("case-return", "TC.RETURN.UI", b => Number.isSafeInteger(b.case_task_id) && b.case_task_id > 0 && typeof b.scan_container === "string" && b.scan_container.length > 0 && b.scan_container.length <= 150
  && Number.isSafeInteger(b.expected_content_version) && b.expected_content_version >= 0 && Boolean(b.destinations) && typeof b.destinations === "object" && !Array.isArray(b.destinations) && Object.keys(b.destinations).length > 0 && Object.keys(b.destinations).length <= 200
  && Object.entries(b.destinations).every(([key, value]) => key.length > 0 && typeof value === "string" && value.length > 0 && value.length <= 60), "возврат сборки");
const transport = { path: (b: Body) => `/api/case-pick/tasks/${b.case_task_id}/return-carrier`, payload: ({ case_task_id: _, ...body }: Body) => body };
const blocked: Record<string, string> = { PERMISSION: "Запросите право возврата сборки и выполнения по собственнику товара.", PARENT: "Сначала отсоедините сборку от объединённого места.",
  ASSEMBLY: "Сначала завершите или разберите активную сборку на весах.", STATE: "Возврат для текущего состояния сборки недоступен.", EMPTY: "В сборке нет товара для возврата." };

export function CaseReturn({ wh, user }: { wh: string; user: string }) {
  const [scan, setScan] = useState(""), [requested, setRequested] = useState(""), [reload, setReload] = useState(0), [targets, setTargets] = useState<Record<string, string>>({});
  const [review, setReview] = useState<Omit<Body, "operation_id"> | null>(null);
  const read = useRead<Context>(requested ? `/api/case-pick/resolve-carrier?warehouse_id=${encodeURIComponent(wh)}&pallet_identifier=${encodeURIComponent(requested)}` : null, reload);
  const cmd = useCommand<Body, Result>(returns, "", user, wh, { STOCK_RULE_REJECTED: "состав, состояние сборки или права изменились — перечитайте сборку",
    CASE_RETURN_STATE_SCAN_VERSION_CONFLICT: "состояние или состав изменились — перечитайте сборку",
    CASE_RETURN_SCAN_ORIGINAL_CELL_REQUIRED: "ячейка возврата отличается от исходной — повторите скан",
    CASE_RETURN_ALL_LOTS_REQUIRED: "нужно отсканировать ячейки для всего состава",
    TRADE_OWNER_ACCESS_DENIED: "нет права выполнения по текущему собственнику товара",
    STOCK_RELEASE_NOT_ACTIVE: "складские операции приостановлены — повторите команду после разрешения руководителя",
    OPERATION_CONFLICT: "номер операции уже связан с другим содержимым",
    OPERATION_CONTENT_CONFLICT: "сохранённый номер операции связан с другим содержимым" }, (result, body) =>
    result.operation_id === body.operation_id && result.task === body.case_task_id && result.warehouse === Number(wh) && result.status === "RETURNED"
      ? "Товар возвращён в исходные ячейки; сборка отменена. Передайте пустую тару ответственному за её учёт." : null, transport);
  const done = () => { setRequested(""); setScan(""); setTargets({}); setReview(null); };
  const ctx = requested === scan.trim() && !read.loading && !read.error && read.data?.ware_id === Number(wh) && read.data.sscc === requested ? read.data : null;
  const lots = ctx?.physical_lots ?? [], lines = new Map(ctx?.lines.map(line => [line.case_pick_line_id, line]) ?? []);
  const unique = new Set(lots.map(lot => lot.uid)).size === lots.length;
  const ready = Boolean(user && cmd.msg?.tone !== "bad" && ctx?.return_allowed && unique && lots.length > 0 && lots.every(lot => lines.get(lot.case_pick_line_id)?.cell_code === targets[lot.uid]?.trim()));
  const notice = cmd.msg && <><p className={"tc-msg " + cmd.msg.tone} role="status">{cmd.msg.text}</p>{cmd.msg.tech !== undefined && <Tech value={cmd.msg.tech} label="Ответ сервера: технические сведения" />}</>;
  return <section className="tc-panel tc-bind" aria-label="Возврат содержимого сборки">
    <h3>Вернуть товар из сборки <HelpLink anchor="case-return" /></h3>
    {cmd.stored.kind === "damaged" ? <p className="tc-err" role="alert">Сохранённая команда не читается. Передайте технические сведения администратору; новую команду не отправляйте.<Tech value={cmd.stored.raw} /></p>
      : cmd.stored.kind === "ok" ? <><p>Сохранён возврат сборки {cmd.stored.intent.body.scan_container}. Повторите ту же команду, чтобы установить результат. Товар повторно не перемещайте.</p>
        <Act help={{ id: "tradecase.return.retry", text: "Повторить сохранённую команду без изменения номера, состава и ячеек.", anchor: "case-return" }} disabled={cmd.busy} onClick={() => cmd.stored.kind === "ok" && cmd.send(cmd.stored.intent, done)}>Повторить ту же команду</Act><Tech value={cmd.stored.intent.body} label="Сохранённая команда: технические сведения" />{notice}</>
      : review ? <>
        <p>Вернуть весь состав сборки <b>{review.scan_container}</b> по отсканированным исходным ячейкам. После подтверждения сборка будет отменена.</p>
        <ul>{Object.entries(review.destinations).map(([uid, cell], i) => { const lot = lots.find(l => l.uid === uid); return <li key={uid}>Место {i + 1}: {lot?.physical_qty ?? "—"} {lot ? UOM[lot.base_uom] ?? lot.base_uom : ""} → <b>{cell}</b></li>; })}</ul>
        <Act help={{ id: "tradecase.return.send", text: "Подтвердить возврат всего показанного состава по отсканированным исходным ячейкам. Сохранить текущего собственника товара.", anchor: "case-return" }} disabled={cmd.busy}
          onClick={() => { cmd.start(review, done); setReview(null); }}>Вернуть товары в ячейки</Act>
        <Act help={{ id: "tradecase.return.cancel", text: "Вернуться к проверке адресов без отправки команды.", anchor: "case-return" }} onClick={() => setReview(null)}>Назад к сканам</Act>
      </> : <>
        <form className="tc-scanrow" onSubmit={e => { e.preventDefault(); cmd.setMsg(null); setRequested(scan.trim()); setTargets({}); setReview(null); setReload(n => n + 1); }}>
          <label>Идентификатор паллеты<input value={scan} maxLength={150} onChange={e => setScan(e.target.value)} autoComplete="off"
            title="Отсканируйте этикетку сборки и нажмите Enter или введите идентификатор вручную." data-help-id="tradecase.return.scan" /></label>
          <button type="submit" disabled={!scan.trim() || read.loading} title="Прочитать текущий состав сборки и исходные ячейки без записи." data-help-id="tradecase.return.read">Прочитать сборку</button>
        </form>
        {read.loading && <p className="tc-note">Читаем состав…</p>}{read.error && <p className="tc-err" role="alert">{read.error}</p>}
        {ctx && <>
          <p>Сборка <b>{ctx.sscc}</b> · сейчас в {ctx.current_cell || "—"} · версия {ctx.content_version}.</p>
          {!ctx.return_allowed && <p className="tc-msg warn">{blocked[ctx.return_blocking_reason ?? "STATE"] ?? blocked.STATE}</p>}
          {!unique && <p className="tc-err">В составе повторяются идентификаторы мест. Передайте сборку руководителю смены для проверки.</p>}
          <div className="tc-return-lots">{lots.map((lot, i) => <article key={lot.uid + i}>
            <b>Место {i + 1} · {lines.get(lot.case_pick_line_id)?.product_name ?? "Товар не найден"}</b>
            <p>Вернуть {lot.physical_qty} {UOM[lot.base_uom] ?? lot.base_uom} в ячейку <b>{lines.get(lot.case_pick_line_id)?.cell_code ?? "—"}</b>.</p>
            <label>Скан исходной ячейки<input value={targets[lot.uid] ?? ""} maxLength={60} onChange={e => setTargets(v => ({ ...v, [lot.uid]: e.target.value }))}
              title="Отсканируйте показанную исходную ячейку после возврата товара." data-help-id={"tradecase.return.target." + i} aria-label={"Скан исходной ячейки места " + (i + 1)} /></label>
          </article>)}</div>
          <Act help={{ id: "tradecase.return.review", text: "Сверить сканы всех исходных ячеек и показать возврат перед отправкой.", anchor: "case-return" }} disabled={!ready || cmd.busy}
            onClick={() => ctx && setReview({ case_task_id: ctx.case_pick_task_id, scan_container: ctx.sscc, expected_content_version: ctx.content_version,
              destinations: Object.fromEntries(lots.map(lot => [lot.uid, targets[lot.uid].trim()])) })}>Проверить возврат</Act>
        </>}{notice}
      </>}
  </section>;
}
