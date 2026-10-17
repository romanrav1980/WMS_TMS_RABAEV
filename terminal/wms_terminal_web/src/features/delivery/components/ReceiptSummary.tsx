import { HelpHint } from "../help/HelpHint";
import type { ReceiptResult, ReceiptWeight } from "../contracts";
import { manualWeightHelp } from "../manualWeight";

const columns = [["shipped", "Отправлено"], ["accepted", "Принято"], ["missing", "Недостача"], ["refused", "Отказ"], ["damaged", "Повреждено"], ["extra", "Излишек"]] as const;
const positive = (value?: string) => Boolean(value && /[1-9]/.test(value));
const next = [
 ["missing", "Передайте недостачу диспетчеру для расследования."],
 ["refused", "Согласуйте дальнейшую судьбу отказанного товара с диспетчером."],
 ["damaged", "Сохраните подтверждающие фотографии повреждений и согласуйте возврат."],
 ["extra", "Передайте излишек на разбирательство; он не становится доступным запасом автоматически."],
] as const;

/** Вес из сохранённого акта. Источник подписывается так, как его записал сервер; без поля — блок не показывается. */
function WeightOutcome({ weight }: { weight: ReceiptWeight }) {
 const manual = weight.measurement_origin === "MANUAL_CONFIRMED";
 return <section className="store-app-weight-outcome" aria-label="Вес в акте">
  <h3>Вес места {manual ? "· введено пользователем" : "· получено от прибора"} <a className="store-app-help-link" href={manualWeightHelp("confirm")} target="_blank" rel="noopener"
   title="Как читать вес в акте: источник, допуск и приёмка по акту. Откроется в новой вкладке" data-help-id="receipt.weight.help">Справка</a></h3>
  <dl><dt>Фактически</dt><dd>{weight.observed_gross_kg} кг</dd><dt>Отгружено</dt><dd>{weight.shipping_gross_kg} кг</dd>
   <dt>Разница</dt><dd>{weight.delta_kg} кг (допуск ±{weight.tolerance_kg ?? "не задан"} кг) · {weight.in_tolerance === 1 ? "в допуске" : "вне допуска"}</dd>
   {weight.act_confirmed === 1 && <><dt>Приёмка</dt><dd>по акту с пересчётом</dd></>}
   <dt>Источник</dt><dd>{manual ? `введено пользователем${weight.recorded_by ? " · " + weight.recorded_by : ""}` : `прибор ${weight.device_id ?? "—"}`}</dd></dl>
 </section>;
}
const validWeight = (w: unknown): w is ReceiptWeight => !!w && typeof w === "object" && typeof (w as ReceiptWeight).measurement_origin === "string"
 && typeof (w as ReceiptWeight).observed_gross_kg === "string" && typeof (w as ReceiptWeight).shipping_gross_kg === "string" && typeof (w as ReceiptWeight).delta_kg === "string"
 && [0, 1].includes((w as ReceiptWeight).in_tolerance) && [0, 1].includes((w as ReceiptWeight).act_confirmed);

export function ReceiptSummary({ result, onNext }: { result: ReceiptResult; onNext: () => void }) {
 return <section className="store-app-screen store-app-receipt-act" aria-label="Подтверждённый акт приёмки">
  <h2>{result.status === "DISCREPANCY" ? "Акт расхождения при приёмке" : "Приёмка подтверждена"} <HelpHint helpId="receipt.act" tip="Акт — итог приёмки; дальнейшие решения выполняются отдельными штатными действиями" article="store-receiving-recovery" /></h2>
  <p>Грузовое место: {result.root}. Операция: <code>{result.operation_id}</code></p>
  <div className="store-app-table-wrap"><table>
   <thead><tr><th>Товар / партия</th><th>ЕИ</th>{columns.map(([key, label]) => <th key={key}>{label}</th>)}</tr></thead>
   <tbody>{result.accepted_lines.map((row) => <tr key={row.line_no}>
    <td>{row.article} / {row.lot_uid}</td><td>{row.base_uom}</td>
    {columns.map(([key]) => <td key={key}>{row[key] ?? "Не передано"}</td>)}
   </tr>)}</tbody>
  </table></div>
  {validWeight(result.weight) && <WeightOutcome weight={result.weight} />}
  {result.discrepancy_case_id && <p>Разбирательство: <code>{result.discrepancy_case_id}</code></p>}
  <ul>{next.filter(([key]) => result.accepted_lines.some((row) => positive(row[key]))).map(([key, text]) => <li key={key}>{text}</li>)}</ul>
  <p>Государственная квитанция этим актом не подтверждается. Складское проведение здесь не выполняется.</p>
  <button type="button" title="Вернуться к поставкам после просмотра сохранённого акта" data-help-id="receipt.back" onClick={onNext}>К списку поставок</button>
 </section>;
}
