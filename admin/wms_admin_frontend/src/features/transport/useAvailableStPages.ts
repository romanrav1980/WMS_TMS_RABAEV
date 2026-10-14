import {useCallback,useEffect,useRef,useState} from "react";
import {apiFetch} from "../../api";

// NI02.2 (C-0018): доступные СТ страницами по 200 из Oracle (GET /api/admin/transport/available-sts?page&page_size).
// Сервер не отдаёт общего числа строк: полная страница означает лишь, что следующая страница возможна.
// Новые параметры сбрасывают страницы; ответ на устаревший запрос отбрасывается и не перезаписывает текущий.
export const ST_PAGE_SIZE=200;
export type StPageState<T>={rows:T[];pages:number;hasMore:boolean;loading:boolean;error:string;loadedAt:Date|null};

// Статус ответа: поле status ошибки apiFetch или префикс «NNN:» в тексте — без зависимости от конкретного класса ошибки.
export function httpStatus(e:unknown):number|null{
 const status=(e as {status?:unknown}|null)?.status;
 if(typeof status==="number")return status;
 const m=/^(\d{3})/.exec(e instanceof Error?e.message:"");return m?Number(m[1]):null;
}
export function stPageError(e:unknown):string{
 const status=httpStatus(e);
 if(status!==null){
  if(status===401)return "Нужно войти заново.";
  if(status===403)return "Нет права на просмотр доступных СТ.";
  if(status===422)return "Параметры фильтра отклонены сервером.";
  return "Сервер ответил ошибкой "+status+".";
 }
 return e instanceof Error&&e.name==="AbortError"?"":"Сервер транспорта недоступен. Проверьте соединение.";
}

export function useAvailableStPages<T extends {ST_NUMBER:string}>(query:string){
 const [state,setState]=useState<StPageState<T>>({rows:[],pages:0,hasMore:false,loading:false,error:"",loadedAt:null});
 const serial=useRef(0),controller=useRef<AbortController|null>(null),current=useRef(state);current.current=state;

 const fetchPage=useCallback((page:number,signal:AbortSignal)=>{
  const params=new URLSearchParams(query);params.set("page",String(page));params.set("page_size",String(ST_PAGE_SIZE));
  return apiFetch<T[]>(`/api/admin/transport/available-sts?${params}`,{signal});
 },[query]);

 // Загружает страницы 1..count заново (смена фильтров — 1; обновление после мутации — уже загруженное число).
 const loadPages=useCallback(async(count:number)=>{
  controller.current?.abort();const ctrl=new AbortController();controller.current=ctrl;const mine=++serial.current;
  setState(s=>({...s,loading:true,error:""}));
  const rows:T[]=[];const seen=new Set<string>();let last=0;let pages=0;
  try{
   for(let page=1;page<=Math.max(1,count);page++){
    const data=await fetchPage(page,ctrl.signal);if(mine!==serial.current)return;
    for(const r of data)if(!seen.has(r.ST_NUMBER)){seen.add(r.ST_NUMBER);rows.push(r);}
    pages=page;last=data.length;if(data.length<ST_PAGE_SIZE)break;
   }
   setState({rows,pages,hasMore:last===ST_PAGE_SIZE,loading:false,error:"",loadedAt:new Date()});
  }catch(e){
   if(mine!==serial.current)return;const text=stPageError(e);if(!text)return;
   setState({rows:[],pages:0,hasMore:false,loading:false,error:text,loadedAt:null});
  }
 },[fetchPage]);

 const loadMore=useCallback(async()=>{
  const s=current.current;if(s.loading||!s.hasMore)return;
  const ctrl=new AbortController();controller.current=ctrl;const mine=++serial.current;const page=s.pages+1;
  setState(x=>({...x,loading:true,error:""}));
  try{
   const data=await fetchPage(page,ctrl.signal);if(mine!==serial.current)return;
   setState(x=>{const seen=new Set(x.rows.map(r=>r.ST_NUMBER));return{rows:[...x.rows,...data.filter(r=>!seen.has(r.ST_NUMBER))],pages:page,hasMore:data.length===ST_PAGE_SIZE,loading:false,error:"",loadedAt:new Date()};});
  }catch(e){
   if(mine!==serial.current)return;const text=stPageError(e);if(!text)return;
   setState(x=>({...x,loading:false,error:"Следующая страница не загружена: "+text}));
  }
 },[fetchPage]);

 useEffect(()=>{void loadPages(1);return()=>{controller.current?.abort();};},[loadPages]);
 const reload=useCallback(()=>loadPages(Math.max(1,current.current.pages)),[loadPages]);
 return{...state,loadMore,reload,retry:reload};
}

// Каталог складов для серверного фильтра. Существующий справочник требует права настроек склада;
// без него фильтр остаётся вводом номера склада — список не выдумывается из загруженных строк.
export type WareOption={id:number;name:string};
export function useWarehouseCatalog(){
 const [state,setState]=useState<{items:WareOption[]|null;reason:string}>({items:null,reason:""});
 useEffect(()=>{let alive=true;
  apiFetch<Array<Record<string,unknown>>>("/api/admin/warehouses?limit=500").then(rows=>{if(!alive)return;
   setState({items:rows.map(r=>({id:Number(r.ID??r.id),name:String(r.NAME??r.name??"")})).filter(w=>Number.isSafeInteger(w.id)&&w.id>0).sort((a,b)=>a.id-b.id),reason:""});
  }).catch(e=>{if(alive)setState({items:null,reason:httpStatus(e)===403?"нет права на справочник складов — укажите номер склада":"справочник складов недоступен — укажите номер склада"});});
  return()=>{alive=false;};},[]);
 return state;
}

// Параметры запроса доступных СТ из текущих фильтров диспетчера (всё уходит на сервер, включая склад).
export type StFilters={stDate:string;dateTo:string;wareId:string;unassignedOnly:boolean;addrMask:string;stMask:string;stMaskExclude:boolean;trType:string;assembledOnly:boolean;notAssembledOnly:boolean;maxWeight:number|null;maxVol:number|null;articul:string};
export function availableStQuery(f:StFilters):string{
 const p=new URLSearchParams({stdate:f.stDate});
 if(f.wareId)p.set("ware_id",f.wareId);
 if(!f.unassignedOnly)p.set("unassigned_only","false");
 if(f.dateTo)p.set("date_to",f.dateTo);
 if(f.addrMask)p.set("addr_mask",f.addrMask);
 if(f.stMask){p.set("st_mask",f.stMask);if(f.stMaskExclude)p.set("st_mask_exclude","true");}
 if(f.trType)p.set("transport_type",f.trType);
 if(f.assembledOnly)p.set("assembled_only","true");
 if(f.notAssembledOnly)p.set("not_assembled_only","true");
 if(f.maxWeight!=null)p.set("max_weight_kg",String(f.maxWeight));
 if(f.maxVol!=null)p.set("max_volume_m3",String(f.maxVol));
 if(f.articul)p.set("articul",f.articul);
 return p.toString();
}
// Выбор живёт только среди видимых СТ: скрытые фильтром или устаревшие номера не уходят в назначение.
export function useVisibleSelection(visible:string[],setSelected:(fn:(prev:Set<string>)=>Set<string>)=>void){
 const key=visible.join("\n");
 useEffect(()=>{
  const allowed=new Set(visible);
  setSelected(prev=>{if(prev.size===0)return prev;const next=new Set([...prev].filter(n=>allowed.has(n)));return next.size===prev.size?prev:next;});
  // eslint-disable-next-line react-hooks/exhaustive-deps
 },[key]);
}
