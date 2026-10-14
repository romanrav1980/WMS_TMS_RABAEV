import {useCallback,useEffect,useRef,useState} from "react";
import {driverApiBase,driverRequest} from "./driverApi";
import type {DriverCredentials,DriverTrip,DriverStop,DriverOperation} from "./driverApi";
type View="trips"|"sts"|"ops";
type Intent={operation:number;action:"start"|"done";trip:number};
function today(){const d=new Date();return [d.getFullYear(),String(d.getMonth()+1).padStart(2,"0"),String(d.getDate()).padStart(2,"0")].join("-");}
function saved(key:string):Intent|null{
 const raw=localStorage.getItem(key);if(!raw)return null;const v=JSON.parse(raw);
 if(!Number.isSafeInteger(v.operation)||v.operation<1||!Number.isSafeInteger(v.trip)||v.trip<1||!["start","done"].includes(v.action))throw Error("Сохранённая отметка повреждена; требуется разбор исходного запроса.");
 return v;
}
export function useDriverWorkspace(){
 const [credentials,setCredentials]=useState<DriverCredentials|null>(null),[tripDate,setDate]=useState(today);
 const [trips,setTrips]=useState<DriverTrip[]>([]),[selectedTrip,setSelectedTrip]=useState<DriverTrip|null>(null);
 const [tripSts,setSts]=useState<DriverStop[]>([]),[tripOps,setOps]=useState<DriverOperation[]>([]);
 const [activeView,setView]=useState<View>("trips"),[loading,setLoading]=useState(false),[opLoading,setOpLoading]=useState(false),[error,setError]=useState<string|null>(null);
 const [pending,setPending]=useState<Intent|null>(null);const epoch=useRef(0),inFlight=useRef(false);
 const key=useCallback((c:DriverCredentials)=>"driver.fact:"+driverApiBase()+":"+c.username+":"+c.driverId,[]);
 async function login(c:DriverCredentials){
  const version=++epoch.current;setLoading(true);setError(null);
  try{const data=await driverRequest<DriverTrip[]>(c,"/trips?driver_id="+c.driverId+"&trip_date="+tripDate);if(version!==epoch.current)return;
   if(!Array.isArray(data))throw Error("Неверный список рейсов.");const intent=saved(key(c));setCredentials(c);setTrips(data);setPending(intent);
  }catch(e){if(version===epoch.current)setError(String(e));}finally{if(version===epoch.current)setLoading(false);}
 }
 const refresh=useCallback(async()=>{
  if(!credentials)return;const version=++epoch.current;setLoading(true);setError(null);setTrips([]);setSelectedTrip(null);setSts([]);setOps([]);
  try{const data=await driverRequest<DriverTrip[]>(credentials,"/trips?driver_id="+credentials.driverId+"&trip_date="+tripDate);
   if(version===epoch.current){if(!Array.isArray(data))throw Error("Неверный список рейсов.");setTrips(data);setPending(saved(key(credentials)));}}
  catch(e){if(version===epoch.current)setError(String(e));}finally{if(version===epoch.current)setLoading(false);}
 },[credentials,tripDate,key]);
 useEffect(()=>{void refresh();return()=>{epoch.current++;};},[refresh]);
 async function selectTrip(trip:DriverTrip){
  if(!credentials||inFlight.current)return;const version=++epoch.current;setSelectedTrip(trip);setView("ops");setSts([]);setOps([]);setLoading(true);setError(null);
  try{const suffix="?driver_id="+credentials.driverId;const [st,ops]=await Promise.all([driverRequest<DriverStop[]>(credentials,"/trips/"+trip.task_id+"/sts"+suffix),driverRequest<DriverOperation[]>(credentials,"/trips/"+trip.task_id+"/ops"+suffix)]);
   if(version!==epoch.current)return;if(!Array.isArray(st)||!Array.isArray(ops))throw Error("Неверный ответ по рейсу.");setSts(st);setOps(ops);}
  catch(e){if(version===epoch.current)setError(String(e));}finally{if(version===epoch.current)setLoading(false);}
 }
 async function send(intent:Intent){
  if(!credentials||inFlight.current)return;const identity=key(credentials),raw=JSON.stringify(intent),version=epoch.current;let confirmed=false;
  if(localStorage.getItem(identity)!==raw){setError("Сохранённая отметка изменилась. Перечитайте рейсы.");return;}
  inFlight.current=true;setOpLoading(true);setError(null);
  try{const result=await driverRequest<{op_id:number;trip_id:number;driver_id:number;status:string;stock_changed:boolean}>(credentials,"/ops/"+intent.operation+"/"+intent.action+"?driver_id="+credentials.driverId,true);
   if(version!==epoch.current||localStorage.getItem(identity)!==raw)return;
   if(result.op_id!==intent.operation||result.trip_id!==intent.trip||result.driver_id!==credentials.driverId||result.stock_changed!==false||!["in_progress","done"].includes(result.status))throw Error("Ответ не подтверждает исходную отметку.");
   localStorage.removeItem(identity);setPending(null);confirmed=true;
   const ops=await driverRequest<DriverOperation[]>(credentials,"/trips/"+intent.trip+"/ops?driver_id="+credentials.driverId);
   if(version===epoch.current&&selectedTrip?.task_id===intent.trip){if(!Array.isArray(ops))throw Error("Неверный список операций.");setOps(ops);}
  }catch(e){if(version===epoch.current)setError(String(e)+(confirmed?" Отметка подтверждена. Перечитайте рейс.":" Повторите сохранённую отметку; время первого проведения сохранится."));}
  finally{inFlight.current=false;setOpLoading(false);}
 }
 async function markOp(operation:number,action:"start"|"done"){
  if(!credentials||!selectedTrip||inFlight.current)return;
  try{if(saved(key(credentials)))throw Error("Сначала повторите сохранённую отметку.");const intent={operation,action,trip:selectedTrip.task_id};
   localStorage.setItem(key(credentials),JSON.stringify(intent));setPending(intent);await send(intent);
  }catch(e){setError(String(e));}
 }
 function logout(){epoch.current++;setCredentials(null);setTrips([]);setSelectedTrip(null);setSts([]);setOps([]);setPending(null);setError(null);setView("trips");}
 return {driverId:credentials?.driverId??null,tripDate,setTripDate:(day:string)=>{if(!inFlight.current){setView("trips");setDate(day);}},trips,loading,error,setError,selectedTrip,tripSts,tripOps,opLoading,activeView,setActiveView:setView,login,logout,selectTrip,markOp,pending,retry:()=>pending?send(pending):Promise.resolve(),refresh};
}
