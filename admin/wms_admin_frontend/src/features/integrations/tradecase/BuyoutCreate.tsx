import { useEffect, useRef, useState } from "react";
import { apiFetch } from "../../../api";
import { buyoutsPostPath, executionPath, listPath, normMrc, stockUnitsPath, tcHelp, transitUnitsPath } from "./api";
import type { Buyout, BuyoutBody, DocCard, DocRow, Page, Payload, StockUnit, TripExec, UnitPage } from "./api";
import { journal } from "./intent";
import type { Names } from "./Lists";
import { useCommand } from "./useCommand";
import { useRead } from "./useRead";
import { Act, BUYOUT, UOM, HelpLink, Tech, Time, str } from "./ui";

const buyoutJournal = journal<BuyoutBody>("buyout", "TC.BUYOUT.UI", b => typeof b.buyout_id === "string" && /^[A-Za-z0-9_.:-]{1,100}$/.test(b.buyout_id)
  && Number.isSafeInteger(b.expected_basis_version) && Array.isArray(b.unit_keys) && b.unit_keys.length > 0 && b.unit_keys.length <= 10000 && b.unit_keys.every(k => /^[0-9a-f]{64}$/i.test(k)), "выкуп");
const REASONS: Record<string, string> = { TRADE_BUYOUT_UNIT_ALREADY_HELD: "часть кодов уже удержана другим выкупом", TRADE_OWNER_ACCESS_DENIED: "нет права на собственника",
  ACCESS_DENIED: "нет права выкупа на этом складе", VERSION_CONFLICT: "основание изменилось — перечитайте документ", TRADE_SITE_DISABLED: "приём на площадке выключен",
  OPERATION_CONFLICT: "номер операции уже использован с другими данными", OPERATION_CONTENT_CONFLICT: "номер операции уже использован с другими данными" };
const safe = (v: string) => v.replace(/[^A-Za-z0-9_.:-]/g, "_").slice(0, 40);
const MODES = ["BEFORE_PICK", "AFTER_PICK", "IN_TRANSIT"];
const MAX = 10000;

/** Все страницы кодов по курсору сервера; до чтения всех страниц набор не подтверждается. */
async function allUnits(page: (after: string | null) => string, signal: AbortSignal, progress: (n: number) => void): Promise<StockUnit[]> {
  const out: StockUnit[] = []; let after: string | null = null;
  for (let i = 0; i < 101; i++) {
    const p: UnitPage<StockUnit> = await apiFetch(page(after), { signal });
    if (p.owner_scope_filtered) throw new Error("Часть состава скрыта правами собственника. Запросите доступ к полному составу перед выкупом.");
    out.push(...p.items); progress(out.length);
    if (out.length > MAX) throw new Error("Больше 10000 кодов — одним выкупом не оформляется.");
    if (!p.has_more) return out;
    if (!p.next_after || p.next_after === after) throw new Error("Сервер не подтвердил следующую страницу состава. Перечитайте коды.");
    after = p.next_after;
  }
  throw new Error("Больше 10000 кодов — одним выкупом не оформляется.");
}

/** Строки финансового основания BUYOUT с выбором строки для выкупа. */
export function BuyoutBasis(props: { wh: string; user: string; order: DocCard; names: Names; onDone: (id: string) => void }) {
  const [line, setLine] = useState<string | null>(null), lines = (Array.isArray(props.order.payload.lines) ? props.order.payload.lines : []) as Payload[];
  const chosen = lines.find(l => str(l.line_id) === line);
  return <section className="tc-bind"><h4>Выкуп по финансовому основанию <HelpLink anchor="buyout.create" /></h4>
    <p className="tc-note">Выберите строку финансового основания. Собственник товара изменится после подтверждения СКМ.</p>
    <div className="tc-pager">{lines.map(l => <Act key={str(l.line_id)} help={tcHelp.createBuyout} aria-pressed={line === str(l.line_id)} onClick={() => setLine(str(l.line_id))}>Строка {str(l.line_id)}: {str(l.quantity)} {UOM[str(l.uom)] ?? str(l.uom)}</Act>)}</div>
    {chosen && <BuyoutCreate key={str(chosen.line_id)} {...props} line={chosen} />}</section>;
}

type Demand = { order: string; line: string; qty: string };
/** Исходная строка OUTBOUND с тем же товаром, МРЦ и собственниками (первая страница заказов склада). */
function DemandPicker({ wh, line, value, onChange }: { wh: string; line: Payload; value: Demand | null; onChange: (d: Demand | null) => void }) {
  const orders = useRead<Page<DocRow>>(listPath(wh, "ORDER", null));
  const options: Demand[] = (orders.data?.items ?? []).filter(o => o.payload.order_kind === "OUTBOUND" && o.status === "ACCEPTED")
    .flatMap(o => ((o.payload.lines ?? []) as Payload[]).filter(l => str(l.sku_id) === str(line.sku_id) && normMrc(l.mrc) === normMrc(line.mrc)
      && str(l.source_owner_id) === str(line.source_owner_id) && str(l.target_owner_id) === str(line.target_owner_id))
      .map(l => ({ order: o.document_id, line: str(l.line_id), qty: str(l.quantity) })));
  return <label>Исходный заказ отгрузки и строка<select value={value ? value.order + "\u0000" + value.line : ""} onChange={e => onChange(options.find(d => d.order + "\u0000" + d.line === e.target.value) ?? null)}
    title="Заказ отгрузки, для которого собран или погружен этот товар. Сервер сверит принадлежность кодов этой строке" data-help-id="tradecase.buyout.demand">
    <option value="">{orders.loading ? "Читаем заказы…" : options.length ? "Выберите строку" : "Подходящих строк нет"}</option>
    {options.map(d => <option key={d.order + ":" + d.line} value={d.order + "\u0000" + d.line}>{d.order} / строка {d.line}: {d.qty}</option>)}</select>
    {orders.data?.has_more && <small className="tc-note">Показана первая страница заказов.</small>}</label>;
}

/** Выезд в пути: внешний рейс → погрузка DEPARTED, груз ещё не передан получателю. */
function LoadPicker({ wh, value, onChange }: { wh: string; value: string; onChange: (load: string, departed: string | null) => void }) {
  const [trip, setTrip] = useState("");
  const trips = useRead<Page<DocRow>>(listPath(wh, "TRIP", null)), ex = useRead<TripExec>(trip ? executionPath(wh, trip) : null);
  const loads = (ex.data?.loads ?? []).filter(l => l.status === "DEPARTED" && !l.custody_released);
  return <><label>Внешний рейс<select value={trip} onChange={e => { setTrip(e.target.value); onChange("", null); }} title="Рейс, в котором груз уже выехал" data-help-id="tradecase.buyout.trip">
      <option value="">Выберите рейс</option>{(trips.data?.items ?? []).map(t => <option key={t.document_id} value={t.document_id}>{t.document_id} · машина {str(t.payload.vehicle_id)}</option>)}</select></label>
    {trip && (ex.error ? <p className="tc-err">{ex.error.includes("не найден") ? "Рейс ещё не привязан к фактическому рейсу склада." : ex.error}</p> : ex.data && <label>Погрузка в пути<select value={value}
      onChange={e => onChange(e.target.value, loads.find(l => l.load_operation_id === e.target.value)?.departed_at ?? null)} title="Выехавшая погрузка, груз которой ещё не передан получателю" data-help-id="tradecase.buyout.loadop">
      <option value="">{loads.length ? "Выберите погрузку" : "Нет выехавших погрузок в пути"}</option>{loads.map(l => <option key={l.load_operation_id} value={l.load_operation_id}>{l.load_operation_id} · место {l.identifier}</option>)}</select></label>)}</>;
}

/** Создание выкупа: до сборки (паллета), после сборки (CASE + исходный заказ), в пути (погрузка в машине + исходный заказ). */
export function BuyoutCreate({ wh, user, order, line, names, onDone }: { wh: string; user: string; order: DocCard; line: Payload; names: Names; onDone: (id: string) => void }) {
  const [scan, setScan] = useState(""), [units, setUnits] = useState<StockUnit[] | null>(null), [loading, setLoading] = useState(0), [error, setError] = useState(""), [count, setCount] = useState(0);
  const [demand, setDemand] = useState<Demand | null>(null), [load, setLoad] = useState(""), [departed, setDeparted] = useState<string | null>(null);
  const abort = useRef<AbortController | null>(null);
  useEffect(() => () => abort.current?.abort(), []);
  useEffect(() => { abort.current?.abort(); setUnits(null); setLoading(0); }, [scan, demand?.order, demand?.line, load]);
  const cmd = useCommand<BuyoutBody, Buyout>(buyoutJournal, buyoutsPostPath(wh), user, wh, REASONS,
    (r, b) => r.buyout_id === b.buyout_id ? `Запрос выкупа принят складом: ${r.requested_units} кодов.` : null);
  const mode = str(order.payload.buyout_mode), sku = str(line.sku_id), mrc = normMrc(line.mrc), owner = str(line.source_owner_id), qty = Number(line.quantity);
  const name = (kind: string, id: string) => { const t = names.get(kind + ":" + id); return t ? `${t} (${id})` : id; };
  if (!MODES.includes(mode)) return <p className="tc-note">Момент выкупа «{mode}» этим экраном не поддерживается.</p>;
  if (str(line.uom) !== "EA") return <p className="tc-note">Строка в единицах «{str(line.uom)}»: выбор кодов по коробам на этом экране не поддерживается.</p>;
  if (!user) return <p className="tc-note">Определяем пользователя…</p>;
  const s = cmd.stored, note = cmd.msg && <p className={"tc-msg " + cmd.msg.tone} role="status">{cmd.msg.text}{cmd.msg.tech !== undefined && <Tech value={cmd.msg.tech} />}</p>;
  if (s.kind === "damaged") return <section className="tc-bind bad"><h4>Выкуп заблокирован</h4><p>Сохранённая команда выкупа на этом складе повреждена; новая не создаётся.</p><Tech value={s.raw} /></section>;
  if (s.kind === "ok") { const b = s.intent.body; return <section className="tc-bind warn"><h4>Сохранённая команда выкупа <HelpLink anchor="unknown" label="Что делать" /></h4>
    <p>Выкуп по основанию {b.basis_order_id}/{b.basis_line_id}{b.demand_order_id ? `, исходный заказ ${b.demand_order_id}/${b.demand_line_id}` : ""}{b.load_operation_id ? `, погрузка ${b.load_operation_id}` : ""}: кодов {b.unit_keys.length}. {s.intent.sent ? "Отправка уже была, результат не подтверждён." : "Ещё не отправлена."} Данные команды не меняются.</p>
    <Act help={tcHelp.retry} disabled={cmd.busy} onClick={() => cmd.send(s.intent, () => onDone(b.buyout_id))}>Повторить ту же команду</Act>{note}<Tech value={b} label="Номер операции и тело команды" /></section>; }
  // Подходят: тот же товар, МРЦ (нормализованно), собственник-источник, код подтверждён СКМ, не удержан другим выкупом.
  // До сборки резерв исключается; после сборки и в пути резерв под исходный заказ допустим — принадлежность сверяет сервер.
  const eligible = (units ?? []).filter(u => u.sku_id === sku && normMrc(u.mrc) === mrc && u.owner_id === owner && u.mark_state === "VALID" && !u.buyout_hold
    && (mode !== "BEFORE_PICK" || !u.hard_reserved)).sort((a, b) => a.physical_unit_key.localeCompare(b.physical_unit_key));
  const limit = Math.min(MAX, qty || MAX, eligible.length), chosen = eligible.slice(0, Math.min(count, limit));
  const ready = (mode === "BEFORE_PICK" || demand) && (mode !== "IN_TRANSIT" || load);
  async function read() {
    abort.current?.abort(); const c = new AbortController(); abort.current = c; setError(""); setUnits(null); setLoading(1);
    const page = mode === "IN_TRANSIT" ? (a: string | null) => transitUnitsPath(wh, load, a) : (a: string | null) => stockUnitsPath(wh, scan.trim(), a);
    try { const all = await allUnits(page, c.signal, n => setLoading(n || 1)); if (!c.signal.aborted) { setUnits(all); setCount(Number.MAX_SAFE_INTEGER); } }
    catch (e) { if (!c.signal.aborted) setError(String((e as Error).message)); } finally { if (!c.signal.aborted) setLoading(0); }
  }
  const place = mode === "IN_TRANSIT" ? `в пути: погрузка ${load}${departed ? ", выезд " : ""}` : `паллета ${scan.trim()}, адрес ${[...new Set(chosen.map(u => str(u.cell)))].join(", ")}`;
  return <section className="tc-bind"><h4>Выкуп {BUYOUT[mode]} · строка {str(line.line_id)} <HelpLink anchor="buyout.create" /></h4>
    {mode !== "BEFORE_PICK" && <DemandPicker wh={wh} line={line} value={demand} onChange={d => { setDemand(d); setUnits(null); }} />}
    {mode === "IN_TRANSIT" ? <><LoadPicker wh={wh} value={load} onChange={(l, d) => { setLoad(l); setDeparted(d); setUnits(null); }} />
      <Act help={tcHelp.loadTransit} disabled={!ready || loading > 0} onClick={read}>Прочитать груз в машине</Act></>
    : <form onSubmit={e => { e.preventDefault(); if (scan.trim() && ready) read(); }}>
      <label>{mode === "AFTER_PICK" ? "Штрихкод собранного места (CASE) или идентификатор паллеты" : "Идентификатор паллеты"}<input value={scan} onChange={e => { setScan(e.target.value); setUnits(null); }} maxLength={200} autoComplete="off" title={tcHelp.scan.text} data-help-id="tradecase.buyout.scan" /></label>
      <button type="submit" disabled={!scan.trim() || !ready || loading > 0} title={tcHelp.loadUnits.text} data-help-id={tcHelp.loadUnits.id}>Прочитать коды</button></form>}
    {loading > 0 && <p className="tc-note">Читаем коды… {loading > 1 ? loading : ""}</p>}{error && <p className="tc-err" role="alert">{error}</p>}
    {units && <div className="tc-review">
      <p>Кодов {mode === "IN_TRANSIT" ? "в погрузке" : "на месте"}: {units.length}. Подходят строке (товар {name("SKU", sku)}, МРЦ {mrc}, собственник {name("OWNER", owner)}, код подтверждён СКМ, не удержан другим выкупом{mode === "BEFORE_PICK" ? ", без резерва" : ""}): <b>{eligible.length}</b>. В строке: {str(line.quantity)} шт.</p>
      <label className="tc-inline">Кодов в выкуп<input type="number" min={1} max={limit} value={Math.min(count, limit)} onChange={e => setCount(Math.max(0, Math.min(Number(e.target.value) || 0, limit)))} title="Сколько подходящих кодов включить; набор берётся из актуальных данных" data-help-id="tradecase.buyout.count" /></label>
      {chosen.length > 0 && <p>Будет запрошен выкуп <b>{chosen.length}</b> кодов ({BUYOUT[mode]}): {name("OWNER", owner)} → {name("OWNER", str(line.target_owner_id))}, {place}{mode === "IN_TRANSIT" && departed ? <Time value={departed} /> : null};
        основание {order.document_id}/{str(line.line_id)} (версия {order.document_version}){demand ? `, исходный заказ ${demand.order}/${demand.line}` : ""}. Собственник сменится только после ответа СКМ{mode === "IN_TRANSIT" ? "; повторной отгрузки не будет" : ""}.</p>}
      <Act help={tcHelp.sendBuyout} disabled={!chosen.length || cmd.busy} onClick={() => cmd.start({ buyout_id: `UI.${safe(order.document_id)}.${safe(str(line.line_id))}.${crypto.randomUUID().slice(0, 8)}`,
        basis_order_id: order.document_id, basis_line_id: str(line.line_id), expected_basis_version: order.document_version, unit_keys: chosen.map(u => u.physical_unit_key),
        ...(demand ? { demand_order_id: demand.order, demand_line_id: demand.line } : {}), ...(mode === "IN_TRANSIT" ? { load_operation_id: load } : {}) }, r => onDone(r.buyout_id))}>Запросить выкуп</Act>
      <Tech value={chosen.map(u => ({ key: u.physical_unit_key, place: u.location_kind === "VEHICLE_TRANSIT" ? "в пути" : u.cell }))} label="Ключи выбранных кодов" /></div>}
    {note}</section>;
}
