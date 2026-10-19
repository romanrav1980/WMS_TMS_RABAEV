import type { StockGroup } from "./api";
import type { Names } from "./Lists";
import { str } from "./ui";

/** Сумма десятичных строк без округления (масштаб по максимальному числу знаков после запятой). */
function add(a: string, b: string): string {
  const scale = Math.max((a.split(".")[1] ?? "").length, (b.split(".")[1] ?? "").length);
  const n = (v: string) => { const [i, f = ""] = v.split("."); return BigInt(i + f.padEnd(scale, "0")); };
  const s = (n(a) + n(b)).toString().padStart(scale + 1, "0");
  return scale ? s.slice(0, -scale) + "." + s.slice(-scale) : s;
}
const decimal = (v: string) => /^\d+(\.\d+)?$/.test(v);

/** Запас по серверным группам. Один идентификатор паллеты может иметь несколько групп — строки не склеиваются;
 *  итоги — только по этой странице и по каждой единице отдельно, не общий остаток склада. */
export function StockList({ rows, names }: { rows: StockGroup[]; names: Names }) {
  const name = (kind: string, id: string) => { const t = names.get(kind + ":" + id); return t ? `${t} (${id})` : id; };
  const totals = new Map<string, string>();
  for (const r of rows) if (decimal(r.base_quantity)) totals.set(r.base_uom, add(totals.get(r.base_uom) ?? "0", r.base_quantity));
  return <>
    <div className="tc-scroll"><table className="tc-table"><thead><tr><th>Идентификатор паллеты</th><th>Адрес</th><th>Товар</th><th>Собственник</th><th>МРЦ</th><th>Срок</th>
      <th>Количество</th><th>Резерв</th><th title="Статус кодов маркировки по ответам СКМ">Коды: подтверждено / ожидает / отклонено</th></tr></thead>
      <tbody>{rows.map((r, i) => <tr key={r.pallet_identifier + ":" + i}><td><b>{r.pallet_identifier}</b></td><td>{str(r.cell)}</td><td>{name("SKU", r.sku_id)}</td>
        <td>{name("OWNER", r.owner_id)}</td><td>{str(r.mrc)}</td><td>{str(r.expiry_date)}</td><td>{r.base_quantity} {r.base_uom}</td><td>{r.hard_reserved_base} {r.base_uom}</td>
        <td><span className="tc-chip ok">{r.valid_units}</span> / <span className="tc-chip">{r.pending_units}</span> / <span className={"tc-chip" + (r.rejected_units ? " bad" : "")}>{r.rejected_units}</span></td></tr>)}</tbody></table></div>
    <p className="tc-note">Итого на этой странице: {[...totals].map(([uom, q]) => `${q} ${uom}`).join(" · ") || "—"}. Это не общий остаток склада; групп: {rows.length}.</p>
  </>;
}
