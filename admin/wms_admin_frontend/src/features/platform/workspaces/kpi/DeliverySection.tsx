import { useState } from "react";
import type { DeliveryKpi } from "./contracts";
import { number } from "./useKpi";
import { rawLink } from "../OpsParts";
import { moment } from "./useKpi";
import { sourceReason, receiptMode } from "./labels";

const timing = { ON_TIME: "Вовремя", EARLY: "Раньше окна", LATE: "Позже окна", NO_ARRIVAL: "Нет прибытия", NO_PLAN: "Нет плана" };
const fullness = { FULL: "Полностью", WITH_ISSUES: "С расхождениями", PENDING: "Ожидается приёмка" };

export function DeliverySection({ data, zone }: { data: DeliveryKpi; zone: string }) {
 const [selected, setSelected] = useState<string | null>(null);
 const row = data.deliveries.find(value => value.load_operation_id + "|" + value.store_address === selected);
 return <section className="ops-panel kpi-section" aria-label="KPI доставки"><h2>Доставка</h2>
  <div className="kpi-delivery-metrics"><article className="kpi-metric"><span>Прибытие в плановое окно</span><strong>{data.timing.on_time_percent_of_observed === null ? "Нет данных" : number(data.timing.on_time_percent_of_observed) + "%"}</strong><small>{data.timing.ON_TIME} из {data.timing.observed_planned} прибытий с планом</small></article>
   <article className="kpi-metric"><span>Магазин принял полностью</span><strong>{data.receipt.full_percent_of_received === null ? "Нет данных" : number(data.receipt.full_percent_of_received) + "%"}</strong><small>{data.receipt.FULL} из {data.receipt.received} завершённых приёмок</small></article></div>
  <div className="kpi-counts"><span>Раньше окна: {data.timing.EARLY}</span><span>Позже: {data.timing.LATE}</span><span>Нет прибытия: {data.timing.NO_ARRIVAL}</span><span>Нет плана: {data.timing.NO_PLAN}</span><span>С расхождениями: {data.receipt.WITH_ISSUES}</span><span>Приёмка ожидается: {data.receipt.PENDING}</span></div>
  <p className="ops-note">Проценты по наблюдённым фактам. Ожидающие поставки и отсутствие плана показаны отдельно.</p>
  {!data.deliveries.length ? <p>За период нет поставок с плановым окном или подтверждёнными событиями.</p> : <div className="kpi-scroll"><table><thead><tr><th>Магазин / рейс</th><th>Плановое окно</th><th>Прибытие</th><th>Приёмка</th><th>Факты</th></tr></thead><tbody>{data.deliveries.map(value => {
   const key = value.load_operation_id + "|" + value.store_address;
   return <tr key={key}><td>{value.store_address}<br /><small>Рейс {value.trip_id}</small></td><td>{moment(value.window_start, zone)}<br />{moment(value.window_finish, zone)}</td><td><span className={"kpi-state " + (value.on_time_state === "ON_TIME" ? "good" : "warn")}>{timing[value.on_time_state]}</span><br /><small>{moment(value.arrived_at, zone)}</small></td><td>{fullness[value.full_state]}</td>
    <td><button type="button" onClick={() => setSelected(selected === key ? null : key)} title="Показать исходную погрузку, окно и акт приёмки магазина" data-help-id="kpi.delivery.facts">{selected === key ? "Скрыть" : "Открыть"}</button></td></tr>;
  })}</tbody></table></div>}
  {row && <section className="kpi-details" aria-label="Факты доставки"><h3>Рейс {row.trip_id} · {row.store_address}</h3><dl><dt>Погрузка</dt><dd className="kpi-code">{row.load_operation_id}</dd><dt>Прибытие машины</dt><dd>{moment(row.arrived_at, zone)} · {timing[row.on_time_state]}</dd><dt>Акт магазина</dt><dd className="kpi-code">{row.receipt_operation_id ?? "Ещё не подтверждён"}</dd><dt>Способ приёмки</dt><dd>{receiptMode(row.receipt_mode)}</dd><dt>Завершение приёмки</dt><dd>{moment(row.received_at, zone)}</dd><dt>Состав</dt><dd>{row.line_count} строк · с расхождениями {row.issue_count}</dd></dl>
   <a href={rawLink("transport-loading.html") + "?trip_id=" + row.trip_id} target="_blank" rel="noreferrer" title="Открыть погрузку и выезд этого рейса, сохранив текущий отчёт" data-help-id="kpi.delivery.trip">Открыть погрузку рейса</a></section>}
  <details className="kpi-details"><summary title="Показать серверную формулу и ограничения расчёта доставки" data-help-id="kpi.delivery.sources">Источники и формула</summary><p>{data.formula_version}. Прибытие сравнивается с включительными границами окна, зафиксированного до выезда. Полноту подтверждает магазин.</p><ul>{data.source_limitations.map(reason => <li key={reason} title={reason}>{sourceReason(reason)}</li>)}</ul></details>
 </section>;
}
