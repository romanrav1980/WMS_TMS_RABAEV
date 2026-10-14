import type {TareIntent} from "./api";
type Result={operation_id:string;status:string;goods_stock_changed:boolean;resolution_kind?:string;total_tare_changed?:boolean;destination_quantity?:string;short_quantity?:string;tare_balance_changed?:boolean;offer_operation_id?:string;quantity?:string};
export function tareResult(value:unknown,intent:TareIntent):Result {
 if(!value||typeof value!=="object")throw Error("Нет подтверждения операции. Повторите сохранённый запрос.");
 const r=value as Result;
 const status=intent.path==="/offer"?"WAITING_OTHER_PARTICIPANT":intent.path==="/loss-report"?"REPORTED":"POSTED";
 // Заявление о недостаче не меняет общий баланс тары (C-0020): native отдаёт total_tare_changed=null, допустимо false/null.
 if(r.operation_id!==intent.body.operation_id||r.status!==status||r.goods_stock_changed!==false)
  throw Error("Ответ не соответствует сохранённой операции. Повторите тот же запрос.");
 if(intent.path==="/accept"&&(r.offer_operation_id!==intent.body.offer_operation_id||r.quantity!==intent.body.accepted_quantity||!/^[0-9]+$/.test(r.destination_quantity||"")||!/^[0-9]+$/.test(r.short_quantity||"")||r.tare_balance_changed!==true))
  throw Error("Приёмка не подтверждена полным ответом. Повторите сохранённый запрос.");
 if(intent.path==="/offer"&&r.tare_balance_changed!==false)throw Error("Нет подтверждения предложения передачи.");
 if(intent.path==="/loss-report"&&(r.quantity!==intent.body.quantity||r.total_tare_changed===true))throw Error("Заявление о недостаче не подтверждено полным ответом. Повторите сохранённый запрос.");
 if(intent.path==="/damage"&&(r.resolution_kind!=="DAMAGE"||r.total_tare_changed!==false||r.quantity!==intent.body.quantity))throw Error("Повреждение не подтверждено полным ответом. Повторите сохранённый запрос.");
 if(intent.path==="/writeoff"&&(r.resolution_kind!=="WRITE_OFF"||r.total_tare_changed!==true||r.quantity!==intent.body.quantity))throw Error("Списание не подтверждено полным ответом. Повторите сохранённый запрос.");
 return r;
}
