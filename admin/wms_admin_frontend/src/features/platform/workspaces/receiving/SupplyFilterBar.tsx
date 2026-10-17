import type { HelpEntry } from "../../help/catalog";
import { HelpButton } from "../../help/HelpButton";
import { WarehousePicker } from "../resources/WarehousePicker";
import { BASIS, MAX_DAYS } from "./supplyQuery";
import type { DateBasis, SupplyFilter } from "./supplyQuery";

const h = (id: string, text: string): HelpEntry => ({ id: "receiving.filter." + id, text, article: "receiving-lead" });
const help = {
  from: h("from", `Первый календарный день окна (включительно). Окно — не больше ${MAX_DAYS} дней.`),
  to: h("to", "Последний календарный день окна (включительно)."),
  basis: h("basis", "По какой дате отбирать поставки: плановая дата приёмки, фактическая дата приёмки или дата документа. Даты — календарные поля источника, часовой пояс не известен."),
  unplanned: h("unplanned", "Показать отдельно поставки без плановой даты приёмки (backlog). В плитки и схему выбранных дней они не входят."),
  reset: h("reset", "Вернуть окно к дате в шапке рабочего места."),
};

/** Склад, окно дат и смысл даты для поставок SAP. Значения уходят серверу; клиент ничего не дофильтровывает. */
export function SupplyFilterBar({ f, onChange, onReset, custom, day, note }: { f: SupplyFilter; onChange: (f: SupplyFilter, byUser: boolean) => void; onReset: () => void; custom: boolean; day: string; note: string }) {
  const basis = BASIS.find(b => b.id === f.basis)!;
  return <div className="ops-panel rg-window" style={{ gridColumn: "1/-1" }}>
    <WarehousePicker capability="warehouse_tasks" value={f.warehouseId} onChange={id => onChange({ ...f, warehouseId: id }, false)} />
    <label>с <input type="date" value={f.from} onChange={e => e.target.value && onChange({ ...f, from: e.target.value }, true)} title={help.from.text} data-help-id={help.from.id} /></label>
    <label>по <input type="date" value={f.to} onChange={e => e.target.value && onChange({ ...f, to: e.target.value }, true)} title={help.to.text} data-help-id={help.to.id} /></label>
    <label>по дате <select value={f.basis} onChange={e => onChange({ ...f, basis: e.target.value as DateBasis }, false)} title={`${help.basis.text}\n${basis.hint}`} data-help-id={help.basis.id}>
      {BASIS.map(b => <option key={b.id} value={b.id}>{b.label}</option>)}</select></label>
    {f.basis === "PLANNED_ACCEPT" && <label className="rg-check"><input type="checkbox" checked={f.unplanned} onChange={e => onChange({ ...f, unplanned: e.target.checked }, false)}
      title={help.unplanned.text} data-help-id={help.unplanned.id} /> без плановой даты — отдельно</label>}
    {custom && <HelpButton help={help.reset} onClick={onReset}>День {day}</HelpButton>}
    <span className="ops-note">{basis.hint} Даты — календарные поля источника, пояс не известен. {note}</span>
  </div>;
}
