import { useState } from "react";
import { sortPath, tcHelp } from "./api";
import type { SortBody, SortResult } from "./api";
import { journal } from "./intent";
import { useCommand } from "./useCommand";
import { Act, HelpLink, Tech } from "./ui";

/** Серверная операция разделения подключена root (API_READY_C0136, 13 HTTP). Флаг оставлен, чтобы снова выключить отправку без правки формы. */
export const SORT_READY = true;
const OFF = "Недоступно: серверная операция разделения ещё не подключена. ";
const PROFILE = { system_code: "CRPT", profile_code: "TOBACCO" }; // единственный сканпрофиль, доступный в QA
const sortJournal = journal<SortBody>("sort", "TC.SORT.UI", b => typeof b.source_pallet === "string" && b.source_pallet.length > 0 && b.source_pallet.length <= 200
  && typeof b.source_cell === "string" && b.source_cell.length <= 60 && typeof b.target_cell === "string" && b.target_cell.length > 0 && b.target_cell.length <= 60
  && Array.isArray(b.scans) && b.scans.length > 0 && b.scans.length <= 10000, "разделение");
const REASONS: Record<string, string> = { ACCESS_DENIED: "нет права разделения на этом складе", TRADE_OWNER_ACCESS_DENIED: "нет права на собственника",
  OPERATION_CONFLICT: "номер операции уже использован с другими данными", OPERATION_CONTENT_CONFLICT: "номер операции уже использован с другими данными" };

/** Физическое разделение паллеты: исходная паллета и ячейки, сканы маркировки (Enter), счётчик и явное подтверждение переноса.
 *  Новый идентификатор берётся из ответа сервера (uid); этикетка и регуляторная агрегация этим не подтверждаются. */
export function SortPanel({ wh, user }: { wh: string; user: string }) {
  const [src, setSrc] = useState(""), [from, setFrom] = useState(""), [to, setTo] = useState(""), [scan, setScan] = useState(""), [codes, setCodes] = useState<string[]>([]), [sure, setSure] = useState(false), [note, setNote] = useState("");
  const [result, setResult] = useState<SortResult | null>(null);
  const cmd = useCommand<SortBody, SortResult>(sortJournal, sortPath(wh), user, wh, REASONS,
    (r, b) => r.operation_id === b.operation_id && r.uid ? `Перенесено ${r.base_quantity} ${r.base_uom}: ${r.from_cell} → ${r.cell}.` : null);
  const done = (r: SortResult) => { setResult(r); setCodes([]); setSure(false); }; // после любого успеха — и первой отправки, и повтора
  const add = () => { const c = scan.trim(); setScan(""); if (!c) return; if (codes.includes(c)) { setNote("Этот код уже отсканирован."); return; } if (codes.length >= 10000) { setNote("Не больше 10000 кодов за одну операцию."); return; } setNote(""); setCodes(v => [...v, c]); };
  const s = cmd.stored, msg = cmd.msg && <p className={"tc-msg " + cmd.msg.tone} role="status">{cmd.msg.text}{cmd.msg.tech !== undefined && <Tech value={cmd.msg.tech} />}</p>;
  const ready = Boolean(src.trim() && to.trim() && codes.length && sure);
  return <section className="tc-panel tc-sort" aria-label="Разделение паллеты">
    <h3>Физическое разделение паллеты <HelpLink anchor="sort" /></h3>
    {!SORT_READY && <p className="tc-msg warn">Серверная операция разделения ещё не подключена: форму можно заполнить, отправка недоступна.</p>}
    {result && <div className="tc-msg ok" role="status">Новый идентификатор паллеты: <b>{result.uid}</b> (исходная {result.source_uid}), ячейка {result.cell}.
      <br />Это внутренний идентификатор, не новая SSCC. Регуляторная агрегация: {result.regulatory_composition_status === "PENDING" ? "ожидает подтверждения" : result.regulatory_composition_status ?? "не подтверждена"}; этикетка не напечатана.
      <br />Следующий шаг: оформить новую этикетку и регуляторную агрегацию отдельно.</div>}
    {s.kind === "damaged" ? <><p className="tc-msg bad">Сохранённая команда разделения повреждена; новая не создаётся.</p><Tech value={s.raw} /></>
    : s.kind === "ok" ? <div className="tc-bind warn"><p>Сохранённая команда: паллета {s.intent.body.source_pallet}, {s.intent.body.source_cell} → {s.intent.body.target_cell}, кодов {s.intent.body.scans.length}. {s.intent.sent ? "Результат не подтверждён." : "Ещё не отправлена."} Данные не меняются.</p>
      <Act help={SORT_READY ? tcHelp.retry : { ...tcHelp.retry, text: OFF + tcHelp.retry.text }} disabled={cmd.busy || !SORT_READY} onClick={() => cmd.send(s.intent, done)}>Повторить ту же команду</Act>{msg}</div>
    : <>
      <div className="tc-sort-grid">
        <label>Идентификатор исходной паллеты<input value={src} maxLength={200} onChange={e => setSrc(e.target.value)} autoComplete="off" title="Отсканируйте исходную паллету" data-help-id="tradecase.sort.source" /></label>
        <label>Исходная ячейка<input value={from} maxLength={60} onChange={e => setFrom(e.target.value)} autoComplete="off" title="Ячейка, где стоит исходная паллета" data-help-id="tradecase.sort.from" /></label>
        <label>Целевая ячейка<input value={to} maxLength={60} onChange={e => setTo(e.target.value)} autoComplete="off" title="Пустая ячейка хранения, сортировки или ожидания этого склада" data-help-id="tradecase.sort.to" /></label>
        <label>Профиль маркировки<select value="CRPT/TOBACCO" disabled title="В QA доступен только профиль CRPT / TOBACCO" data-help-id="tradecase.sort.profile"><option>CRPT/TOBACCO</option></select></label>
      </div>
      <form onSubmit={e => { e.preventDefault(); add(); }} className="tc-scanrow">
        <label>Скан кода маркировки<input value={scan} onChange={e => setScan(e.target.value)} autoComplete="off" title={tcHelp.addScan.text} data-help-id={tcHelp.addScan.id} /></label>
        <button type="submit" disabled={!scan.trim()} title={tcHelp.addScan.text} data-help-id="tradecase.sort.add">Добавить</button>
        <Act help={tcHelp.removeScan} disabled={!codes.length} onClick={() => setCodes(v => v.slice(0, -1))}>Убрать последний</Act>
      </form>
      <p className="tc-note">Принято сканов: <b>{codes.length}</b>{codes.length ? ` · последний: ${codes[codes.length - 1]}` : ""}</p>{note && <p className="tc-msg warn">{note}</p>}
      <label className="tc-check"><input type="checkbox" checked={sure} onChange={e => setSure(e.target.checked)} title="Подтвердите, что отсканированные коды физически переносятся в целевую ячейку" data-help-id="tradecase.sort.confirm" /> Подтверждаю перенос {codes.length} кодов с паллеты {src || "—"} в ячейку {to || "—"}</label>
      <Act help={SORT_READY ? tcHelp.sendSort : { ...tcHelp.sendSort, text: OFF + tcHelp.sendSort.text }} disabled={!ready || cmd.busy || !SORT_READY}
        onClick={() => cmd.start({ source_pallet: src.trim(), source_cell: from.trim(), target_cell: to.trim(), scans: codes.map(code => ({ ...PROFILE, code })) }, done)}>
        {SORT_READY ? "Разделить" : "Разделить (не подключено)"}</Act>{msg}
    </>}
  </section>;
}
