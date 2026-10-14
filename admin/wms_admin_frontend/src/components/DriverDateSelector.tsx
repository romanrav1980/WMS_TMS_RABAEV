export function driverTodayIso() {const d=new Date();return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,"0")}-${String(d.getDate()).padStart(2,"0")}`;}
export function DriverDateSelector({date,onChange}:{date:string;onChange:(date:string)=>void}) {
 function shift(days:number) {
  const next=new Date(date);next.setUTCDate(next.getUTCDate()+days);onChange(next.toISOString().slice(0,10));
 }
 return <div className="driver-date-row">
  <button onClick={()=>shift(-1)}>◄</button>
  <input type="date" value={date} onChange={event=>event.target.value && onChange(event.target.value)}/>
  <button onClick={()=>shift(1)}>►</button>
  <button onClick={()=>onChange(driverTodayIso())} className="driver-today-btn">Сегодня</button>
 </div>;
}
