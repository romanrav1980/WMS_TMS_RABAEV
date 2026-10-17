import { useState } from "react";
import type { PickerKpi, PickerRow, QualityQuantity } from "./contracts";
import { number, hours } from "./useKpi";
import { moment } from "./useKpi";
import { sourceReason } from "./labels";

const events = (n: number) => n % 10 === 1 && n % 100 !== 11 ? "событие" : [2, 3, 4].includes(n % 10) && ![12, 13, 14].includes(n % 100) ? "события" : "событий";
/** Количества в разных единицах не складываются: каждое показано по товару и единице. */
const quantities = (list: QualityQuantity[]) => list.map(q => `${q.article}: ${number(q.quantity)} ${q.base_uom}`).join(" · ");

export function PickerSection({ data, zone }: { data: PickerKpi; zone: string }) {
 const [selected, setSelected] = useState(""), [page, setPage] = useState(0);
 const operator = data.operators.find(row => row.operator_id === selected) ?? (data.operators.length === 1 ? data.operators[0] : null);
 const facts = operator?.facts ?? [], currentPage = Math.min(page, Math.max(0, Math.ceil(facts.length / 50) - 1));
 const choose = (id: string) => { setSelected(id); setPage(0); };
 const cards = [
  ["Сборка · строки/ч", operator?.rates.lines_per_assembly_hour, operator?.registered_assembly_hours],
  ["Сборка · коробки/ч", operator?.rates.boxes_per_assembly_hour, operator?.registered_assembly_hours],
  ["Смена · строки/ч", operator?.rates.lines_per_shift_hour, operator?.registered_shift_hours],
  ["Смена · коробки/ч", operator?.rates.boxes_per_shift_hour, operator?.registered_shift_hours],
 ] as const;
 return <section className="ops-panel kpi-section" aria-label="Выработка комплектовщиков">
  <div className="kpi-heading"><h2>Выработка</h2><label>Сотрудник <select value={operator?.operator_id ?? ""} onChange={event => choose(event.target.value)} title="Выберите сотрудника, чтобы увидеть четыре показателя и исходные отборы" data-help-id="kpi.operator">
   <option value="">Выберите сотрудника</option>{data.operators.map(row => <option key={row.operator_id}>{row.operator_id}</option>)}</select></label></div>
  <p className="ops-note">По зарегистрированным интервалам · полнота учёта всей работы смены не подтверждена. Коробки — только целые, остаток — штуками отдельно.</p>
  <div className="kpi-metrics">{cards.map(([label, value, time]) => <article className="kpi-metric" key={label}>
   <span>{label}</span><strong>{number(value ?? null)}</strong><small>{operator ? hours(time ?? null) : "Выберите сотрудника"}</small></article>)}</div>
  {operator && <OperatorSummary operator={operator} />}
  {!data.operators.length ? <p>За период нет зарегистрированных отборов и рабочего времени.</p> : <div className="kpi-scroll"><table><thead><tr><th>Сотрудник</th><th>Строки/ч сборки</th><th>Коробки/ч сборки</th><th>Строки/ч смены</th><th>Коробки/ч смены</th><th>Строк · коробок · штук</th></tr></thead>
   <tbody>{data.operators.map(row => <tr key={row.operator_id}><td><button type="button" onClick={() => choose(row.operator_id)} title="Открыть подтверждённые отборы, завершённые строки и причины отсутствующих показателей сотрудника" data-help-id="kpi.operator.facts">{row.operator_id}</button></td>
    {[row.rates.lines_per_assembly_hour, row.rates.boxes_per_assembly_hour, row.rates.lines_per_shift_hour, row.rates.boxes_per_shift_hour].map((value, index) => <td key={index}>{number(value)}</td>)}
    <td>{row.completed_lines} · {number(row.boxes)} · {number(row.pieces)}</td></tr>)}</tbody></table></div>}
  {operator && <details className="kpi-details"><summary title="Показать исходные операции, завершённые строки, связанные возвраты и ограничения времени" data-help-id="kpi.pick.details">Факты и качество данных · {operator.operator_id}</summary>
   {!!operator.box_reasons.length && <p className="kpi-warning">Число коробок неизвестно: {operator.box_reasons.map(sourceReason).join(" ")}</p>}
   {!!operator.uncovered_work_operations.length && <p className="kpi-warning">Отборов вне зарегистрированной сборки: {operator.uncovered_work_operations.length}. Часовая выработка сборки не подтверждена.</p>}
   {!!operator.uncovered_shift_operations.length && <p className="kpi-warning">Отборов вне зарегистрированной смены: {operator.uncovered_shift_operations.length}.</p>}
   <LineCompletions operator={operator} zone={zone} />
   <OperatorQuality operator={operator} />
   <h3 className="kpi-subhead">Отборы</h3>
   <div className="kpi-scroll"><table><thead><tr><th>Запись факта</th><th>Задание / строка</th><th>Товар</th><th>Подобрано</th><th>Целых коробок</th><th>Штук</th><th>Операция</th></tr></thead><tbody>{facts.slice(currentPage * 50, currentPage * 50 + 50).map(fact => <tr key={fact.operation_id}>
    <td>{moment(fact.at, zone)}</td><td>{fact.task_id} / {fact.line_id}</td><td>{fact.article}</td><td>{number(fact.delta)} {fact.base_uom}</td><td>{number(fact.boxes)}</td><td>{number(fact.pieces)}</td><td className="kpi-code">{fact.operation_id}</td></tr>)}</tbody></table></div>
   {facts.length > 50 && <div className="kpi-paging"><button type="button" disabled={!currentPage} onClick={() => setPage(currentPage - 1)} title="Предыдущие50фактов этого ответа" data-help-id="kpi.facts.previous">← Назад</button><span>{currentPage * 50 + 1}–{Math.min(facts.length, currentPage * 50 + 50)} из {facts.length}</span><button type="button" disabled={(currentPage + 1) * 50 >= facts.length} onClick={() => setPage(currentPage + 1)} title="Следующие50фактов этого ответа" data-help-id="kpi.facts.next">Далее →</button></div>}
  </details>}
  <details className="kpi-details"><summary title="Показать версию формулы, момент наблюдения и ограничения источника" data-help-id="kpi.picker.sources">Источники и формула</summary><p>{data.formula_version} · наблюдение {moment(data.as_of, zone)}.</p><ul>{data.source_limitations.map(reason => <li key={reason} title={reason}>{sourceReason(reason)}</li>)}</ul></details>
 </section>;
}

/** Итог сотрудника: строки (из них с согласованной недостачей), целые коробки, штуки, покрытие наблюдённых отборов временем. */
function OperatorSummary({ operator }: { operator: PickerRow }) {
 const c = operator.observed_pick_coverage;
 return <div className="kpi-summary" aria-label={"Итог " + operator.operator_id}>
  <p className="ops-note">Завершено строк: <b>{operator.completed_lines}</b>{operator.shortage_completed_lines ? <> (из них с согласованной недостачей: <b>{operator.shortage_completed_lines}</b>)</> : null}
   {" · "}целых коробок: <b>{number(operator.boxes)}</b> · штук отдельно: <b>{number(operator.pieces)}</b>. Паузы исключены из сборки, включены во время смены.</p>
  <p className="ops-note" title="Показывает только, попали ли наблюдённые отборы в зарегистрированные интервалы. Это не табель и не подтверждение всей работы смены" data-help-id="kpi.coverage">
   Отборы во времени: сборки — {c.covered_work} из {c.total}, смены — {c.covered_shift} из {c.total}{c.complete_for_observed_picks ? " · все наблюдённые отборы во времени" : " · не все наблюдённые отборы во времени"}.</p>
  {operator.return_events > 0 && <p className="kpi-quality-note">Связанные возвраты по его строкам: {operator.return_events} · {quantities(operator.returned_quantities)}. Выполненная работа не уменьшается; это событие качества по заданию, не вина сотрудника.</p>}
 </div>;
}

/** Происхождение завершённых строк: время последнего физического отбора и отдельное время согласования недостачи. */
function LineCompletions({ operator, zone }: { operator: PickerRow; zone: string }) {
 if (!operator.line_completions.length) return <p className="ops-note">Завершённых строк в периоде нет.</p>;
 return <><h3 className="kpi-subhead">Завершённые строки</h3>
  <div className="kpi-scroll"><table><thead><tr><th>Задание / строка</th><th>Как завершена</th><th>Подобрано</th><th>Недостача</th><th>Последний отбор</th><th>Согласовано</th><th>Операция</th></tr></thead>
   <tbody>{operator.line_completions.map(line => <tr key={line.operation_id}><td>{line.task_id} / {line.line_id}</td>
    <td><span className={"kpi-state " + (line.kind === "FULL" ? "good" : "warn")}>{line.kind === "FULL" ? "Полностью" : "С согласованной недостачей"}</span></td>
    <td>{number(line.quantity)}</td><td>{line.kind === "FULL" ? "—" : number(line.shortage_quantity)}</td><td>{moment(line.at, zone)}</td>
    <td>{line.approved_at ? moment(line.approved_at, zone) : "—"}</td><td className="kpi-code">{line.operation_id}</td></tr>)}</tbody></table></div></>;
}

/** Недостачи и связанные возвраты по товару и единице; не суммируются между единицами и не превращаются в вину сотрудника. */
function OperatorQuality({ operator }: { operator: PickerRow }) {
 if (!operator.shortage_quantities.length && !operator.return_events) return null;
 return <dl className="kpi-quality">
  {!!operator.shortage_quantities.length && <><dt>Согласованная недостача</dt><dd>{quantities(operator.shortage_quantities)}</dd></>}
  {!!operator.return_events && <><dt>Связанные возвраты</dt><dd>{operator.return_events} {events(operator.return_events)} · {quantities(operator.returned_quantities) || "количество не указано"}
   <br /><small>Возвраты относятся к заданиям, в которых он отбирал строки; если строку делили несколько человек, возврат не делится и не суммируется как вина.</small></dd></>}
 </dl>;
}
