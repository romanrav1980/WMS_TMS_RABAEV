import { useState } from "react";
import { API_BASE } from "../../../../api";
import type { ReadState } from "../../access-admin/useApiRead";
import { useUrlWarehouse } from "../useUrlWarehouse";
import { KpiFilters, initialFilters, query, type Filters } from "./Filters";
import { parsePicker, parseDelivery } from "./contracts";
import { useKpi } from "./useKpi";
import { PickerSection } from "./PickerSection";
import { DeliverySection } from "./DeliverySection";
import "./kpi.css";

function Source({ label, state }: { label: string; state: ReadState<unknown> }) {
 return <div className="kpi-source" role="status"><b>{label}</b>{state.loading ? " · читаем…" : state.at ? " · получено " + state.at.toLocaleTimeString("ru-RU") : ""}
  {state.error && <p className="ops-err">{state.error}{state.data ? " Показан предыдущий успешный ответ этого периода." : ""}</p>}</div>;
}

export function KpiDesk({ day, reload }: { day: string; reload: number }) {
 const [warehouse, selectWarehouse] = useUrlWarehouse();
 const [draft, setDraft] = useState<Filters>(() => initialFilters(day, warehouse));
 const [applied, setApplied] = useState(draft), [message, setMessage] = useState("");
 const search = query(applied), dirty = JSON.stringify(draft) !== JSON.stringify(applied);
 const picker = useKpi(search ? "/api/resources/picker-kpis?" + search : null, Number(applied.warehouse), parsePicker, reload);
 const delivery = useKpi(search ? "/api/delivery/timing/kpis?" + search : null, Number(applied.warehouse), parseDelivery, reload);
 function apply() {
  if (!query(draft)) { setMessage("Укажите склад и корректный период до31дня."); return; }
  selectWarehouse(draft.warehouse); setApplied({ ...draft }); setMessage("");
  const url = new URL(location.href); url.searchParams.set("kpi_start", draft.start); url.searchParams.set("kpi_finish", draft.finish); url.searchParams.set("kpi_zone", draft.zone); history.replaceState(history.state, "", url);
 }
 return <div className="kpi-layout"><div className="kpi-heading"><h1>Показатели смены и доставки</h1><a href={API_BASE.replace(/\/$/, "") + "/help/kpi-workplace.html"} target="_blank" rel="noreferrer" title="Формулы, знаменатели и причины отсутствующих значений" data-help-id="kpi.help">Справка</a></div>
  <KpiFilters value={draft} onChange={setDraft} onApply={apply} />
  {message && <p className="ops-err" role="alert">{message}</p>}
  {dirty ? <p className="ops-note">Фильтры изменены. Нажмите «Применить», чтобы прочитать выбранный склад и период.</p> : !search ? <p>Выберите склад и период. Каждый источник проверяет свои права.</p> : <>
   <Source label="Выработка" state={picker} />{picker.data && <PickerSection key={"picker:" + search} data={picker.data} zone={applied.zone} />}
   <Source label="Доставка" state={delivery} />{delivery.data && <DeliverySection key={"delivery:" + search} data={delivery.data} zone={applied.zone} />}
  </>}
 </div>;
}
