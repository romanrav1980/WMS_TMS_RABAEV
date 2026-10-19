import { tcHelp } from "./api";
import type { DocRow, MsgRow, Payload, Tab } from "./api";
import { Act, BUYOUT, ORDER_KIND, Time, docStatus, str, yes } from "./ui";

export type Names = Map<string, string>;
const name = (names: Names, kind: string, id: unknown) => { const v = str(id); const t = names.get(kind + ":" + v); return t ? `${t} (${v})` : v; };
const arr = (v: unknown) => Array.isArray(v) ? v : [];

/** Колонки списка для каждого вида документа. Значения — из payload; названия — из уже полученных страниц, без N+1. */
function columns(tab: Tab, names: Names): [string, (p: Payload) => React.ReactNode][] {
  switch (tab) {
    case "ORDER": return [["Получатель", p => name(names, "RECIPIENT", p.recipient_id)], ["Вид", p => ORDER_KIND[str(p.order_kind)] ?? str(p.order_kind)],
      ["Отгрузка (план)", p => <Time value={p.planned_ship_at} />], ["Строк", p => arr(p.lines).length]];
    case "TRIP": return [["Машина", p => str(p.vehicle_id)], ["Выезд (план)", p => <Time value={p.planned_departure_at} />], ["Заказов", p => new Set(arr(p.orders).map(o => (o as Payload).order_id)).size]];
    case "RECIPIENT": return [["Название", p => str(p.title)], ["Собственник после выкупа", p => name(names, "OWNER", p.target_owner_id)],
      ["Выкуп", p => BUYOUT[str(p.buyout_mode)] ?? str(p.buyout_mode)], ["Мин. ОСГ, дн.", p => str(p.min_osg_days)]];
    case "NEED": return [["Получатель", p => name(names, "RECIPIENT", p.recipient_id)], ["Товар", p => name(names, "SKU", p.sku_id)], ["Данные на", p => <Time value={p.snapshot_at} />], ["Период до", p => <Time value={p.period_until} />]];
    case "SKU": return [["Название", p => str(p.title)], ["В коробе, шт.", p => str(p.units_per_box)], ["МРЦ", p => arr(p.permitted_mrc).join(", ") || "—"]];
    case "SUPPLY": return [["Идентификатор паллеты", p => str(p.pallet_identifier)], ["Товар", p => name(names, "SKU", p.sku_id)], ["Собственник", p => name(names, "OWNER", p.owner_id)],
      ["МРЦ", p => str(p.mrc)], ["Срок", p => str(p.expiry_date)], ["Кодов в составе", p => arr(p.codes).length]];
    default: return [["Название", p => str(p.title)], ["Активен", p => yes(p.active)]];
  }
}

export function DocList({ tab, rows, names, selected, onOpen }: { tab: Tab; rows: DocRow[]; names: Names; selected: string; onOpen: (id: string) => void }) {
  const cols = columns(tab, names);
  return <div className="tc-scroll"><table className="tc-table"><thead><tr><th>Документ</th><th>Версия</th><th>Состояние</th>{cols.map(([t]) => <th key={t}>{t}</th>)}<th /></tr></thead>
    <tbody>{rows.map(r => <tr key={r.document_id} className={r.document_id === selected ? "is-selected" : ""}>
      <td><b>{r.document_id}</b></td><td>{r.version}</td><td>{docStatus(r.status)}</td>{cols.map(([t, f]) => <td key={t}>{f(r.payload)}</td>)}
      <td><Act help={tcHelp.open} onClick={() => onOpen(r.document_id)}>Открыть</Act></td></tr>)}</tbody></table></div>;
}

export const resultChip = (s: string) => s === "ACCEPTED" ? <span className="tc-chip ok">Принято основание</span>
  : s === "REJECTED" ? <span className="tc-chip bad">Отклонено</span> : <span className="tc-chip">{s}</span>;
export const KIND_NAME: Record<string, string> = { ORDER: "Заказ", TRIP: "Рейс", RECIPIENT: "Получатель", SKU: "Товар", OWNER: "Собственник", SUPPLY: "Поставка", NEED: "Потребность" };

export function MsgList({ rows, selected, onOpen }: { rows: MsgRow[]; selected: string; onOpen: (id: string) => void }) {
  return <div className="tc-scroll"><table className="tc-table"><thead><tr><th>Документ</th><th>Версия</th><th>Приём на складе</th><th>Ответ источнику</th><th>Время</th><th /></tr></thead>
    <tbody>{rows.map(m => <tr key={m.event_id} className={m.event_id === selected ? "is-selected" : ""}>
      <td>{KIND_NAME[m.entity_type] ?? m.entity_type} <b>{m.document_id}</b></td><td>{m.version}</td><td>{resultChip(m.result.status)}</td>
      <td>{m.result.external_delivery === "PENDING" ? "в очереди" : str(m.result.external_delivery)}{m.result.external_business === "NOT_CONFIRMED" ? " · внешний ответ не получен" : ""}</td>
      <td><Time value={m.result.occurred_at} /></td><td><Act help={tcHelp.openMessage} onClick={() => onOpen(m.event_id)}>Открыть</Act></td></tr>)}</tbody></table></div>;
}
