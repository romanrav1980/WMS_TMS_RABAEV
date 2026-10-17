import { useApiRead } from "../../access-admin";
import { useEffect, useState } from "react";

export type Filters = { warehouse: string; start: string; finish: string; zone: "+03:00" | "+00:00" };
type Workspaces = { warehouses: { warehouse_id: number; title: string }[]; has_more: boolean };

export function initialFilters(day: string, warehouse: string): Filters {
 const next = new Date(day + "T00:00:00Z"); next.setUTCDate(next.getUTCDate() + 1);
 const query = new URLSearchParams(location.search);
 return { warehouse, start: query.get("kpi_start") || day + "T00:00", finish: query.get("kpi_finish") || next.toISOString().slice(0, 10) + "T00:00", zone: query.get("kpi_zone") === "+00:00" ? "+00:00" : "+03:00" };
}

export function query(filters: Filters): string | null {
 const warehouse = Number(filters.warehouse), start = Date.parse(filters.start + filters.zone), finish = Date.parse(filters.finish + filters.zone);
 if (!/^[1-9]\d*$/.test(filters.warehouse) || !Number.isSafeInteger(warehouse) || !Number.isFinite(start) || !Number.isFinite(finish) || finish <= start || finish - start > 31 * 86400000) return null;
 return new URLSearchParams({ warehouse_id: filters.warehouse, start_at: new Date(start).toISOString(), finish_at: new Date(finish).toISOString() }).toString();
}

export function KpiFilters({ value, onChange, onApply }: { value: Filters; onChange: (value: Filters) => void; onApply: () => void }) {
 const read = useApiRead<Workspaces>("/api/access/workspaces");
 const [open, setOpen] = useState(() => !query(value) || !matchMedia("(max-width:600px)").matches);
 useEffect(() => {
  const media = matchMedia("(max-width:600px)");
  const resize = () => { if (media.matches && query(value)) setOpen(false); };
  media.addEventListener("change", resize); return () => media.removeEventListener("change", resize);
 }, [value]);
 return <details className="ops-panel kpi-filter-panel" open={open} onToggle={event => setOpen(event.currentTarget.open)}>
  <summary title="Открыть или свернуть выбор склада, периода и часового пояса" data-help-id="kpi.filters">Параметры отчёта <small>{value.warehouse ? "Склад " + value.warehouse : "Выберите склад"} · {value.zone === "+03:00" ? "МСК" : "UTC"} · {value.start.replace("T", " ")} → {value.finish.replace("T", " ")}</small></summary>
  <form className="kpi-filters" onSubmit={event => { event.preventDefault(); onApply(); if (query(value) && matchMedia("(max-width:600px)").matches) setOpen(false); }}>
  <label>Склад / РЦ<input value={value.warehouse} inputMode="numeric" list="kpi-warehouses" onChange={event => onChange({ ...value, warehouse: event.target.value.replace(/\D/g, "") })} title="Выберите склад из разрешённого списка; права на каждый показатель проверит сервер" data-help-id="kpi.warehouse" /></label>
  <datalist id="kpi-warehouses">{read.data?.warehouses.map(row => <option key={row.warehouse_id} value={row.warehouse_id}>{row.title}</option>)}</datalist>
  <label>С<input type="datetime-local" value={value.start} onChange={event => onChange({ ...value, start: event.target.value })} title="Начало отчётного периода включительно" data-help-id="kpi.start" /></label>
  <label>До<input type="datetime-local" value={value.finish} onChange={event => onChange({ ...value, finish: event.target.value })} title="Конец отчётного периода не включается; максимум31день" data-help-id="kpi.finish" /></label>
  <label>Время<select value={value.zone} onChange={event => onChange({ ...value, zone: event.target.value as Filters["zone"] })} title="Явный часовой пояс границ отчёта" data-help-id="kpi.zone"><option value="+03:00">МСК · UTC+03</option><option value="+00:00">UTC</option></select></label>
  <button type="submit" title="Прочитать серверные KPI для выбранного склада и периода" data-help-id="kpi.apply">Применить</button>
  {read.error && <small className="ops-err">Список складов не прочитан; код можно ввести вручную.</small>}
  {read.data?.has_more && <small className="ops-note">Список складов ограничен; введите нужный код.</small>}
 </form></details>;
}
