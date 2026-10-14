from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/tare.py");s=p.read_text(encoding="utf-8-sig")
s=s.replace('return {"trip":trips[0],','customers=self.gateway.fetch_all("select CUSTOMER_ID,CUSTOMER_NAME from RRL_CUSTOMER where ACTIVE=1 order by CUSTOMER_NAME fetch first 200 rows only")\n        return {"customers":customers,"trip":trips[0],')
out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/tare-ledger.html");s=p.read_text(encoding="utf-8-sig").replace('<button id="tareBalances">Показать баланс</button>','<button id="tareBalances">Показать баланс</button><button id="tareDebt">Показать долг магазинов</button>')
out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/tare-ledger.js");s=p.read_text(encoding="utf-8-sig")
s=s.replace(' async function loadOffers()',""" async function debt(){await read(async current=>{const data=await request("/warehouses/"+number("tareWare")+"/store-debt");if(!current())return;el("tareRows").replaceChildren(...data.map(row=>{const p=document.createElement("p");const state={UNCONFIGURED_LEGACY:"Срок исторической передачи не задан",WAITING_NEXT_DELIVERY:"До следующей подтверждённой поставки",OVERDUE:"Просрочено",OPEN:"Срок не наступил"}[row.debt_state]||row.debt_state;p.textContent=row.store_addr+" · "+row.pallet_type_name+" · осталось "+row.outstanding_quantity+" · "+state+(row.effective_due_at?" · срок "+row.effective_due_at+" · "+row.timezone_region:"");return p;}));say("Долг рассчитан по подтверждённым передачам и возвратам.");});}
 async function loadOffers()""",1)
s=s.replace('[["tareContext",loadContext],','[["tareDebt",debt],["tareContext",loadContext],')
out[str(p)]=s
p=Path("admin/wms_admin_frontend/src/features/inventory/api.ts");s=p.read_text(encoding="utf-8-sig")+'''
export type TareDebt={store_addr:string;pallet_type_name:string;outstanding_quantity:string;debt_state:string;effective_due_at:string|null;timezone_region:string|null};
'''
out[str(p)]=s
p=Path("admin/wms_admin_frontend/src/features/inventory/useTare.ts");s=p.read_text(encoding="utf-8-sig").replace('TareContext}','TareContext,TareDebt}')
s=s.replace(' const [context,',' const [debts,setDebts]=useState<TareDebt[]>([]);\n const [context,')
s=s.replace('setRows([]);setContext(null);','setRows([]);setDebts([]);setContext(null);')
s=s.replace(' async function send(',''' async function loadDebt(wareId:number){
  if(locked.current||intentRef.current||!Number.isSafeInteger(wareId)||wareId<1)return;const scope=key;locked.current=true;setBusy(true);
  try{const data=await tareRequest<TareDebt[]>("/warehouses/"+wareId+"/store-debt",credentials);if(current.current===scope)setDebts(data);}
  catch(e){if(current.current===scope)setMessage(String(e));}finally{locked.current=false;setBusy(false);}
 }
 async function send(''',1)
s=s.replace('return{rows,context,','return{rows,debts,loadDebt,context,')
out[str(p)]=s
p=Path("admin/wms_admin_frontend/src/features/inventory/TarePanel.tsx");s=p.read_text(encoding="utf-8-sig")
s=s.replace(' {flow.pending&&', ''' <button disabled={disabled||!owner} onClick={()=>void flow.loadDebt(Number(owner))}>Показать долг магазинов по таре</button>
 {flow.debts.map((row,index)=><p key={row.store_addr+":"+index}>{row.store_addr} · {row.pallet_type_name} · осталось {row.outstanding_quantity} · {({UNCONFIGURED_LEGACY:"Срок исторической передачи не задан",WAITING_NEXT_DELIVERY:"До следующей подтверждённой поставки",OVERDUE:"Просрочено",OPEN:"Срок не наступил"} as Record<string,string>)[row.debt_state]||row.debt_state}{row.effective_due_at?" · до "+new Date(row.effective_due_at).toLocaleString("ru-RU",{timeZone:row.timezone_region||"UTC"}):""}</p>)}
 {flow.pending&&''',1)
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
