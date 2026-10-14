import type {ReceiptBody,StorePreview} from './contracts';
import {receiptRequest} from './api';
import type {ReceiptCredentials,PendingReceipt} from './contracts';
import {parseReceiptIntent} from './receiptIntentValidation';
export interface ReceiptResultLine {line_no:number;lot_uid:string;article:string;base_uom:string;shipped?:string;accepted:string;missing?:string;refused?:string;damaged?:string;extra?:string}
export interface ReceiptResult {operation_id:string;load_operation_id:string;store_address:string;root:string;status:'ACCEPTED'|'DISCREPANCY';discrepancy_case_id?:string;accepted_lines:ReceiptResultLine[];government_ack_created?:boolean;regulatory_ack_verified?:boolean}
const object=(value:unknown):value is Record<string,unknown>=>Boolean(value&&typeof value==='object');
const quantity=(value:unknown):value is string=>typeof value==='string'&&/^(?:\d+(?:\.\d+)?|\.\d+)$/.test(value);
export function receiptResult(value:unknown,body:ReceiptBody):ReceiptResult {
 if(!object(value)||value.operation_id!==body.operation_id||value.load_operation_id!==body.load_operation_id||value.store_address!==body.store_address||
  !['ACCEPTED','DISCREPANCY'].includes(String(value.status))||typeof value.root!=='string'||!Array.isArray(value.accepted_lines)||!value.accepted_lines.length||value.accepted_lines.length>200||
  (value.status==='DISCREPANCY'&&(typeof value.discrepancy_case_id!=='string'||!value.discrepancy_case_id)))throw Error('Ответ сервера не подтверждает исходную приёмку. Сохранённый запрос оставлен для повтора.');
 const lines=value.accepted_lines.map((row:unknown)=>{
  if(!object(row)||!Number.isSafeInteger(row.line_no)||typeof row.lot_uid!=='string'||typeof row.article!=='string'||typeof row.base_uom!=='string'||
    !quantity(row.accepted??row.accepted_quantity)||['shipped','missing','refused','damaged','extra'].some(key=>row[key]!==undefined&&!quantity(row[key])))throw Error('Сервер вернул неподтверждённые количества акта. Повторите сохранённую операцию.');
  if(value.status==='DISCREPANCY'&&['shipped','missing','refused','damaged','extra'].some(key=>!quantity(row[key])))throw Error('В акте расхождения отсутствуют количества. Повторите исходный запрос.');
  return {...row,accepted:row.accepted??row.accepted_quantity} as unknown as ReceiptResultLine;
 });
 return {...value,accepted_lines:lines} as unknown as ReceiptResult;
}
export async function refreshReceiptCorrection(key:string,pending:PendingReceipt,address:string,credentials:ReceiptCredentials):Promise<{raw:string;preview:StorePreview}> {
 const raw=localStorage.getItem(key);
 if(!raw||!pending.confirmedRejection||JSON.stringify(parseReceiptIntent(raw,address))!==JSON.stringify(pending))throw Error('Подтверждённый отказ или сохранённая команда изменились.');
 const preview=await receiptRequest<StorePreview>('/preview?load_operation_id='+encodeURIComponent(pending.body.load_operation_id)+'&store_address='+encodeURIComponent(address),credentials);
 if(preview.load_operation_id!==pending.body.load_operation_id||preview.store_address!==address||!preview.composition_signature||!Array.isArray(preview.snapshot?.nodes))throw Error('Текущий состав не подтверждён. Исходный ввод сохранён.');
 return {raw,preview};
}