import {useEffect,useRef,useState} from "react";
import {tareRequest,tareBase} from "./api";
import type {Credentials,Holder} from "./api";
type Balance={pallet_type_id:number;pallet_type_name:string;condition_code:string;custodian_kind:Holder;custodian_id:string;quantity:string;balance_version:number};
const labels:Record<Holder,string>={WAREHOUSE:"Склад",VEHICLE:"Автомобиль",STORE:"Магазин"};
export function TareBalanceSummary({owner,credentials,revision,disabled}:{owner:number;credentials:Credentials;revision:number;disabled:boolean}){
 const [rows,setRows]=useState<Balance[]|null>(null),[busy,setBusy]=useState(false),[message,setMessage]=useState("");
 const epoch=useRef(0),locked=useRef(false),scope=tareBase()+"|"+credentials.username+"|"+owner+"|"+revision,current=useRef(scope);current.current=scope;
 useEffect(()=>{epoch.current++;setRows(null);setMessage("");return()=>{epoch.current++;};},[scope]);
 async function load(){if(disabled||locked.current)return;const serial=++epoch.current,identity=scope;locked.current=true;setBusy(true);
  try{const data=await tareRequest<Balance[]>("/warehouses/"+owner+"/balances",credentials);if(serial===epoch.current&&identity===current.current)setRows(data);}
  catch(e){if(serial===epoch.current&&identity===current.current)setMessage(String(e));}
  finally{locked.current=false;setBusy(false);}
 }
 return <details className="tare-balances"><summary title="Посмотреть ответственность участников по отдельному балансу тары">Баланс выбранного склада-владельца</summary>
 <button disabled={disabled||busy} title="Прочитать текущие учтённые количества; движение не создаётся" onClick={()=>void load()}>Обновить баланс тары</button>
 <p>Количество учтённой тары, до 200 доступных строк. Резервы сборки могут уменьшать доступность к выдаче; окончательную проверку выполняет сервер.</p>
 {rows?.length===0&&<p>Доступных записей баланса нет. Отсутствие записи не означает проведённый пересчёт с нулём.</p>}
 {rows?.map(r=><p key={r.pallet_type_id+":"+r.condition_code+":"+r.custodian_kind+":"+r.custodian_id}>{labels[r.custodian_kind]} {r.custodian_id} · {r.pallet_type_name} · {r.condition_code==="GOOD"?"пригодная":"повреждённая"}: <strong>{r.quantity}</strong> · версия {r.balance_version}</p>)}
 <p role="status">{message}</p></details>;
}
