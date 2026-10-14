import {useRef,useState} from "react";
import {tareRequest} from "./api";
import type {Credentials,TareBody,TareContext,TareDebt,Holder} from "./api";

type Balance={owner_ware_id:number;pallet_type_id:number;condition_code:"GOOD"|"DAMAGED";custodian_kind:Holder;custodian_id:string;quantity:string;balance_version:number};
export function TareLossForm({tripId,owner,type,context,credentials,disabled,confirm}:{tripId:number;owner:number;type:number;context:TareContext;credentials:Credentials;disabled:boolean;confirm:(body:Omit<TareBody,"operation_id">)=>Promise<void>}){
 const [balances,setBalances]=useState<Balance[]>([]),[debts,setDebts]=useState<TareDebt[]>([]),[selected,setSelected]=useState(""),[claim,setClaim]=useState(""),[quantity,setQuantity]=useState(""),[reason,setReason]=useState(""),[reference,setReference]=useState(""),[scan,setScan]=useState(""),[busy,setBusy]=useState(false),[message,setMessage]=useState("");
 const locked=useRef(false);
 async function load(){if(disabled||locked.current)return;locked.current=true;setBusy(true);try{
  const [rows,loans]=await Promise.all([tareRequest<Balance[]>("/warehouses/"+owner+"/balances",credentials),tareRequest<TareDebt[]>("/warehouses/"+owner+"/store-debt",credentials)]);
  setBalances(rows.filter(row=>row.pallet_type_id===type&&(row.custodian_kind==="STORE"||row.custodian_kind==="VEHICLE"&&row.custodian_id===String(context.trip.vehicle_id))&&BigInt(row.quantity)>0n));setDebts(loans);setSelected("");setClaim("");setMessage("Текущий баланс показан. Заявление исключит количество из доступной тары до независимого решения.");
 }catch(e){setMessage(String(e));}finally{locked.current=false;setBusy(false);}}
 const row=balances[Number(selected)],loans=row?debts.filter(d=>d.pallet_type_id===type&&d.store_addr===row.custodian_id&&d.condition_code===row.condition_code):[];
 async function submit(){if(disabled||busy||selected===""||!row)return;
  const body:Omit<TareBody,"operation_id">={owner_ware_id:owner,pallet_type_id:type,condition:row.condition_code,custodian_kind:row.custodian_kind,custodian_id:row.custodian_id,quantity,expected_version:row.balance_version,reason,decision_reference:reference};
  if(row.custodian_kind==="STORE"){const debt=loans.find(d=>d.claim_key===claim);if(!debt)return;body.source_claim_id=debt.claim_key;}
  if(row.custodian_kind==="VEHICLE"){body.task_id=tripId;body.scan_vehicle=scan;}
  await confirm(body);
 }
 return <fieldset disabled={disabled||busy}><legend>Недостача тары у автомобиля или магазина</legend><button onClick={()=>void load()}>Показать текущую ответственность</button>
 <label>Место и состояние тары<select aria-label="Место и состояние тары" value={selected} onChange={e=>{setSelected(e.target.value);setClaim("");}}><option value="">Выберите баланс</option>{balances.map((r,i)=><option key={r.custodian_kind+":"+r.custodian_id+":"+r.condition_code} value={i}>{r.custodian_kind} {r.custodian_id} · {r.condition_code} · {r.quantity}</option>)}</select></label>
 {selected!==""&&row?.custodian_kind==="STORE"&&<label>Исходная выдача или акт повреждения<select aria-label="Исходная выдача или акт повреждения" value={claim} onChange={e=>setClaim(e.target.value)}><option value="">Выберите исходный долг</option>{loans.map(d=><option key={d.claim_key} value={d.claim_key}>{d.store_addr} · осталось {d.outstanding_quantity} · {d.claim_key}</option>)}</select></label>}
 {selected!==""&&row?.custodian_kind==="VEHICLE"&&<label>Скан машины<input value={scan} onChange={e=>setScan(e.target.value)}/></label>}
 <label>Не обнаружено единиц<input inputMode="numeric" value={quantity} onChange={e=>setQuantity(e.target.value)}/></label><label>Обстоятельства<input maxLength={500} value={reason} onChange={e=>setReason(e.target.value)}/></label><label>Номер акта<input maxLength={60} value={reference} onChange={e=>setReference(e.target.value)}/></label>
 <button disabled={selected===""||!quantity||!reason||!reference||row?.custodian_kind==="STORE"&&!claim||row?.custodian_kind==="VEHICLE"&&!scan} onClick={()=>void submit()}>Заявить недостачу</button><p role="status">{message}</p><p>Окончательное списание или отклонение оформляет другой сотрудник в реестре недостач.</p></fieldset>;
}
