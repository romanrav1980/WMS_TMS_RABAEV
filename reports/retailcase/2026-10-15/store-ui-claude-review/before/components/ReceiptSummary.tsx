import { HelpHint } from "../help/HelpHint";
import type { ReceiptResult } from "../contracts";

const columns = [["shipped", "Отправлено"], ["accepted", "Принято"], ["missing", "Недостача"], ["refused", "Отказ"], ["damaged", "Повреждено"], ["extra", "Излишек"]] as const;
const positive = (value?: string) => Boolean(value && /[1-9]/.test(value));
const next = [
 ["missing", "Передайте недостачу диспетчеру для расследования."],
 ["refused", "Согласуйте дальнейшую судьбу отказанного товара с диспетчером."],
 ["damaged", "Сохраните подтверждающие фотографии повреждений и согласуйте возврат."],
 ["extra", "Передайте излишек на разбирательство; он не становится доступным запасом автоматически."],
] as const;

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
  {result.discrepancy_case_id && <p>Разбирательство: <code>{result.discrepancy_case_id}</code></p>}
  <ul>{next.filter(([key]) => result.accepted_lines.some((row) => positive(row[key]))).map(([key, text]) => <li key={key}>{text}</li>)}</ul>
  <p>Государственная квитанция этим актом не подтверждается. Складское проведение здесь не выполняется.</p>
  <button type="button" title="Вернуться к поставкам после просмотра сохранённого акта" onClick={onNext}>К списку поставок</button>
 </section>;
}
