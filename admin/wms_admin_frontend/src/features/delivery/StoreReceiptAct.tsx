import "./StoreReceiptAct.css";
import {RAW_ADMIN_BASE} from "../../api";
import type {ReceiptResult} from './receiptResult';
const columns=[['shipped','Отправлено'],['accepted','Принято'],['missing','Недостача'],['refused','Отказ'],['damaged','Повреждено'],['extra','Излишек']] as const;
const positive=(value?:string)=>Boolean(value&&/[1-9]/.test(value));
export function StoreReceiptAct({result}:{result:ReceiptResult}) {
 const rawBase=RAW_ADMIN_BASE;
 const next=[['missing','Передайте недостачу диспетчеру для расследования.'],['refused','Согласуйте дальнейшую судьбу отказанного товара с диспетчером.'],['damaged','Сохраните подтверждающие фотографии повреждений и согласуйте возврат.'],['extra','Передайте излишек на разбирательство; он не становится доступным запасом автоматически.']] as const;
 return <section className="driver-st-card store-receipt-act" aria-label="Подтверждённый акт приёмки">
  <h3>{result.status==='DISCREPANCY'?'Акт расхождения при приёмке':'Приёмка подтверждена'}</h3>
  <p>Магазин: {result.store_address}. Грузовое место: {result.root}.</p><p>Операция: <code>{result.operation_id}</code></p>
  <div style={{overflowX:'auto'}}><table><thead><tr><th>Товар / партия</th><th>ЕИ</th>{columns.map(([key,label])=><th key={key}>{label}</th>)}</tr></thead>
   <tbody>{result.accepted_lines.map(row=><tr key={row.line_no}><td>{row.article} / {row.lot_uid}</td><td>{row.base_uom}</td>{columns.map(([key])=><td key={key}>{row[key]??'Не передано'}</td>)}</tr>)}</tbody></table></div>
  {result.discrepancy_case_id&&<p>Разбирательство: <code>{result.discrepancy_case_id}</code>{rawBase&&<> · <a href={rawBase+'/store-investigations.html?case_id='+encodeURIComponent(result.discrepancy_case_id)} target="_blank" rel="noreferrer" title="Досье разбирательства: потребуется отдельный вход с правами диспетчера">Открыть досье диспетчера</a></>}</p>}
  <ul>{next.filter(([key])=>result.accepted_lines.some(row=>positive(row[key]))).map(([key,text])=><li key={key}>{text}</li>)}</ul>
  <p>{result.status==='DISCREPANCY'?'Акт зарегистрирован. Решение о возврате и складское проведение выполняются отдельными штатными действиями.':'Можно перейти к следующему фактически доставленному грузовому месту.'}</p>
  <p>Государственная квитанция этим актом не подтверждается. Повторного списания со склада здесь не выполняется.</p>
 </section>;
}